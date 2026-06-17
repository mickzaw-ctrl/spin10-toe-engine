"""
SHZ Spin10 – GPU Pool Entrypoint
=================================
Uruchamia REST + gRPC z load-balanced pool aktorów GPU.
Auto-detekcja: jeśli brak realnych GPU, symuluj 8 dla benchmarku.
"""

import asyncio
import logging
import os

import jax
import uvicorn

import grpc_server_pool
import spin10_gateway_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [SciML Pool] %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    # Auto-config: jeśli brak GPU/TPU, symuluj 8 dla testów pool
    try:
        gpus = jax.devices("gpu")
    except RuntimeError:
        gpus = []
    try:
        tpus = jax.devices("tpu")
    except RuntimeError:
        tpus = []
    if not gpus and not tpus:
        logger.warning("No accelerators — setting MOCK_GPUS=8 for pool benchmark.")
        os.environ["MOCK_GPUS"] = "8"
    else:
        logger.info(f"Akceleratory: GPU={len(gpus)}, TPU={len(tpus)}")

    # 1. gRPC pool server
    grpc_srv = await grpc_server_pool.serve_grpc_pool(port=50051)

    # 2. REST pool server
    config = uvicorn.Config(
        spin10_gateway_pool.app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
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
        logger.info("Shutdown GPU pool.")
