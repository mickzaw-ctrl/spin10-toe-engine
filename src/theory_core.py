"""Relational Spin(10) programme — complete theoretical specification as code.

This module closes the *internal* structure of the research programme:

- the established Spin(10) group theory and SM embedding;
- standard GUT estimates with every input declared;
- an independent thermal-graph ensemble that never injects d_S(T);
- a lattice mass-gap diagnostic that never imports 1.71 GeV;
- the prescribed-P Jacobson–Clausius action (Gate 3), which does
  not derive P(N,T);
- a prediction registry that satisfies the five-field contract or
  is marked incomplete.

It does not claim a validated Theory of Everything.
"""

from __future__ import annotations

import math
import time
from typing import Any

import networkx as nx
import numpy as np

ESTABLISHED = "established_physics"
HYPOTHESIS = "project_hypothesis"
UNVERIFIED = "unverified_assumption"
REJECTED = "rejected_as_stated"
INCOMPLETE = "incomplete_prediction"
CALIBRATION = "calibration"

M_Z = 91.1876
M_P = 0.938272
YEAR_PER_GEV_INV = 6.582e-25 / 3.15576e7  # ħ/GeV in years


# ---------------------------------------------------------------------------
# Established Spin(10) group theory
# ---------------------------------------------------------------------------

SPINOR_16 = (
    # (name, SU(3)_C, SU(2)_L, Y, B-L, T3R)
    ("u_L", "3", "2", 1.0 / 6.0, 1.0 / 3.0, 0.0),
    ("d_L", "3", "2", 1.0 / 6.0, 1.0 / 3.0, 0.0),
    ("u_c", "3bar", "1", -2.0 / 3.0, -1.0 / 3.0, -0.5),
    ("d_c", "3bar", "1", 1.0 / 3.0, -1.0 / 3.0, 0.5),
    ("nu_L", "1", "2", -0.5, -1.0, 0.0),
    ("e_L", "1", "2", -0.5, -1.0, 0.0),
    ("nu_c", "1", "1", 0.0, 1.0, -0.5),
    ("e_c", "1", "1", 1.0, 1.0, 0.5),
)


def spin10_group() -> dict[str, Any]:
    """Textbook Spin(10) facts. Nothing here is a new prediction."""

    generators = []
    for i in range(10):
        for j in range(i + 1, 10):
            matrix = np.zeros((10, 10), dtype=np.complex128)
            matrix[i, j] = -1j
            matrix[j, i] = 1j
            generators.append(matrix)
    traces = np.array(
        [[np.real(np.trace(a @ b)) for b in generators] for a in generators]
    )
    off = traces.copy()
    np.fill_diagonal(off, 0.0)
    # 16 = 10 + 5bar + 1 under SU(5); 16 = (4,2,1)+(4bar,1,2) under PS.
    su5 = {"10": 10, "5bar": 5, "1": 1}
    pati_salam = {"(4,2,1)": 8, "(4bar,1,2)": 8}
    return {
        "status": ESTABLISHED,
        "group": "Spin(10) ≅ SO(10)",
        "n_generators": len(generators),
        "rank": 5,
        "representations": {
            "10": "vector / electroweak Higgs",
            "16": "one SM generation + ν_R",
            "45": "adjoint gauge bosons",
            "126": "type-I seesaw / B−L Higgs",
            "210": "Pati–Salam breaking",
        },
        "su5_branching": su5,
        "pati_salam_branching": pati_salam,
        "spinor_16": [
            {
                "field": name,
                "SU3": su3,
                "SU2": su2,
                "Y": y,
                "B_minus_L": bl,
                "T3R": t3,
            }
            for name, su3, su2, y, bl, t3 in SPINOR_16
        ],
        "hypercharge_identity": "Y = (B−L)/2 + T_{3R}",
        "weinberg_gut": 3.0 / 8.0,
        "n_generations": {
            "value": 3,
            "status": UNVERIFIED,
            "reason": (
                "Spin(10) supplies one 16. Three copies are an input. "
                "E8 ⊃ SU(4)×Spin(10) yields four 16s, not three. "
                "ind(D)=⟨k⟩−1 is not the Atiyah–Singer theorem."
            ),
        },
        "algebra_checks": {
            "hermitian_generators": bool(all(np.allclose(g, g.conj().T) for g in generators)),
            "off_diagonal_trace_max": float(np.max(np.abs(off))),
            "diagonal_trace": float(np.mean(np.diag(traces))),
        },
        "note": (
            "These are standard facts of compact simple Lie groups. "
            "They do not derive α_em, Λ, or three generations."
        ),
    }


