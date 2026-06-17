"""
gRPC dla TPU Pod – entrypoint do shardowanego surrogate.
"""

import asyncio
import logging
from typing import AsyncIterator

import grpc
import ray

from core_tpu_pod import get_tpu_actor
import spin10_pb2
import spin10_pb2_grpc

logger = logging.getLogger(__name__)

class QuantumGatewayTPUServicer(spin10_pb2_grpc.QuantumGatewayServicer):
    def __init__(self):
        self.actor = get_tpu_actor()
        self.version = "3.0.0-tpu-pod"

    async def Simulate(self, request, context) -> spin10_pb2.SimulationResponse:
        try:
            ref = self.actor.run_batch.remote(
                batch_size=request.batch_size,
                seed=hash(request.batch_size + request.priority) % (2**31)
            )
            result = await asyncio.to_thread(ray.get, ref)
        except Exception as exc:
            logger.exception("TPU Pod gRPC error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return spin10_pb2.SimulationResponse()

        return spin10_pb2.SimulationResponse(
            status=result.get("status", "SUCCESS"),
            task_id=0,
            source=result.get("source", "UNKNOWN"),
            result=result.get("result", 0.0),
            message=f"mesh={result.get('mesh','?')}",
            latency_ms=0.0,
        )

    async def Health(self, request, context) -> spin10_pb2.HealthResponse:
        ref = self.actor.run_batch.remote(batch_size=1, seed=0)  # lightweight
        try:
            result = await asyncio.to_thread(ray.get, ref)
            healthy = result.get("status") == "SUCCESS"
        except Exception:
            healthy = False
        return spin10_pb2.HealthResponse(
            ray_initialized=ray.is_initialized(),
            healthy=healthy,
            version=self.version,
        )

    async def StreamSimulate(self, request, context) -> AsyncIterator[spin10_pb2.SimulationResponse]:
        yield spin10_pb2.SimulationResponse(
            status="PENDING", task_id=0, source="PENDING",
            result=0.0, message="TPU Pod shard dispatch", latency_ms=0.0,
        )
        try:
            ref = self.actor.run_batch.remote(
                batch_size=request.batch_size,
                seed=hash(request.batch_size + request.priority) % (2**31)
            )
            result = await asyncio.to_thread(ray.get, ref)
        except Exception as exc:
            yield spin10_pb2.SimulationResponse(
                status="ERROR", task_id=0, source="ERROR",
                result=0.0, message=str(exc), latency_ms=0.0,
            )
            return

        yield spin10_pb2.SimulationResponse(
            status=result.get("status", "SUCCESS"),
            task_id=0,
            source=result.get("source", "UNKNOWN"),
            result=result.get("result", 0.0),
            message=f"mesh={result.get('mesh','?')}",
            latency_ms=0.0,
        )

async def serve_grpc_tpu(port: int = 50051):
    server = grpc.aio.server(options=[("grpc.max_concurrent_streams", 100)])
    spin10_pb2_grpc.add_QuantumGatewayServicer_to_server(
        QuantumGatewayTPUServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    logger.info(f"gRPC TPU Pod server nasłuchuje na porcie {port}")
    return server
