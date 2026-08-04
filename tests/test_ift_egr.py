"""Regression and scientific-contract tests for IFT-EGR v0.2."""

from __future__ import annotations

import unittest

import jax
import jax.numpy as jnp
import numpy as np

import ift_egr


class IFTEGRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = ift_egr.RelationalGraph.init_thermal(
            n_nodes=4,
            dim=3,
            beta=1.1,
            key=jax.random.PRNGKey(7),
        )

    def assert_density_matrices(self, rho: jax.Array) -> None:
        values = np.asarray(rho)
        hermiticity = np.max(
            np.abs(values - np.swapaxes(values.conj(), -1, -2))
        )
        traces = np.trace(values, axis1=-2, axis2=-1).real
        eigenvalues = np.linalg.eigvalsh(values)
        self.assertLess(hermiticity, 1.0e-10)
        self.assertTrue(np.allclose(traces, 1.0, atol=1.0e-10))
        self.assertGreaterEqual(float(np.min(eigenvalues)), -1.0e-10)

    def test_diagonal_qfi_matches_classical_fisher_metric(self) -> None:
        probability = 0.3
        velocity = 0.02
        rho = jnp.diag(jnp.array([probability, 1.0 - probability]))
        tangent = jnp.diag(jnp.array([velocity, -velocity]))
        observed = float(ift_egr.quantum_fisher_information(rho, tangent))
        expected = velocity**2 * (
            1.0 / probability + 1.0 / (1.0 - probability)
        )
        self.assertAlmostEqual(expected, observed, places=12)

    def test_static_state_has_zero_information_frequency(self) -> None:
        omega = ift_egr.information_frequency_matrix(
            self.graph.edge_rho, self.graph.edge_rho, dt_coord=0.01
        )
        self.assertLess(float(jnp.max(jnp.abs(omega))), 1.0e-12)

    def test_graph_flow_is_nonzero_and_preserves_density_states(self) -> None:
        evolved = ift_egr.rg_flow_step(self.graph, dt=0.02)
        change = float(jnp.linalg.norm(evolved.edge_rho - self.graph.edge_rho))
        self.assertGreater(change, 1.0e-10)
        self.assert_density_matrices(evolved.edge_rho)
        self.assertTrue(
            np.allclose(
                np.asarray(evolved.edge_rho),
                np.swapaxes(np.asarray(evolved.edge_rho), 0, 1),
                atol=1.0e-10,
            )
        )

    def test_bures_speed_converges_when_step_is_halved(self) -> None:
        full = ift_egr.rg_flow_step(self.graph, dt=0.01)
        half = ift_egr.rg_flow_step(self.graph, dt=0.005)
        omega_full = ift_egr.information_frequency_matrix(
            self.graph.edge_rho, full.edge_rho, dt_coord=0.01
        )
        omega_half = ift_egr.information_frequency_matrix(
            self.graph.edge_rho, half.edge_rho, dt_coord=0.005
        )
        numerator = float(jnp.linalg.norm(omega_full - omega_half))
        denominator = max(float(jnp.linalg.norm(omega_half)), 1.0e-14)
        self.assertLess(numerator / denominator, 0.03)

    def test_clock_counts_undirected_edges_and_advances(self) -> None:
        evolved = ift_egr.rg_flow_step(self.graph, dt=0.01)
        old = ift_egr.InformationClock.init(n_nodes=4)
        clock = ift_egr.compute_information_clock(
            self.graph.edge_rho,
            evolved.edge_rho,
            self.graph.adj,
            old,
            dt_coord=0.01,
        )
        self.assertGreater(float(clock.omega_global), 0.0)
        self.assertAlmostEqual(
            float(clock.tau_proper),
            float(clock.omega_global) * 0.01,
            places=12,
        )

    def test_friedmann_uses_physical_hubble_without_lapse_factor(self) -> None:
        state = ift_egr.CosmologicalState(
            a=jnp.float64(1.0),
            H_coord=jnp.float64(0.0),
            H_proper=jnp.float64(0.0),
            rho_matter=jnp.float64(0.2),
            rho_rad=jnp.float64(0.1),
            G_eff=jnp.float64(1.0),
            Lambda_eff=jnp.float64(0.3),
            Xi=jnp.float64(0.0),
            tau_proper=jnp.float64(0.0),
            omega=jnp.float64(2.0),
        )
        h_one = float(ift_egr.friedmann_ift(state, jnp.float64(1.0)))
        h_two = float(ift_egr.friedmann_ift(state, jnp.float64(2.0)))
        self.assertAlmostEqual(h_one, h_two, places=12)
        self.assertAlmostEqual(2.0 * h_two, 2.0 * h_one, places=12)

    def test_negative_friedmann_branch_fails_closed(self) -> None:
        state = ift_egr.CosmologicalState(
            a=jnp.float64(1.0),
            H_coord=jnp.float64(0.0),
            H_proper=jnp.float64(0.0),
            rho_matter=jnp.float64(0.0),
            rho_rad=jnp.float64(0.0),
            G_eff=jnp.float64(1.0),
            Lambda_eff=jnp.float64(-3.0),
            Xi=jnp.float64(0.0),
            tau_proper=jnp.float64(0.0),
            omega=jnp.float64(1.0),
        )
        self.assertTrue(np.isnan(float(ift_egr.friedmann_ift(state, 1.0))))

    def test_short_evolution_is_finite_and_obeys_lapse_relation(self) -> None:
        history, _, state, clock = ift_egr.evolve_ift_universe(
            n_steps=4,
            dt_coord=0.001,
            dt_rg=0.005,
            n_nodes=4,
            dim=3,
            seed=11,
        )
        self.assertEqual(4, len(history["a"]))
        self.assertTrue(np.all(np.isfinite(np.asarray(history["a"]))))
        self.assertAlmostEqual(
            float(state.H_coord),
            float(clock.omega_global * state.H_proper),
            places=10,
        )


if __name__ == "__main__":
    unittest.main()
