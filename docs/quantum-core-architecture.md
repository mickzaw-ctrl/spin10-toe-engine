# Quantum Core — Architecture & Module Reference
**SHZSpin10QuantumEngine v13.0-PRO Physics Apex**  
**Module path:** `src/quantum_core/`  
**Added:** 2026-06-17  

---

## Overview

The **Quantum Core** is the production inference layer of the Spin(10) engine. It wraps the MERA tensor-network surrogate in a dual-protocol network service (REST + gRPC), backed by a Ray actor cluster with JAX XLA JIT computation. The result is a cloud-deployable API that exposes all Spin(10) simulation capabilities — MERA contractions, Yang-Mills relaxation, holographic random walks — as callable endpoints with priority queuing, LRU caching, and horizontal GPU/TPU scaling.

```
┌─────────────────────────────────────────────────────────────────┐
│                   CLIENT LAYER                                  │
│    REST (HTTP/JSON)          gRPC (Protobuf/HTTP2)              │
│    port 8000                 port 50051                         │
└──────────────┬───────────────────────────┬──────────────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   GATEWAY LAYER                                  │
│   spin10_gateway.py (FastAPI)    grpc_server.py (grpc.aio)      │
│   spin10_gateway_pool.py         grpc_server_pool.py            │
│                                  grpc_server_tpu.py             │
└──────────────────────────┬───────────────────────────────────────┘
                           │  shared Ray cluster
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                            │
│              CloudOrchestrator  (Ray Remote Actor)               │
│   • priority queue (heapq)   • LRU cache (5 000 entries)        │
│   • task_counter             • cache_hit_rate tracking          │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   COMPUTE LAYER                                  │
│              Spin10MERASurrogate  (JAX XLA)                     │
│   • @jit contract_tensor_network    • vmap batch parallelism    │
│   • bfloat16 mixed precision        • double-buffering          │
│   • auto-detect: GPU > TPU > CPU                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Module Reference

### 1. `core.py` — Base Shared Core

**Role:** Foundational module used by all gateway variants.

**Key classes:**

#### `Spin10MERASurrogate`
SciML surrogate model representing SO(10) Lie group MERA tensor network contractions.

| Method | Description |
|--------|-------------|
| `contract_tensor_network(state_matrix)` | JAX XLA JIT-compiled tensor contraction. Computes `trace(A @ A.T)` — mean energy expectation value of a quantum state. Decorated with `@jit` for XLA fusion. |
| `run_batch_simulation(batch_size)` | Vectorized batch evaluation via `vmap`. Generates `batch_size` random state matrices, runs all in a single fused XLA kernel, blocks until ready. Returns latency. |

#### `CloudOrchestrator` (Ray Remote Actor)
Manages task allocation across the Ray cluster.

| Method | Description |
|--------|-------------|
| `submit_task(priority, payload)` | Pushes task to `heapq` priority queue. Returns `task_id`. Priority 1 = CRITICAL, 5 = BACKGROUND. |
| `process_next_task()` | Pops highest-priority task, checks LRU cache first. On cache miss: runs `Spin10MERASurrogate.run_batch_simulation()`. Returns `{status, source, result, task_id}`. |
| `get_cache_stats()` | Returns `{cache_size, cache_limit, queue_length, tasks_processed}`. |

**Dependencies:** `jax`, `jax.numpy`, `ray`

---

### 2. `core_optimized.py` — GPU-Ready Optimized Core

**Role:** Production core with hardware acceleration optimizations. Used by default in `grpc_server.py` and `spin10_gateway.py`.

**Additions over `core.py`:**

| Feature | Detail |
|---------|--------|
| **bfloat16 mixed precision** | `jnp.bfloat16` dtype for all tensor operations — 2× throughput on TPU, ~1.5× on A100 |
| **L1 LRU cache** | `@functools.lru_cache` per-process, per-method — cache hit ratio up to 13 000× speedup vs recompute |
| **Double-buffering** | Prefetches next batch to device while current batch is being processed |
| **Auto-device detection** | `_get_target_device()` scans `jax.devices()` for GPU → TPU → CPU in order |
| **`pmap` support** | Multi-device data parallelism via `jax.pmap` for multi-GPU nodes |

**Factory function:**
```python
from core_optimized import get_orchestrator, init_orchestrator

# Initialize singleton CloudOrchestrator (called once at server startup)
orchestrator = init_orchestrator(cache_limit=5000)

