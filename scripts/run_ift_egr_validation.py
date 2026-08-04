#!/usr/bin/env python3
"""Run a fail-closed IFT-EGR stability validation and write a JSON artifact."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ift_egr import evolve_ift_universe  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=600)
    parser.add_argument("--dt-coordinate", type=float, default=0.001)
    parser.add_argument("--dt-rg", type=float, default=0.01)
    parser.add_argument("--nodes", type=int, default=32)
    parser.add_argument("--edge-modes", type=int, default=6)
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument(
        "--output", type=Path, default=Path("results/ift_egr_validation.json")
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    history, _, state, clock = evolve_ift_universe(
        n_steps=args.steps,
        dt_coord=args.dt_coordinate,
        dt_rg=args.dt_rg,
        n_nodes=args.nodes,
        dim=args.edge_modes,
        seed=args.seed,
    )
    all_finite = all(
        math.isfinite(value) for values in history.values() for value in values
    )
    residual = abs(float(state.H_coord - clock.omega_global * state.H_proper))
    omega_positive = min(history["omega_global"]) > 0.0
    scale_positive = min(history["a"]) > 0.0
    passed = all_finite and residual < 1.0e-10 and omega_positive and scale_positive

    report = {
        "schema_version": "ift-egr-validation-v1",
        "scientific_status": "project_hypothesis_not_validated",
        "numerical_status": "PASS" if passed else "FAIL",
        "configuration": {
            "steps": args.steps,
            "dt_coordinate": args.dt_coordinate,
            "dt_rg": args.dt_rg,
            "nodes": args.nodes,
            "edge_modes": args.edge_modes,
            "seed": args.seed,
        },
        "invariants": {
            "all_finite": all_finite,
            "positive_information_frequency": omega_positive,
            "positive_scale_factor": scale_positive,
            "hubble_lapse_residual": residual,
        },
        "ranges": {
            "scale_factor": [min(history["a"]), max(history["a"])],
            "omega_global": [
                min(history["omega_global"]),
                max(history["omega_global"]),
            ],
            "H_proper": [min(history["H_proper"]), max(history["H_proper"])],
            "G_eff": [min(history["G_eff"]), max(history["G_eff"])],
            "Xi": [min(history["Xi"]), max(history["Xi"])],
        },
        "assumption_ledger": [
            {
                "class": "established_physics",
                "assumption": "SLD/QFI algebra and the Bures metric normalization",
            },
            {
                "class": "project_hypothesis",
                "assumption": "Proper time is proportional to Bures path length",
            },
            {
                "class": "project_hypothesis",
                "assumption": "Entropy response defines G_eff and modular variance defines Xi",
            },
            {
                "class": "unverified_assumption",
                "assumption": "Graph information frequency has a covariant continuum gravity limit",
            },
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
