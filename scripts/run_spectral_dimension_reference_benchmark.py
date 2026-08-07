#!/usr/bin/env python3
"""Benchmark the raw spectral-dimension estimator on known periodic graphs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys

import networkx as nx
import numpy as np

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spectral_dimension_random_walk import RandomWalkSpectralDimension  # noqa: E402


def run_benchmark() -> dict:
    cases = [
        ("cycle_1d", nx.cycle_graph(512), 1.0),
        ("periodic_torus_2d", nx.grid_2d_graph(32, 32, periodic=True), 2.0),
    ]
    seeds = [11, 22, 33]
    results = []
    for name, graph, target in cases:
        estimates = []
        for seed in seeds:
            times, _, dimensions = (
                RandomWalkSpectralDimension.exact_spectral_dimension_random_walk(
                    graph,
                    max_steps=100,
                    num_walkers=8000,
                    lazy_prob=0.5,
                    seed=seed,
                )
            )
            fit_window = (times >= 10) & (times <= 35)
            estimates.append(float(np.median(dimensions[fit_window])))
        mean = statistics.fmean(estimates)
        results.append(
            {
                "graph": name,
                "nodes": graph.number_of_nodes(),
                "target_dimension": target,
                "seed_estimates": estimates,
                "mean_estimate": mean,
                "absolute_error": abs(mean - target),
            }
        )
    return {
        "benchmark_id": "TCD-SPECTRAL-REFERENCE-001",
        "method": "lazy random walk; median d_S for steps 10..35 inclusive",
        "parameters": {
            "seeds": seeds,
            "max_steps": 100,
            "num_walkers": 8000,
            "lazy_probability": 0.5,
        },
        "results": results,
        "classification": "numerical_method_validation_not_TCD_validation",
        "pass_rule": "absolute error below 0.15 for each reference graph",
        "passed": all(result["absolute_error"] < 0.15 for result in results),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/tcd_spectral_reference_benchmark.json"),
    )
    args = parser.parse_args()
    report = run_benchmark()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.output}")
    for row in report["results"]:
        print(
            row["graph"],
            f"target={row['target_dimension']:.3f}",
            f"mean={row['mean_estimate']:.6f}",
            f"abs_error={row['absolute_error']:.6f}",
        )
    print("PASS" if report["passed"] else "FAIL")


if __name__ == "__main__":
    main()
