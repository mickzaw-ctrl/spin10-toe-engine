"""
SHZ Spin10 Quantum Cloud Gateway – REST (FastAPI)
=================================================
Zmodernizowany FastAPI, współdzielący computational core z gRPC.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import ray
import uvicorn
from fastapi import FastAPI

from core_optimized import get_orchestrator, init_orchestrator

logger = logging.getLogger(__name__)

orchestrator_ref = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Zarządza cyklem życia klastra Ray przy starcie/zamykaniu servera."""
    global orchestrator_ref
    orchestrator_ref = init_orchestrator(cache_limit=1000)
    logger.info("FastAPI lifespan: klaster Ray i CloudOrchestrator gotowi.")
    yield
    ray.shutdown()
    logger.info("FastAPI lifespan: klaster Ray zamknięty.")


app = FastAPI(
    title="SHZ Spin10 Quantum Cloud Gateway",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/api/v1/simulate")
async def trigger_simulation(priority: int = 3, batch_size: int = 1000) -> dict:
    """
    Endpoint B2B. Klient korporacyjny przesyła żądanie symulacji.
    """
    if orchestrator_ref is None:
        return {"status": "ERROR", "message": "Orchestrator nie jest gotowy."}

    payload = {"batch_size": batch_size}

    task_id_ref = orchestrator_ref.submit_task.remote(priority, payload)
    result_ref = orchestrator_ref.process_next_task.remote()

    task_id = await asyncio.to_thread(ray.get, task_id_ref)
    computation_result = await asyncio.to_thread(ray.get, result_ref)

    return {
        "status": "SUCCESS",
        "client_task_id": task_id,
        "data": computation_result,
    }


@app.get("/health")
async def health_check() -> dict:
    """Prosty healthcheck dla klastra i bramki."""
    ray_ready = ray.is_initialized()
    return {"status": "healthy", "ray_initialized": ray_ready}
