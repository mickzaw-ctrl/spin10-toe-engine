"""
SHZ Spin10 – GPU Actor Pool + Load balancer
============================================
Horizontal scaling: N aktorów Ray, z których każdy zajmuje 1 GPU.
Load balancer: priority P=1 -> least loaded, P=5 -> round-robin.
Auto-fallback to CPU when no GPU available.
"""

import asyncio
import hashlib
import heapq
import logging
import time
from collections import OrderedDict
from functools import lru_cache
from typing import Any, Dict, List, Optional

import jax
import jax.numpy as jnp
from jax import jit, vmap
import ray

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 0. Device detection per actor
# -----------------------------------------------------------------------------

def _pick_device(gpu_id: int = 0):
    """Selects specific GPU for actor."""
    try:
        gpus = jax.devices("gpu")
    except RuntimeError:
        gpus = []
    if gpus and gpu_id < len(gpus):
        return gpus[gpu_id]
    try:
        tpus = jax.devices("tpu")
    except RuntimeError:
        tpus = []
    if tpus:
        return tpus[0]
    try:
        cpus = jax.devices("cpu")
    except RuntimeError:
        cpus = []
    if cpus:
        return cpus[0]
    return jax.devices()[0]

# -----------------------------------------------------------------------------
# 1. Surrogate (per-actor, bound to device)
# -----------------------------------------------------------------------------

class Spin10MERASurrogateGPU:
    """Surogat związany z konkretnym GPU/CPU."""

    def __init__(self, device: jax.Device, bond_dimension: int = 10, use_bfloat16: bool = False):
        self.device = device
        self.bond_dim = bond_dimension
        self.dtype = jnp.bfloat16 if use_bfloat16 else jnp.float32
        logger.info(f"[SurrogateGPU] device={device}, bond={bond_dimension}, dtype={self.dtype}")

    @staticmethod
    @jit
    def _contract(state_matrix: jax.Array) -> jax.Array:
        if state_matrix.ndim == 2:
            transformed = jnp.dot(state_matrix, state_matrix.T)
            return jnp.trace(transformed)
        transformed = jnp.einsum('bij,bkj->bik', state_matrix, state_matrix)
        return jnp.trace(transformed, axis1=1, axis2=2)

    @lru_cache(maxsize=10_000)
    def _cached_mean_energy(self, batch_size: int, bond_dim: int, seed: int) -> float:
        return float(self._compute_mean_energy(batch_size, bond_dim, seed))

    def _compute_mean_energy(self, batch_size: int, bond_dim: int, seed: int) -> float:
        try:
            key = jax.random.key(seed)
        except AttributeError:
            key = jax.random.PRNGKey(seed)

        shape = (batch_size, bond_dim, bond_dim)
        batch_states = jax.random.normal(key, shape, dtype=self.dtype)
        batch_states = jax.device_put(batch_states, self.device)

        start = time.perf_counter()
        vmapped = vmap(self._contract)
        results = vmapped(batch_states)
        jax.block_until_ready(results)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(f"[JIT] device={self.device.platform}, batch={batch_size}, "
                    f"bond={bond_dim}, time={elapsed:.2f}ms")
        return jnp.mean(results)

    def run_batch(self, batch_size: int = 1000, seed: int = 42) -> float:
        return self._cached_mean_energy(batch_size, self.bond_dim, seed)

# -----------------------------------------------------------------------------
# 2. Ray Actor – 1 GPU per actor
# -----------------------------------------------------------------------------

@ray.remote(num_gpus=1)
class CloudOrchestratorGPU:
    """Aktor zarezerwowany na 1 GPU. Trzyma własną kolejkę i cache."""

    def __init__(self, gpu_id: int = 0, cache_limit: int = 100_000,
                 bond_dim: int = 10, use_bfloat16: bool = False):
        self.device = _pick_device(gpu_id)
        self.surrogate = Spin10MERASurrogateGPU(
            device=self.device, bond_dimension=bond_dim, use_bfloat16=use_bfloat16
        )
        self.task_queue: list = []
        self.result_cache: OrderedDict[str, Any] = OrderedDict()
        self.cache_limit = cache_limit
        self.task_counter = 0
        logger.info(f"[ActorGPU] id={gpu_id}, device={self.device}")

    def submit_task(self, priority: int, payload: dict) -> int:
        task_id = self.task_counter
        heapq.heappush(self.task_queue, (priority, task_id, payload))
        self.task_counter += 1
        return task_id

    def queue_size(self) -> int:
        return len(self.task_queue)

    def _cache_key(self, payload: dict) -> str:
        return hashlib.md5(str(sorted(payload.items())).encode()).hexdigest()

    def process_next_task(self) -> dict:
        if not self.task_queue:
            return {"status": "IDLE", "message": "Brak tasks"}

        priority, task_id, payload = heapq.heappop(self.task_queue)
        ckey = self._cache_key(payload)

        if ckey in self.result_cache:
            self.result_cache.move_to_end(ckey)
            return {
                "task_id": task_id, "source": "CACHE",
                "result": self.result_cache[ckey], "status": "SUCCESS",
            }

        batch_size = payload.get("batch_size", 1000)
        seed = payload.get("seed", 42)
        result = self.surrogate.run_batch(batch_size, seed)

        self.result_cache[ckey] = result
        if len(self.result_cache) > self.cache_limit:
            self.result_cache.popitem(last=False)

        return {
            "task_id": task_id, "source": "COMPUTED",
            "result": result, "status": "SUCCESS",
        }

