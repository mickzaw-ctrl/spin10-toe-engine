#!/usr/bin/env python3
"""Exploratory follow-up after the preregistered 2D benchmark failed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import networkx as nx
import numpy as np

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spectral_dimension_random_walk import RandomWalkSpectralDimension  # noqa: E402


def run_sensitivity() -> dict:
    graph = nx.grid_2d_graph(48, 48, periodic=True)
    rows = []
    for walkers in (8000, 20000):
        for start, stop in ((8, 25), (10, 35), (15, 45)):
            estimates = []
            for seed in (11, 22, 33):
                times, _, dimensions = (
                    RandomWalkSpectralDimension.exact_spectral_dimension_random_walk(
                        graph,
                        max_steps=100,
                        num_walkers=walkers,
                        lazy_prob=0.5,
                        seed=seed,
                    )
                )
                mask = (times >= start) & (times <= stop)
                estimates.append(float(np.median(dimensions[mask])))
            mean = float(np.mean(estimates))
            rows.append(
                {
                    "walkers": walkers,
                    "fit_window_inclusive": [start, stop],
                    "seed_estimates": estimates,
                    "mean_estimate": mean,
                    "absolute_error_from_2D": abs(mean - 2.0),
                }
            )
    powered_rows = [row for row in rows if row["walkers"] == 20000]
    return {
        "experiment_id": "TCD-SPECTRAL-SENSITIVITY-001",
        "status": "exploratory_followup_after_primary_failure",
        "graph": "48x48 periodic square lattice",
        "seeds": [11, 22, 33],
        "rows": rows,
        "followup_rule": "all 20,000-walker window means within 0.05 of d_S=2",
        "followup_passed": all(
            row["absolute_error_from_2D"] < 0.05 for row in powered_rows
        ),
        "interpretation": (
            "The raw estimator is usable only after walker-count and fit-window "
            "requirements are frozen before testing TCD graph ensembles."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/tcd_spectral_sensitivity_followup.json"),
    )
    args = parser.parse_args()
    report = run_sensitivity()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.output}")
    for row in report["rows"]:
        print(
            f"walkers={row['walkers']}",
            f"window={row['fit_window_inclusive']}",
            f"mean={row['mean_estimate']:.6f}",
            f"error={row['absolute_error_from_2D']:.6f}",
        )
    print("FOLLOWUP_PASS" if report["followup_passed"] else "FOLLOWUP_FAIL")


if __name__ == "__main__":
    main()
