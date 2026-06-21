"""
Command Line Interface for SHZSpin10 Ultima Apex Engine.
"""
import argparse
import json
from .engine import SHZSpin10UltimaApex


def main():
    parser = argparse.ArgumentParser(
        prog="shzspin10",
        description="SHZSpin10 Ultima Apex v14.5 — Unified Quantum Theory of Everything Engine"
    )
    parser.add_argument(
        "--output-json", "-o", type=str, default="shz_spin10_v14_ultima.json",
        help="Path to write the JSON synthesis report"
    )
    parser.add_argument(
        "--no-dashboard", action="store_true",
        help="Skip printing the console dashboard"
    )
    parser.add_argument(
        "--version", "-v", action="version", version="%(prog)s 14.5.0"
    )
    args = parser.parse_args()

    engine = SHZSpin10UltimaApex()
    report = engine.run_ultima_simulation()

    if not args.no_dashboard:
        engine.display_ultima_dashboard(report)

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print(f"\n>>> DOKUMENT SYNTEZY ULTIMA ZAPISANY: {args.output_json}")


def open_dashboard():
    import os
    import webbrowser
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(pkg_dir, "dashboard.html")
    if os.path.exists(html_path):
        url = "file://" + html_path
        print(f">>> Opening dashboard: {url}")
        webbrowser.open(url)
    else:
        print(f"dashboard.html not found in {pkg_dir}")
        print("Generating dynamic report instead...")
        engine = SHZSpin10UltimaApex()
        report = engine.run_ultima_simulation()
        engine.display_ultima_dashboard(report)


if __name__ == "__main__":
    main()
