"""Observational confrontation against a frozen published-data card.

This module does **not** mint validated Theory-of-Everything predictions.
It classifies every comparison as compatible, not_excluded, excluded,
circular, incomplete, or rejected_formula.

A row becomes a validated observational prediction only if all five
contract fields are present, the target is not an input, and an official
likelihood is used. No row currently meets that bar.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from numerical_rge_solver import NumericalRGESolver
from inflation_contract import evaluate_ns_contract, legacy_ns_band_audit
from theory_core import (
    CALIBRATION,
    ESTABLISHED,
    HYPOTHESIS,
    INCOMPLETE,
    REJECTED,
    proton_lifetime_estimate,
    type_i_seesaw,
)

COMPATIBLE = "compatible"
NOT_EXCLUDED = "not_excluded"
EXCLUDED = "excluded"
CIRCULAR = "circular"
INCOMPLETE_ROW = "incomplete"
REJECTED_FORMULA = "rejected_formula"

CARD_PATH = Path(__file__).resolve().parents[1] / "docs" / "OBSERVATIONAL_CARD.json"


def load_card(path: Path | None = None) -> dict[str, Any]:
    target = path or CARD_PATH
    return json.loads(target.read_text())


def _gaussian_pull(theory: float, value: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return (theory - value) / sigma


def _row(
    ident: str,
    observable: str,
    *,
    theory: float | None,
    data: float | None,
    verdict: str,
    why: str,
    source: str,
    status: str,
    sigma: float | None = None,
    pull: float | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "id": ident,
        "observable": observable,
        "theory": theory,
        "data": data,
        "sigma": sigma,
        "pull": pull,
        "verdict": verdict,
        "validated": False,
        "contract_complete": False,
        "why_not_validated": why,
        "source": source,
        "status": status,
    }
    if extra:
        payload.update(extra)
    return payload


def _legacy_marketing_rows(
    analysis: dict[str, Any],
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Audit the v8–v14 marketing table. None of these is a TOE validation."""

    fnl = data["f_nl_equilateral"]
    gluino = data["gluino_lhc"]
    band = legacy_ns_band_audit()
    return [
        _row(
            "C11",
            "M_GUT from two-loop SM/MSSM running",
            theory=analysis["M_GUT_GeV"],
            data=None,
            verdict=CIRCULAR,
            why=(
                "M_Z couplings and M_SUSY are inputs. Closest-approach scale "
                "is a diagnostic, not a Spin(10) derivation. The legacy "
                "1.03e16 GeV is the same class of number."
            ),
            source="in-repo two-loop RGE; M_Z couplings declared",
            status=ESTABLISHED,
        ),
        _row(
            "C12",
            "sin²θ_W at a Spin(10) point",
            theory=0.375,
            data=0.375,
            verdict=CIRCULAR,
            why=(
                "Group theory in GUT normalisation gives exactly 3/8. "
                "The legacy 0.3779 is the running diagnostic at closest "
                "approach, not a low-energy prediction and not Planck data."
            ),
            source="Lie algebra of Spin(10); running diagnostic in analyze_unification",
            status=ESTABLISHED,
            extra={
                "running_diagnostic": analysis["sin2_theta_W_GUT"],
                "legacy_claim": 0.3779,
            },
        ),
        _row(
            "C13",
            "Immirzi γ = 0.2739",
            theory=0.2739,
            data=0.2739,
            verdict=CIRCULAR,
            why=(
                "γ is chosen so that a state-counting model matches S=A/4. "
                "That is a calibration, not a derivation from Spin(10)."
            ),
            source="LQG entropy-matching literature (ENP/ME values)",
            status=CALIBRATION,
        ),
        _row(
            "C14",
            "f_NL^equil legacy 14.5",
            theory=14.5,
            data=fnl["value"],
            sigma=fnl["sigma"],
            verdict=INCOMPLETE_ROW,
            why=(
                "No in-repo bispectrum. A pull against Planck −26±47 would be "
                "circular marketing: the target was never an input-independent "
                "calculation. Future CMB-S4 reach is not a present validation."
            ),
            source=fnl["source"],
            status=INCOMPLETE,
        ),
        _row(
            "C15",
            "m_gluino legacy 10.6 TeV",
            theory=1.06e4,
            data=gluino["limit"],
            verdict=INCOMPLETE_ROW,
            why=(
                "No spectrum calculation. 10.6 TeV is a Split-SUSY slogan "
                "tied to a declared M_SUSY. It sits above the LHC "
                f"~{gluino['limit']:.0f} GeV simplified-model floor, which "
                "does not confirm it."
            ),
            source=gluino["source"],
            status=INCOMPLETE,
        ),
        _row(
            "C16",
            "m_axion legacy 28.5 neV",
            theory=28.5e-9,
            data=None,
            verdict=INCOMPLETE_ROW,
            why="No implementing axion-mass derivation or CASPEr likelihood.",
            source="legacy engine slogan; CASPEr is a future search, not a measurement of 28.5 neV",
            status=INCOMPLETE,
        ),
        _row(
            "C17",
            "BR(μ→eee) legacy ~10⁻¹⁶",
            theory=1.0e-16,
            data=None,
            verdict=INCOMPLETE_ROW,
            why="No frozen loop calculation. Mu3e Phase-II is a future search.",
            source="legacy engine slogan",
            status=INCOMPLETE,
        ),
        _row(
            "C18",
            "Ω_GW(1 mHz) legacy 10⁻⁷",
            theory=1.0e-7,
            data=None,
            verdict=INCOMPLETE_ROW,
            why=(
                "No tensor-spectrum calculation. A future LISA sensitivity "
                "band is not data. The number is a slogan from the synthetic suite."
            ),
            source="legacy engine slogan; LISA is not flying",
            status=INCOMPLETE,
        ),
        _row(
            "C19",
            "legacy τ(p→e⁺π⁰) ~10³⁵–³⁶ yr",
            theory=None,
            data=data["tau_p_eppi0"]["limit"],
            verdict=REJECTED_FORMULA,
            why=(
                "The implemented dimension-6 estimate at default α_H=0.015 is "
                "about 2e34 yr and is excluded by Super-K 2.4e34 yr. The "
                "marketing band 10^35–36 yr is not that formula. The table's "
                "1.7e34 Hyper-K figure is also a stale limit."
            ),
            source=data["tau_p_eppi0"]["source"],
            status=REJECTED,
        ),
        _row(
            "C20",
            "d_S(T) interpolation 4→2",
            theory=None,
            data=None,
            verdict=REJECTED_FORMULA,
            why=(
                "Gate 1 on the independent 3D-torus ensemble (action = "
                "Manhattan length, no d_S in the action) is NO-GO for the "
                "HOLD interpolation. A qualitative CDT UV reduction is not "
                "evidence for this curve."
            ),
            source="Gate 1 in src/theory_core.py; CDT context arXiv:hep-th/0505113",
            status=REJECTED,
        ),
        _row(
            "C21",
            "asymptotic-safety g* = 0.83",
            theory=0.83,
            data=None,
            verdict=INCOMPLETE_ROW,
            why="No implementing UV-fixed-point calculation from Spin(10).",
            source="legacy engine slogan",
            status=INCOMPLETE,
        ),
        _row(
            "C22",
            "legacy α_s shift −0.0006",
            theory=-0.0006,
            data=None,
            verdict=INCOMPLETE_ROW,
            why=(
                "The pasted table gives −0.0006 with no formula. Apex instead "
                "multiplies α_s(M_Z) by 0.9736. Neither is a derivation."
            ),
            source="unidentified legacy table entry",
            status=INCOMPLETE,
        ),
        _row(
            "C23",
            "legacy n_s band 0.9629–0.9667",
            theory=0.9667,
            data=data["n_s"]["value"],
            sigma=data["n_s"]["sigma"],
            verdict=CIRCULAR,
            why=(
                f"The band is 1−2/N for hand-chosen N∈[{band['N_lo']:.2f}, "
                f"{band['N_hi']:.2f}]. That inverts the quoted tilt. "
                "Contract C1 derives N from reheating and is a different row."
            ),
            source=data["n_s"]["source"],
            status=CALIBRATION,
            extra={
                "N_lo": band["N_lo"],
                "N_hi": band["N_hi"],
                "formula": band["formula"],
                "distinct_from_contract": band["distinct_from_contract"],
            },
        ),
    ]


