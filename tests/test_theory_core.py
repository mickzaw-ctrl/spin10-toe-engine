"""Contracts for the v16 theoretical specification."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from theory_core import (  # noqa: E402
    CALIBRATION,
    ESTABLISHED,
    REJECTED,
    UNVERIFIED,
    complete_theory,
    hold_interpolation,
    proton_lifetime_estimate,
    spin10_group,
    type_i_seesaw,
    u1_wilson_mass_gap,
)


class TheoryCoreTests(unittest.TestCase):
    def test_spin10_has_45_hermitian_generators_and_one_16(self) -> None:
        group = spin10_group()
        self.assertEqual(group["n_generators"], 45)
        self.assertTrue(group["algebra_checks"]["hermitian_generators"])
        self.assertEqual(group["algebra_checks"]["off_diagonal_trace_max"], 0.0)
        self.assertEqual(sum(group["su5_branching"].values()), 16)
        self.assertEqual(sum(group["pati_salam_branching"].values()), 16)
        self.assertEqual(group["weinberg_gut"], 0.375)
        self.assertEqual(group["n_generations"]["status"], UNVERIFIED)

    def test_proton_lifetime_scales_as_m_to_the_fourth(self) -> None:
        low = proton_lifetime_estimate(1.0e16, 0.04)
        high = proton_lifetime_estimate(2.0e16, 0.04)
        self.assertAlmostEqual(high["tau_years"] / low["tau_years"], 16.0, places=8)
        self.assertEqual(low["status"], ESTABLISHED)
        self.assertFalse(low["prediction_contract"]["complete"])

    def test_seesaw_is_m_d_squared_over_m_r(self) -> None:
        result = type_i_seesaw(100.0, 1.0e14)
        self.assertAlmostEqual(result["m_nu_eV"], 0.1)
        self.assertFalse(result["prediction_contract"]["complete"])

    def test_hold_interpolation_limits(self) -> None:
        self.assertAlmostEqual(hold_interpolation(0.0), 4.0)
        self.assertAlmostEqual(hold_interpolation(1.0), 3.0)
        self.assertLess(hold_interpolation(1.0e12), 2.000001)

    def test_mass_gap_does_not_import_glueball_mass(self) -> None:
        gap = u1_wilson_mass_gap(side=6, beta=1.2, sweeps=30, seed=4)
        self.assertFalse(gap["qcd_reference_used_as_input"])
        self.assertGreater(gap["sigma_a2"], 0.0)
        self.assertTrue(math.isfinite(gap["R_m_over_sqrt_sigma"]))

    def test_complete_theory_stays_empirically_open(self) -> None:
        report = complete_theory(run_gates=True, fast=True)
        self.assertEqual(report["version"], "16.1")
        self.assertEqual(report["validated_observational_predictions"], 0)
        self.assertFalse(report["toe_conditions"]["is_toe"])
        self.assertFalse(report["toe_conditions"]["necessary_all_met"])
        statuses = {row["id"]: row["status"] for row in report["registry"]}
        self.assertEqual(statuses["P7"], CALIBRATION)
        self.assertEqual(statuses["P8"], REJECTED)
        self.assertEqual(statuses["P9"], REJECTED)
        self.assertEqual(statuses["P10"], REJECTED)
        self.assertEqual(statuses["P11"], ESTABLISHED)
        self.assertEqual(statuses["P12"], REJECTED)
        self.assertEqual(statuses["P13"], REJECTED)
        self.assertIn(report["gate1_independent_spectral_flow"]["decision"], {"NO-GO", "HOLD"})
        self.assertEqual(len(report["gate1_independent_spectral_flow"]["points"]), 5)
        gate3 = report["gate3_jacobson_action"]
        self.assertEqual(gate3["decisions"]["jacobson_derives_P"], "NO-GO")
        self.assertEqual(gate3["decisions"]["geff_is_the_field_equation"], "NO-GO")
        self.assertEqual(gate3["validated_observational_predictions"], 0)


if __name__ == "__main__":
    unittest.main()
