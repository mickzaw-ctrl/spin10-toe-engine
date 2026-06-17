"""
FastAPI dla GPU Pool – REST entrypoint do pool aktorów GPU.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import jax
import ray
import uvicorn
from fastapi import FastAPI

from core_gpu_pool import init_pool, get_pool

logger = logging.getLogger(__name__)

pool_ref = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool_ref
    pool_ref = init_pool(num_actors=None, cache_limit=100_000, bond_dim=10, use_bfloat16=False)
    logger.info(f"FastAPI Pool: {await pool_ref.health()} actors ready.")
    yield
    ray.shutdown()

app = FastAPI(
    title="SHZ Spin10 Quantum Cloud Gateway – GPU Pool",
    version="2.0.0",
    lifespan=lifespan,
)

@app.post("/api/v1/simulate")
async def trigger_simulation(priority: int = 3, batch_size: int = 1000) -> dict:
    if pool_ref is None:
        return {"status": "ERROR", "message": "Pool niegotowy"}

    payload = {"batch_size": batch_size}
    task_id = await pool_ref.submit(priority, payload)
    result = await pool_ref.process()

    return {
        "status": "SUCCESS",
        "client_task_id": task_id,
        "data": result,
        "pool_actors": len(pool_ref.actors),
    }

@app.get("/health")
async def health_check() -> dict:
    h = await pool_ref.health() if pool_ref else {"actors": 0}
    return {
        "status": "healthy",
        "ray_initialized": ray.is_initialized(),
        "pool": h,
    }

@app.get("/pool/status")
async def pool_status() -> dict:
    if pool_ref is None:
        return {"status": "not_initialized"}
    return {
        "actors_total": len(pool_ref.actors),
        "accelerator_available": pool_ref.has_accelerator,
        "platform": jax.devices()[0].platform if pool_ref.actors else "unknown",
    }