def confront_observables(
    alpha: float = 3.75,
    n_efolds: float = 60.0,
    m_susy: float = 5000.0,
    m_dirac_gev: float = 100.0,
    m_majorana_gev: float = 1.0e14,
    alpha_h_gev3: float = 0.015,
    legacy_br_mueg: float = 8.0e-14,
) -> dict[str, Any]:
    """Compare declared-input theory numbers to the frozen data card."""

    card = load_card()
    data = card["entries"]
    rows: list[dict[str, Any]] = []

    ns_obs = data["n_s"]
    contract = evaluate_ns_contract(alpha, ns_obs["value"], ns_obs["sigma"])
    pred = contract["prediction"]
    rows.append(
        {
            "id": "C1",
            "observable": "n_s (N from reheating, not chosen)",
            "theory": pred["n_s"],
            "data": ns_obs["value"],
            "sigma": ns_obs["sigma"],
            "pull": contract["pull"],
            "verdict": COMPATIBLE if contract["passes_nogo"] else EXCLUDED,
            "validated": False,
            "validated_phenomenology": bool(contract["passes_nogo"]),
            "contract_complete": True,
            "contract_id": contract["contract_id"],
            "why_not_validated": (
                "Contract is complete for the α-attractor + instant-reheating "
                f"hypothesis (N={pred['N']:.2f} from A_s and T_reh=T_end). "
                "α remains a project choice. This is not a TOE validation."
            ),
            "source": ns_obs["source"],
            "status": HYPOTHESIS,
            "N_derived": pred["N"],
            "lnL": contract["likelihood"]["lnL"],
            "nogo": contract["nogo"]["rule"],
        }
    )

    r_lim = data["r"]
    rows.append(
        {
            "id": "C2",
            "observable": "r (same derived N)",
            "theory": pred["r"],
            "data": r_lim["limit"],
            "sigma": None,
            "pull": None,
            "verdict": NOT_EXCLUDED if pred["r"] < r_lim["limit"] else EXCLUDED,
            "validated": False,
            "contract_complete": False,
            "why_not_validated": "An upper limit cannot confirm a point prediction.",
            "source": r_lim["source"],
            "status": HYPOTHESIS,
        }
    )

    n_s_manual = 1.0 - 2.0 / n_efolds
    pull_manual = _gaussian_pull(n_s_manual, ns_obs["value"], ns_obs["sigma"])
    rows.append(
        {
            "id": "C1b",
            "observable": "n_s with hand-chosen N (control)",
            "theory": n_s_manual,
            "data": ns_obs["value"],
            "sigma": ns_obs["sigma"],
            "pull": pull_manual,
            "verdict": CIRCULAR,
            "validated": False,
            "contract_complete": False,
            "why_not_validated": "N is chosen by hand. This row exists to show the circular alternative.",
            "source": ns_obs["source"],
            "status": CALIBRATION,
        }
    )

    t_vals, g_vals, _a, _b = NumericalRGESolver.integrate_2loop_rge_flow(
        M_SUSY=m_susy, n_points=120
    )
    analysis = NumericalRGESolver.analyze_unification(t_vals, g_vals)
    proton = proton_lifetime_estimate(
        analysis["M_GUT_GeV"], analysis["alpha_GUT"], alpha_h_gev3=alpha_h_gev3
    )
    tau = proton["tau_years"]
    sk = data["tau_p_eppi0"]
    # τ ∝ α_H^{-2}; the largest α_H still allowed by Super-K.
    alpha_h_max = alpha_h_gev3 * math.sqrt(tau / sk["limit"]) if tau > 0 else None
    rows.append(
        {
            "id": "C3",
            "observable": "τ(p→e⁺π⁰) [yr]",
            "theory": tau,
            "data": sk["limit"],
            "sigma": None,
            "pull": None,
            "verdict": NOT_EXCLUDED if tau > sk["limit"] else EXCLUDED,
            "validated": False,
            "why_not_validated": (
                "Standard dimension-6 estimate. α_H is declared. "
                f"Super-K requires α_H ≲ {alpha_h_max:.4f} GeV³ for these M_GUT, α_GUT."
                if alpha_h_max
                else "Standard dimension-6 estimate with a declared α_H."
            ),
            "source": sk["source"],
            "status": ESTABLISHED,
            "alpha_H_GeV3": alpha_h_gev3,
            "alpha_H_max_for_SK": alpha_h_max,
            "M_GUT_GeV": analysis["M_GUT_GeV"],
        }
    )

    meg = data["mu_e_gamma"]
    rows.append(
        {
            "id": "C4",
            "observable": "BR(μ→eγ) legacy claim",
            "theory": legacy_br_mueg,
            "data": meg["limit"],
            "sigma": None,
            "pull": None,
            "verdict": NOT_EXCLUDED if legacy_br_mueg < meg["limit"] else EXCLUDED,
            "validated": False,
            "why_not_validated": (
                "No frozen loop calculation or official MEG-II likelihood in-repo. "
                "The number 8e-14 is a legacy claim, not a derivation."
            ),
            "source": meg["source"],
            "status": INCOMPLETE,
        }
    )

    rows.append(
        {
            "id": "C5",
            "observable": "η_B",
            "theory": None,
            "data": data["eta_B"]["value"],
            "sigma": data["eta_B"]["sigma"],
            "pull": None,
            "verdict": INCOMPLETE_ROW,
            "validated": False,
            "why_not_validated": "No implementing Boltzmann/leptogenesis solver with frozen inputs.",
            "source": data["eta_B"]["source"],
            "status": INCOMPLETE,
        }
    )

    seesaw = type_i_seesaw(m_dirac_gev, m_majorana_gev)
    sum_nu = seesaw["m_nu_eV"]  # single-mass hierarchical stand-in
    nu_lim = data["sum_m_nu"]
    rows.append(
        {
            "id": "C6",
            "observable": "m_ν3 (type-I seesaw, one mass)",
            "theory": sum_nu,
            "data": nu_lim["limit"],
            "sigma": None,
            "pull": None,
            "verdict": NOT_EXCLUDED if sum_nu < nu_lim["limit"] else EXCLUDED,
            "validated": False,
            "why_not_validated": "m_D and M_R are declared inputs, not derived Yukawas.",
            "source": nu_lim["source"],
            "status": ESTABLISHED,
        }
    )

    g1_z, g2_z, g3_z = g_vals[:, 0]
    alpha_s_input = float((g3_z**2) / (4.0 * math.pi))
    gy2 = (3.0 / 5.0) * g1_z**2
    sin2_mz = float(gy2 / (gy2 + g2_z**2))
    rows.append(
        {
            "id": "C7",
            "observable": "α_s(M_Z)",
            "theory": alpha_s_input,
            "data": data["alpha_s_mz"]["value"],
            "sigma": data["alpha_s_mz"]["sigma"],
            "pull": _gaussian_pull(alpha_s_input, data["alpha_s_mz"]["value"], data["alpha_s_mz"]["sigma"]),
            "verdict": CIRCULAR,
            "validated": False,
            "why_not_validated": "α_s(M_Z) is an RGE boundary condition, not a prediction.",
            "source": data["alpha_s_mz"]["source"],
            "status": CALIBRATION,
        }
    )
    rows.append(
        {
            "id": "C8",
            "observable": "sin²θ_W(M_Z) from M_Z inputs",
            "theory": sin2_mz,
            "data": data["sin2_theta_w_mz"]["value"],
            "sigma": data["sin2_theta_w_mz"]["sigma"],
            "pull": _gaussian_pull(sin2_mz, data["sin2_theta_w_mz"]["value"], data["sin2_theta_w_mz"]["sigma"]),
            "verdict": CIRCULAR,
            "validated": False,
            "why_not_validated": "Computed from the same g1(M_Z), g2(M_Z) that were put in.",
            "source": data["sin2_theta_w_mz"]["source"],
            "status": CALIBRATION,
        }
    )
    rows.append(
        {
            "id": "C9",
            "observable": "1/α_em from Apex top-down",
            "theory": 137.036,
            "data": data["alpha_em_inv"]["value"],
            "sigma": data["alpha_em_inv"]["sigma"],
            "pull": _gaussian_pull(137.036, data["alpha_em_inv"]["value"], data["alpha_em_inv"]["sigma"]),
            "verdict": CIRCULAR,
            "validated": False,
            "why_not_validated": "Hidden offset −6.5504 is applied to hit the PDG target.",
            "source": data["alpha_em_inv"]["source"],
            "status": CALIBRATION,
        }
    )
    rows.append(
        {
            "id": "C10",
            "observable": "Ω_Λ from T_c⁴/M_Pl²",
            "theory": None,
            "data": 0.685,
            "sigma": None,
            "pull": None,
            "verdict": REJECTED_FORMULA,
            "validated": False,
            "why_not_validated": "Wrong dimensions; misses the Λ scale by ~42 orders.",
            "source": "TCD v15 audit",
            "status": REJECTED,
        }
    )

    rows.extend(_legacy_marketing_rows(analysis, data))

    counts = {
        COMPATIBLE: 0,
        NOT_EXCLUDED: 0,
        EXCLUDED: 0,
        CIRCULAR: 0,
        INCOMPLETE_ROW: 0,
        REJECTED_FORMULA: 0,
    }
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1

    gaussian = [row for row in rows if row["pull"] is not None and row["verdict"] == COMPATIBLE]
    chi2 = float(sum(row["pull"] ** 2 for row in gaussian))
    ndof = len(gaussian)

    complete = [row for row in rows if row.get("contract_complete")]
    pheno_pass = [row for row in complete if row.get("validated_phenomenology")]
    return {
        "title": "Observational confrontation",
        "card_id": card["card_id"],
        "validated_observational_predictions": 0,
        "validated_toe": False,
        "contract_complete_rows": len(complete),
        "phenomenology_contracts_passed": len(pheno_pass),
        "validation_rule": (
            "A TOE validation requires an independent derivation from Spin(10), "
            "immutable inputs excluding the target, an official likelihood, "
            "and a preregistered no-go. Row C1 now meets that bar for the "
            "α-attractor + instant-reheating hypothesis only: N is derived "
            "from A_s and reheating, the Planck n_s Gaussian is frozen, "
            "and |pull|>2 is the no-go. It is not a TOE validation."
        ),
        "inputs": {
            "alpha": alpha,
            "N_efolds": n_efolds,
            "M_SUSY_GeV": m_susy,
            "m_D_GeV": m_dirac_gev,
            "M_R_GeV": m_majorana_gev,
            "alpha_H_GeV3": alpha_h_gev3,
        },
        "rows": rows,
        "counts": counts,
        "chi2_compatible_gaussian": chi2,
        "ndof_compatible_gaussian": ndof,
        "note": card["note"],
    }
