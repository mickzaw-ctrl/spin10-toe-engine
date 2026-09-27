# -*- coding: utf-8 -*-
"""
Konfrontacja przebudowanego sektora inflacji z danymi 2025/2026 — runner.

Uruchomienie:
    PYTHONPATH=src python3 scripts/konfrontuj_inflacje.py

Wyjście: results/konfrontacja_inflacja.json
         results/inflacja/konfrontacja_inflacja.png
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inflacja_alpha_attractor import (                      # noqa: E402
    PotencjalAlpha, TloInflacji, skan_podgrzewania,
)
from konfrontacja_inflacja import pelna_konfrontacja       # noqa: E402


def main() -> dict:
    t0 = time.time()
    print("=" * 88)
    print(" SEKTOR INFLACJI PO PRZEBUDOWIE vs DANE 2025/2026 (Planck18 · ACT DR6 · BK18 · DESI)")
    print("=" * 88)

    k = pelna_konfrontacja()

    print("\n[1] Wiersze konfrontacji")
    print(f"    {'scenariusz':<32} {'obserwabla':<38} {'pull':<12} werdykt")
    print("    " + "-" * 94)
    for w in k["wiersze"]:
        print(f"    {w['scenariusz'][:31]:<32} {w['obserwabla'][:37]:<38} "
              f"{w['pull']:<12} {w['verdict']}")

    print("\n[2] Podsumowanie")
    for kl, w in k["podsumowanie"].items():
        print(f"    {kl}: {w}")

    out = ROOT / "results" / "konfrontacja_inflacja.json"
    out.write_text(json.dumps(k, indent=2, ensure_ascii=False, default=str))
    print(f"\nZapisano: {out}")

    rysuj(k, ROOT / "results" / "inflacja" / "konfrontacja_inflacja.png")
    print(f"Czas: {time.time() - t0:.1f}s")
    return k


def _elipsa(ax, cx, sig, label, kolor):
    from matplotlib.patches import Ellipse
    for n in (1.0, 2.0):
        ax.add_patch(Ellipse((cx, 0.006), width=2 * n * sig, height=2 * n * 0.010,
                             facecolor=kolor, alpha=0.10 if n > 1 else 0.20,
                             edgecolor=kolor, lw=1))
    ax.annotate(label, (cx, 0.027), ha="center", fontsize=8, color=kolor)


def rysuj(k: dict, out_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path.parent.mkdir(parents=True, exist_ok=True)
    dane = k["dane"]

    pot = PotencjalAlpha(alpha=3.75)
    tlo = TloInflacji(pot, n_max=100.0)
    Ns = np.linspace(45.0, 62.0, 60)
    ns_c = np.array([tlo.obserwable(N)["n_s"] for N in Ns])
    r_c = np.array([tlo.obserwable(N)["r"] for N in Ns])

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.9))

    # --- (1) plaszczyzna n_s-r --------------------------------------------
    ax = axes[0]
    ax.axhspan(0, 0.036, color="#dddddd", alpha=0.6)
    ax.text(0.947, 0.034, "r < 0.036 (BK18)", fontsize=7, color="#555555", va="top")
    ax.set_ylim(0, 0.04); ax.set_xlim(0.944, 0.982)
    for kl, lab, kol in [("n_s_planck", "Planck18", "#7d2e2e"),
                         ("n_s_pact", "P-ACT", "#b8860b"),
                         ("n_s_pactlb", "P-ACT-LB", "#1f4e79")]:
        _elipsa(ax, dane[kl]["value"], dane[kl]["sigma"], lab, kol)
    ax.plot(ns_c, r_c, "-", color="#2e8b57", lw=2, label="α-attractor Spin(10) (dokładne tło)")
    for N in (50, 55, 60):
        o = tlo.obserwable(N)
        ax.plot(o["n_s"], o["r"], "o", color="#2e8b57", ms=8)
        ax.annotate(f"N={N}", (o["n_s"], o["r"] + 0.0015), fontsize=7, ha="center")
    ax.set_xlabel("$n_s$"); ax.set_ylabel("$r$")
    ax.set_title("Płaszczyzna n_s–r (dane vs krzywa N)")
    ax.legend(fontsize=8, loc="upper right")

    # --- (2) podgrzewanie: n_s(T_rh) z pasami danych ----------------------
    ax = axes[1]
    rh = skan_podgrzewania(tlo, np.logspace(2, 15, 14), w_rh=0.0)
    ax.plot(np.log10(rh["T_rh"]), rh["n_s"], "o-", color="#2e8b57", ms=4, label="n_s(T_rh), w_rh=0")
    for kl, lab, kol in [("n_s_planck", "Planck18", "#7d2e2e"),
                         ("n_s_pact", "P-ACT", "#b8860b"),
                         ("n_s_pactlb", "P-ACT-LB", "#1f4e79")]:
        c, s = dane[kl]["value"], dane[kl]["sigma"]
        ax.axhspan(c - s, c + s, color=kol, alpha=0.18)
        ax.text(2.1, c + s * 1.15, lab, fontsize=7, color=kol)
    ax2 = ax.twinx()
    ax2.plot(np.log10(rh["T_rh"]), rh["r"], "s--", color="#666666", ms=3)
    ax2.set_ylabel("r", color="#666666")
    ax.set_xlabel("log₁₀ T_rh [GeV]"); ax.set_ylabel("n_s")
    ax.set_title("Podgrzewanie: n_s i r vs T_rh")
    ax.legend(fontsize=8, loc="lower right")

    # --- (3) napięcia późnego Wszechświata --------------------------------
    ax = axes[2]
    serie = [
        ("H₀: Planck18", dane["H0_planck"]["value"], dane["H0_planck"]["sigma"], "#7d2e2e"),
        ("H₀: SH0ES", dane["H0_shoes"]["value"], dane["H0_shoes"]["sigma"], "#1f4e79"),
        ("S₈: Planck18", dane["S8_planck"]["value"], dane["S8_planck"]["sigma"], "#7d2e2e"),
        ("S₈: KiDS+DES-Y3", dane["S8_weaklens"]["value"], dane["S8_weaklens"]["sigma"], "#1f4e79"),
    ]
    y = np.arange(len(serie))
    for yi, (lab, v, s, kol) in zip(y, serie):
        ax.errorbar(v, yi, xerr=s, fmt="o", color=kol, ms=8, capsize=5)
        ax.text(v, yi + 0.28, lab, fontsize=8, ha="center", color=kol)
    ax.set_yticks([])
    ax.set_title("Napięcia: H₀ (4.9σ), S₈ (2.0σ)\n(kontekst współdzielony z ΛCDM, poza predykcjami silnika)",
                 fontsize=9)
    ax.set_xlabel("zmierzona wartość")
    ax.set_xlim(0.6, 75.5)
    ax.set_xscale("symlog", linthresh=1.0)

    fig.suptitle("Przebudowa sektora inflacji: ACT DR6 przesuwa n_s w górę — vanilla α-attractor = TENSION 2.3-2.5σ z P-ACT-LB",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"Zapisano wykres: {out_path}")


if __name__ == "__main__":
    main()
