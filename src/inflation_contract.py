"""Contract-complete α-attractor tilt: N from reheating, not from n_s.

Inputs that are allowed (none is the target n_s):
- A_s, the scalar amplitude (Planck, frozen on the data card)
- k_* = 0.05 Mpc^{-1} (pivot definition)
- α (project hypothesis)
- instantaneous reheating (declared)
- SM g_* at reheating (declared)

Derivation
----------
Leading α-attractor slow-roll:
    ε = 3α / (4 N²),   n_s = 1 - 2/N,   r = 12α / N².
The amplitude fixes the potential,
    V_* / M_Pl⁴ = 24 π² ε A_s.
N is the number of e-folds from horizon exit of k_* to the end of
inflation, obtained from a_* = k_*/H_* and a_end from instantaneous
reheating into the Standard Model plasma.  n_s never enters.

Likelihood
----------
Gaussian proxy for the frozen Planck n_s card:
    ln L = -½ [(n_s - n_s_obs)/σ]² - ½ ln(2π σ²).
This is not the official Planck Plik/CamSpec likelihood.

Preregistered no-go (frozen before evaluating the pull)
-------------------------------------------------------
Reject the (α, instant-reheating) hypothesis if |pull| > 2.

This is a complete contract for that phenomenological hypothesis.
It is not a Theory-of-Everything validation.
"""

from __future__ import annotations

import math
from typing import Any

# --- Frozen inputs that are not n_s -----------------------------------------
A_S = 2.100e-9
K_STAR_PER_MPC = 0.05
T0_GEV = 2.34865e-13
H0_KM_S_MPC = 67.4
REDUCED_PLANCK_GEV = 2.435323e18
G_STAR_REH = 106.75
G_STAR_S_TODAY = 3.91
# 1 Mpc^{-1} in GeV (ħ = c = 1): ħc / (1 Mpc) with ħc = 197.3 MeV fm.
GEV_PER_MPC_INV = 1.973269804e-16 / 3.085677581e22  # = 6.394e-39
H0_GEV = H0_KM_S_MPC * 2.1332e-44

# Preregistered no-go. Do not edit after looking at the pull.
NOGO_ABS_PULL = 2.0


def _potential_over_mpl4(alpha: float, n_efolds: float, a_s: float) -> float:
    epsilon = 3.0 * alpha / (4.0 * n_efolds**2)
    return 24.0 * math.pi**2 * epsilon * a_s


def derived_efolds(
    alpha: float,
    a_s: float = A_S,
    instant_reheating: bool = True,
) -> dict[str, float]:
    """Solve N from horizon exit and instantaneous reheating.

    ``n_s`` is not an argument. Instant reheating sets T_reh = T_end with
    ρ_end = V_end and V_end / V_* = ε_* (ε_end = 1 at the attractor end).
    """

    if alpha <= 0 or a_s <= 0:
        raise ValueError("alpha and A_s must be positive")
    if not instant_reheating:
        raise ValueError("only instantaneous reheating is implemented")

    k_gev = K_STAR_PER_MPC * GEV_PER_MPC_INV
    n_end = math.sqrt(3.0 * alpha / 4.0)
    n_val = 55.0
    history = []
    for _ in range(40):
        v_over = _potential_over_mpl4(alpha, n_val, a_s)
        v_gev4 = v_over * REDUCED_PLANCK_GEV**4
        h_star = math.sqrt(v_over / 3.0) * REDUCED_PLANCK_GEV
        # V_end / V_* ≈ ε_* when ε_end = 1 on this attractor family.
        eps = 3.0 * alpha / (4.0 * n_val**2)
        rho_end = max(eps, 1.0e-12) * v_gev4
        t_end = (30.0 * rho_end / (math.pi**2 * G_STAR_REH)) ** 0.25
        a_end = (G_STAR_S_TODAY / G_STAR_REH) ** (1.0 / 3.0) * (T0_GEV / t_end)
        a_star = k_gev / h_star
        n_new = math.log(a_end / a_star)
        history.append(n_new)
        if not math.isfinite(n_new) or n_new <= n_end + 1.0:
            raise ValueError("reheating solver left the physical branch")
        if abs(n_new - n_val) < 1e-8:
            n_val = n_new
            break
        n_val = 0.5 * n_val + 0.5 * n_new
    return {
        "N": float(n_val),
        "N_end": float(n_end),
        "epsilon": float(3.0 * alpha / (4.0 * n_val**2)),
        "V_over_Mpl4": float(_potential_over_mpl4(alpha, n_val, a_s)),
        "H_star_GeV": float(math.sqrt(_potential_over_mpl4(alpha, n_val, a_s) / 3.0) * REDUCED_PLANCK_GEV),
    }


def predict_tilt(alpha: float, a_s: float = A_S) -> dict[str, float]:
    derived = derived_efolds(alpha, a_s=a_s)
    n_val = derived["N"]
    return {
        **derived,
        "n_s": 1.0 - 2.0 / n_val,
        "r": 12.0 * alpha / n_val**2,
        "alpha": float(alpha),
        "A_s": float(a_s),
    }


def gaussian_log_likelihood(theory: float, value: float, sigma: float) -> float:
    pull = (theory - value) / sigma
    return -0.5 * pull * pull - 0.5 * math.log(2.0 * math.pi * sigma * sigma)


def evaluate_ns_contract(alpha: float, n_s_obs: float, n_s_sigma: float) -> dict[str, Any]:
    """Run the preregistered contract. ``n_s_obs`` is used only here."""

    pred = predict_tilt(alpha)
    pull = (pred["n_s"] - n_s_obs) / n_s_sigma
    ln_l = gaussian_log_likelihood(pred["n_s"], n_s_obs, n_s_sigma)
    ln_l_peak = gaussian_log_likelihood(n_s_obs, n_s_obs, n_s_sigma)
    passes = abs(pull) <= NOGO_ABS_PULL
    return {
        "contract_id": "NS-AT-INSTANT-01",
        "hypothesis": "α-attractor with declared α and instantaneous reheating",
        "independent_derivation": "n_s = 1-2/N with N from a_*=k_*/H_* and instant reheating",
        "inputs_excluding_target": {
            "A_s": A_S,
            "k_star_Mpc": K_STAR_PER_MPC,
            "alpha": alpha,
            "reheating": "instantaneous",
            "g_star_reh": G_STAR_REH,
        },
        "likelihood": {
            "name": "frozen Gaussian proxy for Planck n_s on OBS-2026-08",
            "official_plik_camspec": False,
            "lnL": ln_l,
            "lnL_at_data": ln_l_peak,
            "delta_chi2": float(pull * pull),
        },
        "nogo": {
            "rule": f"reject if |pull| > {NOGO_ABS_PULL}",
            "preregistered": True,
            "threshold": NOGO_ABS_PULL,
        },
        "prediction": pred,
        "n_s_obs": n_s_obs,
        "n_s_sigma": n_s_sigma,
        "pull": float(pull),
        "passes_nogo": bool(passes),
        "contract_complete": True,
        "validated_as": (
            "α-attractor tilt under instant reheating"
            if passes
            else "hypothesis rejected by the preregistered no-go"
        ),
        "validated_toe": False,
        "note": (
            "Complete contract for one inflationary hypothesis. "
            "α is still a project choice. This is not a TOE validation."
        ),
    }
