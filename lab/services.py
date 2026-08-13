"""Computation layer for the Research Lab.

Every returned payload carries an epistemic ``status``:

- ``established_physics`` — standard formula, declared inputs
- ``project_hypothesis`` — repository ansatz, not derived
- ``unverified_assumption`` — mapping without an operator correspondence
- ``rejected_as_stated`` — failed a dimensional or numerical gate
- ``incomplete_prediction`` — missing signal, covariance, or likelihood
- ``calibration`` — hidden factor fitted to a target

Nothing in this module converts a reference input into a confirmed prediction.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ift_egr_closure import (  # noqa: E402
    ClosureInputError,
    audit_partial_order,
    causal_order_violation_fraction,
    gft_condensate_number_profile,
    isolated_horizon_entropy_upper_bound,
    lqc_area_gap_planck,
    lqc_critical_density_ratio,
    lqc_hubble_squared,
    puncture_area_planck,
)
from numerical_rge_solver import NumericalRGESolver  # noqa: E402
from termo_chromo_dynamics import (  # noqa: E402
    CONST,
    TCDInputError,
    ThermoChromoDynamicsEngine,
    carnot_efficiency,
    lattice_beta_from_alpha,
    qcd_crossover_formula_audit,
    qcd_dark_energy_scale_audit,
    thermal_delta_g_fraction,
)

ESTABLISHED = "established_physics"
HYPOTHESIS = "project_hypothesis"
UNVERIFIED = "unverified_assumption"
REJECTED = "rejected_as_stated"
INCOMPLETE = "incomplete_prediction"
CALIBRATION = "calibration"

PLANCK_NS = 0.9649
PLANCK_NS_ERR = 0.0042
BICEP_R_LIMIT = 0.036
M_Z = 91.1876
ALPHA_EM_PDG_INV = 137.036
ALPHA_S_PDG = 0.1180
APEX_ALPHA_S_FACTOR = 0.9736
APEX_ALPHA_EM_OFFSET = 6.5504


def _finite(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite numeric value")
    return number


def _clamp_int(value: Any, lo: int, hi: int, name: str) -> int:
    if isinstance(value, bool) or int(value) != value:
        raise ValueError(f"{name} must be an integer")
    number = int(value)
    if number < lo or number > hi:
        raise ValueError(f"{name} must lie in [{lo}, {hi}]")
    return number


def _clamp_float(value: Any, lo: float, hi: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    number = _finite(value)
    if number < lo or number > hi:
        raise ValueError(f"{name} must lie in [{lo}, {hi}]")
    return number


def lab_status() -> dict[str, Any]:
    ledger_path = REPO_ROOT / "docs" / "TCD_ASSUMPTION_LEDGER.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    counts: dict[str, int] = {}
    for entry in ledger.get("entries", []):
        key = entry.get("classification", "unknown")
        counts[key] = counts.get(key, 0) + 1
    return {
        "name": "Spin(10) Research Lab",
        "version": "16.1.0",
        "scientific_status": "internally closed research programme; physical theory empirically open",
        "validated_predictions": 0,
        "what_this_is": (
            "A fail-closed workbench plus the v16.1 theoretical specification: "
            "Spin(10) group theory, standard GUT estimates, independent "
            "Gate-1 / Gate-2 computations, and the prescribed-P Jacobson action."
        ),
        "what_this_is_not": (
            "Not a completed Theory of Everything, not an observational "
            "validation, and not a commercial inference service."
        ),
        "gates": {
            "KEEP": [
                "Fail-closed TCD architecture and assumption ledger",
                "Standard one-loop / two-loop SM–MSSM RGE baseline",
                "Random-walk spectral estimator on reference graphs",
                "Standard LQC bounce algebra (imported, not derived here)",
                "Spin(10) 16-embedding and sin²θ_W=3/8 at a GUT point",
                "Prescribed-P action ∫ P R and the extra-term theorem (Gate 3)",
            ],
            "HOLD": [
                "Causal-fraction ↔ Polyakov map",
                "Graph coherence ansatz P(N,T)=1−c/√N_eff (still underived)",
                "Spin(10) identification of the alpha-attractor parameter",
            ],
            "NO-GO": [
                "QCD crossover formula → 156 MeV",
                "Dark energy from T_c^4 / M_Pl^2",
                "Torsion-resummed fifth force at 10^{-6}",
                "Thermal ΔG/G ~ 10^{-2} at BBN",
                "TCD d_S(T) interpolation on the independent 3D-torus ensemble",
                "N_gen=3 from Atiyah–Singer or E8 as stated",
                "Einstein with G_eff=G0/P as the field equation for variable P",
                "P(N,T) from the local Clausius argument",
            ],
        },
        "ledger_counts": counts,
        "modules": [
            {"id": "rge", "label": "Gauge unification RGE", "status": ESTABLISHED},
            {"id": "spectral", "label": "Spectral dimension estimator", "status": ESTABLISHED},
            {"id": "tcd", "label": "TCD audit diagnostics", "status": HYPOTHESIS},
            {"id": "lqc", "label": "LQC / IFT-EGR closure", "status": ESTABLISHED},
            {"id": "inflation", "label": "α-attractor phenomenology", "status": ESTABLISHED},
            {"id": "theory", "label": "v16.1 theoretical specification", "status": ESTABLISHED},
            {"id": "jacobson", "label": "Jacobson / prescribed-P action", "status": ESTABLISHED},
            {"id": "data", "label": "Observational confrontation", "status": ESTABLISHED},
            {"id": "ledger", "label": "Assumption ledger", "status": ESTABLISHED},
        ],
    }


def run_rge(m_susy: float = 5000.0, loops: int = 2, n_points: int = 240) -> dict[str, Any]:
    """Integrate SM → split-SUSY / MSSM gauge couplings from M_Z upward."""

    susy = _clamp_float(m_susy, 200.0, 1.0e7, "m_susy")
    loop_count = _clamp_int(loops, 1, 2, "loops")
    points = _clamp_int(n_points, 40, 800, "n_points")

    solver = NumericalRGESolver
    if loop_count == 1:
        t_vals, g_vals, alpha_gut_end, _best = solver.integrate_1loop_rge_flow(
            M_SUSY=susy, n_points=points
        )
        method = "one-loop SM / MSSM threshold"
    else:
        t_vals, g_vals, alpha_gut_end, _best = solver.integrate_2loop_rge_flow(
            M_SUSY=susy, n_points=points
        )
        method = "two-loop SM / MSSM threshold"

    analysis = solver.analyze_unification(t_vals, g_vals)
    mu = np.exp(t_vals)
    alphas = (g_vals**2) / (4.0 * np.pi)
    alpha_inv = 1.0 / alphas

    g1_z, g2_z, g3_z = g_vals[:, 0]
    gy2 = (3.0 / 5.0) * g1_z**2
    alpha_em_mz = (gy2 * g2_z**2) / (4.0 * np.pi * (gy2 + g2_z**2))
    alpha_s_mz = float(alphas[2, 0])

    stride = max(1, len(mu) // 220)
    return {
        "status": ESTABLISHED,
        "method": method,
        "note": (
            "Standard gauge RGE with a declared Split-SUSY threshold. "
            "Unification quality is a diagnostic, not a Spin(10) derivation. "
            "Low-energy couplings are inputs at M_Z, not predictions."
        ),
        "inputs": {"M_SUSY_GeV": susy, "loops": loop_count, "n_points": points},
        "mu_GeV": mu[::stride].tolist(),
        "alpha_inv": {
            "1": alpha_inv[0, ::stride].tolist(),
            "2": alpha_inv[1, ::stride].tolist(),
            "3": alpha_inv[2, ::stride].tolist(),
        },
        "analysis": {
            **analysis,
            "alpha_GUT_at_target_scale": float(alpha_gut_end),
            "alpha_s_MZ_input": alpha_s_mz,
            "alpha_em_MZ_from_inputs": float(alpha_em_mz),
            "alpha_em_MZ_inv": float(1.0 / alpha_em_mz),
            "sin2_theta_W_MZ": float(gy2 / (gy2 + g2_z**2)),
        },
        "calibration_audit": {
            "status": CALIBRATION,
            "apex_hidden_alpha_s_factor": APEX_ALPHA_S_FACTOR,
            "apex_hidden_alpha_em_offset": APEX_ALPHA_EM_OFFSET,
            "note": (
                "physics_apex_v13_core.py multiplies α_s(M_Z) by 0.9736 and "
                "subtracts 6.5504 from 1/α_em to hit PDG targets. Those knobs "
                "are not a top-down derivation."
            ),
            "pdg_alpha_s_MZ": ALPHA_S_PDG,
            "pdg_alpha_em_inv": ALPHA_EM_PDG_INV,
        },
        "references": [
            "Machacek, Vaughn, Nucl. Phys. B 222 (1983) 83",
            "Martin, Vaughn, Phys. Rev. D 50 (1994) 2282",
        ],
    }


def _neighbors_regular(graph: nx.Graph) -> np.ndarray:
    nodes = list(graph.nodes())
    index = {node: i for i, node in enumerate(nodes)}
    degrees = [graph.degree(node) for node in nodes]
    if len(set(degrees)) != 1:
        raise ValueError("vectorized walker requires a regular graph")
    degree = degrees[0]
    table = np.empty((len(nodes), degree), dtype=np.int32)
    for i, node in enumerate(nodes):
        table[i] = [index[nbr] for nbr in graph.neighbors(node)]
    return table


def _spectral_from_return(return_probs: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t_vals = np.arange(1, len(return_probs) + 1, dtype=np.float64)
    valid = return_probs > 0
    t_valid = t_vals[valid]
    p_valid = return_probs[valid]
    if len(t_valid) < 5:
        return t_valid, p_valid, np.zeros_like(t_valid)

    log_t = np.log(t_valid)
    log_p = np.log(p_valid)
    d_s = np.zeros_like(t_valid)
    window = min(7, len(t_valid))
    half = window // 2
    for i in range(len(t_valid)):
        start = max(0, i - half)
        end = min(len(t_valid), i + half + 1)
        if end - start < 3:
            left = max(0, i - 1)
            right = min(len(t_valid) - 1, i + 1)
            denom = log_t[right] - log_t[left]
            d_s[i] = -2.0 * (log_p[right] - log_p[left]) / denom if denom else 0.0
        else:
            slope, _ = np.polyfit(log_t[start:end], log_p[start:end], 1)
            d_s[i] = -2.0 * slope
    return t_valid, p_valid, d_s


def _lazy_walk(neighbors: np.ndarray, steps: int, walkers: int, lazy: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n_nodes, degree = neighbors.shape
    current = rng.integers(0, n_nodes, size=walkers, dtype=np.int32)
    start = current.copy()
    probs = np.empty(steps, dtype=np.float64)
    for t in range(steps):
        move = rng.random(walkers) >= lazy
        if np.any(move):
            movers = current[move]
            choices = rng.integers(0, degree, size=movers.shape[0])
            current[move] = neighbors[movers, choices]
        probs[t] = float(np.mean(current == start))
    return probs


def run_spectral(
    graph: str = "torus",
    size: int = 24,
    walkers: int = 4000,
    steps: int = 80,
    seed: int = 42,
) -> dict[str, Any]:
    """Estimate d_S(t) on a reference graph with known continuum dimension."""

    kind = str(graph).lower()
    if kind not in {"cycle", "torus", "random"}:
        raise ValueError("graph must be cycle, torus, or random")
    walkers_n = _clamp_int(walkers, 200, 20000, "walkers")
    steps_n = _clamp_int(steps, 20, 250, "steps")
    seed_n = _clamp_int(seed, 0, 10**9, "seed")

    if kind == "cycle":
        n = _clamp_int(size, 20, 400, "size")
        g = nx.cycle_graph(n)
        expected = 1.0
        label = f"1D cycle, N={n}"
    elif kind == "torus":
        n = _clamp_int(size, 8, 40, "size")
        g = nx.grid_2d_graph(n, n, periodic=True)
        expected = 2.0
        label = f"2D periodic torus, {n}×{n}"
    else:
        n = _clamp_int(size, 16, 120, "size")
        if n % 2:
            n += 1
        g = nx.random_regular_graph(4, n, seed=seed_n)
        expected = None
        label = f"4-regular random graph, N={n}"

    started = time.perf_counter()
    neighbors = _neighbors_regular(g)
    probs = _lazy_walk(neighbors, steps_n, walkers_n, 0.5, seed_n)
    t_vals, p_vals, d_s = _spectral_from_return(probs)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    # Fit window away from t=1 transients and finite-size saturation.
    t_sat = max(12.0, math.sqrt(g.number_of_nodes()) * 1.2)
    fit = (t_vals >= 8.0) & (t_vals <= t_sat)
    if int(np.sum(fit)) < 4:
        fit = t_vals >= max(4.0, t_vals[len(t_vals) // 3] if len(t_vals) else 4.0)
    d_fit = float(np.mean(d_s[fit])) if np.any(fit) else float("nan")
    d_err = abs(d_fit - expected) if expected is not None and math.isfinite(d_fit) else None
    passed = d_err is not None and d_err < 0.15

    return {
        "status": ESTABLISHED,
        "note": (
            "Lazy random-walk estimator d_S = −2 d ln P / d ln t. "
            "A pass on a reference graph validates the estimator, not the "
            "TCD d_S(T) interpolation."
        ),
        "graph": kind,
        "label": label,
        "n_nodes": g.number_of_nodes(),
        "n_edges": g.number_of_edges(),
        "walkers": walkers_n,
        "steps": steps_n,
        "seed": seed_n,
        "elapsed_ms": elapsed_ms,
        "expected_dimension": expected,
        "fit_mean_d_S": d_fit,
        "absolute_error": d_err,
        "pass_threshold": 0.15,
        "estimator_pass": passed,
        "t": t_vals.tolist(),
        "return_probability": p_vals.tolist(),
        "d_S": d_s.tolist(),
        "hypothesis_curve_status": HYPOTHESIS,
        "hypothesis_note": (
            "The TCD target d_S = 4(1−e^{−N/150}) is a project curve and "
            "is never treated as data."
        ),
    }


def run_tcd_sweep(points: int = 80) -> dict[str, Any]:
    """Temperature sweep of TCD diagnostics with explicit classifications."""

    n_points = _clamp_int(points, 20, 200, "points")
    engine = ThermoChromoDynamicsEngine()
    chromo = engine.chromo
    coupling = engine.coupling
    thermo = engine.thermo

    t_mev = np.geomspace(20.0, 800.0, n_points)
    polyakov = [chromo.polyakov_loop(float(t)) for t in t_mev]
    cf = [chromo.causal_fraction_from_polyakov(float(t)) for t in t_mev]
    sigma = [chromo.string_tension(float(t)) for t in t_mev]
    eta_s = [chromo.eta_over_s(float(t)) for t in t_mev]

    t_star = CONST.spectral_transition_gev
    t_planck = np.geomspace(1.0e12, 1.0e22, n_points)
    d_s = [coupling.spectral_dimension_T(float(t)) for t in t_planck]

    t_ratio = np.array([0.01, 0.1, 1.0, 10.0, 100.0])
    frozen_curve = {
        str(ratio): coupling.spectral_dimension_T(ratio * t_star) for ratio in t_ratio
    }

    audit = engine.compute_critical_temperatures()
    dark = qcd_dark_energy_scale_audit(
        CONST.qcd_crossover_gev,
        CONST.planck_mass_gev,
        CONST.reduced_planck_mass_gev,
        CONST.alpha_gut,
        CONST.dark_energy_density_reference_gev4,
    )
    formula = audit["T_c_formula_audit"]
    try:
        coherence = thermo.holographic_coherence()
        coherence_status = HYPOTHESIS
    except TCDInputError as exc:
        coherence = None
        coherence_status = f"outside_ansatz_domain: {exc}"

    return {
        "status": HYPOTHESIS,
        "note": (
            "Toy diagnostics only. Lattice T_c is an input. The CF–Polyakov "
            "map is unverified. Spectral d_S(T) is a HOLD interpolation."
        ),
        "t_mev": t_mev.tolist(),
        "polyakov": {
            "values": polyakov,
            "status": HYPOTHESIS,
            "note": "Logistic crossover, not a lattice Polyakov loop.",
        },
        "causal_fraction": {
            "values": cf,
            "status": UNVERIFIED,
            "note": "Anti-correlated with the toy Polyakov diagnostic.",
        },
        "string_tension_GeV2": {
            "values": sigma,
            "status": HYPOTHESIS,
            "note": "Continuous toy parametrization of σ(T).",
        },
        "eta_over_s": {
            "values": eta_s,
            "status": HYPOTHESIS,
            "note": "Phenomenological interpolation around the KSS bound.",
        },
        "spectral": {
            "T_GeV": t_planck.tolist(),
            "d_S": d_s,
            "T_star_GeV": t_star,
            "frozen_predictions": frozen_curve,
            "status": HYPOTHESIS,
            "decision": "HOLD",
        },
        "audits": {
            "qcd_crossover": {**formula, "decision": "NO-GO"},
            "dark_energy": {**dark, "decision": "NO-GO"},
            "lattice_beta_unit_norm": {
                "beta": lattice_beta_from_alpha(CONST.alpha_gut, 1.0),
                "legacy_claim": 24.0,
                "status": REJECTED,
                "decision": "NO-GO",
            },
            "carnot_planck_to_gut": {
                "efficiency": carnot_efficiency(CONST.planck_mass_gev, CONST.gut_scale_gev),
                "legacy_claim": 0.87,
                "status": REJECTED,
                "decision": "NO-GO",
            },
            "delta_g": {
                "today": thermal_delta_g_fraction(2.35e-13, CONST.gut_scale_gev),
                "bbn_1MeV": thermal_delta_g_fraction(1.0e-3, CONST.gut_scale_gev),
                "gut": thermal_delta_g_fraction(CONST.gut_scale_gev, CONST.gut_scale_gev),
                "status": HYPOTHESIS,
                "decision": "NO-GO without covariant derivation",
            },
            "coherence_P": {
                "value": coherence,
                "status": coherence_status,
                "decision": "HOLD",
            },
            "lattice_Tc_MeV": {
                "value": CONST.T_c_QCD_MeV,
                "uncertainty": CONST.T_c_err_MeV,
                "status": ESTABLISHED,
                "note": "HotQCD external reference, not a TCD output.",
                "source": "arXiv:1908.09552",
            },
        },
        "kss_bound": 1.0 / (4.0 * math.pi),
        "t_c_mev": CONST.T_c_QCD_MeV,
    }


def run_lqc(gamma: float = 0.2375, spin: float = 0.5, punctures: int = 100) -> dict[str, Any]:
    """Standard LQC / isolated-horizon algebra plus GFT and causal-order checks."""

    gamma_v = _clamp_float(gamma, 0.05, 1.5, "gamma")
    spin_v = _clamp_float(spin, 0.5, 20.0, "spin")
    if abs(2.0 * spin_v - round(2.0 * spin_v)) > 1e-9:
        raise ValueError("spin must be a positive half-integer")
    n_p = _clamp_int(punctures, 1, 10_000, "punctures")

    delta = lqc_area_gap_planck(gamma_v)
    rho_c = lqc_critical_density_ratio(gamma_v)
    area = puncture_area_planck(spin_v, gamma_v)
    entropy = isolated_horizon_entropy_upper_bound([spin_v] * n_p)

    rho = np.linspace(0.0, rho_c, 160)
    h2 = np.array([lqc_hubble_squared(float(value), rho_c) for value in rho])
    bounce_idx = int(np.argmax(h2))

    phi = np.linspace(-1.2, 1.2, 160)
    condensate = gft_condensate_number_profile(phi, minimum_number=1.0)

    # A 4-element causal diamond: 0 ≼ 1, 0 ≼ 2, 1 ≼ 3, 2 ≼ 3.
    order = np.array(
        [
            [1, 1, 1, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
        ],
        dtype=bool,
    )
    weights_ok = np.array(
        [
            [0.0, 0.4, 0.4, 0.0],
            [0.0, 0.0, 0.0, 0.3],
            [0.0, 0.0, 0.0, 0.3],
            [0.0, 0.0, 0.0, 0.0],
        ]
    )
    weights_bad = weights_ok.copy()
    weights_bad[3, 0] = 0.5
    audit = audit_partial_order(order)
    violation_ok = causal_order_violation_fraction(weights_ok, order)
    violation_bad = causal_order_violation_fraction(weights_bad, order)

    return {
        "status": ESTABLISHED,
        "note": (
            "These are standard LQC / isolated-horizon identities and a "
            "free-GFT number-profile ansatz. They are not IFT-EGR predictions "
            "and do not derive the cosmological constant."
        ),
        "inputs": {"gamma": gamma_v, "spin": spin_v, "punctures": n_p},
        "area_gap_planck": delta,
        "rho_c_over_rho_Pl": rho_c,
        "puncture_area_planck": area,
        "entropy_upper_bound": entropy,
        "entropy_per_area": entropy / (n_p * area),
        "bekenstein_hawking_target": 0.25,
        "immirzi_note": (
            "Matching S ≈ A/4ℓ_P² selects γ from a state-counting model. "
            "Common literature values are γ≈0.2375 (DL) and γ≈0.274 (ME). "
            "The engine does not derive γ from Spin(10)."
        ),
        "bounce": {
            "rho_over_rho_Pl": rho.tolist(),
            "H2": h2.tolist(),
            "rho_at_max_H2": float(rho[bounce_idx]),
            "H2_max": float(h2[bounce_idx]),
            "note": "H² ∝ ρ(1−ρ/ρ_c) vanishes at the bounce ρ=ρ_c.",
        },
        "gft": {
            "phi": phi.tolist(),
            "N_phi": condensate.tolist(),
            "status": HYPOTHESIS,
            "note": "N(φ)=N_min cosh(√(12πG) φ). Does not identify quanta with punctures.",
        },
        "causal_order": {
            "is_partial_order": audit.is_partial_order,
            "reflexive": audit.is_reflexive,
            "antisymmetric": audit.is_antisymmetric,
            "transitive": audit.is_transitive,
            "violation_causal_kernel": violation_ok,
            "violation_with_backward_weight": violation_bad,
            "status": ESTABLISHED,
            "note": "Zero violation is necessary but not sufficient for a causal quantum theory.",
        },
    }


def run_inflation(alpha: float = 3.75, n_efolds: float = 60.0) -> dict[str, Any]:
    """α-attractor slow-roll phenomenology with Planck comparison bands."""

    alpha_v = _clamp_float(alpha, 0.1, 20.0, "alpha")
    n_v = _clamp_float(n_efolds, 40.0, 80.0, "n_efolds")

    def observables(alpha_loc: float, n_loc: float) -> dict[str, float]:
        epsilon = 3.0 * alpha_loc / (4.0 * n_loc**2)
        n_s = 1.0 - 2.0 / n_loc
        n_s_sr = 1.0 - 6.0 * epsilon + 2.0 * (2.0 / n_loc)
        r = 12.0 * alpha_loc / n_loc**2
        return {
            "epsilon": epsilon,
            "n_s_leading": n_s,
            "n_s_slow_roll": n_s_sr,
            "r": r,
        }

    here = observables(alpha_v, n_v)
    n_grid = np.linspace(45.0, 75.0, 80)
    curve = [observables(alpha_v, float(n)) for n in n_grid]
    alpha_grid = np.linspace(0.2, 10.0, 80)
    r_vs_alpha = [observables(float(a), n_v)["r"] for a in alpha_grid]

    n_s = here["n_s_leading"]
    sigma = abs(n_s - PLANCK_NS) / PLANCK_NS_ERR
    r_ok = here["r"] < BICEP_R_LIMIT

    return {
        "status": ESTABLISHED,
        "hypothesis_status": HYPOTHESIS,
        "note": (
            "α-attractors are a standard inflationary class. Identifying "
            "α = dim(Spin(10))/12 = 3.75 is a project hypothesis, not a derivation."
        ),
        "inputs": {"alpha": alpha_v, "N_efolds": n_v},
        "observables": here,
        "comparison": {
            "planck_n_s": PLANCK_NS,
            "planck_n_s_err": PLANCK_NS_ERR,
            "n_s_pull_sigma": sigma,
            "bicep_r_limit": BICEP_R_LIMIT,
            "r_below_limit": r_ok,
        },
        "n_grid": n_grid.tolist(),
        "n_s_of_N": [row["n_s_leading"] for row in curve],
        "r_of_N": [row["r"] for row in curve],
        "alpha_grid": alpha_grid.tolist(),
        "r_of_alpha": r_vs_alpha,
        "spin10_alpha": 45.0 / 12.0,
    }


def run_ledger() -> dict[str, Any]:
    path = REPO_ROOT / "docs" / "TCD_ASSUMPTION_LEDGER.json"
    ledger = json.loads(path.read_text())
    legacy = [
        {
            "observable": "BR(μ→eγ)",
            "legacy_value": "8e-14",
            "reference": "MEG-II < 6e-14 (target)",
            "status": INCOMPLETE,
            "reason": "No frozen loop calculation or official likelihood in-repo.",
        },
        {
            "observable": "α_em",
            "legacy_value": "1/137.036",
            "reference": "PDG 1/137.036",
            "status": CALIBRATION,
            "reason": "Hidden offset −6.5504 applied after one-loop running.",
        },
        {
            "observable": "α_s(M_Z)",
            "legacy_value": "0.118",
            "reference": "PDG 0.1180",
            "status": CALIBRATION,
            "reason": "Hidden factor 0.9736 applied after RGE integration.",
        },
        {
            "observable": "Immirzi γ",
            "legacy_value": "0.2739",
            "reference": "LQG entropy-matching literature",
            "status": UNVERIFIED,
            "reason": "Selected by a closeness check, not derived from Spin(10).",
        },
        {
            "observable": "n_s / r",
            "legacy_value": "0.9667 / 0.0125",
            "reference": "Planck PR4 / BICEP",
            "status": HYPOTHESIS,
            "reason": "Standard α-attractor formulae; α=3.75 is a project choice.",
        },
        {
            "observable": "T_c QCD",
            "legacy_value": "156.5 MeV",
            "reference": "HotQCD 156.5±1.5 MeV",
            "status": REJECTED,
            "reason": "TCD formula evaluates to ≈294 MeV; 156.5 MeV is an input.",
        },
        {
            "observable": "Ω_Λ from T_c^4/M_Pl^2",
            "legacy_value": "0.685",
            "reference": "Planck ΛCDM",
            "status": REJECTED,
            "reason": "Wrong dimensions; misses the Λ scale by ~42 orders.",
        },
        {
            "observable": "d_S(T) 4→2",
            "legacy_value": "interpolation",
            "reference": "Gate 1 independent 3D-torus ensemble",
            "status": REJECTED,
            "reason": "Gate 1 is NO-GO for the HOLD interpolation on that ensemble.",
        },
        {
            "observable": "η_B",
            "legacy_value": "6.11e-10",
            "reference": "Planck+BBN 6.12e-10",
            "status": INCOMPLETE,
            "reason": "No Boltzmann/leptogenesis solver; agreement is not a derivation.",
        },
        {
            "observable": "f_NL^eq",
            "legacy_value": "14.5",
            "reference": "Planck 2018 equilateral −26±47",
            "status": INCOMPLETE,
            "reason": "No bispectrum. Future CMB-S4 reach is not a validation.",
        },
        {
            "observable": "m_gluino",
            "legacy_value": "10.6 TeV",
            "reference": "LHC ≳ 2.2 TeV",
            "status": INCOMPLETE,
            "reason": "Split-SUSY slogan at a declared M_SUSY; no spectrum.",
        },
        {
            "observable": "m_axion",
            "legacy_value": "28.5 neV",
            "reference": "CASPEr (future search)",
            "status": INCOMPLETE,
            "reason": "No axion-mass derivation or CASPEr likelihood.",
        },
        {
            "observable": "Ω_GW(1 mHz)",
            "legacy_value": "1e-7",
            "reference": "LISA (not flying)",
            "status": INCOMPLETE,
            "reason": "No tensor spectrum. A future sensitivity is not data.",
        },
        {
            "observable": "τ_p marketing 1e35–36 yr",
            "legacy_value": "1e35–36",
            "reference": "Super-K > 2.4e34 yr",
            "status": REJECTED,
            "reason": "Implemented estimate is ~2e34 yr and is excluded at α_H=0.015.",
        },
        {
            "observable": "g* (AS)",
            "legacy_value": "0.83",
            "reference": "none",
            "status": INCOMPLETE,
            "reason": "No UV fixed-point calculation from Spin(10).",
        },
    ]
    return {
        "status": ESTABLISHED,
        "ledger": ledger,
        "legacy_claims": legacy,
        "validated_predictions": 0,
    }


def run_theory(fast: bool = True) -> dict[str, Any]:
    """Run the v16 specification, including independent gates."""

    from theory_core import complete_theory

    return complete_theory(run_gates=True, fast=bool(fast))


def run_jacobson(
    n_nodes: int = 1_000_000,
    omega: float = 0.0,
    points: int = 80,
) -> dict[str, Any]:
    """Gate 3: prescribed-P action, extra-term sizes, no derivation of P."""

    from jacobson_clausius import (
        JacobsonInputError,
        gate3_jacobson_action,
        temperature_sweep,
    )

    nodes = _clamp_int(n_nodes, 100, 10**10, "n_nodes")
    omega_v = _clamp_float(omega, 0.0, 1.0e5, "omega")
    n_points = _clamp_int(points, 20, 200, "points")
    try:
        report = gate3_jacobson_action(n_nodes=nodes, omega=omega_v)
        sweep = temperature_sweep(n_nodes=nodes, omega=omega_v, points=n_points)
    except JacobsonInputError as exc:
        raise ValueError(str(exc)) from exc
    return {
        **report,
        "sweep": sweep,
        "status": ESTABLISHED,
        "hypothesis_status": HYPOTHESIS,
        "note": (
            "Jacobson 1995 is established under its own assumptions. "
            "The covariant action is for prescribed P. "
            "P(N,T) is still a project ansatz. TOE validated = 0."
        ),
    }


def run_confrontation(
    alpha: float = 3.75,
    n_efolds: float = 60.0,
    m_susy: float = 5000.0,
    alpha_h_gev3: float = 0.015,
) -> dict[str, Any]:
    """Confront declared-input theory numbers with the frozen data card."""

    from observational_confrontation import confront_observables

    return confront_observables(
        alpha=_clamp_float(alpha, 0.1, 20.0, "alpha"),
        n_efolds=_clamp_float(n_efolds, 40.0, 80.0, "n_efolds"),
        m_susy=_clamp_float(m_susy, 200.0, 1.0e7, "m_susy"),
        alpha_h_gev3=_clamp_float(alpha_h_gev3, 0.001, 0.05, "alpha_h_gev3"),
    )


def run_gauge_snapshot(n_nodes: int = 24, seed: int = 7) -> dict[str, Any]:
    """One-shot SO(10) Wilson-loop snapshot on a small random regular graph."""

    from explicit_spin10_gauge import ExplicitSpin10GaugeGraph

    n = _clamp_int(n_nodes, 12, 40, "n_nodes")
    if n % 2:
        n += 1
    started = time.perf_counter()
    graph = ExplicitSpin10GaugeGraph(N=n, k_target=3, seed=_clamp_int(seed, 0, 10**9, "seed"))
    plaquettes = graph.all_plaquettes()
    loops = [graph.exact_wilson_loop(tri) for tri in plaquettes] if plaquettes else [0.0]
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    return {
        "status": ESTABLISHED,
        "note": (
            "Initial SO(10) link variables on a small graph. This is a "
            "gauge-theory diagnostic, not a continuum Yang–Mills solution."
        ),
        "n_nodes": graph.N,
        "n_edges": graph.G.number_of_edges(),
        "n_plaquettes": len(plaquettes),
        "n_generators": len(graph.generators),
        "wilson_mean": float(np.mean(loops)),
        "wilson_std": float(np.std(loops)),
        "elapsed_ms": elapsed_ms,
    }
