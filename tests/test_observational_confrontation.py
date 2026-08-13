"""Contracts for the frozen observational confrontation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from observational_confrontation import (  # noqa: E402
    CIRCULAR,
    COMPATIBLE,
    EXCLUDED,
    INCOMPLETE_ROW,
    NOT_EXCLUDED,
    REJECTED_FORMULA,
    confront_observables,
    load_card,
)


class ObservationalConfrontationTests(unittest.TestCase):
    def test_card_is_frozen_and_has_required_experiments(self) -> None:
        card = load_card()
        self.assertTrue(card["frozen"])
        for key in ("n_s", "r", "mu_e_gamma", "tau_p_eppi0"):
            self.assertIn(key, card["entries"])

    def test_no_row_is_a_validated_prediction(self) -> None:
        report = confront_observables()
        self.assertEqual(report["validated_observational_predictions"], 0)
        self.assertTrue(all(not row["validated"] for row in report["rows"]))

    def test_ns_is_compatible_and_r_is_not_excluded(self) -> None:
        report = confront_observables(alpha=3.75, n_efolds=60.0)
        by_id = {row["id"]: row for row in report["rows"]}
        self.assertEqual(by_id["C1"]["verdict"], COMPATIBLE)
        self.assertLess(abs(by_id["C1"]["pull"]), 1.0)
        self.assertEqual(by_id["C2"]["verdict"], NOT_EXCLUDED)

    def test_default_proton_estimate_is_below_super_k(self) -> None:
        report = confront_observables(alpha_h_gev3=0.015)
        proton = next(row for row in report["rows"] if row["id"] == "C3")
        self.assertEqual(proton["verdict"], EXCLUDED)
        self.assertLess(proton["theory"], proton["data"])

    def test_smaller_hadronic_element_survives_super_k(self) -> None:
        report = confront_observables(alpha_h_gev3=0.008)
        proton = next(row for row in report["rows"] if row["id"] == "C3")
        self.assertEqual(proton["verdict"], NOT_EXCLUDED)

    def test_circular_and_incomplete_rows_are_not_counted_as_data(self) -> None:
        report = confront_observables()
        by_id = {row["id"]: row for row in report["rows"]}
        self.assertEqual(by_id["C7"]["verdict"], CIRCULAR)
        self.assertEqual(by_id["C9"]["verdict"], CIRCULAR)
        self.assertEqual(by_id["C5"]["verdict"], INCOMPLETE_ROW)
        self.assertEqual(by_id["C10"]["verdict"], REJECTED_FORMULA)
        self.assertEqual(report["ndof_compatible_gaussian"], 1)


if __name__ == "__main__":
    unittest.main()
