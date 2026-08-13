"""Contract tests for the fail-closed Research Lab wrappers."""

from __future__ import annotations

import math
import unittest

from lab import services


class ResearchLabTests(unittest.TestCase):
    def test_status_does_not_claim_validated_predictions(self) -> None:
        status = services.lab_status()
        self.assertEqual(status["validated_predictions"], 0)
        self.assertIn("not a completed theory of everything", status["what_this_is_not"].lower())
        self.assertTrue(status["gates"]["KEEP"])
        self.assertTrue(status["gates"]["NO-GO"])

    def test_rge_is_established_and_uses_mz_as_input(self) -> None:
        result = services.run_rge(m_susy=5000.0, loops=2, n_points=80)
        self.assertEqual(result["status"], services.ESTABLISHED)
        self.assertGreater(result["analysis"]["M_GUT_GeV"], 1.0e15)
        self.assertLess(result["analysis"]["M_GUT_GeV"], 1.0e17)
        self.assertAlmostEqual(result["analysis"]["alpha_s_MZ_input"], 1.221**2 / (4.0 * math.pi), places=3)
        self.assertEqual(result["calibration_audit"]["apex_hidden_alpha_em_offset"], 6.5504)

    def test_spectral_cycle_recovers_one_dimension(self) -> None:
        result = services.run_spectral(graph="cycle", size=48, walkers=1200, steps=50, seed=3)
        self.assertEqual(result["expected_dimension"], 1.0)
        self.assertLess(result["absolute_error"], 0.15)
        self.assertTrue(result["estimator_pass"])
        self.assertEqual(result["status"], services.ESTABLISHED)

    def test_tcd_rejects_crossover_and_dark_energy(self) -> None:
        result = services.run_tcd_sweep(points=24)
        qcd = result["audits"]["qcd_crossover"]
        dark = result["audits"]["dark_energy"]
        self.assertEqual(qcd["status"], services.REJECTED)
        self.assertGreater(qcd["formula_value_GeV"], 0.28)
        self.assertEqual(dark["status"], services.REJECTED)
        self.assertGreater(dark["lambda_ratio_candidate_to_reference"], 1.0e40)
        self.assertEqual(result["audits"]["lattice_Tc_MeV"]["value"], 156.5)

    def test_lqc_reproduces_standard_critical_density(self) -> None:
        result = services.run_lqc(gamma=0.2375, spin=0.5, punctures=50)
        self.assertAlmostEqual(result["rho_c_over_rho_Pl"], 0.40937381647831045, places=8)
        self.assertTrue(result["causal_order"]["is_partial_order"])
        self.assertEqual(result["causal_order"]["violation_causal_kernel"], 0.0)
        self.assertGreater(result["causal_order"]["violation_with_backward_weight"], 0.0)
        self.assertAlmostEqual(result["bounce"]["H2"][-1], 0.0, places=12)

    def test_inflation_matches_alpha_attractor_formulae(self) -> None:
        result = services.run_inflation(alpha=3.75, n_efolds=60.0)
        self.assertAlmostEqual(result["observables"]["n_s_leading"], 1.0 - 2.0 / 60.0)
        self.assertAlmostEqual(result["observables"]["r"], 12.0 * 3.75 / 60.0**2)
        self.assertEqual(result["hypothesis_status"], services.HYPOTHESIS)
        self.assertLess(result["observables"]["r"], 0.036)

    def test_ledger_keeps_zero_validated_predictions(self) -> None:
        result = services.run_ledger()
        self.assertEqual(result["validated_predictions"], 0)
        statuses = {row["observable"]: row["status"] for row in result["legacy_claims"]}
        self.assertEqual(statuses["α_em"], services.CALIBRATION)
        self.assertEqual(statuses["T_c QCD"], services.REJECTED)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            services.run_rge(m_susy=1.0)
        with self.assertRaises(ValueError):
            services.run_spectral(graph="klein")
        with self.assertRaises(ValueError):
            services.run_lqc(spin=0.7)


if __name__ == "__main__":
    unittest.main()
