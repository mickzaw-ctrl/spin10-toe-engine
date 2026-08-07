"""Scientific-integrity contracts for the TCD v15 research prototype."""

from __future__ import annotations

import json
import math
import unittest

from termo_chromo_dynamics import (
    CONST,
    INCOMPLETE,
    PROJECT_HYPOTHESIS,
    REJECTED,
    ChromoSector,
    TCDInputError,
    ThermoChromoDynamicsEngine,
    ThermoSector,
    carnot_efficiency,
    qcd_crossover_formula_audit,
    qcd_dark_energy_scale_audit,
    lattice_beta_from_alpha,
    thermal_beta_correction,
    thermal_delta_g_fraction,
)


class TCDScientificContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ThermoChromoDynamicsEngine(N=10**6, M_SUSY_GeV=5000.0)

    def test_qcd_dark_energy_claim_fails_dimensional_and_scale_gates(self) -> None:
        audit = qcd_dark_energy_scale_audit(
            CONST.qcd_crossover_gev,
            CONST.planck_mass_gev,
            CONST.reduced_planck_mass_gev,
            CONST.alpha_gut,
            CONST.dark_energy_density_reference_gev4,
        )
        self.assertEqual(audit["status"], REJECTED)
        self.assertGreater(audit["lambda_ratio_candidate_to_reference"], 1e40)
        self.assertGreater(audit["instanton_density_ratio_to_reference"], 1e30)
        self.assertTrue(any("GeV2" in key for key in audit))
        self.assertTrue(any("GeV4" in key for key in audit))

    def test_supplied_qcd_crossover_formula_is_numerically_rejected(self) -> None:
        audit = qcd_crossover_formula_audit(
            CONST.lambda_qcd_gev,
            1.0 - 0.33 / math.sqrt(1e6),
            CONST.causal_fraction_reference,
            CONST.qcd_crossover_gev,
        )
        self.assertEqual(audit["status"], REJECTED)
        self.assertAlmostEqual(audit["formula_value_GeV"], 0.29398, places=4)
        self.assertGreater(audit["relative_error"], 0.8)

    def test_beta10_is_not_alpha_gut_inverse(self) -> None:
        beta = lattice_beta_from_alpha(1.0 / 24.0)
        self.assertAlmostEqual(beta, 1.909859317102744, places=14)
        self.assertNotAlmostEqual(beta, 24.0, places=1)

    def test_spectral_dimension_has_declared_limits_and_midpoint(self) -> None:
        coupling = self.engine.coupling
        self.assertAlmostEqual(coupling.spectral_dimension_T(0.0), 4.0, places=14)
        self.assertAlmostEqual(
            coupling.spectral_dimension_T(CONST.spectral_transition_gev),
            3.0,
            places=14,
        )
        self.assertLess(coupling.spectral_dimension_T(1e40), 2.00001)

    def test_delta_g_ansatz_does_not_reproduce_supplied_orders_of_magnitude(self) -> None:
        today = thermal_delta_g_fraction(2.35e-13, CONST.gut_scale_gev)
        bbn = thermal_delta_g_fraction(1e-3, CONST.gut_scale_gev)
        self.assertAlmostEqual(today, 1.4459683078308771e-57, places=70)
        self.assertAlmostEqual(bbn, 2.6183219698159843e-38, places=50)
        self.assertLess(bbn, 1e-30)

    def test_carnot_efficiency_uses_actual_declared_scale_ratio(self) -> None:
        efficiency = carnot_efficiency(CONST.planck_mass_gev, CONST.gut_scale_gev)
        self.assertAlmostEqual(efficiency, 0.9991557377049181, places=14)
        self.assertNotAlmostEqual(efficiency, 0.87, places=2)

    def test_thermal_beta_ansatz_is_quadratic_and_zero_at_zero_temperature(self) -> None:
        zero = thermal_beta_correction(0.7, 0.0, 5000.0, 2.77)
        low = thermal_beta_correction(0.7, 100.0, 5000.0, 2.77)
        high = thermal_beta_correction(0.7, 200.0, 5000.0, 2.77)
        self.assertEqual(zero, 0.0)
        self.assertAlmostEqual(high / low, 4.0, places=14)

    def test_public_scalar_inputs_reject_booleans(self) -> None:
        with self.assertRaises(TCDInputError):
            ThermoSector(N=True)
        with self.assertRaises(TCDInputError):
            thermal_beta_correction(True, 1.0, 5000.0, 1.0)
        with self.assertRaises(TCDInputError):
            carnot_efficiency(True, 0.0)

    def test_polyakov_cf_mapping_is_not_reported_as_established(self) -> None:
        temperatures = self.engine.compute_critical_temperatures()
        self.assertEqual(temperatures["CF_Polyakov_map_status"], "unverified_assumption")
        self.assertEqual(temperatures["T_c_status"], "external lattice-QCD reference input")

    def test_wilson_area_diagnostic_decreases_with_area(self) -> None:
        chromo = ChromoSector()
        small = chromo.wilson_loop_expectation(0.1, 50.0)
        large = chromo.wilson_loop_expectation(1.0, 50.0)
        self.assertGreater(small, large)
        self.assertGreaterEqual(large, 0.0)
        self.assertLessEqual(small, 1.0)

    def test_reference_calibrated_glueball_is_not_a_prediction(self) -> None:
        result = self.engine.chromo.glueball_spectrum()
        self.assertEqual(result["status"], PROJECT_HYPOTHESIS)
        self.assertIn("input", result["warning"])

    def test_fifth_force_has_no_fabricated_resummation(self) -> None:
        result = self.engine.chromo.fifth_force_alpha(1.0)
        self.assertEqual(result["status"], INCOMPLETE)
        self.assertIsNone(result["alpha_5_with_torsion_resummed_phenom"])
        self.assertLess(result["alpha_5_bare_x_hidden"], 1e-35)

    def test_rge_defaults_to_a_standard_one_loop_threshold_baseline(self) -> None:
        result = self.engine.coupling.integrate_thermo_chromo_rge()
        self.assertTrue(result["success"])
        self.assertFalse(result["thermal_correction_enabled"])
        self.assertEqual(result["thermal_term_status"], "unverified_assumption")
        self.assertGreater(result["alpha_s_MZ"], 0.0)
        self.assertLess(result["alpha_s_MZ"], 1.0)

    def test_full_report_cannot_claim_validation_or_zero_new_parameters(self) -> None:
        report = self.engine.run_full_tcd_simulation()
        consistency = report["consistency_with_heptalogy"]
        self.assertFalse(consistency["tests_executed_by_report"])
        self.assertFalse(consistency["total_40/40_TCD"])
        self.assertFalse(consistency["zero_new_parameters"])
        self.assertEqual(report["falsification_criteria"]["status"], INCOMPLETE)
        serialized = json.dumps(report)
        self.assertNotIn("CONFIRMED", serialized.upper())
        self.assertIsNone(
            report["emergent_gravity_Jacobson"]["Omega_Lambda_TCD_calib"]
        )

    def test_piecewise_eos_is_explicitly_a_toy_schedule(self) -> None:
        history = self.engine.compute_eos_history()
        self.assertEqual(history["status"], PROJECT_HYPOTHESIS)
        values = {row["T_GeV"]: row["w_toy"] for row in history["eos_history"]}
        self.assertEqual(values[1e20], -0.99)
        self.assertEqual(values[1.0], 1.0 / 3.0)
        self.assertEqual(values[1e-3], 1.0 / 3.0)
        self.assertEqual(values[2e-13], -1.0)


if __name__ == "__main__":
    unittest.main()
