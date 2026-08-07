#!/usr/bin/env python3
"""Run the scientifically gated Thermo-Chromo-Dynamics v15 prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from termo_chromo_dynamics import ThermoChromoDynamicsEngine  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run TCD toy diagnostics without observational-validation claims."
    )
    parser.add_argument("--nodes", type=int, default=10**6)
    parser.add_argument("--susy-scale-gev", type=float, default=5000.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/termo_chromo_dynamics_report.json"),
    )
    args = parser.parse_args()

    engine = ThermoChromoDynamicsEngine(
        N=args.nodes,
        M_SUSY_GeV=args.susy_scale_gev,
    )
    report = engine.run_full_tcd_simulation()

    print("Thermo-Chromo-Dynamics v15 research prototype")
    print(f"Scientific status: {report['scientific_status']}")
    print(f"Graph nodes: {report['N_graph']}")
    print(
        "QCD crossover input: "
        f"{report['critical_temperatures']['T_c_QCD_MeV']:.1f} MeV "
        "(external lattice reference, not a TCD prediction)"
    )

    scale_audit = report["emergent_gravity_Jacobson"]["scale_audit"]
    print(
        "QCD dark-energy relation: "
        f"{scale_audit['status']} — "
        f"Lambda ratio={scale_audit['lambda_ratio_candidate_to_reference']:.3e}"
    )

    fifth_force = report["tcd_predictions"]["TCD-3_fifth_force"]
    print(
        "Fifth-force status: "
        f"{fifth_force['status']} — bare hidden-sector diagnostic "
        f"{fifth_force['alpha_5_bare_x_hidden']:.3e}"
    )

    print(
        "Validation claim: "
        f"40/40={report['consistency_with_heptalogy']['total_40/40_TCD']}"
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
