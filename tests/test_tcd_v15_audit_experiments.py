"""Regression contracts for the seven reproducible TCD v15 audit experiments."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

SCRIPTS_ROOT = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from run_tcd_v15_audit_experiments import run_all_experiments  # noqa: E402


class TCDV15AuditExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_all_experiments(Path(__file__).resolve().parents[1])["results"]

    def test_1_spectral_flow_has_declared_limits_and_monotonicity(self) -> None:
        result = self.result["exp1_spectral_dimension"]
        self.assertTrue(result["strictly_monotonically_decreasing"])
        self.assertEqual(result["key_limits"]["IR_limit_T_0"], 4.0)
        self.assertEqual(result["key_limits"]["midpoint_T_Tstar"], 3.0)
        self.assertLess(result["key_limits"]["UV_limit_T_1e12_Tstar"], 2.000001)
        self.assertIn("project_parameterization", result["classification"])

    def test_2_coherence_domain_matches_analytic_boundary(self) -> None:
        result = self.result["exp2_coherence_domain"]
        for check in result["numerical_boundary_checks"].values():
            self.assertTrue(check["numerical_match_exact"])
            self.assertTrue(check["raises_exception_just_above_crit"])
        boundary = result["analytical_boundaries"]["N_1e6"]
        self.assertAlmostEqual(boundary["ratio_crit_T_over_TGUT"], 3030.3028653030256)

    def test_3_polyakov_cf_map_is_explicitly_anti_correlated(self) -> None:
        result = self.result["exp3_polyakov_cf"]
        checks = result["monotonicity_verified"]
        self.assertTrue(checks["Polyakov_L_strictly_monotone_increasing"])
        self.assertTrue(checks["CausalFraction_CF_strictly_monotone_decreasing"])
        self.assertTrue(checks["CF_vs_L_anti_correlated"])

    def test_4_qcd_crossover_fails_target_and_physical_cf_domain(self) -> None:
        result = self.result["exp4_qcd_crossover"]
        default = result["default_evaluation"]
        domain = result["untuned_domain_reach_analysis"]
        self.assertAlmostEqual(default["Tc_predicted_MeV"], 293.98942011598917)
        self.assertGreater(default["relative_error"], 0.87)
        self.assertGreater(domain["CF_required_at_default_Lambda_and_P_eq_1"], 1.0)
        self.assertFalse(domain["is_CF_req_within_physical_bound_CF_leq_1"])

    def test_5_dark_energy_candidates_fail_scale_and_dimension_gates(self) -> None:
        result = self.result["exp5_dark_energy"]
        candidate_1 = result["candidate_1_dimensional"]
        candidate_2 = result["candidate_2_instanton"]
        self.assertIn("GeV^2", candidate_1["unit_note"])
        self.assertIn("GeV^4", candidate_1["unit_note"])
        self.assertGreater(candidate_1["default_discrepancy_orders"], 41.0)
        self.assertGreater(candidate_2["default_discrepancy_orders"], 31.0)

    def test_6_thermal_gravity_values_and_gut_domain_are_explicit(self) -> None:
        result = self.result["exp6_thermal_delta_g"]
        epochs = {row["epoch"]: row for row in result["epoch_results"]}
        self.assertAlmostEqual(
            epochs["BBN_1MeV"]["DeltaG_over_G_evaluated"],
            2.6183219698159843e-38,
            places=50,
        )
        self.assertGreater(
            epochs["GUT_1.03e16GeV"]["DeltaG_over_G_evaluated"], 1.0
        )

    def test_7_rge_target_match_is_calibration_not_prediction(self) -> None:
        result = self.result["exp7_rge_sensitivity"]
        self.assertAlmostEqual(
            result["calibration_diagnostic"]["fitted_M_SUSY_TeV_for_exact_alpha_s"],
            3.5011076424898318,
            places=10,
        )
        alpha_s = [row["alpha_s_MZ"] for row in result["sweep_table"]]
        self.assertLess(alpha_s[0], alpha_s[-1])
        self.assertIn("not predicted", result["calibration_diagnostic"]["note"])


if __name__ == "__main__":
    unittest.main()
