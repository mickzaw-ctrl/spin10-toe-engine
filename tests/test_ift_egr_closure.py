"""Scientific-contract tests for the isolated IFT-EGR v0.3 closure module."""

from __future__ import annotations

import json
import math
from pathlib import Path
import unittest

import numpy as np

import ift_egr_closure as closure


class IFTEGRClosureTests(unittest.TestCase):
    def test_standard_lqc_area_gap_reproduces_known_critical_density(self) -> None:
        observed = closure.lqc_critical_density_ratio(gamma=0.2375)
        self.assertAlmostEqual(observed, 0.40937381647831045, places=14)

    def test_lqc_bounce_occurs_at_critical_density(self) -> None:
        rho_c = closure.lqc_critical_density_ratio(gamma=0.2375)
        self.assertAlmostEqual(closure.lqc_hubble_squared(rho_c, rho_c), 0.0, places=14)
        with self.assertRaises(closure.ClosureInputError):
            closure.lqc_hubble_squared(1.01 * rho_c, rho_c)

    def test_half_spin_maximizes_independent_puncture_entropy_area_ratio(self) -> None:
        candidates = [0.5 * index for index in range(1, 11)]
        self.assertEqual(closure.dominant_spin(candidates), 0.5)
        entropy = closure.isolated_horizon_entropy_upper_bound([0.5] * 4)
        self.assertAlmostEqual(entropy, 4.0 * math.log(2.0), places=14)

    def test_spherical_horizon_area_removes_legacy_factor_two(self) -> None:
        gamma = 0.2375
        observed = closure.spherical_horizon_radius_planck(1, 0.5, gamma)
        expected = math.sqrt(math.sqrt(3.0) * gamma)
        legacy_disk_area_result = 2.0 * expected
        self.assertAlmostEqual(observed, expected, places=14)
        self.assertAlmostEqual(legacy_disk_area_result / observed, 2.0, places=14)

    def test_holographic_lambda_is_dimensionally_valid_but_only_inverse_area(self) -> None:
        coefficient = 3.0 * math.pi / 4.0
        entropy_one = closure.isolated_horizon_entropy_upper_bound([0.5] * 10)
        entropy_two = closure.isolated_horizon_entropy_upper_bound([0.5] * 20)
        lambda_one = closure.holographic_lambda_planck(entropy_one, coefficient)
        lambda_two = closure.holographic_lambda_planck(entropy_two, coefficient)
        self.assertAlmostEqual(lambda_two / lambda_one, 0.5, places=14)
        with self.assertRaises(TypeError):
            closure.holographic_lambda_planck(entropy_one)  # type: ignore[call-arg]

    def test_classical_integration_constant_fails_closed_at_bounce(self) -> None:
        rho_c = closure.lqc_critical_density_ratio(gamma=0.2375)
        with self.assertRaisesRegex(closure.ClosureInputError, "modified emergence law"):
            closure.classical_padmanabhan_constant(
                hubble_squared=0.0,
                rho=rho_c,
                regime="quantum_bounce",
            )

    def test_sixty_efolds_do_not_overlap_claimed_72_to_140_window(self) -> None:
        self.assertIsNone(closure.efold_intersection(60.0, 60.0, 72.0, 140.0))
        self.assertEqual(closure.efold_intersection(55.0, 75.0, 72.0, 140.0), (72.0, 75.0))

    def test_chain_relation_is_a_partial_order(self) -> None:
        relation = np.array(
            [
                [1, 1, 1],
                [0, 1, 1],
                [0, 0, 1],
            ],
            dtype=bool,
        )
        audit = closure.audit_partial_order(relation)
        self.assertTrue(audit.is_partial_order)

        future_kernel = np.array(
            [
                [0.0, 1.0, 0.5],
                [0.0, 0.0, 2.0],
                [0.0, 0.0, 0.0],
            ]
        )
        self.assertAlmostEqual(
            closure.causal_order_violation_fraction(future_kernel, relation),
            0.0,
            places=14,
        )
        future_kernel[2, 0] = 0.5
        self.assertGreater(
            closure.causal_order_violation_fraction(future_kernel, relation),
            0.0,
        )

    def test_symmetric_complete_relation_is_not_a_causal_partial_order(self) -> None:
        relation = np.ones((3, 3), dtype=bool)
        audit = closure.audit_partial_order(relation)
        self.assertFalse(audit.is_antisymmetric)
        self.assertFalse(audit.is_partial_order)

    def test_free_gft_profile_is_symmetric_but_not_a_puncture_mapping(self) -> None:
        phi = np.array([-0.25, 0.0, 0.25])
        values = closure.gft_condensate_number_profile(phi, minimum_number=7.0)
        self.assertAlmostEqual(values[0], values[2], places=14)
        self.assertAlmostEqual(values[1], 7.0, places=14)
        self.assertIn("does not identify", closure.gft_condensate_number_profile.__doc__)

    def test_assumption_ledger_has_required_epistemic_classes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        ledger = json.loads(
            (root / "docs" / "IFT_EGR_CLOSURE_ASSUMPTIONS.json").read_text()
        )
        classifications = {entry["classification"] for entry in ledger["entries"]}
        self.assertEqual(ledger["status"], "OPEN")
        self.assertTrue(
            {
                "established_physics",
                "project_hypothesis",
                "unverified_assumption",
                "rejected_assumption",
            }.issubset(classifications)
        )


if __name__ == "__main__":
    unittest.main()