def breaking_chain() -> dict[str, Any]:
    return {
        "status": ESTABLISHED,
        "channels": {
            "georgi_glashow": "Spin(10) → SU(5)×U(1)_χ → SM → SU(3)_C×U(1)_EM",
            "pati_salam": "Spin(10) → SU(4)_C×SU(2)_L×SU(2)_R → SM → SU(3)_C×U(1)_EM",
        },
        "higgs": {"210": "PS breaking", "126": "seesaw / B−L", "10": "electroweak"},
        "massive_gauge_bosons": 45 - 12,
        "note": "Group embeddings are standard. Scales are not derived here.",
    }


# ---------------------------------------------------------------------------
# Standard GUT estimates with declared inputs
# ---------------------------------------------------------------------------

def proton_lifetime_estimate(
    m_gut_gev: float,
    alpha_gut: float,
    alpha_h_gev3: float = 0.015,
) -> dict[str, Any]:
    """Dimension-6 p → e⁺π⁰ lifetime with a declared hadronic matrix element.

    The scaling τ ∝ M_X⁴ / (α_GUT² m_p⁵) is standard. The overall
    prefactor is fixed by the declared α_H, not computed from Spin(10).
    """

    if m_gut_gev <= 0 or alpha_gut <= 0 or alpha_h_gev3 <= 0:
        raise ValueError("proton-lifetime inputs must be positive")
    # Literature-shaped prefactor (Hisano / Nath–Fileviez Pérez reviews).
    # τ_0 = 1.0e34 yr at M_X=1e16 GeV, α=0.04, α_H=0.015 GeV³.
    tau = (
        1.0e34
        * (m_gut_gev / 1.0e16) ** 4
        * (0.04 / alpha_gut) ** 2
        * (0.015 / alpha_h_gev3) ** 2
    )
    sk_limit = 2.4e34
    return {
        "status": ESTABLISHED,
        "channel": "p → e⁺ π⁰",
        "tau_years": float(tau),
        "inputs": {
            "M_X_GeV": float(m_gut_gev),
            "alpha_GUT": float(alpha_gut),
            "alpha_H_GeV3": float(alpha_h_gev3),
        },
        "super_k_limit_years": sk_limit,
        "above_super_k": bool(tau > sk_limit),
        "note": (
            "Standard dimension-6 GUT estimate. The hadronic matrix element "
            "α_H is an external input. SU(5) uses the same formula."
        ),
        "prediction_contract": {
            "observable": "τ(p→e⁺π⁰)",
            "signal": f"{tau:.3e} yr for the declared inputs",
            "null": "proton is stable on the Super-K exposure",
            "data": "Super-K / Hyper-K published limit",
            "sensitivity": "requires τ ≲ few × 10^35 yr for Hyper-K",
            "complete": False,
            "missing": "frozen M_GUT from an input-independent calculation",
        },
    }


def type_i_seesaw(m_dirac_gev: float, m_majorana_gev: float) -> dict[str, Any]:
    """m_ν = m_D² / M_R with both masses declared."""

    if m_dirac_gev <= 0 or m_majorana_gev <= 0:
        raise ValueError("seesaw masses must be positive")
    m_nu_gev = m_dirac_gev**2 / m_majorana_gev
    m_nu_ev = m_nu_gev * 1.0e9
    return {
        "status": ESTABLISHED,
        "formula": "m_ν = m_D² / M_R",
        "m_D_GeV": float(m_dirac_gev),
        "M_R_GeV": float(m_majorana_gev),
        "m_nu_eV": float(m_nu_ev),
        "note": (
            "Type-I seesaw is standard. Spin(10) supplies ν_R in the 16; "
            "it does not fix m_D or M_R without a Yukawa theory."
        ),
        "prediction_contract": {
            "observable": "Σ m_ν",
            "signal": None,
            "complete": False,
            "missing": "derived (m_D, M_R) from a frozen Yukawa sector",
        },
    }


