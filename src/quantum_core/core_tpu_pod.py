"""
SHZ Spin10 – TPU Pod Core (pjit / mesh sharding)
=================================================
Shardowanie batchu na osi 'data' TPU Pod.
Auto-detect API: jax.sharding (JAX 0.4+) > jax.experimental.pjit (legacy) > jit fallback.
Mock mesh na CPU dla developmentu (emulacja wielu urządzeń).
"""

import logging
import time
from typing import Optional, Tuple

import jax
import jax.numpy as jnp
import numpy as np

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 0. API sharding – auto-detect
# -----------------------------------------------------------------------------

HAS_MODERN_SHARDING = False
HAS_PJIT = False

# Modern JAX 0.4+ (jax.sharding)
try:
    from jax.sharding import Mesh, PartitionSpec, NamedSharding
    from jax.experimental.mesh_utils import create_device_mesh
    HAS_MODERN_SHARDING = True
    logger.info("[TPU Pod] Using modern jax.sharding API.")
except ImportError:
    logger.info("[TPU Pod] jax.sharding not available.")

# Legacy JAX (pjit)
if not HAS_MODERN_SHARDING:
    try:
        from jax.experimental.pjit import pjit, PartitionSpec
        from jax.experimental.maps import Mesh
        HAS_PJIT = True
        logger.info("[TPU Pod] Using legacy jax.experimental.pjit API.")
    except ImportError:
        logger.info("[TPU Pod] pjit not available – falling back to standard jit.")

# -----------------------------------------------------------------------------
# 1. Mesh factory
# -----------------------------------------------------------------------------

def make_tpu_mesh(devices=None, axis_names=('data', 'model')) -> Optional[Tuple]:
    """Tworzy mesh dla TPU Pod lub mock mesh na CPU."""
    if devices is None:
        devices = jax.devices()
    n = len(devices)

    if n == 1:
        return None  # single device – no mesh

    # CPU mock / multi-host TPU: create mesh from available devices
    ndim = len(axis_names)
    if ndim == 1:
        shape = (n,)
    else:
        # square-ish 2D grid
        d1 = int(np.sqrt(n))
        while n % d1 != 0 and d1 > 1:
            d1 -= 1
        d2 = n // d1
        shape = (d1, d2)

    if HAS_MODERN_SHARDING:
        try:
            mesh_devices = create_device_mesh(shape, devices)
            return Mesh(mesh_devices, axis_names)
        except Exception:
            pass  # fallback below
    if HAS_PJIT:
        try:
            mesh_devices = np.array(devices).reshape(shape)
            return Mesh(mesh_devices, axis_names)
        except Exception:
            pass

    return None

# -----------------------------------------------------------------------------
# 2. Surrogate TPU Pod
# -----------------------------------------------------------------------------

