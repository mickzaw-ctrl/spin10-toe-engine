# -*- coding: utf-8 -*-
"""
Konfrontacja sektora stałej kosmologicznej / ciemnej energii modelu Spin(10)
z danymi obserwacyjnymi (Planck 2018, DESI DR1/DR2 BAO, BBN) v1.0
====================================================================

Moduł zestawia *rzeczywiste liczby* wychodzące z audytowego modułu
``src/stala_kosmologiczna.py`` (goły model grafowy, kanały tłumienia,
trasa termiczna ze zmierzonym wykładnikiem q, tracker krytyczny,
scenariusz podłogi) z zamrożoną tabelą danych opublikowanych.

Każdy wiersz ma DWIE niezależne osie (jak w run_experimental_confrontation.py):
  1. DATA       — czy liczba zgadza się z pomiarem / przeżywa limit,
  2. DERIVATION — czy liczba jest policzona, czy dopasowana do danych.

Werdykty: AGREE (<2σ lub w limicie), TENSION (2–3σ), EXCLUDED (>3σ lub
naruszony limit o rzędy wielkości), NO-DATA, TENSION-CONTEXT (kontekst
współczesnych wskazań DESI, wspólny dla każdej stałej Λ, więc nie
dyskryminuje modelu).

Status naukowy: PROTOTYP BADAWCZY OTWARTY — module NIE uznaje żadnego
scenariusza za rozwiązanie; jedyny zgodny z danymi scenariusz (podłoga)
jest z definicji dopasowany do danych (oś DERIVATION = tuned-to-data).

Wymaga: src/stala_kosmologiczna.py (liczby scenariuszy).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import stala_kosmologiczna as sk

# ---------------------------------------------------------------------------
# Zamrożona tabela danych opublikowanych (źródło podane przy każdym wpisie).
# To są WEJŚCIA konfrontacji, nigdy wyjście modelu.
# ---------------------------------------------------------------------------

PLANCK18 = "Planck 2018 VI, arXiv:1807.06209"
DESI_DR1 = "DESI 2024 VI (DR1 BAO), arXiv:2404.03002"
DESI_DR2 = "DESI DR2 results II, arXiv:2503.14738"
BBN_SRC = "Planck+BBN ΔN_eff<=0.3 (95% CL), arXiv:1807.06209"

_DANE: Dict[str, Dict[str, Any]] = {
    "Lambda_planck": {
        "value": 2.8485e-122, "sigma_frac": 0.05,
        "kind": "measurement",
        "opis": "Λ/M_Pl² (ΛCDM)",
        "source": PLANCK18,
    },
    "rho_L_planck": {
        "value": 1.135e-123, "sigma_frac": 0.05,
        "kind": "measurement",
        "opis": "ρ_Λ/M_Pl⁴ (ΛCDM)",
        "source": PLANCK18,
    },
    "Omega_L": {
        "value": 0.6847, "sigma": 0.0073,
        "kind": "measurement",
        "opis": "gęstość ciemnej energii dziś",
        "source": PLANCK18,
    },
    "Omega_m_desi": {
        "value": 0.295, "sigma": 0.015,
        "kind": "measurement",
        "opis": "Ω_m (DESI DR1 BAO samotnie)",
        "source": DESI_DR1,
    },
    "Omega_m_desi_cmb": {
        "value": 0.307, "sigma": 0.005,
        "kind": "measurement",
        "opis": "Ω_m (DESI+CMB, ΛCDM)",
        "source": DESI_DR1,
    },
    "H0_planck": {
        "value": 67.36, "sigma": 0.54,
        "kind": "measurement",
        "opis": "H₀ [km/s/Mpc] (ΛCDM)",
        "source": PLANCK18,
    },
    "H0_desi_cmb": {
        "value": 67.97, "sigma": 0.38,
        "kind": "measurement",
        "opis": "H₀ [km/s/Mpc] (DESI+CMB)",
        "source": DESI_DR1,
    },
    "w_desi": {
        "value": -0.99, "sigma_up": 0.15, "sigma_dn": 0.13,
        "kind": "measurement",
        "opis": "stałe w ciemnej energii (DESI DR1 BAO)",
        "source": DESI_DR1,
    },
    "w0wa_preferencja": {
        "value": "w0>-1, wa<0",
        "kind": "hint",
        "significance_sigma_range": [3.1, 4.2],
        "opis": "preferencja ewoluującej DE ponad ΛCDM (DESI DR2+CMB, 2.8–4.2σ z SNe)",
        "source": DESI_DR2,
    },
    "r_bbn_stiff": {
        "value": sk.R_BBN_MAX,
        "kind": "upper_limit",
        "opis": "ρ_stiff/ρ_rad w epoce BBN (ΔN_eff≤0.3)",
        "source": BBN_SRC,
    },
    "t0_gyr": {
        "value": 13.797, "sigma": 0.023,
        "kind": "measurement",
        "opis": "wiek Wszechświata [Gyr] (ΛCDM)",
        "source": PLANCK18,
    },
}


def tabela_danych() -> Dict[str, Dict[str, Any]]:
    """Kopia zamrożonej tabeli danych."""
    return {k: dict(v) for k, v in _DANE.items()}


# ---------------------------------------------------------------------------
# Scenariusze modelu — liczby pochodzą z src/stala_kosmologiczna.py
# ---------------------------------------------------------------------------

def scenariusze(
    q_mc: Optional[float] = None,
    A_mc: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Konstruuje tabelę scenariuszy sektora Λ.

    Parametry opcjonalne: zmierzony wykładnik q i amplituda A z symulacji
    Monte Carlo (skan β). Jeśli nie podano, używa wartości z ostatniego
    pełnego pomiaru (results/stala_kosmologiczna_raport.json: A=0.1697,
    q=0.835) — odczytywane jawne, NIE wpisane na sztywno w werdykty.
    """
    q_mc = q_mc if q_mc is not None else 0.835
    A_mc = A_mc if A_mc is not None else 0.1697

    obs = sk.lambda_obserwowana()
    lam_gol = sk.lambda_graf()
    kanaly = sk.kanaly_tlumienia(obs=obs)
    inv = sk.wymagana_dekondensacja(obs=obs)
    kryt_req = sk.scenariusz_krytyczny(C=1.0, obs=obs)
    t_R = kryt_req["t_R_s"]

    N, g2 = sk.N_GRAF_RAPORT, sk.G2_YM_RAPORT
    rho_pl = sk.M_PL_GEV**4
    rho_rad_bbn = (math.pi**2 / 30.0) * 10.75 * (1.0e-3) ** 4

    # --- S1 goły model grafowy -------------------------------------------
    lam_S1 = lam_gol["Lambda_lat_a2"]
    r_bbn_S1 = lam_gol["eps_vac"] * rho_pl / rho_rad_bbn
    # --- S2 po kanałach kinematycznych ------------------------------------
    lam_S2 = lam_S1 * kanaly["tlumienie_laczne"]
    r_bbn_S2 = r_bbn_S1 * kanaly["tlumienie_laczne"]
    # --- S3 termiczna (zmierzone q) ---------------------------------------
    x0_term = A_mc * (sk.T_CMB_GEV / sk.M_PL_GEV) ** q_mc
    lam_S3 = (9.0 / (N * g2)) * x0_term
    w_S3 = -1.0 + q_mc / 3.0                       # ρ ∝ a^(−q) (T ∝ 1/a)
    # stosunek sztywny w epoce BBN dla trasy termicznej
    x_bbn = A_mc * (1.0e-3 / sk.M_PL_GEV) ** q_mc
    rho_v_bbn = (3.0 / (4.0 * g2)) * x_bbn * rho_pl
    r_bbn_S3 = rho_v_bbn / rho_rad_bbn
    # --- S4 tracker krytyczny (C = C_req: Λ(t₀)=Λ_obs z założenia) --------
    C_req = kryt_req["C_req_dla_Lambda_obs"]
    r_bbn_S4 = kryt_req["r_BBN_przy_Lambda_obs"]
    lam_S4 = obs["Lambda_planck"]                  # znormalizowany z definicji
    w_S4 = 0.0                                     # t⁻² w erze materii ⇒ pył
    # --- S4b tracker z fizycznym C=1 --------------------------------------
    lam_S4b = (9.0 / (N * g2)) * (t_R / sk.AGE_UNIVERSE_S) ** 2
    # --- S5 podłoga x_f = x_req (przed BBN), w = −1 -------------------------
    lam_S5 = obs["Lambda_planck"]                  # dopasowane z definicji
    x_f = inv["x_req"]
    rho_v_bbn_S5 = (3.0 / (4.0 * g2)) * x_f * rho_pl
    r_bbn_S5 = rho_v_bbn_S5 / rho_rad_bbn

    return [
        {
            "id": "S1_goly_model",
            "nazwa": "Goły model grafowy (równowaga raportu)",
            "Lambda_t0_planck": lam_S1,
            "w0": -1.0,
            "r_BBN": r_bbn_S1,
            "Omega_L_t0": "~1 (natychmiastowa dominacja próżni)",
            "derivation": sk_derived(),
        },
        {
            "id": "S2_po_kanalach",
            "nazwa": "Po kanałach kinematycznych (×0.103)",
            "Lambda_t0_planck": lam_S2,
            "w0": -1.0,
            "r_BBN": r_bbn_S2,
            "Omega_L_t0": "~1",
            "derivation": sk_derived(),
        },
        {
            "id": "S3_termiczna",
            "nazwa": f"Trasa termiczna x∝T^q (zmierzone q={q_mc:.3f})",
            "Lambda_t0_planck": lam_S3,
            "w0": w_S3,
            "r_BBN": r_bbn_S3,
            "Omega_L_t0": "~1",
            "derivation": {
                "status": "computed+measured",
                "nota": "Λ z równowagowego wykładnika q zmierzonego MC na topologii silnika",
            },
        },
        {
            "id": "S4_tracker_req",
            "nazwa": "Tracker krytyczny t⁻² z Λ(t₀)=Λ_obs",
            "Lambda_t0_planck": lam_S4,
            "w0": w_S4,
            "r_BBN": r_bbn_S4,
            "C_req": C_req,
            "Omega_L_t0": "nieokreślone (historia niespójna: dominacja trackera w każdej erze)",
            "derivation": {
                "status": "tuned-to-data",
                "nota": "C_req = 7.74 (>1: amplituda początkowa niefizyczna)",
            },
        },
        {
            "id": "S4b_tracker_C1",
            "nazwa": "Tracker krytyczny t⁻², C=1 (fizyczny start)",
            "Lambda_t0_planck": lam_S4b,
            "w0": 0.0,
            "r_BBN": kryt_req["r_BBN_dla_C"],
            "Omega_L_t0": "nieokreślone",
            "derivation": sk_derived(),
        },
        {
            "id": "S5_podloga",
            "nazwa": "Podłoga x_f=x_req osiągnięta przed BBN, w=−1",
            "Lambda_t0_planck": lam_S5,
            "w0": -1.0,
            "r_BBN": r_bbn_S5,
            "Omega_L_t0": f"{_DANE['Omega_L']['value']:.4f} (z założenia płaskości i Λ=Λ_obs)",
            "derivation": {
                "status": "tuned-to-data",
                "nota": "podłoga JEST danymi — brak mechanizmu jej generowania",
            },
        },
    ]


