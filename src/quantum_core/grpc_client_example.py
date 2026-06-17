"""
Przykładowy klient gRPC dla bramki Spin10.

Użycie:
    python grpc_client_example.py simulate --priority 1 --batch_size 500
    python grpc_client_example.py stream --priority 2 --batch_size 200
    python grpc_client_example.py health
"""

import argparse
import asyncio
import sys

import grpc

import spin10_pb2
import spin10_pb2_grpc


async def call_simulate(priority: int, batch_size: int):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = spin10_pb2_grpc.QuantumGatewayStub(channel)
        request = spin10_pb2.SimulationRequest(
            priority=priority, batch_size=batch_size
        )
        response = await stub.Simulate(request)
        print("[Simulate] Response:")
        print(f"  status : {response.status}")
        print(f"  task_id: {response.task_id}")
        print(f"  source : {response.source}")
        print(f"  result : {response.result}")
        print(f"  message: {response.message}")


async def call_stream(priority: int, batch_size: int):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = spin10_pb2_grpc.QuantumGatewayStub(channel)
        request = spin10_pb2.SimulationRequest(
            priority=priority, batch_size=batch_size
        )
        async for response in stub.StreamSimulate(request):
            print("[StreamSimulate] chunk:")
            print(f"  status : {response.status}")
            print(f"  task_id: {response.task_id}")
            print(f"  source : {response.source}")
            print(f"  result : {response.result}")
            print(f"  message: {response.message}")
            print("-" * 40)


async def call_health():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = spin10_pb2_grpc.QuantumGatewayStub(channel)
        response = await stub.Health(spin10_pb2.Empty())
        print("[Health] Response:")
        print(f"  ray_initialized: {response.ray_initialized}")
        print(f"  healthy        : {response.healthy}")
        print(f"  version        : {response.version}")


async def main():
    parser = argparse.ArgumentParser(description="Spin10 gRPC client")
    subparsers = parser.add_subparsers(dest="cmd")

    p_sim = subparsers.add_parser("simulate", help="Jednożądaniowa symulacja")
    p_sim.add_argument("--priority", type=int, default=3)
    p_sim.add_argument("--batch_size", type=int, default=1000)

    p_str = subparsers.add_parser("stream", help="Strumieniowana symulacja")
    p_str.add_argument("--priority", type=int, default=3)
    p_str.add_argument("--batch_size", type=int, default=1000)

    subparsers.add_parser("health", help="Healthcheck klastra")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    if args.cmd == "simulate":
        await call_simulate(args.priority, args.batch_size)
    elif args.cmd == "stream":
        await call_stream(args.priority, args.batch_size)
    elif args.cmd == "health":
        await call_health()


if __name__ == "__main__":
    asyncio.run(main())
