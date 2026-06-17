"""
SHZ Spin10 Quantum Cloud Gateway – Unified Entrypoint
======================================================
Runs concurrently:
  • REST API (FastAPI + uvicorn) na porcie 8000
  • gRPC (grpc.aio) na porcie 50051

Both services share one Ray cluster and actor CloudOrchestrator.
"""

import asyncio
import logging

import uvicorn

import grpc_server
import spin10_gateway

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [SciML Node] %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    # 1. gRPC server
    grpc_srv = await grpc_server.serve_grpc(port=50051)

    # 2. REST (FastAPI) via uvicorn
    config = uvicorn.Config(
        spin10_gateway.app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    api_srv = uvicorn.Server(config)

    # Startingy oba współbieżnie; uvicorn.Server.serve() jest awaitable
    await asyncio.gather(
        grpc_srv.wait_for_termination(),
        api_srv.serve(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown sygnał otrzymany. Zamykanie bramki...")
