# -*- coding: utf-8 -*-
"""
Konfrontacja przebudowanego sektora inflacji z danymi 2025/2026
===============================================================

Zestawia wyniki ``src/inflacja_alpha_attractor.py`` (dokładne tło +
podgrzewanie) z zamrożoną tabelą aktualnych danych:

  - Planck 2018 (bazowa),
  - ACT DR6: P-ACT n_s = 0.9709±0.0038,
    P-ACT-LB n_s = 0.9743±0.0034 (2σ powyżej Planck-a),
  - BK18: r < 0.036 (95% CL); kombinacja P-ACT-LB-BK18: r < 0.038,
  - A_s z Planck 2018,
  - napięcia późnego Wszechświata: SH0ES H₀ = 73.04±1.04 (vs Planck) —
    Hubble tension ~4.9σ; S₈: KiDS/DES-Y3 joint S₈ = 0.790 vs Planck 0.832
    (~2.0σ); DESI DR2 w₀wₐ (z konfrontacji sektora Λ).

Kluczowy wynik: po przebudowie N_⋆ przestaje być arbitralne — sektor
podgrzewania (w_rh=0, drgające minimum kwadratowe) daje N_⋆ ≲ 57, czyli
n_s ≤ 0.966. Wobec P-ACT-LB vanilla α-attractor Spin(10) ma napięcie
~2.5-2.6σ; wobec Planck 2018 / P-ACT bez BAO — zgodność.

Werdyki: AGREE (<2σ), TENSION (2-3σ), EXCLUDED (>3σ), NO-DATA,
TENSION-CONTEXT (napięcia współdzielone z ΛCDM / sprzeczności w danych,
nie dyskryminujące modelu).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np

import stala_kosmologiczna as sk
from inflacja_alpha_attractor import (
    PotencjalAlpha, TloInflacji, skan_podgrzewania, predykcje_LO,
    normalizuj_V0_dla_As, wymagane_N_dla_ns, A_S_OBS,
)

# ---------------------------------------------------------------------------
# Zamrożona tabela danych 2025/2026 (WEJŚCIE, źródło per wpis)
# ---------------------------------------------------------------------------

ACT_SRC = "ACT DR6 (2025), P-ACT i P-ACT-LB (po arXiv:2503.14452, 2504.xx)"
PLANCK18 = "Planck 2018 VI/X, arXiv:1807.06209, arXiv:1905.05697"
BK18_SRC = "BICEP/Keck BK18, PRL 127, 151301 (2021), arXiv:2110.00483"
SH0ES_SRC = "SH0ES/Pantheon+ (Riess et al. 2022), ApJ 934 L7, arXiv:2112.04510"
S8_SRC = "DES Y3 + KiDS-1000 joint (2024), arXiv:2405.05311 / Open J. As."

_DANE: Dict[str, Dict[str, Any]] = {
    "n_s_planck": {"value": 0.9649, "sigma": 0.0042, "kind": "measurement",
                   "source": PLANCK18},
    "n_s_pact": {"value": 0.9709, "sigma": 0.0038, "kind": "measurement",
                 "source": ACT_SRC},
    "n_s_pactlb": {"value": 0.9743, "sigma": 0.0034, "kind": "measurement",
                   "source": ACT_SRC + " + DESI"},
    "A_s": {"value": 2.099e-9, "sigma": 2.938e-11, "kind": "measurement",
            "source": PLANCK18},
    "r_0.05": {"value": 0.036, "kind": "upper_limit", "cl": "95%",
               "source": BK18_SRC},
    "r_combo": {"value": 0.038, "kind": "upper_limit", "cl": "95%",
                "source": "P-ACT-LB-BK18 (po arXiv:2606.24131)"},
    "alpha_s_planck": {"value": -0.0041, "sigma": 0.0067, "kind": "measurement",
                       "note": "ΛCDM+running",
                       "source": PLANCK18 + " IX"},
    "alpha_s_actext": {"value": 0.0119, "sigma": 0.0063, "kind": "extended_fit",
                       "note": "ACT+P z α_s i β_s swobodnymi",
                       "source": "arXiv:2511.01612 (fit rozszerzony)"},
    "H0_planck": {"value": 67.36, "sigma": 0.54, "kind": "measurement",
                  "source": PLANCK18},
    "H0_shoes": {"value": 73.04, "sigma": 1.04, "kind": "measurement",
                 "source": SH0ES_SRC},
    "S8_planck": {"value": 0.832, "sigma": 0.013, "kind": "measurement",
                  "source": PLANCK18},
    "S8_weaklens": {"value": 0.790, "sigma": 0.016, "kind": "measurement",
                    "source": S8_SRC},
}


def tabela_danych() -> Dict[str, Dict[str, Any]]:
    return {k: dict(v) for k, v in _DANE.items()}


AGREE = "AGREE"
TENSION = "TENSION"
EXCLUDED = "EXCLUDED"
NO_DATA = "NO-DATA"
TENSION_CONTEXT = "TENSION-CONTEXT"


# ---------------------------------------------------------------------------
# Scenariusze inflacyjne
# ---------------------------------------------------------------------------

def buduj_scenariusze(
    alpha: float = 3.75,
    tlo: Optional[TloInflacji] = None,
) -> Dict[str, Any]:
    """
    Konstruuje fizyczne punkty predykcji:

      I0 vanilla    : silnik obecnie — N=60 sztywno, wzory LO,
      I1 vanilla NLO: N=60 sztywno, ale z dokładnego tła (ten moduł),
      I2 reheat     : podgrzewanie — zakres N_⋆ ∈ [N_min, N_max] fizyczny
                      (T_rh ∈ [1, 1e15] GeV, w_rh=0).
    """
    pot = PotencjalAlpha(alpha=alpha)
    tlo = tlo or TloInflacji(pot, n_max=100.0)

    # I0: stare wzory LO przy sztywnym N=60
    i0 = predykcje_LO(60.0, alpha)
    # I1: ten moduł, N=60
    o60 = tlo.obserwable(60.0)
    r60 = tlo.running(60.0)
    norm60 = normalizuj_V0_dla_As(tlo, 60.0)
    i1 = {"n_s": o60["n_s"], "r": o60["r"], "alpha_s": r60["alpha_s"],
          "beta_s": r60["beta_s"], "V_quarter": norm60["V_k_quarter_GeV"]}
    # I2: podgrzewanie
    Trh = np.logspace(0, 15, 16)
    rh = skan_podgrzewania(tlo, Trh, w_rh=0.0)
    i2 = {
        "N_range": (float(rh["N_star"].min()), float(rh["N_star"].max())),
        "n_s_range": (float(rh["n_s"].min()), float(rh["n_s"].max())),
        "r_range": (float(np.asarray(rh["r"]).min()), float(np.asarray(rh["r"]).max())),
        "alpha_s_range": (float(rh["alpha_s"].min()), float(rh["alpha_s"].max())),
        "krzywa": rh,
    }
    return {"I0_vanilla_LO": i0, "I1_vanilla_NLO": i1,
            "I2_podgrzewanie": i2, "tlo_polaczone": True, "alpha": alpha}


# ---------------------------------------------------------------------------
# Klasyfikacja wierszy
# ---------------------------------------------------------------------------

def _pull(p: float, v: float, s: float) -> Dict[str, Any]:
    n = (p - v) / s
    a = abs(n)
    return {"n_sigma": n,
            "verdict": AGREE if a < 2.0 else (TENSION if a < 3.0 else EXCLUDED)}


def _limit(wert: float, lim: float) -> Dict[str, Any]:
    return {"n_sigma": None,
            "margin": lim / max(wert, 1e-300),
            "verdict": AGREE if wert < lim else EXCLUDED}


def konfrontuj(scen: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    scen = scen or buduj_scenariusze()
    i0, i1, i2 = scen["I0_vanilla_LO"], scen["I1_vanilla_NLO"], scen["I2_podgrzewanie"]
    d = _DANE
    wiersze: List[Dict[str, Any]] = []

    def dodaj(obs: str, model_val, data_key, verdict_info, scenariusz: str,
              derivation: str, uwaga: str = ""):
        dv = d.get(data_key, {}) if data_key else {}
        wiersze.append({
            "scenariusz": scenariusz, "obserwabla": obs,
            "model": model_val,
            "data": (f"{dv.get('value')} ± {dv.get('sigma')}" if dv.get("kind") == "measurement"
                     else (f"< {dv.get('value')} ({dv.get('cl')})" if dv.get("kind") == "upper_limit"
                           else str(dv.get("value", "kontekst")))),
            "pull": (f"{verdict_info['n_sigma']:+.2f}σ" if verdict_info.get("n_sigma") is not None
                     else f"margin ×{verdict_info.get('margin', float('nan')):.2f}"),
            "verdict": verdict_info["verdict"],
            "derivation": derivation, "source": dv.get("source", "-"),
            "uwaga": uwaga,
        })

    # --- n_s: trzy wektory danych, dwa punkty modelu -----------------------
    for nazwa, val, deriv in [
        ("I0 vanilla N=60 (LO)", i0["n_s_LO"], "hard-coded N=60, wzór LO"),
        ("I1 vanilla N=60 (tło NLO)", i1["n_s"], "hard-coded N=60, dokładne tło"),
        ("I2 podgrzewanie (najlepsze n_s)", i2["n_s_range"][1], "computed (T_rh→max)"),
        ("I2 podgrzewanie (typowe n_s)", 0.5 * (i2["n_s_range"][0] + i2["n_s_range"][1]),
         "computed (połowiczny log T_rh)"),
    ]:
        for klucz in ("n_s_planck", "n_s_pact", "n_s_pactlb"):
            dodaj(f"n_s vs {klucz}", val, klucz, _pull(val, d[klucz]["value"], d[klucz]["sigma"]),
                  nazwa, deriv)

    # --- r: obie granice ---------------------------------------------------
    for nazwa, val, deriv in [
        ("I0 vanilla N=60 (LO)", i0["r_LO"], "hard-coded N=60, wzór LO"),
        ("I1 vanilla N=60 (tło NLO)", i1["r"], "dokładne tło"),
        ("I2 podgrzewanie (max r)", i2["r_range"][1], "computed"),
    ]:
        for klucz in ("r_0.05", "r_combo"):
            dodaj(f"r vs {klucz}", val, klucz, _limit(val, d[klucz]["value"]),
                  nazwa, deriv)

    # --- running ------------------------------------------------------------
    dodaj("α_s = dn_s/dlnk vs Planck18 (+running)", i1["alpha_s"], "alpha_s_planck",
          _pull(i1["alpha_s"], d["alpha_s_planck"]["value"], d["alpha_s_planck"]["sigma"]),
          "I1 vanilla N=60 (tło NLO)", "computed")
    wiersze.append({
        "scenariusz": "I1/I2 vanilla α-attractor", "obserwabla": "α_s vs ACT+P (fit rozszerzony)",
        "model": f"α_s = {i1['alpha_s']:.2e} (<0)",
        "data": f"α_s = {d['alpha_s_actext']['value']} ± {d['alpha_s_actext']['sigma']}",
        "pull": f"{_pull(i1['alpha_s'], d['alpha_s_actext']['value'], d['alpha_s_actext']['sigma'])['n_sigma']:+.2f}σ",
        "verdict": _pull(i1['alpha_s'], d['alpha_s_actext']['value'], d['alpha_s_actext']['sigma'])["verdict"],
        "derivation": "computed", "source": d["alpha_s_actext"]["source"],
        "uwaga": "fit z β_s swobodnym; atraktory przewidują α_s<0 — kierunek odwrotny do wskazania",
    })

    # --- A_s (normalizacja wejściowa) ---------------------------------------
    dodaj("A_s (wejście normalizujące V₀)", A_S_OBS, "A_s",
          {"n_sigma": None, "margin": 1.0, "verdict": AGREE},
          "wszystkie", "measured input",
          uwaga="A_s naprawia V₀ — NIE jest predykcją (liniowość MS)")

    # --- napięcia późnego Wszechświata (kontekst) ----------------------------
    sig_h = math.hypot(d["H0_planck"]["sigma"], d["H0_shoes"]["sigma"])
    pull_h = (d["H0_shoes"]["value"] - d["H0_planck"]["value"]) / sig_h
    wiersze.append({
        "scenariusz": "model dziedziczy Planck-ΛCDM (S5)", "obserwabla": "Hubble tension H₀",
        "model": "H₀ = 67.36 (ΛCDM-inherited)", "data": f"SH0ES {d['H0_shoes']['value']} ± {d['H0_shoes']['sigma']}",
        "pull": f"{pull_h:.2f}σ", "verdict": TENSION_CONTEXT,
        "derivation": "context", "source": SH0ES_SRC,
        "uwaga": "napięcie współdzielone z ΛCDM; sektor Λ silnika nie ma mechanizmu H₀",
    })
    sig_s = math.hypot(d["S8_planck"]["sigma"], d["S8_weaklens"]["sigma"])
    pull_s = (d["S8_planck"]["value"] - d["S8_weaklens"]["value"]) / sig_s
    wiersze.append({
        "scenariusz": "model nie ma sektora formacji struktur", "obserwabla": "S₈ tension",
        "model": "brak predykcji S₈", "data": f"Planck {d['S8_planck']['value']} vs lensing {d['S8_weaklens']['value']}",
        "pull": f"{pull_s:.2f}σ", "verdict": NO_DATA,
        "derivation": "context", "source": S8_SRC,
        "uwaga": "napięcie Planck↔lensing ~2σ obecnie; poza zasięgiem silnika",
    })

    # --- diagnoza deformacji ------------------------------------------------
    n_s_model = i2["n_s_range"][1]
    nm_req = wymagane_N_dla_ns(d["n_s_pactlb"]["value"])
    wiersze.append({
        "scenariusz": "diagnoza", "obserwabla": "wymagana zmiana dla P-ACT-LB",
        "model": f"n_s_max={n_s_model:.4f}; N_wym przy LO = {nm_req:.1f} (fizycznie ≤ ~57)",
        "data": f"n_s = {d['n_s_pactlb']['value']} ± {d['n_s_pactlb']['sigma']}",
        "pull": f"{_pull(n_s_model, d['n_s_pactlb']['value'], d['n_s_pactlb']['sigma'])['n_sigma']:+.2f}σ",
        "verdict": _pull(n_s_model, d["n_s_pactlb"]["value"], d["n_s_pactlb"]["sigma"])["verdict"],
        "derivation": "computed",
        "source": d["n_s_pactlb"]["source"],
        "uwaga": "vanilla: N poza zasięgiem podgrzewania → wymaga deformacji potencjału "
                 "(literatura: δ≈0.017, arXiv:2606.24131 — zewnętrznie dopasowane)",
    })
    return wiersze


def podsumowanie(wiersze: List[Dict[str, Any]]) -> Dict[str, Any]:
    lic = {AGREE: 0, TENSION: 0, EXCLUDED: 0, NO_DATA: 0, TENSION_CONTEXT: 0}
    for w in wiersze:
        lic[w["verdict"]] = lic.get(w["verdict"], 0) + 1
    nap_pactlb = [w for w in wiersze if w["obserwabla"].startswith("n_s vs n_s_pactlb")]
    najlepszy_pull = min(abs(float(w["pull"].rstrip("σ"))) for w in nap_pactlb)
    return {
        "liczniki": lic,
        "najlepszy_pull_ns_pactlb_sigma": najlepszy_pull,
        "werdykt_sektora": (
            "TENSION z P-ACT-LB dla każdego wariantu vanilla (najlepszy "
            f"|pull| = {najlepszy_pull:.2f}σ); AGREE z Planck 2018 i P-ACT; "
            "r bezpieczne poniżej BK18; α_s<0 sprzeczny kierunkowo ze "
            "wskazaniem ACT (fit rozszerzony)."
        ),
        "uczciwosc": "A_s i α są wejściami/uwarunkowaniami; N=60 fizycznie "
                     "niedostępne (podgrzewanie w=0 daje N≤~57)",
    }


def pelna_konfrontacja(alpha: float = 3.75,
                       tlo: Optional[TloInflacji] = None) -> Dict[str, Any]:
    scen = buduj_scenariusze(alpha=alpha, tlo=tlo)
    wi = konfrontuj(scen)
    return {
        "dane": tabela_danych(),
        "scenariusze": _scenariusze_json(scen),
        "wiersze": wi,
        "podsumowanie": podsumowanie(wi),
    }


def _scenariusze_json(scen: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in scen.items():
        if k == "tlo_polaczone":
            continue
        if isinstance(v, dict) and "krzywa" in v:
            out[k] = {kk: vv for kk, vv in v.items() if kk != "krzywa"}
        else:
            out[k] = v
    return out
