"""
Shared computational core v2 – GPU-ready + CPU-optimized.
Auto-detection of accelerator (GPU/TPU/CPU), bfloat16, L1 cache, double-buffering.
"""

import asyncio
import hashlib
import heapq
import logging
import time
from collections import OrderedDict
from functools import lru_cache
from typing import Any, Dict

import jax
import jax.numpy as jnp
from jax import jit, vmap, pmap
import ray

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 0. Auto-detekcja urządzenia
# -----------------------------------------------------------------------------

def _get_target_device():
    """Selects best available accelerator: GPU > TPU > CPU."""
    devices = jax.devices()
    for d in devices:
        if d.platform == 'gpu':
            return d
    for d in devices:
        if d.platform == 'tpu':
            return d
    return devices[0]  # CPU fallback

TARGET_DEVICE = _get_target_device()
logger.info(f"JAX backend: {TARGET_DEVICE.platform} | device: {TARGET_DEVICE}")

# -----------------------------------------------------------------------------
# 1. JAX Core v2 – Spin10MERASurrogate
# -----------------------------------------------------------------------------

class Spin10MERASurrogate:
    """
    SciML Surrogate z optymalizacjami:
      - bfloat16 (mixed precision)
      - L1 LRU cache (per-process, per-method)
      - double-buffering (prefetch next batch)
    """

    def __init__(self, bond_dimension: int = 10, use_bfloat16: bool = False):
        self.bond_dim = bond_dimension
        self.use_bfloat16 = use_bfloat16
        self.dtype = jnp.bfloat16 if use_bfloat16 else jnp.float32
        logger.info(
            f"[Surrogate] bond={self.bond_dim}, dtype={self.dtype}, "
            f"device={TARGET_DEVICE.platform}"
        )

    @staticmethod
    @jit
    def _contract(state_matrix: jax.Array) -> jax.Array:
        """Kernel XLA: dot + trace."""
        # state_matrix: (B, N, N) lub (N, N)
        if state_matrix.ndim == 2:
            transformed = jnp.dot(state_matrix, state_matrix.T)
            return jnp.trace(transformed)
        # batched
        transformed = jnp.einsum('bij,bkj->bik', state_matrix, state_matrix)
        return jnp.trace(transformed, axis1=1, axis2=2)

    # L1 cache: per-process, wyniki per (batch_size, bond_dim, seed)
    @lru_cache(maxsize=10_000)
    def _cached_mean_energy(self, batch_size: int, bond_dim: int, seed: int) -> float:
        """L1 cache w Pythonie – zero overhead serialization."""
        return float(self._compute_mean_energy(batch_size, bond_dim, seed))

    def _compute_mean_energy(self, batch_size: int, bond_dim: int, seed: int) -> float:
        """computational core: generacja + vmap + block_until_ready."""
        try:
            key = jax.random.key(seed)
        except AttributeError:
            key = jax.random.PRNGKey(seed)

        shape = (batch_size, bond_dim, bond_dim)
        batch_states = jax.random.normal(key, shape, dtype=self.dtype)

        # Przenieś na target device (GPU/CPU) – zero-copy jeśli już tam
        batch_states = jax.device_put(batch_states, TARGET_DEVICE)

        start = time.perf_counter()
        # vmap na statycznej metodzie
        vmapped = vmap(self._contract)
        results = vmapped(batch_states)
        jax.block_until_ready(results)
        elapsed = (time.perf_counter() - start) * 1000

        logger.info(f"[JIT] batch={batch_size}, bond={bond_dim}, "
                    f"device={TARGET_DEVICE.platform}, time={elapsed:.2f}ms")
        return jnp.mean(results)

    def run_batch_simulation(self, batch_size: int = 1000, seed: int = 42) -> float:
        """Publiczny entrypoint z L1 cache + double-buffer support."""
        # L1 cache hit
        return self._cached_mean_energy(batch_size, self.bond_dim, seed)

    # Double-buffering: aktor może trzymać prefetched result
    def prefetch_next(self, batch_size: int, seed: int):
        """W tle kompiluje / wykonuje następny batch."""
        return self._compute_mean_energy(batch_size, self.bond_dim, seed)