class Spin10TPUPodSurrogate:
    """
    MERA surrogate z shardowaniem batchu na TPU Pod.
    - Bond dim = 10 (replikowana na wszystkich devices – za mała by shardować).
    - Batch shardowany na osi 'data'.
    - Wsparcie dla mock mesh na CPU (development).
    """

    def __init__(self, bond_dim: int = 10, use_bfloat16: bool = False):
        self.bond_dim = bond_dim
        self.dtype = jnp.bfloat16 if use_bfloat16 else jnp.float32
        self.devices = jax.devices()
        self.n_devices = len(self.devices)

        self.mesh = make_tpu_mesh(self.devices, axis_names=('data', 'model'))
        self._has_mesh = self.mesh is not None

        if self._has_mesh and HAS_MODERN_SHARDING:
            logger.info(f"[TPU Pod] Mesh shape: {self.mesh.shape} | devices: {self.n_devices}")
            # Shard batch on 'data', replicate bond dims
            self.in_spec = NamedSharding(self.mesh, PartitionSpec('data', None, None))
            self.out_spec = NamedSharding(self.mesh, PartitionSpec('data',))
        elif self._has_mesh and HAS_PJIT:
            logger.info(f"[TPU Pod] Legacy pjit mesh: {self.mesh.shape}")
            self.in_spec = PartitionSpec('data', None, None)
            self.out_spec = PartitionSpec('data',)
        else:
            self.in_spec = None
            self.out_spec = None
            logger.info(f"[TPU Pod] No mesh – single-device fallback (devices={self.n_devices}).")

        # Build kernel
        self._kernel = self._build_kernel()

    @staticmethod
    def _contract_kernel(state_matrix: jax.Array) -> jax.Array:
        """XLA kernel: batched einsum + trace."""
        if state_matrix.ndim == 2:
            transformed = jnp.dot(state_matrix, state_matrix.T)
            return jnp.trace(transformed)
        # (B, N, N) -> (B,)
        transformed = jnp.einsum('bij,bkj->bik', state_matrix, state_matrix)
        return jnp.trace(transformed, axis1=1, axis2=2)

    def _build_kernel(self):
        if self._has_mesh and HAS_MODERN_SHARDING:
            # Modern API: jit with sharding constraints
            return jax.jit(
                self._contract_kernel,
                in_shardings=self.in_spec,
                out_shardings=self.out_spec
            )
        elif self._has_mesh and HAS_PJIT:
            # Legacy API: pjit
            return pjit(
                self._contract_kernel,
                in_axis_resources=(self.in_spec,),
                out_axis_resources=self.out_spec
            )
        else:
            # Single-device fallback (also works on CPU mock)
            return jax.jit(self._contract_kernel)

    def _pad_batch(self, batch_size: int) -> int:
        """Wyrównaj batch do wielokrotności liczby urządzeń na osi data."""
        if not self._has_mesh:
            return batch_size
        data_size = self.mesh.shape.get('data', 1)
        if data_size <= 1:
            return batch_size
        if batch_size % data_size == 0:
            return batch_size
        padded = ((batch_size // data_size) + 1) * data_size
        logger.info(f"[TPU Pod] Padded batch: {batch_size} -> {padded} (data axis={data_size})")
        return padded

    def run_batch(self, batch_size: int = 1000, seed: int = 42) -> float:
        """Generuje batch, sharduje, wykonuje kernel, zwraca mean energy."""
        actual_batch = self._pad_batch(batch_size)

        try:
            key = jax.random.key(seed)
        except AttributeError:
            key = jax.random.PRNGKey(seed)

        batch = jax.random.normal(
            key, (actual_batch, self.bond_dim, self.bond_dim), dtype=self.dtype
        )

        # Shard / device_put
        if self._has_mesh and HAS_MODERN_SHARDING:
            batch = jax.device_put(batch, self.in_spec)
        elif self._has_mesh and HAS_PJIT:
            # Legacy: device_put under mesh context not needed, pjit handles it
            pass
        else:
            # Single device: ensure on default device
            batch = jax.device_put(batch)

        start = time.perf_counter()
        results = self._kernel(batch)
        jax.block_until_ready(results)
        elapsed = (time.perf_counter() - start) * 1000

        # Jeśli padding, bierzemy tylko pierwsze batch_size wyników (jeśli shape > batch_size)
        # W praktyce dla trace wynik to (B,), mean jest po wszystkich
        mean_val = float(jnp.mean(results[:batch_size] if results.shape[0] > batch_size else results))

        logger.info(
            f"[TPU Pod] batch={batch_size} (padded={actual_batch}) | "
            f"mesh={getattr(self.mesh, 'shape', 'single')} | "
            f"devices={self.n_devices} | time={elapsed:.2f}ms | result={mean_val:.2f}"
        )
        return mean_val

# -----------------------------------------------------------------------------
# 3. Ray Actor – TPU Pod
# -----------------------------------------------------------------------------

import ray

@ray.remote
class CloudOrchestratorTPU:
    """Aktor Ray zarządzający TPU Pod surrogate."""

    def __init__(self, bond_dim: int = 10, use_bfloat16: bool = False):
        self.surrogate = Spin10TPUPodSurrogate(
            bond_dimension=bond_dim, use_bfloat16=use_bfloat16
        )
        logger.info(f"[ActorTPU] Initialized with {self.surrogate.n_devices} devices.")

    def run_batch(self, batch_size: int = 1000, seed: int = 42) -> dict:
        result = self.surrogate.run_batch(batch_size, seed)
        return {
            "status": "SUCCESS",
            "source": "COMPUTED",
            "result": result,
            "devices": self.surrogate.n_devices,
            "mesh": str(getattr(self.surrogate.mesh, 'shape', 'single')),
        }

# -----------------------------------------------------------------------------
# 4. Singleton
# -----------------------------------------------------------------------------

_tpu_actor = None

def init_tpu_actor(bond_dim=10, use_bfloat16=False):
    global _tpu_actor
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    if _tpu_actor is None:
        _tpu_actor = CloudOrchestratorTPU.remote(bond_dim=bond_dim, use_bfloat16=use_bfloat16)
    return _tpu_actor

def get_tpu_actor(bond_dim=10, use_bfloat16=False):
    if _tpu_actor is None:
        return init_tpu_actor(bond_dim=bond_dim, use_bfloat16=use_bfloat16)
    return _tpu_actor
