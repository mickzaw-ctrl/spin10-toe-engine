# -*- coding: utf-8 -*-
"""
Konfrontacja sektora stałej kosmologicznej modelu Spin(10) z danymi
(Planck 2018, DESI DR1/DR2 BAO, BBN) — runner.

Uruchomienie:
    PYTHONPATH=src python3 scripts/konfrontuj_stala_kosmologiczna.py [--full-mc]

Domyślnie używa ostatniego pomiaru MC q, A z results/stala_kosmologiczna_raport.json;
--full-mc powtarza skan β (kilka minut).

Wyjście: results/konfrontacja_stala_kosmologiczna.json
         results/stala_kosmologiczna/konfrontacja.png
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

import stala_kosmologiczna as sk                     # noqa: E402
import konfrontacja_kosmologiczna as kk              # noqa: E402


def wczytaj_q_A() -> tuple:
    """Ostatni pomiar MC (q, A) z raportu audytowego, jeśli istnieje."""
    p = ROOT / "results" / "stala_kosmologiczna_raport.json"
    if p.exists():
        try:
            r = json.loads(p.read_text())
            fit = r.get("mc_fit_potega", {})
            return float(fit["q"]), float(fit["A"]), "results/stala_kosmologiczna_raport.json"
        except Exception:
            pass
    return 0.835, 0.1697, "wartości domyślne (przedostatni pomiar pełny)"


def main() -> dict:
    t0 = time.time()
    print("=" * 84)
    print(" KONFRONTACJA SEKTORA Λ / CIEMNEJ ENERGII — MODEL SPIN(10) vs DANE")
    print("=" * 84)

    if "--full-mc" in sys.argv:
        print("\n[MC] Powtarzam skan β dla q, A (pełny)...")
        mc = sk.MonteCarloWakuum(N=120, k_target=4, seed=42)
        skany = [mc.skan_beta([1., 2., 4., 8., 16., 32., 64.], 300, 300, seed=j)
                 for j in range(3)]
        from rozwiaz_stala_kosmologiczna import usrednij_skany
        fit = sk.fit_potega_xeq(usrednij_skany(skany))
        q_mc, A_mc, zrodlo = fit["q"], fit["A"], "świeży pomiar MC (--full-mc)"
    else:
        q_mc, A_mc, zrodlo = wczytaj_q_A()
    print(f"\n[Mierzone w MC] q = {q_mc:.3f}, A = {A_mc:.4f}   (źródło: {zrodlo})")

    k = kk.pelna_konfrontacja(q_mc=q_mc, A_mc=A_mc)

    print("\n[1] Wiersze konfrontacji (scenariusz × obserwabla)")
    print(f"    {'scenariusz':<28} {'obserwabla':<26} {'pull':<22} {'werdykt':<16} derivation")
    print("    " + "-" * 96)
    for w in k["wiersze"]:
        print(f"    {w['scenariusz'][:27]:<28} {w['obserwabla'][:25]:<26} "
              f"{w['pull']:<22} {w['verdict']:<16} {w['derivation']['status']}")

    print("\n[2] Werdykty po scenariuszach")
    for sid, v in k["podsumowanie"]["po_scenariuszach"].items():
        print(f"    {sid:<20} → {v['werdykt']:<10} ({v['nazwa']})")

    lic = k["podsumowanie"]["liczniki"]
    print(f"\n[3] Liczniki wierszy: AGREE={lic['AGREE']}, TENSION={lic['TENSION']}, "
          f"EXCLUDED={lic['EXCLUDED']}")
    print(f"    {k['podsumowanie']['uwaga_uczciwosci']}")

    out = ROOT / "results" / "konfrontacja_stala_kosmologiczna.json"
    out.write_text(json.dumps(k, indent=2, ensure_ascii=False, default=str))
    print(f"\nZapisano: {out}")

    rysuj(k, ROOT / "results" / "stala_kosmologiczna" / "konfrontacja.png")
    print(f"Czas: {time.time() - t0:.1f}s")
    return k


def rysuj(k: dict, out_path: Path) -> None:
    """Trzy panele: amplituda Λ, stałe w, stosunek BBN."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sc = k["scenariusze"]
    dane = k["dane"]
    etykiety = ["S1 goły", "S2 kanały", "S3 term.", "S4 tracker*", "S4b tracker C=1", "S5 podłoga*"]

    lam_obs = dane["Lambda_planck"]["value"]
    pulls = [np.log10(s["Lambda_t0_planck"] / lam_obs) for s in sc]
    w0s = [s["w0"] for s in sc]
    rb = [s["r_BBN"] / dane["r_bbn_stiff"]["value"] for s in sc]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    kol = ["#7d2e2e" if abs(p) > 2 else ("#b8860b" if abs(p) > 1 else "#2e8b57") for p in pulls]
    ax.barh(etykiety, pulls, color=kol)
    ax.axvline(0, color="k", lw=1.5)
    for y, p in enumerate(pulls):
        ax.text(p + np.sign(p) * 1.5 if abs(p) > 1 else p + np.sign(p if p else 1) * 0.3,
                y, f"10^{p:.0f}", va="center", fontsize=8)
    ax.set_xlim(-3, 125)
    ax.set_xlabel("log₁₀(Λ_scenariusz / Λ_obs)")
    ax.set_title("Amplituda Λ dziś (Planck 2018)")

    ax = axes[1]
    wd = dane["w_desi"]
    ax.axhspan(wd["value"] - wd["sigma_dn"], wd["value"] + wd["sigma_up"],
               color="#add8e6", alpha=0.5)
    ax.axhline(wd["value"], color="#1f4e79", lw=1.5, label="DESI DR1 BAO: w = −0.99⁺⁰·¹⁵₋₀.₁₃")
    for i, (x, w) in enumerate(zip(np.arange(len(sc)), w0s)):
        ax.plot(x, w, "o", ms=9,
                color="#2e8b57" if abs(w + 1) < 0.14 else "#7d2e2e")
    ax.axhline(-1.0, color="k", ls=":", lw=1)
    ax.set_xticks(np.arange(len(sc))); ax.set_xticklabels(etykiety, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("w₀ (stałe w)")
    ax.set_ylim(-1.3, 0.25)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Równanie stanu dziś")

    ax = axes[2]
    kol = ["#2e8b57" if r < 1 else "#7d2e2e" for r in rb]
    ax.barh(etykiety, np.log10(np.clip(rb, 1e-40, 1e95)), color=kol)
    ax.axvline(0, color="k", lw=1.5)
    ax.set_xlabel("log₁₀[(ρ_stiff/ρ_rad)_BBN / limit]")
    ax.set_xlim(-35, 95)
    ax.set_title("Sztywna składowa przy BBN (limit ΔN_eff≤0.3)")

    fig.suptitle("Konfrontacja sektora Λ modelu Spin(10) z danymi  (* = amplituda dopasowana z konstrukcji)",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"Zapisano wykres: {out_path}")


if __name__ == "__main__":
    main()