# -----------------------------------------------------------------------------
# 3. Pool + Load balancer
# -----------------------------------------------------------------------------

class GPUActorPool:
    """
    Pool aktorów GPU + Load balancer.
    - P=1 (CRITICAL) -> aktor z najmniejszą kolejką.
    - P=5 (BACKGROUND) -> round-robin.
    Fallback: jeśli brak GPU, tworzy 1 aktor na CPU.
    """

    def __init__(self, num_actors: Optional[int] = None,
                 cache_limit: int = 100_000, bond_dim: int = 10,
                 use_bfloat16: bool = False):
        import os
        mock_gpus = int(os.environ.get("MOCK_GPUS", "0"))

        try:
            gpus = jax.devices("gpu")
        except RuntimeError:
            gpus = []
        try:
            tpus = jax.devices("tpu")
        except RuntimeError:
            tpus = []
        self.has_accelerator = bool(gpus or tpus)

        if mock_gpus > 0:
            self.num_actors = num_actors or mock_gpus
            logger.info(f"MOCK_GPUS={mock_gpus} – wymuszam {self.num_actors} aktorów (CPU fallback per actor).")
        elif self.has_accelerator:
            self.num_actors = num_actors or len(gpus) or len(tpus)
        else:
            self.num_actors = 1  # fallback CPU
            logger.warning("No GPU/TPU — pool fallback to 1 CPU actor.")

        self.actors: List = []
        for i in range(self.num_actors):
            try:
                actor = CloudOrchestratorGPU.remote(
                    gpu_id=i, cache_limit=cache_limit,
                    bond_dim=bond_dim, use_bfloat16=use_bfloat16
                )
                self.actors.append(actor)
            except Exception as exc:
                logger.error(f"Nie udało się stworzyć aktora {i}: {exc}")
                break

        self._rr = 0
        logger.info(f"[Pool] Created actors.")

    async def submit(self, priority: int, payload: dict) -> int:
        """Zwraca task_id z wybranego aktora."""
        actor = self._pick_actor(priority)
        return await actor.submit_task.remote(priority, payload)

    async def process(self) -> dict:
        """Przetwarza następne task z aktora wybranego przez Load balancer."""
        # Dla uproszczenia: process_next_task na tym samym akorze co submit
        # W produkcji: śledzenie task_id -> actor mapping
        actor = self._pick_actor(1)  # default: najmniej obciążony
        return await actor.process_next_task.remote()

    def _pick_actor(self, priority: int):
        if priority == 1 and len(self.actors) > 1:
            # Najmniej obciążony – ale asynchronicznie; w MVP round-robin
            # W produkcji: ray.get(queue_size) + min
            idx = self._rr % len(self.actors)
            self._rr += 1
            return self.actors[idx]
        # Round-robin dla P=5 lub gdy 1 actor
        idx = self._rr % len(self.actors)
        self._rr += 1
        return self.actors[idx]

    async def health(self) -> dict:
        return {
            "actors": len(self.actors),
            "accelerator": self.has_accelerator,
            "platform": jax.devices()[0].platform,
        }

# -----------------------------------------------------------------------------
# 4. Singleton wrapper (backward compat)
# -----------------------------------------------------------------------------

_pool: Optional[GPUActorPool] = None

def init_pool(num_actors: Optional[int] = None, **kwargs) -> GPUActorPool:
    global _pool
    if not ray.is_initialized():
        # Dla lokalnego developmentu: symulacja 8 GPU jeśli flaga
        import os
        mock_gpus = int(os.environ.get("MOCK_GPUS", "0"))
        if mock_gpus > 0:
            ray.init(num_gpus=mock_gpus, ignore_reinit_error=True)
        else:
            ray.init(ignore_reinit_error=True)
    if _pool is None:
        _pool = GPUActorPool(num_actors=num_actors, **kwargs)
    return _pool

def get_pool() -> GPUActorPool:
    if _pool is None:
        return init_pool()
    return _pool
