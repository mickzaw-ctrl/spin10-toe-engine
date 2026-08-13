"""Gate 4: one action is written; the imported stack is not that action."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from unified_action import (  # noqa: E402
    ESTABLISHED,
    IMPORTED,
    T2_MET,
    continuum_candidate_action,
    consequence_inventory,
    gate4_unified_action,
    t2_verdict,
)


class UnifiedActionTests(unittest.TestCase):
    def test_action_has_gravity_spin10_and_16(self) -> None:
        action = continuum_candidate_action()
        ids = {term["id"] for term in action["terms"]}
        self.assertEqual(action["status"], ESTABLISHED)
        self.assertEqual(ids, {"S_grav", "S_YM", "S_16", "S_H"})
        self.assertIn("spin(10)", action["terms"][1]["formula"])
        self.assertIn("16", action["terms"][2]["formula"])

    def test_imported_stack_is_not_in_s(self) -> None:
        names = {row["module"] for row in continuum_candidate_action()["not_in_S"]}
        self.assertTrue(any("LQC" in name for name in names))
        self.assertTrue(any("α-attractor" in name or "alpha" in name.lower() for name in names))
        self.assertTrue(any("RGE" in name for name in names))

    def test_ns_and_lqc_are_not_consequences(self) -> None:
        by_id = {row["id"]: row for row in consequence_inventory()}
        self.assertFalse(by_id["I3"]["in_S"])
        self.assertEqual(by_id["I3"]["status"], IMPORTED)
        self.assertFalse(by_id["I4"]["in_S"])
        self.assertTrue(by_id["I1"]["in_S"])
        self.assertTrue(by_id["I2"]["in_S"])

    def test_t2_stays_unmet(self) -> None:
        self.assertFalse(T2_MET)
        verdict = t2_verdict()
        self.assertEqual(verdict["decision"], "UNMET")
        self.assertFalse(verdict["t2_met"])
        self.assertTrue(verdict["clause_i_syntax"])
        self.assertFalse(verdict["clause_ii_consequences"])
        report = gate4_unified_action()
        self.assertFalse(report["is_toe"])
        self.assertEqual(report["validated_observational_predictions"], 0)
        self.assertFalse(report["decisions"]["t2_met"])


if __name__ == "__main__":
    unittest.main()