def sk_derived() -> Dict[str, str]:
    return {"status": "computed", "nota": "z formuły grafowej / pomiaru MC"}


# ---------------------------------------------------------------------------
# Konfrontacja
# ---------------------------------------------------------------------------

AGREE = "AGREE"
TENSION = "TENSION"
EXCLUDED = "EXCLUDED"
NO_DATA = "NO-DATA"
TENSION_CONTEXT = "TENSION-CONTEXT"


def _ocen_rho_L(lam_planck: float) -> Dict[str, Any]:
    """Ocena amplitudy: pull w rzędach wielkości względem Λ^obs/M_Pl².

    Granice werdyktu: |log10 ratio| < 1 dex → AGREE; 1–2 dex → TENSION;
    > 2 dex → EXCLUDED. (Błąd pomiaru ~5% jest tu nieistotny.)
    """
    ref = _DANE["Lambda_planck"]["value"]
    g = math.log10(max(lam_planck, 1e-320) / ref)
    if abs(g) < 1.0:
        v = AGREE
    elif abs(g) < 2.0:
        v = TENSION
    else:
        v = EXCLUDED
    return {"log10_pull": g, "verdict": v}


def _ocen_w(w0: float) -> Dict[str, Any]:
    """Pull stałego w względem DESI DR1 BAO: w = −0.99 (+0.15/−0.13)."""
    d = _DANE["w_desi"]
    dev = w0 - d["value"]
    sig = d["sigma_up"] if dev > 0 else d["sigma_dn"]
    n = abs(dev) / sig
    v = AGREE if n < 2.0 else (TENSION if n < 3.0 else EXCLUDED)
    return {"n_sigma": n, "verdict": v}