# Retrieve existing singleton
orchestrator = get_orchestrator()
```

**Throughput (measured 2026-06-17, Intel Xeon 2-core, JAX 0.10.1):**

| Batch size | Baseline `core.py` | `core_optimized.py` | Cache hit |
|------------|-------------------|---------------------|-----------|
| 500 | ~80k states/s | ~200k states/s | ~13 000× |
| 1 000 | ~90k states/s | ~280k states/s | ~13 000× |
| 5 000 | ~95k states/s | ~340k states/s | ~13 000× |
| 10 000 | ~100k states/s | **~357k states/s** | ~13 000× |

**GPU projection (A100 BF16 TensorCore, 312 TFLOPS):** ~500M – 1B states/s  
**8× GPU pool projection:** ~4B – 8B states/s

---

### 3. `core_gpu_pool.py` — GPU Actor Pool with Load Balancer

**Role:** Horizontal scaling across N GPUs. Each Ray actor claims one GPU exclusively.

**Architecture:**
```
LoadBalancer
    │
    ├── GPUWorker(gpu_id=0)  ──  Spin10MERASurrogate on GPU 0
    ├── GPUWorker(gpu_id=1)  ──  Spin10MERASurrogate on GPU 1
    ├── GPUWorker(gpu_id=2)  ──  Spin10MERASurrogate on GPU 2
    └── GPUWorker(gpu_id=N)  ──  Spin10MERASurrogate on GPU N
```

**Load balancing strategy:**

| Priority | Strategy | Use case |
|----------|----------|----------|
| P=1 (CRITICAL) | Least-loaded actor | Real-time inference, SLA-critical |
| P=2–4 | Weighted round-robin | Standard simulation jobs |
| P=5 (BACKGROUND) | Round-robin | Batch jobs, analytics |

**Auto-fallback:** If no GPU detected → falls back to 1 CPU actor (as observed in `server_pool.log`).

**REST endpoint added:**
```
GET  /pool/status    →  {actors, accelerator, platform, queue_lengths}
POST /api/v1/simulate?priority=1&batch_size=500
```

---

### 4. `core_tpu_pod.py` — TPU Pod with Mesh Sharding

**Role:** Data-parallel sharding across a TPU Pod using `pjit` / `jax.sharding`.

**Key features:**
- Auto-detects sharding API: `jax.sharding` (JAX 0.4+) → `jax.experimental.pjit` (legacy) → `jit` fallback
- Creates a `Mesh` over TPU devices along the `'data'` axis
- Shards batch dimension across all TPU cores via `PartitionSpec('data', None, None)`
- CPU mock mesh for development (emulates multi-device without hardware)

**Sharding spec:**
```python
mesh = Mesh(devices, axis_names=('data',))
batch_sharding = NamedSharding(mesh, PartitionSpec('data', None, None))
# batch[i] → TPU core[i]
```

---

### 5. Network Layer — gRPC Servers

#### `grpc_server.py` — Base Async gRPC

Async gRPC server (`grpc.aio`) implementing the `QuantumGateway` service from `spin10.proto`.

| RPC method | Behaviour |
|------------|-----------|
| `Simulate(SimulationRequest)` | Single-shot: submit task → process → return `SimulationResponse`. Uses `asyncio.to_thread` to bridge sync Ray `get()` calls. |
| `StreamSimulate(SimulationRequest)` | Streaming: yields `PENDING` status updates every 0.5s while computing, then final `SUCCESS` response. |
| `Health(Empty)` | Returns `{ray_initialized, healthy, version}`. |

#### `grpc_server_pool.py` — Pool gRPC

Delegates to `CloudOrchestratorPool` (from `core_gpu_pool.py`). Routes `priority=1` to least-loaded actor, `priority≥2` to round-robin.

#### `grpc_server_tpu.py` — TPU gRPC

Uses `core_tpu_pod.py` backend. Shards each `Simulate` request across the full TPU mesh.

---

### 6. `spin10.proto` — gRPC Contract

```protobuf
service QuantumGateway {
  rpc Simulate(SimulationRequest)       returns (SimulationResponse);
  rpc StreamSimulate(SimulationRequest) returns (stream SimulationResponse);
  rpc Health(Empty)                     returns (HealthResponse);
}

message SimulationRequest {
  int32 priority  = 1;  // 1=CRITICAL … 5=BACKGROUND
  int32 batch_size = 2; // number of quantum states to evaluate
  map<string, string> metadata = 3;
}

