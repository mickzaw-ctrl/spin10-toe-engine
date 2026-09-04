"""Compatibility and scientific-status contracts for the v10 Enterprise API."""

from __future__ import annotations

import unittest

from spin10_enterprise_core import (
    QuantumHardwareBridge,
    SciMLDigitalTwinSurrogate,
    Spin10EnterpriseHPCEngine,
)


class V10APIContractTests(unittest.TestCase):
    def test_hpc_cpu_fallback_is_reported_truthfully(self) -> None:
        result = Spin10EnterpriseHPCEngine(N=16, use_gpu=False).batch_link_variable_relaxation_gpu(
            n_sweeps=1
        )
        self.assertEqual(result["hardware_backend"], "NumPy CPU fallback")
        self.assertFalse(result["gpu_acceleration_enabled"])
        self.assertEqual(result["status"], "completed")

    def test_hpc_speedup_is_nullable_until_benchmarked(self) -> None:
        result = Spin10EnterpriseHPCEngine(N=16, use_gpu=False).batch_link_variable_relaxation_gpu(
            n_sweeps=1
        )
        self.assertIsNone(result["hpc_speedup_factor"])
        self.assertIn("not_measured", result["benchmark_status"])

    def test_hpc_rejects_invalid_public_inputs(self) -> None:
        for value in (0, -1, True, 1.5):
            with self.subTest(N=value), self.assertRaises(ValueError):
                Spin10EnterpriseHPCEngine(N=value)
        with self.assertRaises(ValueError):
            Spin10EnterpriseHPCEngine(N=8).batch_link_variable_relaxation_gpu(0)

    def test_quantum_bridge_exports_qasm_or_declared_fallback(self) -> None:
        result = QuantumHardwareBridge.compile_toe_graph_to_qiskit_circuit(nodes=3, layers=1)
        self.assertEqual(result["qubits_allocated"], 3)
        self.assertIn("OPENQASM 2.0", result["qasm_circuit_code_snippet"])
        self.assertIn(
            result["compiler_backend"],
            {"qiskit.qasm2.dumps", "legacy_QuantumCircuit.qasm", "fallback_qasm_skeleton"},
        )
        self.assertEqual(
            result["scientific_status"],
            "circuit_compilation_smoke_test_not_hardware_validation",
        )

    def test_sciml_outputs_are_explicitly_marked_as_placeholders(self) -> None:
        result = SciMLDigitalTwinSurrogate("audit").predict_materials_phase_transition(
            [0.1, 0.2, 0.3]
        )
        self.assertEqual(
            result["scientific_status"],
            "placeholder_outputs_not_a_trained_or_validated_model",
        )


if __name__ == "__main__":
    unittest.main()