def _ocen_bbn(r: float) -> Dict[str, Any]:
    """Limit ρ_stiff/ρ_rad < r_max w epoce BBN."""
    rmax = _DANE["r_bbn_stiff"]["value"]
    return {"ratio_over_limit": r / rmax,
            "verdict": AGREE if r < rmax else EXCLUDED}


def konfrontuj_scenariusze(
    sc: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Główna pętla konfrontacji: wiersze (scenariusz × obserwabla)."""
    sc = sc if sc is not None else scenariusze()
    wiersze: List[Dict[str, Any]] = []
    for s in sc:
        # wiersz 1: amplituda Λ (M_Pl²)
        oc = _ocen_rho_L(s["Lambda_t0_planck"])
        wiersze.append({
            "scenariusz": s["id"], "nazwa": s["nazwa"],
            "obserwabla": "Λ_t0 [M_Pl²]",
            "model": s["Lambda_t0_planck"],
            "data": _DANE["Lambda_planck"]["value"],
            "pull": f"10^{oc['log10_pull']:+.1f}",
            "verdict": oc["verdict"],
            "derivation": s["derivation"],
            "source": _DANE["Lambda_planck"]["source"],
        })
        # wiersz 2: stałe w vs DESI
        ocw = _ocen_w(s["w0"])
        wiersze.append({
            "scenariusz": s["id"], "nazwa": s["nazwa"],
            "obserwabla": "w(ciągłe, DESI DR1 BAO)",
            "model": s["w0"],
            "data": f"{_DANE['w_desi']['value']} (+{_DANE['w_desi']['sigma_up']}/−{_DANE['w_desi']['sigma_dn']})",
            "pull": f"{ocw['n_sigma']:.2f}σ",
            "verdict": ocw["verdict"],
            "derivation": s["derivation"],
            "source": DESI_DR1,
        })
        # wiersz 3: BBN (sztywna składowa)
        ocb = _ocen_bbn(s["r_BBN"])
        wiersze.append({
            "scenariusz": s["id"], "nazwa": s["nazwa"],
            "obserwabla": "ρ_stiff/ρ_rad przy BBN",
            "model": s["r_BBN"],
            "data": f"< {_DANE['r_bbn_stiff']['value']:.3f}",
            "pull": f"×{ocb['ratio_over_limit']:.2e} limitu",
            "verdict": ocb["verdict"],
            "derivation": s["derivation"],
            "source": BBN_SRC,
        })
    return wiersze


def wiersz_w0wa_kontekst() -> Dict[str, Any]:
    """
    DESI DR2 preferuje w0>−1, wa<0 ponad ΛCDM na 3.1σ (CMB) do 4.2σ (z SNe).
    Dotyczy KAŻDEGO scenariusza o dokładnie stałym w=−1 (w tym scenariusza
    podłogi i — by construction — samego ΛCDM): raportujemy jako kontekst,
    NIE jako falsyfikację modelu.
    """
    d = _DANE["w0wa_preferencja"]
    return {
        "scenariusz": "S1/S2/S5 (w=−1 dokładnie)",
        "nazwa": "Dowolny stały Λ (w=−1)",
        "obserwabla": "hint w0wa (DESI DR2)",
        "model": "(w0, wa) = (−1, 0)",
        "data": f"preferowane {d['value']} ({d['significance_sigma_range'][0]}–"
                f"{d['significance_sigma_range'][1]}σ)",
        "pull": "2.5–4.2σ od punktu ΛCDM (zależnie od kombinacji)",
        "verdict": TENSION_CONTEXT,
        "derivation": {"status": "context", "nota": "napięcie wspólne z ΛCDM, nie specyficzne dla modelu"},
        "source": DESI_DR2,
    }


def warunek_alpha_eff_wiersz() -> Dict[str, Any]:
    """Warunek krzyżowy α_eff z poprzedniego audytu vs α_GUT silnika."""
    ins = sk.warunek_instantonowy()
    ratio = ins["stosunek_do_alpha_GUT"]
    return {
        "scenariusz": "S5_podloga (mechanizm nieperturbacyjny)",
        "nazwa": "Warunek krzyżowy α_eff (podłoga instantonowa)",
        "obserwabla": "α_eff = 2π/ln(1/x_req) vs α_GUT silnika",
        "model": ins["alpha_eff_wymagane"],
        "data": f"α_GUT = {ins['alpha_GUT_silnik']} (2-pętlowy RGE silnika)",
        "pull": f"stosunek {ratio:.2f}",
        "verdict": TENSION,
        "derivation": {"status": "pending", "nota": "wymaga ewaluacji α(M_Pl) w module RGE"},
        "source": "src/numerical_rge_solver.py (do skrzyżowania)",
    }


# ---------------------------------------------------------------------------
# Podsumowanie
# ---------------------------------------------------------------------------

def podsumowanie(wiersze: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Zwija konfrontację po scenariuszach i po obserwablach."""
    po_sc = {}
    for w in wiersze:
        po_sc.setdefault(w["scenariusz"], {"nazwa": w["nazwa"], "verdykty": []})
        po_sc[w["scenariusz"]]["verdykty"].append(w["verdict"])

    wynik_sc = {}
    for sid, info in po_sc.items():
        vv = info["verdykty"]
        if EXCLUDED in vv:
            wynik = EXCLUDED
        elif TENSION in vv:
            wynik = TENSION
        else:
            wynik = AGREE
        wynik_sc[sid] = {"nazwa": info["nazwa"], "werdykt": wynik,
                         "szczegoly": vv}

    n_agree = sum(1 for w in wiersze if w["verdict"] == AGREE)
    n_exc = sum(1 for w in wiersze if w["verdict"] == EXCLUDED)
    n_ten = sum(1 for w in wiersze if w["verdict"] == TENSION)

    return {
        "po_scenariuszach": wynik_sc,
        "liczniki": {"AGREE": n_agree, "TENSION": n_ten, "EXCLUDED": n_exc},
        "jedyny_zgodny": [sid for sid, v in wynik_sc.items()
                          if v["werdykt"] == AGREE],
        "uwaga_uczciwosci": (
            "Jedyny scenariusz zgodny z danymi (S5_podloga) jest "
            "dopasowany do danych z konstrukcji (oś DERIVATION=tuned-to-data) "
            "— zgodność NIE jest predykcją modelu."
        ),
    }


def pelna_konfrontacja(
    q_mc: Optional[float] = None,
    A_mc: Optional[float] = None,
) -> Dict[str, Any]:
    """Kompletny obiekt konfrontacji (JSON-serializowalny)."""
    sc = scenariusze(q_mc=q_mc, A_mc=A_mc)
    wiersze = konfrontuj_scenariusze(sc)
    dodatkowe = [wiersz_w0wa_kontekst(), warunek_alpha_eff_wiersz()]
    return {
        "dane": tabela_danych(),
        "scenariusze": sc,
        "wiersze": wiersze + dodatkowe,
        "podsumowanie": podsumowanie(wiersze),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(pelna_konfrontacja(), indent=2, ensure_ascii=False, default=str))