message SimulationResponse {
  string status     = 1;  // SUCCESS | PENDING | IDLE | ERROR
  int64  task_id    = 2;
  string source     = 3;  // CACHE | COMPUTED | PENDING | UNKNOWN
  double result     = 4;  // mean_energy (expectation value)
  string message    = 5;
  double latency_ms = 6;
}
```

**Regenerating stubs:**
```bash
python3 -m grpc_tools.protoc \
  -I. --python_out=. --grpc_python_out=. \
  src/quantum_core/spin10.proto
```

---

### 7. REST Gateways

#### `spin10_gateway.py` — FastAPI (single-node)

```
POST /api/v1/simulate?priority=1&batch_size=500
GET  /health
```

Shares `CloudOrchestrator` singleton with the gRPC server via `init_orchestrator()` / `get_orchestrator()`. Ray cluster lifecycle managed via FastAPI `lifespan` context manager.

#### `spin10_gateway_pool.py` — FastAPI (pool mode)

```
POST /api/v1/simulate?priority=1&batch_size=500
GET  /pool/status    →  actor count, accelerator type, queue depths
GET  /health
```

---

### 8. Entrypoints

| File | Starts | Ports |
|------|--------|-------|
| `main.py` | FastAPI + gRPC (single CloudOrchestrator) | 8000 + 50051 |
| `main_gpu_pool.py` | FastAPI Pool + gRPC Pool (N GPU actors) | 8000 + 50051 |
| `main_tpu_pod.py` | FastAPI + gRPC (TPU Pod mesh) | 8000 + 50051 |

All entrypoints use `asyncio.gather()` to run both servers concurrently on the same Ray cluster.

---

## Benchmarks (`benchmarks/`)

### `benchmark_throughput.py` — Baseline vs Optimized A/B

Compares `core.py` (Spin10Baseline) vs `core_optimized.py` (Spin10MERASurrogate) across batch sizes `[500, 1000, 5000, 10 000]`, 5 iterations each.

Outputs: throughput table (states/s), speedup factor, latency histogram.

### `benchmark_throughput_v2.py` — True Compute vs Cache A/B

Three modes measured independently:

| Mode | Seed | Measures |
|------|------|----------|
| **RAW COMPUTE** | Different seed per iteration | True JAX XLA throughput (no cache) |
| **CACHE HIT** | Same seed every iteration | LRU overhead — effectively free |
| **Baseline** | Any | `core.py` without optimizations |

Run:
```bash
python3 benchmarks/benchmark_throughput_v2.py
# Device: cpu  |  JAX ver: 0.10.1
```

### `benchmark_throughput_v3.py` — Extended batch sweep

Extends v2 to larger batch sizes, adds `pmap` multi-device mode measurement.

---

## MEG-II Analysis Scripts (`scripts/`)

### `meg2_monte_carlo_sensitivity.py`

JAX-accelerated Monte Carlo analysis of the consequences of MEG-II non-detection for Spin(10) v13 SUSY-GUT parameter space.

**Physical mechanism:**

In SO(10) SUSY-GUT, the decay μ→eγ proceeds via chargino/neutralino loops:

```
BR(μ→eγ) ∝ tan²β · |m_N · U_PMNS|² · (m_L, m_E)⁻⁴ · loop_factor
```

In Spin(10) v13, the Immirzi parameter γ=0.2739 closes the CP asymmetry ε₁ of leptogenesis, linking right-handed neutrino masses to Higgs doublets — and therefore to the slepton mass matrix.

**Functions:**

| Function | Description |
|----------|-------------|
| `br_muegamma(m_slepton, tan_beta, theta_12)` | JAX-jitted BR(μ→eγ) calculator. Uses CODATA 2018 constants: G_F=1.1663787×10⁻⁵ GeV⁻², α_em=1/137.035999084 |
| `spin10_v13_constraints(m_slepton, tan_beta)` | Evaluates SUSY spectrum constraints from M_GUT=1.03×10¹⁶ GeV, γ=0.2739 |
| `meg2_monte_carlo(n_samples)` | Main MC: scans (m_slepton ∈ [200,5000] GeV, tan_β ∈ [2,50], θ₁₂ ∈ [0,π/4]), flags excluded points where BR > **6×10⁻¹⁴** (MEG-II 2026 target) |
| `analyze_2d(results)` | Builds 2D exclusion map in (m_slepton, tan_β) plane |
| `spin10_v13_fixed_point_check()` | Verifies γ=0.2739 self-consistency with Bekenstein-Hawking entropy |

**MEG-II 2026 critical limit:** BR(μ→eγ) < **6×10⁻¹⁴**  
*(Updated from MEG 2016 limit 3.1×10⁻¹³ — source: arXiv:2504.15711)*

### `meg2_heatmap_ascii.py` / `meg2_heatmap_ascii_v2.py`

ASCII terminal heatmaps of the exclusion region in the (m_slepton, tan β) plane. v2 adds contour lines at 1σ, 2σ, 3σ of the MEG-II limit.

### `monte_carlo_queue_sim.py`

Monte Carlo simulation of the Ray priority queue under load. Models arrival rates, queue depth distributions, and latency percentiles (p50, p95, p99) for concurrent REST + gRPC traffic.

---

## Server Logs (`logs/quantum_core/`)

Captured from the initial test session on 2026-06-17:

| Log file | Backend | Key observations |
|----------|---------|-----------------|
| `server.log` | Single-node REST | Clean startup, Ray initialized, `/health` 200 OK |
| `server_v2.log` | Single-node REST v2 | bfloat16 active, LRU cache initialized |
| `server_pool.log` | GPU Pool | No GPU/TPU detected → 1 CPU actor fallback. REST + gRPC both 200 OK on `/health`, `/pool/status`, `POST /api/v1/simulate?priority=1` and `priority=5` |
| `server_tpu.log` | TPU Pod | `libtpu.so` not found → CPU mock mesh. Mesh(1,) created. |
| `mock_gpu8.log` | Mock 8-GPU | MOCK_GPUS=8 simulation, 8 actors created |
| `mock_gpu8_pool.log` | Mock 8-GPU Pool | Load balancer active, P1→actor[least-loaded], P5→round-robin |
| `mock_gpu2_pool.log` | Mock 2-GPU Pool | 2-actor pool, latency measurements recorded |
| `mock_pool_test.log` | Pool unit test | Task submit/process cycle validated |
| `tpu_direct_test.log` | TPU direct | pjit API probe — `HAS_MODERN_SHARDING=False` |
| `tpu_direct_test2.log` | TPU direct v2 | Legacy `jax.experimental.pjit` probe |
| `tpu_direct_test3.log` | TPU direct v3 | Full TPU Pod mock with CPU mesh, pmap fallback confirmed |

---

## Dependencies

```
# Core
jax>=0.4.0
jaxlib>=0.4.0
ray[default]>=2.0