# ---------------------------------------------------------------------------
# Gate 1 — independent thermal graph ensemble
# ---------------------------------------------------------------------------

def _manhattan_torus(a: tuple[int, ...], b: tuple[int, ...], side: int) -> int:
    total = 0
    for x, y in zip(a, b):
        delta = abs(int(x) - int(y))
        total += min(delta, side - delta)
    return total


def _edge_length(graph: nx.Graph, side: int) -> float:
    return float(
        sum(_manhattan_torus(u, v, side) for u, v in graph.edges())
    )


def _propose_swap(
    graph: nx.Graph, rng: np.random.Generator
) -> tuple[tuple[Any, Any], tuple[Any, Any], tuple[Any, Any], tuple[Any, Any]] | None:
    edges = list(graph.edges())
    if len(edges) < 2:
        return None
    i, j = rng.choice(len(edges), size=2, replace=False)
    u, v = edges[int(i)]
    x, y = edges[int(j)]
    if len({u, v, x, y}) < 4:
        return None
    if rng.random() < 0.5:
        a, b, c, d = u, x, v, y
    else:
        a, b, c, d = u, y, v, x
    if graph.has_edge(a, b) or graph.has_edge(c, d):
        return None
    return (u, v), (x, y), (a, b), (c, d)


def _fit_ds(return_probs: np.ndarray) -> float:
    t_vals = np.arange(1, len(return_probs) + 1, dtype=np.float64)
    valid = return_probs > 0
    t_valid = t_vals[valid]
    p_valid = return_probs[valid]
    if len(t_valid) < 8:
        return float("nan")
    log_t = np.log(t_valid)
    log_p = np.log(np.maximum(p_valid, 1e-30))
    window = (t_valid >= 6.0) & (t_valid <= max(12.0, 0.4 * t_valid[-1]))
    if int(np.sum(window)) < 4:
        window = np.ones_like(t_valid, dtype=bool)
        window[:2] = False
    slope, _ = np.polyfit(log_t[window], log_p[window], 1)
    return float(-2.0 * slope)


def _lazy_return(graph: nx.Graph, steps: int, walkers: int, seed: int) -> np.ndarray:
    nodes = list(graph.nodes())
    index = {node: i for i, node in enumerate(nodes)}
    degree = graph.degree(nodes[0])
    table = np.empty((len(nodes), degree), dtype=np.int32)
    for i, node in enumerate(nodes):
        table[i] = [index[nbr] for nbr in graph.neighbors(node)]
    rng = np.random.default_rng(seed)
    current = rng.integers(0, len(nodes), size=walkers, dtype=np.int32)
    start = current.copy()
    probs = np.empty(steps, dtype=np.float64)
    for t in range(steps):
        move = rng.random(walkers) >= 0.5
        if np.any(move):
            movers = current[move]
            picks = rng.integers(0, degree, size=movers.shape[0])
            current[move] = table[movers, picks]
        probs[t] = float(np.mean(current == start))
    return probs


def hold_interpolation(ratio: float, kappa: float = 0.7) -> float:
    """Project ansatz d_S = 2 + 2 / (1 + (T/T*)^κ). Never used as an action."""

    return 2.0 + 2.0 / (1.0 + float(ratio) ** kappa)