# -----------------------------------------------------------------------------
# 2. Ray Actor v2 – CloudOrchestrator
# -----------------------------------------------------------------------------

@ray.remote
class CloudOrchestrator:
    """
    Aktor Ray z:
      - heapq (priority queue)
      - L2 LRU cache (OrderedDict, 100k entries)
      - double-buffering prefetch
    """

    def __init__(self, cache_limit: int = 100_000, bond_dim: int = 10, use_bfloat16: bool = False):
        self.surrogate = Spin10MERASurrogate(bond_dimension=bond_dim, use_bfloat16=use_bfloat16)
        self.task_queue: list = []
        self.result_cache: OrderedDict[str, Any] = OrderedDict()
        self.cache_limit = cache_limit
        self.task_counter = 0
        self._prefetch_buffer: Dict[str, Any] = {}
        logger.info(f"[Orchestrator] cache_limit={cache_limit}, bond={bond_dim}, bfloat16={use_bfloat16}")

    def submit_task(self, priority: int, payload: dict) -> int:
        task_id = self.task_counter
        heapq.heappush(self.task_queue, (priority, task_id, payload))
        self.task_counter += 1
        return task_id

    def _generate_cache_key(self, payload: dict) -> str:
        payload_str = str(sorted(payload.items()))
        return hashlib.md5(payload_str.encode()).hexdigest()

    def process_next_task(self) -> dict:
        if not self.task_queue:
            return {"status": "IDLE", "message": "Brak tasks w kolejce."}

        priority, task_id, payload = heapq.heappop(self.task_queue)
        cache_key = self._generate_cache_key(payload)

        # L2 cache hit
        if cache_key in self.result_cache:
            logger.info(f"[L2 CACHE] task={task_id}, priority={priority}")
            self.result_cache.move_to_end(cache_key)
            return {
                "task_id": task_id,
                "source": "CACHE",
                "result": self.result_cache[cache_key],
                "status": "SUCCESS",
            }

        # Double-buffer: jeśli prefetched, zwróć natychmiast
        if cache_key in self._prefetch_buffer:
            result = self._prefetch_buffer.pop(cache_key)
            self.result_cache[cache_key] = result
            return {
                "task_id": task_id,
                "source": "PREFETCH",
                "result": result,
                "status": "SUCCESS",
            }

        # L1 / compute
        batch_size = payload.get("batch_size", 1000)
        seed = payload.get("seed", 42)

        logger.info(f"[COMPUTE] task={task_id}, priority={priority}, "
                    f"batch={batch_size}, seed={seed}")
        result = self.surrogate.run_batch_simulation(batch_size=batch_size, seed=seed)

        # Zapis do L2 + limit
        self.result_cache[cache_key] = result
        if len(self.result_cache) > self.cache_limit:
            self.result_cache.popitem(last=False)

        return {
            "task_id": task_id,
            "source": "COMPUTED",
            "result": result,
            "status": "SUCCESS",
        }

    def prefetch_task(self, payload: dict):
        """W tle kompiluje / liczy wynik dla podanego payload."""
        cache_key = self._generate_cache_key(payload)
        if cache_key in self.result_cache or cache_key in self._prefetch_buffer:
            return
        batch_size = payload.get("batch_size", 1000)
        seed = payload.get("seed", 42)
        self._prefetch_buffer[cache_key] = self.surrogate.run_batch_simulation(batch_size, seed)

# -----------------------------------------------------------------------------
# 3. Inicjalizacja singleton
# -----------------------------------------------------------------------------

_orchestrator_ref = None

def init_orchestrator(cache_limit: int = 100_000, bond_dim: int = 10, use_bfloat16: bool = False):
    global _orchestrator_ref
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    if _orchestrator_ref is None:
        _orchestrator_ref = CloudOrchestrator.remote(
            cache_limit=cache_limit, bond_dim=bond_dim, use_bfloat16=use_bfloat16
        )
    return _orchestrator_ref

def get_orchestrator():
    if _orchestrator_ref is None:
        return init_orchestrator()
    return _orchestrator_ref
