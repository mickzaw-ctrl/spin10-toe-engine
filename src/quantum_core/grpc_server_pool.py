"""
gRPC dla GPU Pool – Load balancer rozdziela zadania między N aktorów.
"""

import asyncio
import logging
from typing import AsyncIterator

import grpc
import ray

from core_gpu_pool import init_pool, get_pool
import spin10_pb2
import spin10_pb2_grpc

logger = logging.getLogger(__name__)

class QuantumGatewayPoolServicer(spin10_pb2_grpc.QuantumGatewayServicer):
    def __init__(self):
        self.pool = get_pool()
        self.version = "2.0.0-gpu-pool"

    async def Simulate(self, request, context) -> spin10_pb2.SimulationResponse:
        payload = {"batch_size": request.batch_size}
        payload.update(request.metadata)

        try:
            task_id = await self.pool.submit(request.priority, payload)
            result = await self.pool.process()
        except Exception as exc:
            logger.exception("Pool gRPC error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return spin10_pb2.SimulationResponse()

        return spin10_pb2.SimulationResponse(
            status=result.get("status", "SUCCESS"),
            task_id=task_id,
            source=result.get("source", "UNKNOWN"),
            result=result.get("result", 0.0),
            message="OK",
            latency_ms=0.0,
        )

    async def Health(self, request, context) -> spin10_pb2.HealthResponse:
        h = await self.pool.health()
        return spin10_pb2.HealthResponse(
            ray_initialized=ray.is_initialized(),
            healthy=h.get("actors", 0) > 0,
            version=self.version,
        )

    async def StreamSimulate(self, request, context) -> AsyncIterator[spin10_pb2.SimulationResponse]:
        payload = {"batch_size": request.batch_size}
        payload.update(request.metadata)

        yield spin10_pb2.SimulationResponse(
            status="PENDING", task_id=0, source="PENDING",
            result=0.0, message="Pool routing", latency_ms=0.0,
        )

        try:
            task_id = await self.pool.submit(request.priority, payload)
            result = await self.pool.process()
        except Exception as exc:
            yield spin10_pb2.SimulationResponse(
                status="ERROR", task_id=0, source="ERROR",
                result=0.0, message=str(exc), latency_ms=0.0,
            )
            return

        yield spin10_pb2.SimulationResponse(
            status=result.get("status", "SUCCESS"),
            task_id=task_id,
            source=result.get("source", "UNKNOWN"),
            result=result.get("result", 0.0),
            message="OK",
            latency_ms=0.0,
        )

async def serve_grpc_pool(port: int = 50051):
    server = grpc.aio.server(options=[("grpc.max_concurrent_streams", 100)])
    spin10_pb2_grpc.add_QuantumGatewayServicer_to_server(
        QuantumGatewayPoolServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    logger.info(f"gRPC Pool server listening on port {port}")
    return server