def independent_spectral_flow(
    side: int = 4,
    sweeps: int = 80,
    walkers: int = 1600,
    steps: int = 40,
    seed: int = 7,
) -> dict[str, Any]:
    """Measure d_S on a 3D torus whose edges rewire against Manhattan length.

    Temperature enters only the Metropolis weight exp(−ΔS / T_hat) with
    S = Σ_edges ℓ_Manhattan. The HOLD interpolation is compared after
    the measurement and is not part of the action.
    """

    if side < 3 or side > 6:
        raise ValueError("side must lie in [3, 6]")
    rng = np.random.default_rng(seed)
    ratios = (0.01, 0.1, 1.0, 10.0, 100.0)
    started = time.perf_counter()
    rows = []
    for ratio in ratios:
        graph = nx.grid_graph((side, side, side), periodic=True)
        energy = _edge_length(graph, side)
        accepted = 0
        trials = 0
        n_moves = sweeps * graph.number_of_edges()
        for _ in range(n_moves):
            trials += 1
            proposal = _propose_swap(graph, rng)
            if proposal is None:
                continue
            old_a, old_b, new_a, new_b = proposal
            delta = (
                _manhattan_torus(*new_a, side)
                + _manhattan_torus(*new_b, side)
                - _manhattan_torus(*old_a, side)
                - _manhattan_torus(*old_b, side)
            )
            if delta > 0.0 and rng.random() >= math.exp(-delta / ratio):
                continue
            graph.remove_edge(*old_a)
            graph.remove_edge(*old_b)
            graph.add_edge(*new_a)
            graph.add_edge(*new_b)
            energy += delta
            accepted += 1
        probs = _lazy_return(graph, steps=steps, walkers=walkers, seed=seed + int(1000 * ratio))
        measured = _fit_ds(probs)
        target = hold_interpolation(ratio)
        rows.append(
            {
                "T_over_Tstar_convention": ratio,
                "mean_manhattan_length": energy / max(graph.number_of_edges(), 1),
                "acceptance": accepted / max(trials, 1),
                "d_S_measured": measured,
                "d_S_hold": target,
                "abs_error": abs(measured - target) if math.isfinite(measured) else None,
            }
        )
    elapsed = (time.perf_counter() - started) * 1000.0
    finite = [row for row in rows if row["abs_error"] is not None]
    n_fail = sum(1 for row in finite if row["abs_error"] > 0.15)
    decision = "NO-GO" if n_fail >= 3 else "HOLD"
    return {
        "status": ESTABLISHED if decision == "NO-GO" else HYPOTHESIS,
        "decision": decision,
        "protocol": (
            "3D periodic torus, degree-preserving rewiring, action = total "
            "Manhattan length. HOLD curve compared only after unblinding."
        ),
        "scale_map": {
            "status": UNVERIFIED,
            "statement": "T/T* is identified with the Metropolis T_hat by convention.",
        },
        "nogo_rule": "reject HOLD if ≥3 of 5 points differ by more than 0.15",
        "n_fail": n_fail,
        "n_points": len(finite),
        "side": side,
        "n_nodes": side**3,
        "sweeps": sweeps,
        "walkers": walkers,
        "steps": steps,
        "elapsed_ms": elapsed,
        "points": rows,
        "note": (
            "A NO-GO here rejects the interpolation as a description of this "
            "ensemble. It does not prove a different continuum gravity."
        ),
    }


# ---------------------------------------------------------------------------
# Gate 2 — lattice mass gap without a QCD target in the inputs
# ---------------------------------------------------------------------------

