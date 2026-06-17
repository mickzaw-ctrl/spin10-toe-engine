"""
SHZ Spin10 Quantum Cloud Gateway – gRPC
========================================
Asynchronous gRPC service (grpc.aio) sharing JAX+Ray core with FastAPI.
"""

import asyncio
import logging
from typing import AsyncIterator

import grpc
import ray

from core_optimized import get_orchestrator
import spin10_pb2
import spin10_pb2_grpc

logger = logging.getLogger(__name__)


class QuantumGatewayServicer(spin10_pb2_grpc.QuantumGatewayServicer):
    """gRPC service implementation for Spin10 gateway."""

    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.version = "1.0.0"

    async def Simulate(self, request, context) -> spin10_pb2.SimulationResponse:
        """Single-request simulation with priority."""
        payload = {"batch_size": request.batch_size}
        payload.update(request.metadata)

        # Submit and process in one step (FIFO through priority queue))
        task_id_ref = self.orchestrator.submit_task.remote(request.priority, payload)
        result_ref = self.orchestrator.process_next_task.remote()

        try:
            task_id = await asyncio.to_thread(ray.get, task_id_ref)
            result = await asyncio.to_thread(ray.get, result_ref)
        except Exception as exc:
            logger.exception("Error during gRPC evaluation Simulate")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return spin10_pb2.SimulationResponse()

        return spin10_pb2.SimulationResponse(
            status=result.get("status", "SUCCESS"),
            task_id=task_id,
            source=result.get("source", "UNKNOWN"),
            result=result.get("result", 0.0),
            message=result.get("message", "OK"),
            latency_ms=0.0,
        )

    async def Health(self, request, context) -> spin10_pb2.HealthResponse:
        """Healthcheck klastra Ray."""
        ray_ready = ray.is_initialized()
        return spin10_pb2.HealthResponse(
            ray_initialized=ray_ready,
            healthy=ray_ready,
            version=self.version,
        )

    async def StreamSimulate(
        self, request, context
    ) -> AsyncIterator[spin10_pb2.SimulationResponse]:
        """
        Strumieniowana symulacja: najpierw PENDING (przyjęcie do kolejki),
        następnie finalny wynik (COMPUTED / CACHE).
        """
        payload = {"batch_size": request.batch_size}
        payload.update(request.metadata)

        # Yield 1 – PENDING
        yield spin10_pb2.SimulationResponse(
            status="PENDING",
            task_id=0,
            source="PENDING",
            result=0.0,
            message="task przyjęte do kolejki",
            latency_ms=0.0,
        )

        task_id_ref = self.orchestrator.submit_task.remote(request.priority, payload)
        result_ref = self.orchestrator.process_next_task.remote()

        try:
            task_id = await asyncio.to_thread(ray.get, task_id_ref)
            result = await asyncio.to_thread(ray.get, result_ref)
        except Exception as exc:
            logger.exception("Błąd w StreamSimulate")
            yield spin10_pb2.SimulationResponse(
                status="ERROR",
                task_id=0,
                source="ERROR",
                result=0.0,
                message=str(exc),
                latency_ms=0.0,
            )
            return

        # Yield 2 – final result
        yield spin10_pb2.SimulationResponse(
            status=result.get("status", "SUCCESS"),
            task_id=task_id,
            source=result.get("source", "UNKNOWN"),
            result=result.get("result", 0.0),
            message=result.get("message", "OK"),
            latency_ms=0.0,
        )


async def serve_grpc(port: int = 50051):
    """Tworzy i startuje asynchroniczny server gRPC."""
    server = grpc.aio.server(options=[
        ("grpc.max_concurrent_streams", 100),
    ])
    spin10_pb2_grpc.add_QuantumGatewayServicer_to_server(
        QuantumGatewayServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    logger.info(f"gRPC server nasłuchuje na porcie {port}")
    return server
