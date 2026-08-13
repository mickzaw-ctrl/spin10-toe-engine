"""N is derived without n_s; the no-go is frozen."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inflation_contract import (  # noqa: E402
    NOGO_ABS_PULL,
    derived_efolds,
    evaluate_ns_contract,
    predict_tilt,
)


class InflationContractTests(unittest.TestCase):
    def test_n_does_not_depend_on_observed_ns(self) -> None:
        one = derived_efolds(3.75)
        two = derived_efolds(3.75)
        self.assertAlmostEqual(one["N"], two["N"])
        self.assertNotIn("n_s", derived_efolds.__code__.co_varnames)

    def test_leading_ns_is_one_minus_two_over_n(self) -> None:
        pred = predict_tilt(3.75)
        self.assertAlmostEqual(pred["n_s"], 1.0 - 2.0 / pred["N"])
        self.assertAlmostEqual(pred["r"], 12.0 * 3.75 / pred["N"] ** 2)

    def test_preregistered_nogo_is_two_sigma(self) -> None:
        self.assertEqual(NOGO_ABS_PULL, 2.0)
        report = evaluate_ns_contract(3.75, 0.9682, 0.0032)
        self.assertTrue(report["contract_complete"])
        self.assertFalse(report["validated_toe"])
        self.assertEqual(report["nogo"]["threshold"], 2.0)
        self.assertLess(abs(report["pull"]), 2.0)
        self.assertTrue(report["passes_nogo"])

    def test_absurd_data_fails_nogo(self) -> None:
        report = evaluate_ns_contract(3.75, 0.99, 0.0032)
        self.assertFalse(report["passes_nogo"])


if __name__ == "__main__":
    unittest.main()