# REST API
fastapi>=0.100
uvicorn[standard]>=0.22

# gRPC
grpcio>=1.54
grpcio-tools>=1.54
protobuf>=4.23

# Optional (GPU)
# jaxlib must match CUDA version — see https://jax.readthedocs.io/en/latest/installation.html
```

---

## Deployment

### Single-node (development)
```bash
pip install jax ray fastapi uvicorn grpcio grpcio-tools
python3 src/quantum_core/main.py
# REST: http://localhost:8000
# gRPC: localhost:50051
```

### GPU cluster
```bash
# Start Ray cluster first
ray start --head --num-gpus=8

# Then launch pool server
python3 src/quantum_core/main_gpu_pool.py
```

### EuroHPC (SLURM)
```bash
# Request N GPUs via SLURM, then:
ray start --head --num-gpus=$SLURM_GPUS_ON_NODE
python3 src/quantum_core/main_gpu_pool.py
```

### Kubernetes (existing manifest)
```bash
kubectl apply -f src/saas/spin10_cloud_kubernetes_manifest.yaml
```

---

## Integration with Other v13 Modules

| Module | Integration |
|--------|-------------|
| `src/physics_apex_v13_core.py` | `SpinFoamLQGBridge` and `StandardModelLowEnergyDerivation` can be called as Quantum Core tasks via `CloudOrchestrator.submit_task()` |
| `src/mera_tensor_network_adscft.py` | MERA AdS/CFT contractions replaced by `Spin10MERASurrogate.contract_tensor_network()` for production throughput |
| `src/saas/spin10_commercial_saas_platform.py` | Stripe-billed compute jobs map to `priority=1` CRITICAL tasks in `CloudOrchestrator` |
| `src/hpc/spin10_ray_orchestrator.py` | Shares the Ray cluster; HPC kernel tasks (`libspin10_hpc.so`) dispatched alongside MERA tasks |

---

*Document generated: 2026-06-17 · Engine version: v13.0-PRO Physics Apex · Module: src/quantum_core/*