def u1_wilson_mass_gap(
    side: int = 8,
    beta: float = 1.2,
    sweeps: int = 120,
    seed: int = 3,
) -> dict[str, Any]:
    """Compact U(1) gauge theory on a 2D torus.

    Returns a dimensionless ratio m_gap / √σ from Wilson loops and a
    plaquette correlator. The 1.71 GeV glueball reference is not an input.
    """

    if side < 4 or side > 12:
        raise ValueError("U(1) lattice side must lie in [4, 12]")
    rng = np.random.default_rng(seed)
    # Links: [x, y, mu] with mu=0,1. Angle in (-π, π].
    theta = rng.uniform(-math.pi, math.pi, size=(side, side, 2))

    def plaquette(x: int, y: int) -> float:
        return (
            theta[x, y, 0]
            + theta[(x + 1) % side, y, 1]
            - theta[x, (y + 1) % side, 0]
            - theta[x, y, 1]
        )

    def link_action(x: int, y: int, mu: int) -> float:
        if mu == 0:
            return (1.0 - math.cos(plaquette(x, y))) + (
                1.0 - math.cos(plaquette(x, (y - 1) % side))
            )
        return (1.0 - math.cos(plaquette(x, y))) + (
            1.0 - math.cos(plaquette((x - 1) % side, y))
        )

    def sweep() -> None:
        for x in range(side):
            for y in range(side):
                for mu in range(2):
                    old = theta[x, y, mu]
                    s_old = link_action(x, y, mu)
                    theta[x, y, mu] = old + rng.normal(scale=0.8)
                    s_new = link_action(x, y, mu)
                    if s_new > s_old and rng.random() > math.exp(-beta * (s_new - s_old)):
                        theta[x, y, mu] = old

    for _ in range(max(20, sweeps // 5)):
        sweep()
    wilson = {1: [], 2: []}
    corr = []
    for _ in range(sweeps):
        sweep()
        for size in (1, 2):
            acc = 0.0
            count = 0
            for x in range(side):
                for y in range(side):
                    loop = 0.0
                    cx, cy = x, y
                    for _ in range(size):
                        loop += theta[cx, cy, 0]
                        cx = (cx + 1) % side
                    for _ in range(size):
                        loop += theta[cx, cy, 1]
                        cy = (cy + 1) % side
                    for _ in range(size):
                        cx = (cx - 1) % side
                        loop -= theta[cx, cy, 0]
                    for _ in range(size):
                        cy = (cy - 1) % side
                        loop -= theta[cx, cy, 1]
                    acc += math.cos(loop)
                    count += 1
            wilson[size].append(acc / count)
        p0 = np.array([math.cos(plaquette(x, 0)) for x in range(side)])
        p1 = np.array([math.cos(plaquette(x, 2)) for x in range(side)])
        corr.append(float(np.mean(p0 * p1) - np.mean(p0) * np.mean(p1)))

    w1 = max(float(np.mean(wilson[1])), 1e-12)
    w2 = max(float(np.mean(wilson[2])), 1e-12)
    # Area law: W(L) ~ exp(−σ L²). σ a² ≈ −log W(1).
    sigma_a2 = -math.log(w1)
    # Creutz-like check from 2×2.
    sigma_2 = -0.25 * math.log(w2)
    c = max(float(np.mean(np.abs(corr))), 1e-12)
    # Two-step correlator ~ exp(−m * 2).
    m_a = -0.5 * math.log(c)
    ratio = m_a / math.sqrt(max(sigma_a2, 1e-12))
    qcd_ref = 1.71 / math.sqrt(0.18)
    return {
        "status": ESTABLISHED,
        "theory": "2D compact U(1) Wilson action",
        "side": side,
        "beta": beta,
        "sweeps": sweeps,
        "W_1x1": w1,
        "W_2x2": w2,
        "sigma_a2": sigma_a2,
        "sigma_from_2x2": sigma_2,
        "m_a": m_a,
        "R_m_over_sqrt_sigma": ratio,
        "qcd_reference_ratio": qcd_ref,
        "qcd_reference_used_as_input": False,
        "comparison_after_the_fact": {
            "abs_error_to_quenched_qcd": abs(ratio - qcd_ref),
            "note": "Comparison is diagnostic only; 2D U(1) is not 4D SU(3).",
        },
        "prediction_contract": {
            "observable": "R_0++ = m/√σ on a Spin(10) transfer matrix",
            "signal": None,
            "complete": False,
            "missing": "4D non-Abelian transfer matrix and continuum extrapolation",
        },
        "note": (
            "This closes the *software* gate for an independent mass-gap "
            "estimator. It is not a QCD glueball prediction."
        ),
    }


# ---------------------------------------------------------------------------
# Programme synthesis
# ---------------------------------------------------------------------------

AXIOMS = [
    {
        "id": "A1",
        "name": "Spin(10) gauge axiom",
        "statement": "The SM gauge algebra embeds in spin(10); one generation fills a 16.",
        "status": ESTABLISHED,
        "consequence": "ν_R exists; sin²θ_W(GUT)=3/8 in GUT normalisation.",
    },
    {
        "id": "A2",
        "name": "Three copies",
        "statement": "Exactly three 16s are present in nature.",
        "status": UNVERIFIED,
        "consequence": "N_gen=3 is an input, not a topological theorem of this graph.",
    },
    {
        "id": "A3",
        "name": "Relational pregeometry",
        "statement": "A finite graph is a discrete stand-in for pregeometric degrees of freedom.",
        "status": HYPOTHESIS,
        "consequence": "Spectral dimension and mass gap are measurable on that graph.",
    },
    {
        "id": "A4",
        "name": "No hidden calibration",
        "statement": "A number that is fitted to a PDG target is not a derivation.",
        "status": ESTABLISHED,
        "consequence": "α_em=1/137.036 and α_s=0.118 from Apex remain calibrations.",
    },
    {
        "id": "A5",
        "name": "Imported gravity",
        "statement": "LQC bounce algebra and α-attractors are used as standard modules.",
        "status": ESTABLISHED,
        "consequence": "They are not derived from Spin(10) and do not fix Λ.",
    },
]


def complete_theory(
    m_susy: float = 5000.0,
    m_dirac_gev: float = 100.0,
    m_majorana_gev: float = 1.0e14,
    run_gates: bool = True,
    fast: bool = False,
) -> dict[str, Any]:
    """Assemble the closed programme report."""

    from numerical_rge_solver import NumericalRGESolver

    group = spin10_group()
    chain = breaking_chain()
    t_vals, g_vals, _alpha_end, _best = NumericalRGESolver.integrate_2loop_rge_flow(
        M_SUSY=m_susy, n_points=160
    )
    analysis = NumericalRGESolver.analyze_unification(t_vals, g_vals)
    proton = proton_lifetime_estimate(analysis["M_GUT_GeV"], analysis["alpha_GUT"])
    seesaw = type_i_seesaw(m_dirac_gev, m_majorana_gev)
    from jacobson_clausius import gate3_jacobson_action
    from toe_conditions import evaluate_toe_conditions
    from unified_action import gate4_unified_action

    if not run_gates:
        gate1 = {"decision": "SKIPPED", "status": INCOMPLETE, "points": []}
        gate2 = {"R_m_over_sqrt_sigma": None, "prediction_contract": {"complete": False}}
        gate3 = {"decisions": {"geff_is_the_field_equation": "SKIPPED"}, "status": INCOMPLETE}
        gate4 = {"decisions": {"t2_met": False}, "status": INCOMPLETE}
    elif fast:
        gate1 = independent_spectral_flow(sweeps=30, walkers=800, steps=28)
        gate2 = u1_wilson_mass_gap(side=6, sweeps=40)
        gate3 = gate3_jacobson_action(run_identity_check=True)
        gate4 = gate4_unified_action()
    else:
        gate1 = independent_spectral_flow()
        gate2 = u1_wilson_mass_gap()
        gate3 = gate3_jacobson_action()
        gate4 = gate4_unified_action()

    registry = [
        {
            "id": "P1",
            "observable": "sin²θ_W at a Spin(10) unification point",
            "value": 0.375,
            "status": ESTABLISHED,
            "contract": "group theory in GUT normalisation; not a low-energy prediction",
        },
        {
            "id": "P2",
            "observable": "existence of ν_R",
            "value": True,
            "status": ESTABLISHED,
            "contract": "16 of Spin(10); mass is not fixed",
        },
        {
            "id": "P3",
            "observable": "τ(p→e⁺π⁰)",
            "value": proton["tau_years"],
            "status": ESTABLISHED,
            "contract": proton["prediction_contract"],
        },
        {
            "id": "P4",
            "observable": "m_ν from type-I seesaw",
            "value": seesaw["m_nu_eV"],
            "status": ESTABLISHED,
            "contract": seesaw["prediction_contract"],
        },
        {
            "id": "P5",
            "observable": "independent d_S(T) vs HOLD interpolation",
            "value": gate1.get("decision"),
            "status": gate1.get("status", INCOMPLETE),
            "contract": "3-of-5 no-go on an ensemble that does not inject d_S",
        },
        {
            "id": "P6",
            "observable": "R = m/√σ on 2D U(1)",
            "value": gate2.get("R_m_over_sqrt_sigma"),
            "status": ESTABLISHED,
            "contract": gate2.get("prediction_contract") if run_gates else {"complete": False},
        },
        {
            "id": "P7",
            "observable": "α_em = 1/137.036 from Spin(10)",
            "value": None,
            "status": CALIBRATION,
            "contract": "rejected as a derivation; hidden offset −6.5504",
        },
        {
            "id": "P8",
            "observable": "N_gen = 3 from Atiyah–Singer or E8",
            "value": None,
            "status": REJECTED,
            "contract": "false theorem / extra breaking assumption",
        },
        {
            "id": "P9",
            "observable": "Ω_Λ from T_c⁴/M_Pl²",
            "value": None,
            "status": REJECTED,
            "contract": "wrong dimensions",
        },
        {
            "id": "P10",
            "observable": "late-time Λ from the LQC bounce",
            "value": None,
            "status": REJECTED,
            "contract": "classical integration is invalid at ρ=ρ_c",
        },
        {
            "id": "P11",
            "observable": "prescribed-P covariant action ∫ P R",
            "value": "P G_μν + (g_μν □ − ∇_μ ∇_ν) P = 8π G0 T_μν",
            "status": ESTABLISHED,
            "contract": "metric variation only; P is not derived",
        },
        {
            "id": "P12",
            "observable": "Einstein with G_eff = G0/P as the field equation",
            "value": gate3.get("decisions", {}).get("geff_is_the_field_equation"),
            "status": REJECTED,
            "contract": "NO-GO unless ∇P = 0; extra Hessian terms are required",
        },
        {
            "id": "P13",
            "observable": "P(N,T) from the local Clausius argument",
            "value": None,
            "status": REJECTED,
            "contract": "Jacobson 1995 assumes constant η; P remains a project ansatz",
        },
        {
            "id": "P14",
            "observable": "single action containing gravity + Spin(10)",
            "value": gate4.get("action", {}).get("action") if run_gates else None,
            "status": ESTABLISHED,
            "contract": "syntax of S is written; T2 unmet while predictions use the imported stack",
        },
    ]
    open_problems = [
        "Microscopic derivation of P(N,T) from a graph entropy (Jacobson does not supply it).",
        "Kinetic term ω(P) and potential V(P) if P is promoted to a dynamical scalar.",
        "Bulk–boundary map from GFT quanta to isolated-horizon punctures.",
        "Yukawa sector that fixes m_D and M_R without SM mass inputs.",
        "4D non-Abelian transfer matrix for R_0++ with continuum limit.",
        "Official MEG-II / Hyper-K / Planck likelihoods with frozen nuisances.",
    ]
    return {
        "title": "Relational Spin(10) programme — complete specification",
        "version": "16.1",
        "scientific_status": "internally closed research programme; not a validated TOE",
        "is_toe": False,
        "validated_observational_predictions": 0,
        "axioms": AXIOMS,
        "group": group,
        "breaking": chain,
        "unification": {
            "status": ESTABLISHED,
            "M_GUT_GeV": analysis["M_GUT_GeV"],
            "alpha_GUT": analysis["alpha_GUT"],
            "sin2_theta_W_GUT": analysis["sin2_theta_W_GUT"],
            "unification_accuracy": analysis["unification_accuracy"],
            "note": "M_Z couplings are inputs. Unification quality is a diagnostic.",
        },
        "proton": proton,
        "seesaw": seesaw,
        "gate1_independent_spectral_flow": gate1,
        "gate2_mass_gap": gate2,
        "gate3_jacobson_action": gate3,
        "gate4_unified_action": gate4,
        "registry": registry,
        "open_problems": open_problems,
        "toe_conditions": evaluate_toe_conditions(),
        "what_is_closed": [
            "Spin(10) representation theory and SM embedding",
            "Epistemic ledger and fail-closed domains",
            "Independent Gate-1 protocol (ensemble does not inject d_S)",
            "Independent Gate-2 estimator (no 1.71 GeV in the inputs)",
            "Standard GUT lifetime and seesaw formulae with declared inputs",
            "Gate 4 continuum EYM candidate and imported-stack inventory",
        ],
        "what_is_not_closed": [
            "A derivation of the cosmological constant",
            "A derivation of α_em without calibration",
            "A derivation of three generations",
            "A completed causal GFT",
            "T2: claimed predictions as consequences of one action",
            "Any observational validation",
        ],
    }


def demo() -> None:
    report = complete_theory()
    print(report["title"], report["version"])
    print(report["scientific_status"])
    print("Gate 1:", report["gate1_independent_spectral_flow"]["decision"])
    print("Gate 2 R:", report["gate2_mass_gap"]["R_m_over_sqrt_sigma"])
    print("τ_p / yr:", report["proton"]["tau_years"])


if __name__ == "__main__":
    demo()
