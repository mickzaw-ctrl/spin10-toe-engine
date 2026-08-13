"""Gate 5: the measure is specified; T3 stays unmet."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quantum_measure import (  # noqa: E402
    INCOMPLETE,
    MET,
    T3_MET,
    UNMET,
    clause_score,
    discrete_candidate_measure,
    gate5_quantum_measure,
    t3_verdict,
)


class QuantumMeasureTests(unittest.TestCase):
    def test_haar_on_spin10_is_established_and_z_is_incomplete(self) -> None:
        discrete = discrete_candidate_measure()
        self.assertEqual(discrete["status"], INCOMPLETE)
        self.assertEqual(discrete["haar_on_spin10"]["status"], "established_physics")
        self.assertIn("μ(Γ)", discrete["missing"][0])

    def test_only_m1_is_met(self) -> None:
        by_id = {row["id"]: row for row in clause_score()}
        self.assertEqual(by_id["M1"]["status"], MET)
        for ident in ("M2", "M3", "M4", "M5", "M6"):
            self.assertEqual(by_id[ident]["status"], UNMET)

    def test_t3_stays_unmet(self) -> None:
        self.assertFalse(T3_MET)
        verdict = t3_verdict()
        self.assertEqual(verdict["decision"], "UNMET")
        self.assertEqual(verdict["clauses_met"], ["M1"])
        report = gate5_quantum_measure()
        self.assertFalse(report["is_toe"])
        self.assertEqual(report["validated_observational_predictions"], 0)
        self.assertFalse(report["decisions"]["t3_met"])
        self.assertFalse(report["decisions"]["graph_sum_defined"])


if __name__ == "__main__":
    unittest.main()
