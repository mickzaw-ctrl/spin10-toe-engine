"""Necessary TOE conditions stay unmet and refuse a TOE flag."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from toe_conditions import (  # noqa: E402
    MET,
    NECESSARY,
    UNMET,
    assert_not_a_toe,
    evaluate_toe_conditions,
)


class ToeConditionTests(unittest.TestCase):
    def test_checklist_has_twelve_necessary_ids(self) -> None:
        report = evaluate_toe_conditions()
        self.assertEqual(tuple(report["necessary_ids"]), NECESSARY)
        self.assertEqual(len(report["items"]), 12)
        self.assertEqual(report["n_necessary"], 12)

    def test_is_not_a_toe(self) -> None:
        report = evaluate_toe_conditions()
        self.assertFalse(report["is_toe"])
        self.assertFalse(report["validated_toe"])
        self.assertFalse(report["necessary_all_met"])
        self.assertEqual(report["validated_observational_predictions"], 0)
        self.assertGreaterEqual(report["n_unmet"], 8)
        t8 = next(item for item in report["items"] if item["id"] == "T8")
        self.assertEqual(t8["status"], UNMET)

    def test_t12_is_discipline_only(self) -> None:
        report = evaluate_toe_conditions()
        t12 = next(item for item in report["items"] if item["id"] == "T12")
        self.assertEqual(t12["status"], MET)
        self.assertIn("fail-closed", t12["evidence"])

    def test_assert_not_a_toe_rejects_a_forged_flag(self) -> None:
        forged = evaluate_toe_conditions()
        forged["is_toe"] = True
        with self.assertRaises(AssertionError):
            assert_not_a_toe(forged)
        assert_not_a_toe()


if __name__ == "__main__":
    unittest.main()
