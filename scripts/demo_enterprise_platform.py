#!/usr/bin/env python3
"""Run a compatibility demo for the Spin(10) Enterprise v10 API.

This script verifies API execution only. It does not claim physical validation,
measured GPU acceleration, hardware execution, or a trained SciML model.
"""

from __future__ import annotations

from pprint import pprint

from spin10_enterprise_core import (
    GPU_CUDA_AVAILABLE,
    QuantumHardwareBridge,
    SciMLDigitalTwinSurrogate,
    Spin10EnterpriseHPCEngine,
)


def run_enterprise_demo() -> None:
    print("Spin(10) Enterprise v10 API compatibility demo")
    print("Scientific status: software smoke test only\n")

    hpc = Spin10EnterpriseHPCEngine(N=256, use_gpu=True)
    hpc_result = hpc.batch_link_variable_relaxation_gpu(n_sweeps=3)
    print("HPC relaxation")
    pprint(hpc_result)
    if hpc_result["hpc_speedup_factor"] is None:
        print("Speedup: not measured against a frozen baseline")
    print(f"CUDA available: {GPU_CUDA_AVAILABLE}\n")

    print("Quantum Bridge")
    quantum_result = QuantumHardwareBridge.compile_toe_graph_to_qiskit_circuit(
        nodes=4, layers=2
    )
    pprint(quantum_result)
    print()

    print("SciML surrogate")
    sciml_result = SciMLDigitalTwinSurrogate(
        target_industry="API compatibility audit"
    ).predict_materials_phase_transition([0.1, 0.2, 0.3])
    pprint(sciml_result)
    print("\nThe SciML values are placeholders, not outputs from a trained model.")


if __name__ == "__main__":
    run_enterprise_demo()
