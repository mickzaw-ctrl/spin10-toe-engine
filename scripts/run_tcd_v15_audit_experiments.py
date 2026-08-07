#!/usr/bin/env python3
"""Run reproducible numerical audit experiments for TCD v15.0.

All calculations use Python floating-point arithmetic on natural units (GeV).
This script does not modify tracked files.
No physical validation of Thermo-Chromo-Dynamics is claimed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from termo_chromo_dynamics import (
    CONST,
    ChromoSector,
    ThermoChromoDynamicsEngine,
    ThermoSector,
    ThermoChromoCoupling,
    qcd_crossover_formula_audit,
    qcd_dark_energy_scale_audit,
    thermal_delta_g_fraction,
)


def get_git_commit(repo_path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_path, text=True
    ).strip()


# (1) Parameter sweeps for spectral_dimension_T over T/T* from 1e-12 to 1e12
def exp1_spectral_dimension_sweep(engine: ThermoChromoDynamicsEngine) -> Dict[str, Any]:
    log_ratios = [-12.0 + i * 1.0 for i in range(25)]
    sweep_rows = []
    for idx, log_r in enumerate(log_ratios):
        r = 10.0**log_r
        T_GeV = CONST.spectral_transition_gev * r
        dS = engine.coupling.spectral_dimension_T(T_GeV)
        sweep_rows.append({
            "index": idx,
            "log10_T_over_Tstar": log_r,
            "T_over_Tstar": r,
            "T_GeV": T_GeV,
            "spectral_dimension_dS": dS,
        })

    kappa_values = [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    kappa_sensitivity = []
    for k in kappa_values:
        dS_at_Tstar = 2.0 + 2.0 / (1.0 + (1.0)**k)
        dS_at_1e_minus_2 = 2.0 + 2.0 / (1.0 + (1e-2)**k)
        dS_at_1e_plus_2 = 2.0 + 2.0 / (1.0 + (1e2)**k)
        kappa_sensitivity.append({
            "kappa": k,
            "dS_at_1e_minus_2_Tstar": dS_at_1e_minus_2,
            "dS_at_Tstar": dS_at_Tstar,
            "dS_at_1e_plus_2_Tstar": dS_at_1e_plus_2,
        })

    return {
        "experiment": "1_spectral_dimension_sweep",
        "indexing_and_range": "25 decade-spaced points, index 0 (T/T*=1e-12) to index 24 (T/T*=1e12)",
        "formula": "d_S(T) = 2 + 2 / [1 + (T / T*)^kappa] with T* = 1.22e19 GeV, kappa = 0.7",
        "key_limits": {
            "IR_limit_T_0": engine.coupling.spectral_dimension_T(0.0),
            "midpoint_T_Tstar": engine.coupling.spectral_dimension_T(CONST.spectral_transition_gev),
            "UV_limit_T_1e12_Tstar": sweep_rows[-1]["spectral_dimension_dS"],
        },
        "strictly_monotonically_decreasing": all(
            sweep_rows[i]["spectral_dimension_dS"] > sweep_rows[i+1]["spectral_dimension_dS"]
            for i in range(len(sweep_rows)-1)
        ),
        "decade_sweep_data": sweep_rows,
        "kappa_sensitivity": kappa_sensitivity,
        "classification": "project_parameterization_trend_and_analytical_asymptotic_identity",
    }


# (2) P(N,T) domain map over N=1e2..1e8 and T/T_GUT=1e-6..1e6, identifying P<=0 boundary
def exp2_coherence_domain_map() -> Dict[str, Any]:
    N_values = [10**2, 10**3, 10**4, 10**5, 10**6, 10**7, 10**8]
    ratio_log_steps = [-6.0, -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    c = CONST.coherence_coefficient
    c_squared = c**2

    domain_matrix = []
    analytical_boundaries = {}
    numerical_boundary_checks = {}

    for i, N in enumerate(N_values):
        ratio_crit = math.sqrt(N / c_squared - 1.0)
        T_crit_GeV = ratio_crit * CONST.gut_scale_gev
        analytical_boundaries[f"N_1e{int(math.log10(N))}"] = {
            "N": N,
            "ratio_crit_T_over_TGUT": ratio_crit,
            "T_crit_GeV": T_crit_GeV,
        }

        thermo_obj = ThermoSector(N=N)
        ratio_below = ratio_crit * (1.0 - 1e-5)
        ratio_above = ratio_crit * (1.0 + 1e-5)
        P_below = thermo_obj.holographic_coherence(T_GeV=ratio_below * CONST.gut_scale_gev)
        
        raised_above = False
        try:
            thermo_obj.holographic_coherence(T_GeV=ratio_above * CONST.gut_scale_gev)
        except Exception:
            raised_above = True

        numerical_boundary_checks[f"N_1e{int(math.log10(N))}"] = {
            "P_just_below_crit": P_below,
            "raises_exception_just_above_crit": raised_above,
            "numerical_match_exact": P_below > 0.0 and raised_above,
        }

        row_data = []
        for j, log_r in enumerate(ratio_log_steps):
            ratio = 10.0**log_r
            T_GeV = ratio * CONST.gut_scale_gev
            n_eff = float(N) / (1.0 + ratio**2)
            P_val = 1.0 - c / math.sqrt(n_eff)
            valid = P_val > 0.0
            row_data.append({
                "N_index": i,
                "T_ratio_index": j,
                "log10_T_over_TGUT": log_r,
                "T_over_TGUT": ratio,
                "N_eff": n_eff,
                "P_N_T": P_val if valid else None,
                "is_P_positive": valid,
            })
        domain_matrix.append({
            "N": N,
            "log10_N": int(math.log10(N)),
            "analytical_crit_ratio": ratio_crit,
            "decade_grid": row_data,
        })

    return {
        "experiment": "2_coherence_domain_map",
        "indexing_and_range": "N in [1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8] (7 steps, i=0..6); T/T_GUT in 1e-6..1e6 (13 steps, j=0..12)",
        "analytical_condition_for_P_positive": "P(N,T) > 0 <=> T/T_GUT < sqrt(N/c^2 - 1) with c = 0.33",
        "analytical_boundaries": analytical_boundaries,
        "numerical_boundary_checks": numerical_boundary_checks,
        "domain_matrix": domain_matrix,
        "classification": "exact_analytical_and_numerical_boundary",
    }


# (3) CF-vs-Polyakov monotonicity and sensitivity to crossover width
def exp3_polyakov_cf_monotonicity_and_sensitivity() -> Dict[str, Any]:
    chromo = ChromoSector()
    Tc_MeV = CONST.T_c_QCD_MeV

    T_grid_MeV = [i * 10.0 for i in range(31)]
    monotonicity_data = []
    for idx, T_MeV in enumerate(T_grid_MeV):
        L_val = chromo.polyakov_loop(T_MeV)
        CF_val = chromo.causal_fraction_from_polyakov(T_MeV)
        monotonicity_data.append({
            "index": idx,
            "T_MeV": T_MeV,
            "Polyakov_L": L_val,
            "CausalFraction_CF": CF_val,
        })

    dL_dT_all_positive = True
    dCF_dT_all_negative = True
    for i in range(len(monotonicity_data) - 1):
        if monotonicity_data[i+1]["Polyakov_L"] <= monotonicity_data[i]["Polyakov_L"]:
            dL_dT_all_positive = False
        if monotonicity_data[i+1]["CausalFraction_CF"] >= monotonicity_data[i]["CausalFraction_CF"]:
            dCF_dT_all_negative = False

    widths = [5.0, 10.0, 15.0, 20.0, 30.0, 50.0]
    width_sensitivity = []
    for w in widths:
        slope_L_Tc = 1.0 / (4.0 * w)
        slope_CF_Tc = -0.3504 * 0.5 * (0.5**0.8) / w
        CF_at_Tc_minus_10 = 0.30 + 0.438 * (1.0 - 1.0 / (1.0 + math.exp(-(-10.0)/w)))**0.8
        CF_at_Tc = 0.30 + 0.438 * (0.5**0.8)
        CF_at_Tc_plus_10 = 0.30 + 0.438 * (1.0 - 1.0 / (1.0 + math.exp(-(10.0)/w)))**0.8

        width_sensitivity.append({
            "width_w_MeV": w,
            "slope_dL_dT_at_Tc_MeV_inv": slope_L_Tc,
            "slope_dCF_dT_at_Tc_MeV_inv": slope_CF_Tc,
            "CF_at_Tc_minus_10MeV": CF_at_Tc_minus_10,
            "CF_at_Tc": CF_at_Tc,
            "CF_at_Tc_plus_10MeV": CF_at_Tc_plus_10,
        })

    return {
        "experiment": "3_polyakov_cf_monotonicity_and_sensitivity",
        "indexing_and_range": "31 temperature points T=0..300 MeV in 10 MeV steps (index 0..30); width sweep w in [5, 10, 15, 20, 30, 50] MeV",
        "analytical_derivatives": {
            "dL_dT": "dL/dT = (1/w) * L * (1 - L) > 0 for all T",
            "dCF_dL": "dCF/dL = -0.3504 * (1 - L)^(-0.2) < 0 for all L in (0, 1)",
            "dCF_dT": "dCF/dT = - (0.3504 / w) * L * (1 - L)^0.8 < 0 for all T",
        },
        "monotonicity_verified": {
            "Polyakov_L_strictly_monotone_increasing": dL_dT_all_positive,
            "CausalFraction_CF_strictly_monotone_decreasing": dCF_dT_all_negative,
            "CF_vs_L_anti_correlated": dL_dT_all_positive and dCF_dT_all_negative,
        },
        "grid_sample": monotonicity_data[::5],
        "width_sensitivity": width_sensitivity,
        "classification": "analytical_identity_and_parameter_sensitivity",
    }


# (4) QCD crossover formula sensitivity to Lambda_QCD, P and CF and untuned domain reach
def exp4_qcd_crossover_sensitivity_and_domain() -> Dict[str, Any]:
    lambda_ref = CONST.lambda_qcd_gev
    thermo = ThermoSector(N=10**6)
    P_ref = thermo.holographic_coherence()
    CF_ref = CONST.causal_fraction_reference
    Tc_target = CONST.qcd_crossover_gev

    Tc_default = lambda_ref * math.sqrt(P_ref) / CF_ref

    dTc_dLambda = math.sqrt(P_ref) / CF_ref
    dTc_dP = lambda_ref / (2.0 * CF_ref * math.sqrt(P_ref))
    dTc_dCF = - lambda_ref * math.sqrt(P_ref) / (CF_ref**2)

    lambda_sweep = []
    for idx, lam in enumerate([0.150 + i * 0.020 for i in range(11)]):
        tc_val = lam * math.sqrt(P_ref) / CF_ref
        lambda_sweep.append({
            "index": idx,
            "Lambda_QCD_GeV": lam,
            "Tc_predicted_GeV": tc_val,
            "Tc_predicted_MeV": tc_val * 1000.0,
            "rel_error_to_156p5MeV": abs(tc_val - Tc_target) / Tc_target,
        })

    CF_sweep = []
    for idx, cf in enumerate([0.30 + i * 0.05 for i in range(15)]):
        tc_val = lambda_ref * math.sqrt(P_ref) / cf
        CF_sweep.append({
            "index": idx,
            "CF": cf,
            "Tc_predicted_GeV": tc_val,
            "Tc_predicted_MeV": tc_val * 1000.0,
            "rel_error_to_156p5MeV": abs(tc_val - Tc_target) / Tc_target,
        })

    c = CONST.coherence_coefficient
    P_req_default_params = (Tc_target * CF_ref / lambda_ref)**2
    CF_req_P1_default_lambda = lambda_ref * math.sqrt(1.0) / Tc_target

    return {
        "experiment": "4_qcd_crossover_sensitivity_and_domain",
        "formula": "Tc = Lambda_QCD * sqrt(P) / CF",
        "default_evaluation": {
            "Lambda_QCD_GeV": lambda_ref,
            "P": P_ref,
            "CF": CF_ref,
            "Tc_predicted_GeV": Tc_default,
            "Tc_predicted_MeV": Tc_default * 1000.0,
            "lattice_reference_MeV": Tc_target * 1000.0,
            "relative_error": abs(Tc_default - Tc_target) / Tc_target,
        },
        "analytical_partial_derivatives": {
            "dTc_dLambda": dTc_dLambda,
            "dTc_dP_GeV": dTc_dP,
            "dTc_dCF_GeV": dTc_dCF,
        },
        "sweeps": {
            "Lambda_QCD_sweep": lambda_sweep,
            "CF_sweep": CF_sweep,
        },
        "untuned_domain_reach_analysis": {
            "CF_required_at_default_Lambda_and_P_eq_1": CF_req_P1_default_lambda,
            "is_CF_req_within_physical_bound_CF_leq_1": CF_req_P1_default_lambda <= 1.0,
            "P_required_at_default_Lambda_and_CF": P_req_default_params,
            "N_eff_required_for_P_required": (c / (1.0 - P_req_default_params))**2,
            "conclusion": (
                "At default Lambda_QCD = 217 MeV and P <= 1, reaching Tc = 156.5 MeV requires "
                "CF = 1.3866 > 1.0 (unphysical). At CF = 0.738, reaching 156.5 MeV requires P = 0.2831 "
                "(N_eff = 0.212). Under the standard domain CF <= 1.0 and P <= 1.0, 156.5 MeV is ONLY "
                "reachable if Lambda_QCD <= 156.5 MeV."
            ),
        },
        "classification": "parameter_sensitivity_and_domain_non_closure_observation",
    }


# (5) Dark-energy candidate order-of-magnitude sweeps
def exp5_dark_energy_scale_sweeps() -> Dict[str, Any]:
    Tc_ref = CONST.qcd_crossover_gev
    M_Pl = CONST.planck_mass_gev
    M_Pl_red = CONST.reduced_planck_mass_gev
    alpha_GUT_ref = CONST.alpha_gut
    rho_DE_ref = CONST.dark_energy_density_reference_gev4
    Lambda_ref = rho_DE_ref / (M_Pl_red**2)

    cand1_rows = []
    for Tc in [0.100, 0.1565, 0.200, 0.250, 0.300]:
        for Mp in [1.0e18, M_Pl_red, M_Pl]:
            Lambda_cand = (Tc**4) / (Mp**2)
            ratio = Lambda_cand / Lambda_ref
            cand1_rows.append({
                "Tc_GeV": Tc,
                "M_Pl_GeV": Mp,
                "Lambda_candidate_GeV2": Lambda_cand,
                "Lambda_reference_GeV2": Lambda_ref,
                "ratio_to_reference": ratio,
                "log10_discrepancy_orders": math.log10(ratio),
            })

    cand2_rows = []
    for alpha in [0.010, 0.020, 0.0381, 0.050, 0.080, 0.100]:
        for Tc in [0.100, 0.1565, 0.300]:
            rho_inst = (Tc**4) * math.exp(-1.0 / alpha)
            ratio = rho_inst / rho_DE_ref
            cand2_rows.append({
                "alpha_GUT": alpha,
                "Tc_GeV": Tc,
                "rho_instanton_GeV4": rho_inst,
                "rho_reference_GeV4": rho_DE_ref,
                "ratio_to_reference": ratio,
                "log10_discrepancy_orders": math.log10(ratio) if ratio > 0 else None,
            })

    inv_alpha_req = - math.log(rho_DE_ref / (Tc_ref**4))
    alpha_GUT_matching = 1.0 / inv_alpha_req

    return {
        "experiment": "5_dark_energy_scale_sweeps",
        "candidate_1_dimensional": {
            "formula": "Lambda_cand = Tc^4 / M_Pl^2 (GeV^2)",
            "unit_note": "Lambda_cand has units GeV^2; rho_DE has units GeV^4",
            "sweep_table": cand1_rows,
            "default_discrepancy_orders": math.log10((Tc_ref**4 / M_Pl**2) / Lambda_ref),
        },
        "candidate_2_instanton": {
            "formula": "rho_inst = Tc^4 * exp(-1/alpha_GUT) (GeV^4)",
            "sweep_table": cand2_rows,
            "default_discrepancy_orders": math.log10(((Tc_ref**4) * math.exp(-1.0/alpha_GUT_ref)) / rho_DE_ref),
            "alpha_GUT_required_to_match_reference": alpha_GUT_matching,
        },
        "classification": "physical_discrepancy_and_parameter_sweep",
    }


# (6) Thermal DeltaG/G at today, recombination, BBN, EW, GUT
def exp6_thermal_delta_g() -> Dict[str, Any]:
    gut_scale = CONST.gut_scale_gev
    hidden_gen = CONST.hidden_generators
    spin10_dim = CONST.spin10_dimension
    factor = hidden_gen / spin10_dim

    epochs = {
        "today_2.73K": {"T_GeV": 2.35e-13, "claimed_heuristic": 1e-32},
        "recombination_0.25eV": {"T_GeV": 2.5e-10, "claimed_heuristic": None},
        "BBN_1MeV": {"T_GeV": 1.0e-3, "claimed_heuristic": 1e-2},
        "EW_100GeV": {"T_GeV": 1.0e2, "claimed_heuristic": None},
        "GUT_1.03e16GeV": {"T_GeV": gut_scale, "claimed_heuristic": None},
    }

    results = []
    for name, data in epochs.items():
        T_GeV = data["T_GeV"]
        claimed = data["claimed_heuristic"]
        val = thermal_delta_g_fraction(T_GeV, gut_scale, hidden_gen, spin10_dim)
        results.append({
            "epoch": name,
            "T_GeV": T_GeV,
            "DeltaG_over_G_evaluated": val,
            "claimed_heuristic": claimed,
            "discrepancy_orders_of_magnitude": (
                math.log10(val / claimed) if claimed is not None else None
            ),
        })

    return {
        "experiment": "6_thermal_delta_g",
        "formula": "DeltaG/G = (T / M_GUT)^2 * (N_hidden / N_spin10) with M_GUT=1.03e16 GeV, N_hidden=125, N_spin10=45",
        "group_ratio_125_over_45": factor,
        "epoch_results": results,
        "key_observations": [
            "At today (2.35e-13 GeV), evaluated DeltaG/G = 1.45e-57 (25 orders of magnitude below claimed 1e-32).",
            "At BBN (1 MeV), evaluated DeltaG/G = 2.62e-38 (36 orders of magnitude below claimed 1e-2).",
            "The ansatz behaves purely as a tiny high-temperature expansion term, vanishing rapidly at low temperatures.",
        ],
        "classification": "analytical_identity_and_phenomenological_discrepancy",
    }


# (7) One-loop RGE baseline sensitivity to M_SUSY 1–100 TeV
def exp7_rge_m_susy_sensitivity(engine: ThermoChromoDynamicsEngine) -> Dict[str, Any]:
    M_GUT = CONST.gut_scale_gev
    alpha_GUT = CONST.alpha_gut

    b_sm = (4.1, -19.0/6.0, -7.0)
    b_mssm = (6.6, 1.0, -3.0)

    d_alpha_inv_d_ln_Msusy = [
        (b_mssm[i] - b_sm[i]) / (2.0 * math.pi) for i in range(3)
    ]

    susy_scales_tev = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    rows = []
    base_res = engine.coupling.integrate_thermo_chromo_rge(M_GUT=M_GUT, alpha_GUT=alpha_GUT, M_SUSY=1000.0)

    for tev in susy_scales_tev:
        Msusy_GeV = tev * 1000.0
        res = engine.coupling.integrate_thermo_chromo_rge(M_GUT=M_GUT, alpha_GUT=alpha_GUT, M_SUSY=Msusy_GeV)
        
        pct_alpha1 = (res["alpha_1_MZ"] - base_res["alpha_1_MZ"]) / base_res["alpha_1_MZ"] * 100.0
        pct_alpha2 = (res["alpha_2_MZ"] - base_res["alpha_2_MZ"]) / base_res["alpha_2_MZ"] * 100.0
        pct_alphas = (res["alpha_s_MZ"] - base_res["alpha_s_MZ"]) / base_res["alpha_s_MZ"] * 100.0

        rows.append({
            "M_SUSY_TeV": tev,
            "M_SUSY_GeV": Msusy_GeV,
            "alpha_1_MZ": res["alpha_1_MZ"],
            "alpha_2_MZ": res["alpha_2_MZ"],
            "alpha_s_MZ": res["alpha_s_MZ"],
            "g1_MZ": res["g_Z"][0],
            "g2_MZ": res["g_Z"][1],
            "g3_MZ": res["g_Z"][2],
            "pct_change_alpha_1_vs_1TeV": pct_alpha1,
            "pct_change_alpha_2_vs_1TeV": pct_alpha2,
            "pct_change_alpha_s_vs_1TeV": pct_alphas,
        })

    target_alpha_s = 0.1180
    low_tev, high_tev = 0.1, 100.0
    for _ in range(100):
        mid_tev = math.sqrt(low_tev * high_tev)
        mid_alpha_s = engine.coupling.integrate_thermo_chromo_rge(
            M_GUT=M_GUT, alpha_GUT=alpha_GUT, M_SUSY=mid_tev * 1000.0
        )["alpha_s_MZ"]
        if mid_alpha_s < target_alpha_s:
            low_tev = mid_tev
        else:
            high_tev = mid_tev
    fitted_M_SUSY_TeV = math.sqrt(low_tev * high_tev)

    return {
        "experiment": "7_rge_m_susy_sensitivity",
        "indexing_and_range": "7 SUSY mass scales [1, 2, 5, 10, 20, 50, 100] TeV",
        "beta_coefficients": {
            "SM": b_sm,
            "MSSM": b_mssm,
            "delta_b": [b_mssm[i] - b_sm[i] for i in range(3)],
        },
        "analytical_sensitivity_d_alpha_inv_d_ln_Msusy": {
            "gauge_1": d_alpha_inv_d_ln_Msusy[0],
            "gauge_2": d_alpha_inv_d_ln_Msusy[1],
            "gauge_3_alphas": d_alpha_inv_d_ln_Msusy[2],
        },
        "sweep_table": rows,
        "calibration_diagnostic": {
            "target_alpha_s_MZ": target_alpha_s,
            "fitted_M_SUSY_TeV_for_exact_alpha_s": fitted_M_SUSY_TeV,
            "note": "Calibration diagnostic only — target alpha_s is imported from experiment, not predicted.",
        },
        "classification": "parameter_sensitivity_and_baseline_running",
    }


def run_all_experiments(repo_path: Path) -> Dict[str, Any]:
    engine = ThermoChromoDynamicsEngine(N=10**6, M_SUSY_GeV=5000.0)
    commit_hash = get_git_commit(repo_path)

    exp1 = exp1_spectral_dimension_sweep(engine)
    exp2 = exp2_coherence_domain_map()
    exp3 = exp3_polyakov_cf_monotonicity_and_sensitivity()
    exp4 = exp4_qcd_crossover_sensitivity_and_domain()
    exp5 = exp5_dark_energy_scale_sweeps()
    exp6 = exp6_thermal_delta_g()
    exp7 = exp7_rge_m_susy_sensitivity(engine)

    return {
        "experiment_suite": "TCD v15.0 Reproducible Numerical Audit Experiments",
        "git_commit": commit_hash,
        "repo_path": str(repo_path),
        "scientific_disclaimer": "Diagnostic and audit calculations only. No physical validation of Thermo-Chromo-Dynamics is claimed.",
        "results": {
            "exp1_spectral_dimension": exp1,
            "exp2_coherence_domain": exp2,
            "exp3_polyakov_cf": exp3,
            "exp4_qcd_crossover": exp4,
            "exp5_dark_energy": exp5,
            "exp6_thermal_delta_g": exp6,
            "exp7_rge_sensitivity": exp7,
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Run TCD v15.0 Numerical Experiments")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/tcd_v15_final_audit_experiments.json"),
        help="Path to save experiment JSON output",
    )
    args = parser.parse_args()

    repo_path = Path(__file__).resolve().parents[1]
    results = run_all_experiments(repo_path)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"=== TCD v15.0 AUDIT EXPERIMENTS COMPLETED ===")
    print(f"Commit: {results['git_commit']}")
    print(f"Results written to: {args.output}\n")

    print("--- (1) Spectral Dimension d_S(T) ---")
    print(f"  T=0 (IR): {results['results']['exp1_spectral_dimension']['key_limits']['IR_limit_T_0']:.6f}")
    print(f"  T=T*:     {results['results']['exp1_spectral_dimension']['key_limits']['midpoint_T_Tstar']:.6f}")
    print(f"  T=1e12T*: {results['results']['exp1_spectral_dimension']['key_limits']['UV_limit_T_1e12_Tstar']:.6f}")

    print("\n--- (2) P(N,T) Domain Map ---")
    for k, v in results['results']['exp2_coherence_domain']['analytical_boundaries'].items():
        print(f"  {k}: (T/T_GUT)_crit = {v['ratio_crit_T_over_TGUT']:.4f} (T_crit = {v['T_crit_GeV']:.3e} GeV)")

    print("\n--- (3) Polyakov & Causal Fraction ---")
    print(f"  L(T) strictly increasing: {results['results']['exp3_polyakov_cf']['monotonicity_verified']['Polyakov_L_strictly_monotone_increasing']}")
    print(f"  CF(T) strictly decreasing: {results['results']['exp3_polyakov_cf']['monotonicity_verified']['CausalFraction_CF_strictly_monotone_decreasing']}")
    print(f"  Slope dCF/dT at Tc (w=15 MeV): {results['results']['exp3_polyakov_cf']['width_sensitivity'][2]['slope_dCF_dT_at_Tc_MeV_inv']:.6f} / MeV")

    print("\n--- (4) QCD Crossover Formula ---")
    print(f"  Formula Tc default: {results['results']['exp4_qcd_crossover']['default_evaluation']['Tc_predicted_MeV']:.2f} MeV vs Target 156.5 MeV")
    print(f"  Rel Error: {results['results']['exp4_qcd_crossover']['default_evaluation']['relative_error']*100:.2f}%")
    print(f"  CF required for 156.5 MeV at P=1: {results['results']['exp4_qcd_crossover']['untuned_domain_reach_analysis']['CF_required_at_default_Lambda_and_P_eq_1']:.4f} (> 1.0 unphysical)")

    print("\n--- (5) Dark Energy Candidates ---")
    print(f"  Cand 1 (Tc^4/M_Pl^2) Discrepancy: 10^{results['results']['exp5_dark_energy']['candidate_1_dimensional']['default_discrepancy_orders']:.1f}")
    print(f"  Cand 2 (Tc^4 exp(-1/alpha)) Discrepancy: 10^{results['results']['exp5_dark_energy']['candidate_2_instanton']['default_discrepancy_orders']:.1f}")

    print("\n--- (6) Thermal DeltaG/G ---")
    for r in results['results']['exp6_thermal_delta_g']['epoch_results']:
        print(f"  {r['epoch']}: DeltaG/G = {r['DeltaG_over_G_evaluated']:.3e}")

    print("\n--- (7) 1-Loop RGE M_SUSY Sensitivity ---")
    for r in results['results']['exp7_rge_sensitivity']['sweep_table']:
        print(f"  M_SUSY = {r['M_SUSY_TeV']:3.0f} TeV: alpha_1={r['alpha_1_MZ']:.6f}, alpha_2={r['alpha_2_MZ']:.6f}, alpha_s={r['alpha_s_MZ']:.6f}")
    print(f"  Fitted M_SUSY for alpha_s=0.1180: {results['results']['exp7_rge_sensitivity']['calibration_diagnostic']['fitted_M_SUSY_TeV_for_exact_alpha_s']:.3f} TeV")


if __name__ == "__main__":
    main()
