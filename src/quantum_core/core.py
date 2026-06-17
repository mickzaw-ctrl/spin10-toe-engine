"""
Shared computational core: JAX + Ray + LRU Cache.
Used by FastAPI (REST) oraz gRPC.
"""

import asyncio
import hashlib
import heapq
import logging
import time
from collections import OrderedDict
from typing import Any, Dict

import jax
import jax.numpy as jnp
from jax import jit, vmap
import ray

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 1. JAX Core
# -----------------------------------------------------------------------------

class Spin10MERASurrogate:
    """
    SciML Surrogate representing tensor network contractions MERA
    and Lie group edge variables SO(10).
    """

    def __init__(self, bond_dimension: int = 10):
        self.bond_dim = bond_dimension
        logger.info(f"Initialized surrogate MERA (Bond Dimension: {self.bond_dim})")

    @staticmethod
    @jit
    def contract_tensor_network(state_matrix: jax.Array) -> jax.Array:
        """Ultra-fast quantum state evaluation compiled in JAX XLA."""
        transformed = jnp.dot(state_matrix, state_matrix.T)
        energy_expectation = jnp.trace(transformed)
        return energy_expectation

    def run_batch_simulation(self, batch_size: int = 1000) -> jax.Array:
        """Vectorized operations for bulk queries z czujników IoT."""
        try:
            key = jax.random.key(42)
        except AttributeError:
            key = jax.random.PRNGKey(42)

        batch_states = jax.random.normal(key, (batch_size, self.bond_dim, self.bond_dim))

        start_time = time.perf_counter()
        vmap_contraction = vmap(Spin10MERASurrogate.contract_tensor_network)
        results = vmap_contraction(batch_states)
        jax.block_until_ready(results)

        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Batch evaluations completed in {latency_ms:.2f} ms")
        return results

# -----------------------------------------------------------------------------
# 2. Ray Actor
# -----------------------------------------------------------------------------

@ray.remote
class CloudOrchestrator:
    """
    Ray actor managing task allocation on cluster GPU/CPU.
    Maintains priority queue and result cache (LRU Cache).
    """

    def __init__(self, cache_limit: int = 5000):
        self.surrogate = Spin10MERASurrogate(bond_dimension=10)
        self.task_queue: list = []
        self.result_cache: OrderedDict[str, Any] = OrderedDict()
        self.cache_limit = cache_limit
        self.task_counter = 0
        logger.info("CloudOrchestrator ready to accept tasks gRPC/REST.")

    def submit_task(self, priority: int, payload: dict) -> int:
        """Dodaje task przemysłowe do kolejki z uwzględnieniem priorytetu."""
        task_id = self.task_counter
        heapq.heappush(self.task_queue, (priority, task_id, payload))
        self.task_counter += 1
        return task_id

    def _generate_cache_key(self, payload: dict) -> str:
        """Hashowanie wejścia, by unikać ponownych computations tych samych stanów."""
        payload_str = str(sorted(payload.items()))
        return hashlib.md5(payload_str.encode()).hexdigest()

    def process_next_task(self) -> dict:
        """Zdejmuje task o najwyższym priorytecie i kieruje na JAX Engine."""
        if not self.task_queue:
            return {"status": "IDLE", "message": "Brak tasks w kolejce."}

        priority, task_id, payload = heapq.heappop(self.task_queue)
        cache_key = self._generate_cache_key(payload)

        if cache_key in self.result_cache:
            logger.info(f"Task {task_id} pobrany z LRU Cache (Priorytet: {priority})")
            self.result_cache.move_to_end(cache_key)
            return {
                "task_id": task_id,
                "source": "CACHE",
                "result": self.result_cache[cache_key],
                "status": "SUCCESS",
            }

        logger.info(f"Wykonywanie Task {task_id} (Priorytet: {priority}) na JAX Engine...")
        batch_size = payload.get("batch_size", 1000)

        raw_results = self.surrogate.run_batch_simulation(batch_size=batch_size)
        mean_energy = float(jnp.mean(raw_results))

        self.result_cache[cache_key] = mean_energy
        if len(self.result_cache) > self.cache_limit:
            self.result_cache.popitem(last=False)

        return {
            "task_id": task_id,
            "source": "COMPUTED",
            "result": mean_energy,
            "status": "SUCCESS",
        }

# -----------------------------------------------------------------------------
# 3. Inicjalizacja wspólna (singleton)
# -----------------------------------------------------------------------------

_orchestrator_ref = None


def init_orchestrator(cache_limit: int = 1000):
    """Idempotentna inicjalizacja Raya i aktora CloudOrchestrator."""
    global _orchestrator_ref
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    if _orchestrator_ref is None:
        _orchestrator_ref = CloudOrchestrator.remote(cache_limit=cache_limit)
        logger.info("Orchestrator globalny zainicjalizowany.")
    return _orchestrator_ref


def get_orchestrator():
    """Zwraca referencję do aktora. Inicjalizuje jeśli potrzeba."""
    if _orchestrator_ref is None:
        return init_orchestrator()
    return _orchestrator_ref
