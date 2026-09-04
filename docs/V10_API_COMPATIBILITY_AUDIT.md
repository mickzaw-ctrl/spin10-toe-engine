# Enterprise v10 API — Compatibility and Scientific-Status Audit

**Audit date:** 2026-09-04  
**Baseline before the patch:** `c988aa74de73f3752641071943a6d6a53df46bd6`  
**Scope:** API compatibility, runtime smoke tests, and scientific-status labelling  
**Physical-validation status:** not evaluated by these tests

## Findings

The preserved v10 demo and the current v10 implementation had diverged:

1. `scripts/demo_enterprise_platform.py` required `hpc_speedup_factor`, but `Spin10EnterpriseHPCEngine.batch_link_variable_relaxation_gpu()` did not return that field.
2. `QuantumHardwareBridge` called the removed `QuantumCircuit.qasm()` method and failed with current Qiskit.
3. The CPU fallback reported `NVIDIA CUDA GPU Multi-cluster` even when CUDA was unavailable.
4. Fixed SciML values were presented without an explicit placeholder status.

These are software-contract findings. They do not validate the physical Spin(10) model or any performance claim.

## Current public Python API

### HPC relaxation

```python
from spin10_enterprise_core import Spin10EnterpriseHPCEngine

engine = Spin10EnterpriseHPCEngine(N=256, use_gpu=True)
result = engine.batch_link_variable_relaxation_gpu(n_sweeps=3)
```

Constructor:

```text
Spin10EnterpriseHPCEngine(N: int = 1_000_000, use_gpu: bool = True)
```

Method:

```text
batch_link_variable_relaxation_gpu(n_sweeps: int = 10) -> dict
```

Response fields:

| Field | Meaning |
|---|---|
| `hardware_backend` | `CuPy CUDA` or `NumPy CPU fallback` |
| `gpu_acceleration_enabled` | Whether the calculation actually used CuPy/CUDA |
| `nodes_simulated` | Requested graph-node count |
| `tensor_sweeps` | Number of relaxation sweeps |
| `execution_time_seconds` | Measured wall-clock duration for this call |
| `hpc_speedup_factor` | `None` until a frozen CPU/GPU benchmark is run |
| `benchmark_status` | Explicitly reports that no speedup baseline was measured |
| `status` | Execution status, currently `completed` on success |

`N` and `n_sweeps` reject booleans, non-integers, zero, and negative values.

### Quantum Bridge

```python
from spin10_enterprise_core import QuantumHardwareBridge

result = QuantumHardwareBridge.compile_toe_graph_to_qiskit_circuit(
    nodes=4,
    layers=2,
)
```

The exporter now uses:

1. `qiskit.qasm2.dumps(qc)` on current Qiskit;
2. `QuantumCircuit.qasm()` only as a legacy fallback;
3. a declared local QASM skeleton when Qiskit is not installed.

The response includes `compiler_backend`, `hardware_ready`, and:

```text
scientific_status = circuit_compilation_smoke_test_not_hardware_validation
```

A successful QASM export is not evidence that the circuit ran on quantum hardware or that it represents a validated Spin(10) Hamiltonian.

### SciML surrogate

```python
from spin10_enterprise_core import SciMLDigitalTwinSurrogate

result = SciMLDigitalTwinSurrogate("audit").predict_materials_phase_transition(
    [0.1, 0.2, 0.3]
)
```

The legacy numeric strings remain available for API compatibility, but the response now states:

```text
scientific_status = placeholder_outputs_not_a_trained_or_validated_model
```

No model checkpoint, training manifest, held-out validation dataset, ablation, or conventional baseline is attached to these values. They must not be reported as measured predictive performance.

## REST API

When FastAPI is installed, the module exposes:

```text
GET  /enterprise/status
POST /enterprise/simulate-gauge-graph?nodes=<int>&sweeps=<int>
```

The POST endpoint delegates to the same `Spin10EnterpriseHPCEngine` contract. It is a local API surface; deployment, authentication, SLA, and distributed-cluster operation are not established by this smoke test.

## Regression tests

Run:

```bash
PYTHONPATH=src python3 -m unittest -v tests.test_v10_api_contract
PYTHONPATH=src python3 scripts/demo_enterprise_platform.py
```

The five contracts verify:

- truthful CPU/GPU backend reporting;
- nullable speedup until a controlled benchmark exists;
- fail-closed public inputs;
- current and legacy QASM exporter compatibility;
- explicit SciML placeholder status.

## Epistemic classification

| Item | Classification | Confidence |
|---|---|---|
| NumPy/CuPy tensor operation executes | Software capability | High |
| QASM 2 serialization executes | Software capability | High |
| FastAPI routes are importable | Software capability | High |
| GPU speedup | Not measured | High |
| SciML quality percentages | Placeholder, unverified | High |
| Spin(10) physical interpretation of the circuit | Project hypothesis | Low |
| Hardware readiness or production SLA | Not established by this audit | High |

## Next validation gate

A performance claim requires a frozen benchmark with identical inputs on CPU and a named GPU, warm-up exclusion, repeated trials, uncertainty intervals, device/software metadata, and raw timing artifacts. A SciML claim requires a versioned checkpoint, immutable dataset split, licence and contamination records, and controlled comparison against a conventional baseline.
