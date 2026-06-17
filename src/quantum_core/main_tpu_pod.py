"""
SHZ Spin10 – TPU Pod Entrypoint
================================
REST + gRPC z TPU Pod surrogate (mesh sharding / pjit).
Auto-fallback na single-device CPU jeśli brak TPU / multi-device.
"""

import asyncio
import logging
import os

import jax
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

import grpc_server_tpu
from core_tpu_pod import Spin10TPUPodSurrogate, get_tpu_actor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [SciML TPU] %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# FastAPI
# -----------------------------------------------------------------------------

tpu_actor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tpu_actor
    tpu_actor = get_tpu_actor(bond_dim=10, use_bfloat16=False)
    logger.info("FastAPI TPU Pod: actor ready.")
    yield
    import ray
    ray.shutdown()
    logger.info("FastAPI TPU Pod: shutdown.")

app = FastAPI(
    title="SHZ Spin10 TPU Pod Gateway",
    version="3.0.0-tpu-pod",
    lifespan=lifespan,
)

@app.post("/api/v1/simulate")
async def trigger_simulation(batch_size: int = 1000):
    if tpu_actor is None:
        return {"status": "ERROR", "message": "Actor not ready"}
    ref = tpu_actor.run_batch.remote(batch_size=batch_size, seed=42)
    result = await asyncio.to_thread(ray.get, ref)
    return {
        "status": "SUCCESS",
        "data": result,
    }

@app.get("/health")
async def health():
    import ray
    return {
        "status": "healthy",
        "ray_initialized": ray.is_initialized(),
        "jax_devices": len(jax.devices()),
        "jax_platform": jax.devices()[0].platform if jax.devices() else "none",
    }

@app.get("/tpu/status")
async def tpu_status():
    s = Spin10TPUPodSurrogate(bond_dim=10)
    return {
        "devices": s.n_devices,
        "mesh": str(getattr(s.mesh, 'shape', 'single')),
        "has_sharding_api": bool(s.mesh is not None),
        "platform": jax.devices()[0].platform if jax.devices() else "none",
    }

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

async def main():
    grpc_srv = await grpc_server_tpu.serve_grpc_tpu(port=50051)
    config = uvicorn.Config(
        app, host="0.0.0.0", port=8000, log_level="info",
    )
    api_srv = uvicorn.Server(config)
    await asyncio.gather(
        grpc_srv.wait_for_termination(),
        api_srv.serve(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown TPU Pod.")
