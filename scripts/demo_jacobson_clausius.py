#!/usr/bin/env python3
"""Print the Gate-3 Jacobson / prescribed-P report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jacobson_clausius import gate3_jacobson_action  # noqa: E402


def main() -> None:
    report = gate3_jacobson_action()
    print(report["title"])
    print(report["scientific_status"])
    print("decisions:", json.dumps(report["decisions"], indent=2, ensure_ascii=False))
    print("validated_observational_predictions:", report["validated_observational_predictions"])
    print("prescribed action:")
    print(" ", report["prescribed_action"]["action"])
    print(" ", report["prescribed_action"]["metric_equation"])
    print("epochs:")
    for row in report["epochs"]:
        eps = row["eps_friedmann"]
        eps_s = f"{eps:.3e}" if eps is not None else "outside domain"
        print(f"  {row['id']:8s}  P={row['P']}  ε_F={eps_s}")


if __name__ == "__main__":
    main()
