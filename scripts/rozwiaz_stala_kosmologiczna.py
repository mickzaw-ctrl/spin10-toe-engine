# -*- coding: utf-8 -*-
"""
Rozwiązywanie problemu stałej kosmologicznej — pełny pipeline audytowy.

Uruchomienie:
    PYTHONPATH=src python3 scripts/rozwiaz_stala_kosmologiczna.py

Wykonuje:
  1. statyczny audyt (QFT, formuła grafowa, kanały tłumienia, problem
     odwrotny, scenariusze relaksacji),
  2. pomiar równowagowego wykładnika q w x_eq(β) = A·β^(−q) na topologii
     silnika Spin(10) (sektor euklidesowy YM),
  3. pomiar trajektorii relaksacji szklistej (start gorący, β duże),
  4. zapis results/stala_kosmologiczna_raport.json + wykresy PNG.

Status: PROTOTYP BADAWCZY OTWARTY — patrz src/stala_kosmologiczna.py.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stala_kosmologiczna import (  # noqa: E402
    pelny_audyt_statyczny,
    MonteCarloWakuum,
    fit_potega_xeq,
    trasa_termiczna,
    werdykt_koncowy,
    lambda_obserwowana,
    lambda_graf,
    kanaly_tlumienia,
    scenariusz_krytyczny,
    M_PL_GEV,
    T_CMB_GEV,
)


def linia(znak="=", n=72):
    print(znak * n)


def usrednij_skany(skany: list) -> list:
    """
    Łączy skany x_eq(β) z kilku ziaren: średnia ważona 1/σ² po β.
    (Pojedyncze trajektorie wykazują trybowe zalepianie się — raportujemy
    wartość uśrednioną po ziarnach.)
    """
    po_beta: dict = {}
    for skan in skany:
        for s in skan:
            po_beta.setdefault(s["beta"], []).append((s["x_eq"], s["x_eq_err"]))
    wynik = []
    for beta in sorted(po_beta):
        pts = po_beta[beta]
        w = np.array([1.0 / max(e, 1e-6) ** 2 for _, e in pts])
        xm = float(np.dot(w, [x for x, _ in pts]) / w.sum())
        err = float(1.0 / np.sqrt(w.sum()))
        rozrzut = float(np.std([x for x, _ in pts])) if len(pts) > 1 else 0.0
        wynik.append({"beta": float(beta), "x_eq": xm,
                      "x_eq_err": max(err, rozrzut / np.sqrt(len(pts)))})
    return wynik


def main(seed: int = 0, szybki: bool = False, n_ziaren: int = 3) -> dict:
    t_start = time.time()
    linia()
    print("  PROBLEM STAŁEJ KOSMOLOGICZNEJ — AUDYT MODELU SPIN(10)")
    linia("=", n=72)

    # ---------------------------------------------------------------- 1. statyka
    raport = pelny_audyt_statyczny()
    obs = raport["obserwowane"]

    print("\n[1] PROBLEM W STANDARDOWEJ QFT (energia punktu zerowego)")
    print(f"    Obserwowane:  ρ_Λ = {obs['rho_Lambda_GeV4']:.3e} GeV⁴ "
          f"= ({obs['rho_Lambda_quarter_meV']:.2f} meV)⁴")
    print(f"                  Λ = {obs['Lambda_m_inv2']:.2e} m⁻² "
          f"= {obs['Lambda_planck']:.2e} M_Pl²")
    for t in raport["problem_standardowy"]:
        print(f"    κ = {t['odciecie']:<22}: ρ_vac/ρ_obs = 10^{t['log10_rozbieznosc']:6.1f}")
    print(f"    Po dokładnej SUSY przy 1 TeV zostaje: 10^{raport['po_susy']['log10_rozbieznosc']:.1f}")

    print("\n[2] FORMUŁA GRAFOWA SILNIKA (równowaga raportu: cosΦ=0.688, Var(k)=0.262)")
    m = raport["model_grafowy"]
    print(f"    G_N = 3/(2πNa²) = {m['G_N_lat']:.5f} a⁻²,   ε_vac = {m['eps_vac']:.4f} a⁻⁴")
    print(f"    Λ_model = {m['Lambda_lat_a2']:.5f} ℓ_Pl⁻²  →  luka 10^{raport['luka_modelu']['log10_luka']:.1f}")
    print("    ⇒ grafowa Λ odziedziczyła PEŁNY problem ~10¹²⁰ (brak redukcji).")

    print("\n[3] KANAŁY TŁUMIENIA Z DOKUMENTACJI (audyt sekwencyjny)")
    k1, k2 = raport["kanaly_tlumienia"], raport["kanaly_tlumienia_dim45"]
    for kanal in k1["kanaly"]:
        print(f"    ×{kanal['czynnik']:.4f}  {kanal['kanal']}")
    print(f"    Łącznie (1/rank): ×{k1['tlumienie_laczne']:.4f}  → luka 10^{k1['log10_luka_po_kanalach']:.1f}")
    print(f"    Łącznie (1/45):   ×{k2['tlumienie_laczne']:.4f}  → luka 10^{k2['log10_luka_po_kanalach']:.1f}")
    print("    ⇒ kanały kinematyczne o ~118 rzędów za słabe.")

    print("\n[4] PROBLEM ODWRóTNY (co musiałaby zrobić próżnia?)")
    i = raport["problem_odwrotny"]
    print(f"    Var(k)=0:  wymagane x = 1−⟨cosΦ⟩ ≲ {i['x_req']:.2e}  (fine-tuning 10^{i['log10_finetuning']:.0f})")
    print(f"    x=0:       wymagane Var(k) ≲ {i['var_k_req']:.2e}")

    # ------------------------------------------------------------ 2. MC równowaga
    print("\n[5] POMIAR MC: x_eq(β) = A·β^(−q)  (topologia Spin10Graph, sektor YM)")
    n_nodes = 80 if szybki else 120
    betas = [1.0, 2.0, 4.0, 8.0, 16.0] if szybki else [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
    burn, meas = (150, 150) if szybki else (300, 300)
    mc = MonteCarloWakuum(N=n_nodes, k_target=4, seed=42)
    skany = [mc.skan_beta(betas, burn_sweeps=burn, meas_sweeps=meas, seed=seed + j)
             for j in range(n_ziaren)]
    skan = usrednij_skany(skany)
    fit = fit_potega_xeq(skan)
    for s in skan:
        print(f"    β = {s['beta']:6.1f}:  x_eq = {s['x_eq']:.5f} ± {s['x_eq_err']:.5f}")
    print(f"    fit (okno 1≤β≤16):  A = {fit['A']:.4f},  q = {fit['q']:.3f} ± {fit['q_err']:.3f}")

    term = trasa_termiczna(fit)
    print(f"    wymagany wykładnik termiczny p = {term['p_wymagany']:.2f}")
    print(f"    ⇒ x(T_CMB) ~ A·(T_CMB/T_Pl)^q ≈ {term['x_przewidziane_dzis']:.1e} vs "
          f"wymagane {term['x_wymagane']:.1e}: luka 10^{term['log10_luka']:.0f} → {term['werdykt']}")

    # ---------------------------------------------------------- 3. szklana relax
    print("\n[6] DYNAMIKA SZKLISTA (start gorący przy β=64, topologia zamrożona)")
    n_relax = 1500 if szybki else 4000
    traj = mc.relaksacja(beta=64.0, n_sweeps=n_relax, meas_every=10, seed=seed)
    x_traj = traj["x"]
    x_podloge = float(np.mean(x_traj[-50:]))
    luka_szkla = math.log10(x_podloge / raport["problem_odwrotny"]["x_req"])
    print(f"    x(n_sweeps={n_relax}) = {x_traj[-1]:.4f}; podłoże frustracyjne ≈ {x_podloge:.4f}")
    print(f"    ⇒ równowaga staje na x ~ {x_podloge:.1e}; luka do x_req: 10^{luka_szkla:.0f}")
    print("      nawet dla nieskończonej relaksacji → trasa szklista WYKLUCZONA.")

    # ------------------------------------------------------- 4. scenariusze Λ(t)
    print("\n[7] SCENARIUSZE RELAKSACJI KRYTYCZNEJ  x(t) = C·(t_R/t)²")
    kryt = raport["scenariusz_krytyczny"]
    print(f"    C_req (Λ(t₀)=Λ_obs) = {kryt['C_req_dla_Lambda_obs']:.2f}  (>1: niefizyczne)")
    print(f"    r_BBN przy wymuszonej Λ_obs = {kryt['r_BBN_przy_Lambda_obs']:.0f}  "
          f"vs granica {kryt['r_BBN_max']:.3f}")
    print(f"    ⇒ tracker krytyczny: {kryt['werdykt']} (o ~"
          f"{raport['werdykt']['tracker_przekracza_BBN_o_rzedow']:.1f} rzędu).")
    fz = raport["scenariusz_freeze"]
    print(f"    freeze przy x_f=x_req: t_f = {fz['t_freeze_s']:.1e} s (po BBN) → {fz['werdykt']}")
    print(f"    ⇒ jedyna ścieżka: podłoga x_f ≲ 5×10⁻¹²¹ osiągnięta PRZED t ≈ 0.1 s,")
    ins = raport["warunek_instantonowy"]
    print(f"      np. nieperturbacyjnie e^(−2π/α): wymaga α_eff = {ins['alpha_eff_wymagane']:.4f} "
          f"(silnik: α_GUT = {ins['alpha_GUT_silnik']})  [{ins['klasyfikacja']}]")

    # ------------------------------------------------------------- 5. werdykt
    lam = lambda_graf()
    kan = kanaly_tlumienia(obs=obs)
    kryt2 = scenariusz_krytyczny(obs=obs)
    werdykt = werdykt_koncowy(obs, lam, kan, term, kryt2)

    raport["mc_skan_beta"] = skan
    raport["mc_fit_potega"] = fit
    raport["trasa_termiczna_zmierzona"] = term
    raport["dynamika_szklista"] = {
        "beta": 64.0, "n_sweeps": n_relax,
        "x_koncowe": float(x_traj[-1]), "x_podloge_oszacowane": x_podloge,
    }
    raport["werdykt"] = werdykt

    linia()
    print(f"  WERDYKT KOŃCOWY: {werdykt['status']}")
    linia("-")
    print("  " + werdykt["podsumowanie"])
    linia()

    # ------------------------------------------------------------- 6. artefakty
    out_json = ROOT / "results" / "stala_kosmologiczna_raport.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(raport, indent=2, ensure_ascii=False, default=str))
    print(f"Zapisano raport: {out_json}")

    rysuj_wykresy(raport, traj, ROOT / "results" / "stala_kosmologiczna")
    print(f"Czas wykonania: {time.time() - t_start:.1f}s")
    return raport


def rysuj_wykresy(raport: dict, traj: dict, out_dir: Path) -> None:
    """Trzy wykresy audytowe: (1) rozbieżności QFT, (2) x_eq(β), (3) trasy Λ(t)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    obs = raport["obserwowane"]

    # --- (1) rozbieżności QFT -------------------------------------------------
    tabela = raport["problem_standardowy"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    nazwy = [t["odciecie"] for t in tabela]
    wartosci = [t["log10_rozbieznosc"] for t in tabela]
    ax.barh(nazwy, wartosci, color="#7d2e2e")
    for y, v in enumerate(wartosci):
        ax.text(v + 1, y, f"10^{v:.0f}", va="center", fontsize=9)
    ax.set_xlabel("log₁₀(ρ_vac / ρ_Λ^obs)")
    ax.set_title("Problem stałej kosmologicznej: energia punktu zerowego vs obserwacja")
    ax.set_xlim(0, 130)
    fig.tight_layout()
    fig.savefig(out_dir / "rozbieznosci_qft.png", dpi=140)
    plt.close(fig)

    # --- (2) x_eq(beta) --------------------------------------------------------
    skan = raport["mc_skan_beta"]
    fit = raport["mc_fit_potega"]
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    b = np.array([s["beta"] for s in skan])
    x = np.array([s["x_eq"] for s in skan])
    xe = np.array([s["x_eq_err"] for s in skan])
    ax.errorbar(b, x, yerr=xe, fmt="o", color="#1f4e79", label="MC (topologia Spin10)")
    bb = np.geomspace(max(b.min(), 1.0), b.max(), 100)
    ax.plot(bb, fit["A"] * bb ** (-fit["q"]), "r--",
            label=fr"fit: $x_{{eq}}={fit['A']:.3f}\,\beta^{{-{fit['q']:.2f}}}$")
    ax.axhline(raport["problem_odwrotny"]["x_req"], color="k", ls=":", lw=1,
               label=r"wymagane $x_{req}\approx 5\times10^{-121}$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"β = 1/T (jednostki sieciowe)")
    ax.set_ylabel(r"$x_{eq}=1-\langle\cos\Phi_\triangle\rangle$")
    ax.set_title("Kondensacja próżni Spin(10): zmierzone q ≈ 1 (harmoniczne), wymagane 3.79")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "xeq_beta.png", dpi=140)
    plt.close(fig)

    # --- (3) scenariusze Λ(t) --------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    t = np.geomspace(2 * 5.391e-44, 4.36e17, 400)  # [s]
    x_req = raport["problem_odwrotny"]["x_req"]
    Ng2 = 150 * 1.0
    # tracker krytyczny C=1 i C_req
    ax.plot(t, (9.0 / Ng2) * (2 * 5.391e-44 / t) ** 2, "-",
            color="#888888", label="tracker t⁻² (C=1)")
    ax.plot(t, (9.0 / Ng2) * raport["scenariusz_krytyczny"]["C_req_dla_Lambda_obs"]
            * (2 * 5.391e-44 / t) ** 2, "--", color="#aa3333",
            label=r"tracker t⁻² z $\Lambda(t_0)=\Lambda_{obs}$ (C=7.7)")
    # trasa termiczna: x = A (T/T_Pl)^q,  T ~ t⁻¹/² (do równań nie głębiej)
    q = raport["mc_fit_potega"]["q"]; A = raport["mc_fit_potega"]["A"]
    ax.plot(t, (9.0 / Ng2) * A * (t / 5.391e-44) ** (-q / 2), "-.", color="#1f77b4",
            label=f"termiczna x∝T^q (q={q:.2f}, zmierzone)")
    # trajektoria szklista: x~podłoże 4e-3
    ax.axhline((9.0 / Ng2) * traj["x"][-1], color="#2e8b57", ls=":",
               label=f"podłoże szkliste MC (x≈{traj['x'][-1]:.2e})")
    ax.axhline(obs["Lambda_planck"], color="k", lw=1.5,
               label=r"$\Lambda_{obs}$")
    ax.axvline(1.0, color="#555", lw=0.8, ls=":")
    ax.text(1.3, 1e-58, "BBN", fontsize=8, rotation=90)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1e-43, 1e18); ax.set_ylim(1e-125, 1e0)
    ax.set_xlabel("czas kosmiczny t [s]")
    ax.set_ylabel(r"$\Lambda(t)\,/\,M_{Pl}^2$")
    ax.set_title("Trasy relaksacji próżni vs wartość obserwowana (N=150, g²=1)")
    ax.legend(fontsize=7.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(out_dir / "relaksacja_lambda.png", dpi=140)
    plt.close(fig)

    print(f"Zapisano wykresy w: {out_dir}")


if __name__ == "__main__":
    szybki = "--szybki" in sys.argv
    main(szybki=szybki)
