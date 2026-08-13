"""Local Jacobson–Clausius construction and the covariant action for P.

Jacobson 1995 derives the Einstein equation from δQ = T dS on local
Rindler horizons under local equilibrium and a pure area-entropy law
S = η A.  That argument does **not** produce the graph factor P(N,T).

This module closes the *specification* gap that followed from that
fact:

- if a graph correction is *prescribed* as a positive scalar P(x),
  the covariant action is the Jordan-frame Einstein–Hilbert term
  with that factor, and the metric equations contain extra
  Hessian / d'Alembert terms;
- Einstein gravity with the algebraic replacement G → G0/P is
  recovered only when ∇P = 0;
- P(N,T) = 1 − c/√N_eff remains a project ansatz.

Nothing here is a Theory-of-Everything validation.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Iterable, Mapping

ESTABLISHED = "established_physics"
HYPOTHESIS = "project_hypothesis"
UNVERIFIED = "unverified_assumption"
REJECTED = "rejected_as_stated"
INCOMPLETE = "incomplete_prediction"

# Preregistered IR threshold. Do not edit after looking at a new ansatz.
NOGO_IR_EPS = 0.01

# TCD coherence ansatz, declared — not derived here.
DEFAULT_N = 10**6
DEFAULT_C = 0.33
DEFAULT_TGUT_GEV = 1.03e16
DEFAULT_TODAY_GEV = 2.35e-13
DEFAULT_BBN_GEV = 1.0e-3
DEFAULT_QCD_GEV = 0.1565
DEFAULT_PLANCK_GEV = 1.22e19

# Cassini / VLBI bound on a light Brans–Dicke field (Bertotti et al. 2003).
# Applies only if P is promoted to an independent light scalar.
CASSINI_OMEGA_MIN = 4.0e4


class JacobsonInputError(ValueError):
    """Raised when a Jacobson / P-action calculation receives an invalid input."""


def _positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise JacobsonInputError(f"{name} must be numeric, not boolean")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise JacobsonInputError(f"{name} must be positive and finite")
    return result


def _nonnegative_finite(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise JacobsonInputError(f"{name} must be numeric, not boolean")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise JacobsonInputError(f"{name} must be non-negative and finite")
    return result


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or int(value) != value:
        raise JacobsonInputError(f"{name} must be an integer")
    number = int(value)
    if number <= 0:
        raise JacobsonInputError(f"{name} must be a positive integer")
    return number


# ---------------------------------------------------------------------------
# Established local Clausius argument (Jacobson 1995)
# ---------------------------------------------------------------------------

def jacobson_1995_einstein() -> dict[str, Any]:
    """Record the established local Clausius derivation and its assumptions."""

    return {
        "status": ESTABLISHED,
        "id": "JC-1995",
        "statement": (
            "On every local Rindler horizon, the Clausius relation δQ = T dS "
            "with Unruh temperature T = κ/2π and area entropy S = η A, "
            "together with local equilibrium (vanishing expansion of the "
            "horizon generators in the instantaneous rest frame and no "
            "internal entropy production), implies the Einstein equation "
            "G_μν + Λ g_μν = (2π/η) T_μν.  For η = 1/(4 G) this is GR."
        ),
        "assumptions": [
            "a local Rindler horizon through each spacetime point",
            "Unruh temperature T = κ/2π for the boost Killing field",
            "entropy strictly proportional to area, S = η A with η constant",
            "local equilibrium: shear / expansion arranged so that entropy "
            "production can be neglected at the point",
            "heat flux identified with the matter stress-energy through the horizon",
        ],
        "equation": "G_{μν} + Λ g_{μν} = (2π/η) T_{μν}",
        "area_entropy": "S = η A",
        "unruh": "T = κ / 2π  (ħ = k_B = c = 1)",
        "does_not_derive": [
            "the graph factor P(N,T)",
            "a microscopic count of graph configurations",
            "Einstein gravity with the algebraic replacement G → G0/P when ∇P ≠ 0",
            "a kinetic term ω(P) or a potential V(P)",
        ],
        "references": [
            "T. Jacobson, Phys. Rev. Lett. 75, 1260 (1995); arXiv:gr-qc/9504004",
            "C. Eling, R. Guedens, T. Jacobson, Phys. Rev. Lett. 96, 121301 (2006); arXiv:gr-qc/0602001",
        ],
        "note": (
            "EGJ 2006 showed that a non-constant entropy density requires a "
            "non-equilibrium entropy-production term (shear viscosity) before "
            "the Clausius argument recovers the correct field equations.  "
            "A naive substitution S → η P A inside the 1995 argument is "
            "therefore not a derivation of Einstein gravity with G_eff = G0/P."
        ),
    }


def naive_clausius_with_variable_p() -> dict[str, Any]:
    """Classify the illegal step S → η P A inside equilibrium Clausius."""

    return {
        "status": REJECTED,
        "id": "JC-NAIVE-P",
        "statement": (
            "Replacing S = η A by S = η P(N,T) A inside the equilibrium "
            "Clausius relation and reading off G_μν = 8π (G0/P) T_μν."
        ),
        "reason": (
            "For spacetime-dependent P the variation of area entropy produces "
            "∇∇P and □P terms.  Equilibrium Clausius with constant η does not "
            "generate them; EGJ 2006 requires extra entropy production.  "
            "The algebraic map G_eff = G0/P keeps only the φ G_μν piece."
        ),
        "holds_iff": "∇P = 0 and □P = 0 (constant P on the region of interest)",
    }


# ---------------------------------------------------------------------------
# Covariant action for any prescribed graph correction P(x)
# ---------------------------------------------------------------------------

def prescribed_p_action() -> dict[str, Any]:
    """Jordan-frame Einstein–Hilbert action with a prescribed factor P(x).

    P is **not** varied.  The only field equation is the metric equation.
    This is well-defined for every P > 0 and is the covariant completion
    of “put a graph correction in front of the area / Einstein–Hilbert term.”
    """

    return {
        "status": ESTABLISHED,
        "id": "JC-ACTION-PRESCRIBED",
        "reading": "P is a prescribed positive scalar, not a dynamical field",
        "action": (
            "S[g; P] = (1 / 16π G0) ∫ d⁴x √−g  P(x) R[g]  +  S_m[g, ψ]"
        ),
        "metric_equation": (
            "P G_μν + (g_μν □ − ∇_μ ∇_ν) P  =  8π G0 T_μν"
        ),
        "geff_piece": "P G_μν  is the Einstein tensor with G_eff = G0/P",
        "extra_terms": "(g_μν □ − ∇_μ ∇_ν) P",
        "extra_terms_vanish_iff": "∇P = 0",
        "matter": "S_m is minimally coupled to g; no direct P–matter vertex is assumed",
        "note": (
            "This is ordinary metric variation of ∫ P R, the same calculation "
            "that produces the Hessian terms of Brans–Dicke when the BD "
            "scalar is held fixed.  It is not a derivation of P from a graph."
        ),
        "does_not_derive": ["P(N,T)", "ω(P)", "V(P)"],
    }


def dynamical_scalar_tensor_action() -> dict[str, Any]:
    """If P is promoted to an independent scalar, ω and V are required."""

    return {
        "status": INCOMPLETE,
        "id": "JC-ACTION-DYNAMICAL",
        "reading": "P is varied as a Brans–Dicke-like scalar",
        "action": (
            "S[g,P] = (1 / 16π G0) ∫ d⁴x √−g [ P R − (ω(P)/P) ∇^α P ∇_α P "
            "− V(P) ] + S_m[g, ψ]"
        ),
        "missing": [
            "a graph derivation of the kinetic function ω(P)",
            "a graph derivation of the potential V(P)",
            "a statement that P is a propagating degree of freedom",
        ],
        "cassini_constraint": {
            "status": ESTABLISHED,
            "statement": (
                "A light Brans–Dicke field with constant ω must satisfy "
                f"ω > {CASSINI_OMEGA_MIN:.0e} (Cassini/VLBI)."
            ),
            "applies_to_prescribed_P": False,
            "applies_to_dynamical_P": True,
            "default_omega_zero": (
                "ω = 0 as a dynamical BD theory is excluded by Cassini.  "
                "That bound does not apply to a prescribed background P(T)."
            ),
        },
        "note": (
            "The programme does not currently vary P.  The prescribed-P "
            "action is the closed specification; the dynamical reading stays "
            "incomplete."
        ),
    }


# ---------------------------------------------------------------------------
# Project ansatz P(N,T) — declared, not derived
# ---------------------------------------------------------------------------

def project_coherence_p(
    n_nodes: int,
    temperature_gev: float,
    coherence_coefficient: float = DEFAULT_C,
    gut_scale_gev: float = DEFAULT_TGUT_GEV,
) -> dict[str, Any]:
    """Evaluate P = 1 − c / √N_eff(T) and its T-derivatives.

    N_eff = N / (1 + (T/T_GUT)²).  This is the TCD holographic-coherence
    ansatz.  Jacobson’s argument is not used.
    """

    nodes = _positive_int(n_nodes, "n_nodes")
    temperature = _nonnegative_finite(temperature_gev, "temperature_gev")
    coeff = _positive_finite(coherence_coefficient, "coherence_coefficient")
    gut = _positive_finite(gut_scale_gev, "gut_scale_gev")
    x = temperature / gut
    n_eff = nodes / (1.0 + x * x)
    prefactor = coeff / math.sqrt(float(nodes))
    value = 1.0 - prefactor * math.sqrt(1.0 + x * x)
    if value <= 0.0:
        raise JacobsonInputError(
            "coherence ansatz is non-positive for the declared (N, T)"
        )
    # dP/dT = − (c/√N) T / (T_GUT² √(1+x²))
    dpdT = -prefactor * temperature / (gut * gut * math.sqrt(1.0 + x * x))
    # d²P/dT² = − (c/√N) / (T_GUT² (1+x²)^{3/2})
    d2pdT2 = -prefactor / (gut * gut * (1.0 + x * x) ** 1.5)
    return {
        "status": HYPOTHESIS,
        "formula": "P = 1 − c / √N_eff,  N_eff = N / (1 + (T/T_GUT)²)",
        "P": value,
        "dP_dT_GeV_inv": dpdT,
        "d2P_dT2_GeV_inv2": d2pdT2,
        "N": nodes,
        "N_eff": n_eff,
        "T_GeV": temperature,
        "x_T_over_TGUT": x,
        "c": coeff,
        "T_GUT_GeV": gut,
        "G_eff_over_G0": 1.0 / value,
    }


def p_domain_wall(
    n_nodes: int,
    coherence_coefficient: float = DEFAULT_C,
    gut_scale_gev: float = DEFAULT_TGUT_GEV,
) -> dict[str, Any]:
    """Largest T at which the ansatz still has P > 0."""

    nodes = _positive_int(n_nodes, "n_nodes")
    coeff = _positive_finite(coherence_coefficient, "coherence_coefficient")
    gut = _positive_finite(gut_scale_gev, "gut_scale_gev")
    ratio = nodes / (coeff * coeff)
    if ratio <= 1.0:
        return {
            "status": HYPOTHESIS,
            "P_positive_anywhere": False,
            "T_max_GeV": 0.0,
            "x_max": 0.0,
            "reason": "N ≤ c²; the ansatz is non-positive at every T",
        }
    x_max = math.sqrt(ratio - 1.0)
    return {
        "status": HYPOTHESIS,
        "P_positive_anywhere": True,
        "T_max_GeV": gut * x_max,
        "x_max": x_max,
        "condition": "P > 0  ⇔  T/T_GUT < √(N/c² − 1)",
    }


# ---------------------------------------------------------------------------
# Extra terms on a homogeneous FLRW background
# ---------------------------------------------------------------------------

def friedmann_extra_fractions(
    p_value: float,
    dpdT: float,
    d2pdT2: float,
    temperature_gev: float,
    omega: float = 0.0,
    background: str = "radiation",
) -> dict[str, Any]:
    """Dimensionless extra-term sizes relative to Einstein-with-G_eff.

    Photon temperature is taken to satisfy Ṫ = −H T (declared, standard
    after e⁺e⁻ annihilation).  The Friedmann fraction

        ε_F = |Ṗ| / (H P) = T |dP/dT| / P

    is then independent of H.  The acceleration fraction ε_acc uses a
    declared background (radiation Ḣ = −2 H², matter −3/2 H²,
    de Sitter Ḣ = 0) only for P̈.

    Metric convention: ds² = −dt² + a² dx², G_00 = 3 H².
    Prescribed-P 00 equation (ω = 0):

        3 P H² + 3 H Ṗ = 8π G0 ρ

    so  3 H² = 8π (G0/P) ρ − 3 H (Ṗ/P).  The relative correction is ε_F.
    A constant-ω kinetic term, if someone *declares* one without varying
    P, adds (ω/2) (Ṗ/(H P))² to that fraction.
    """

    p_val = _positive_finite(p_value, "p_value")
    temperature = _nonnegative_finite(temperature_gev, "temperature_gev")
    if isinstance(dpdT, bool) or not math.isfinite(float(dpdT)):
        raise JacobsonInputError("dP/dT must be a finite number")
    if isinstance(d2pdT2, bool) or not math.isfinite(float(d2pdT2)):
        raise JacobsonInputError("d²P/dT² must be a finite number")
    omega_val = _nonnegative_finite(omega, "omega")
    kind = str(background).lower()
    if kind not in {"radiation", "matter", "de_sitter"}:
        raise JacobsonInputError("background must be radiation, matter, or de_sitter")

    p_t = float(dpdT)
    p_tt = float(d2pdT2)
    eps_f = temperature * abs(p_t) / p_val
    # Ṗ = (dP/dT) Ṫ = − H T P_T   ⇒   Ṗ / (H P) = − T P_T / P
    pdot_over_hp = -temperature * p_t / p_val
    eps_omega = 0.5 * omega_val * pdot_over_hp**2

    # ε_acc = |P̈ + 2 H Ṗ| / (P H²), background-dependent.
    # Radiation: T² P'' + T P'
    # Matter:    T² P'' + 0.5 T P'
    # de Sitter: T² P'' − T P'
    t_pt = temperature * p_t
    t2_ptt = temperature * temperature * p_tt
    if kind == "radiation":
        acc_combo = t2_ptt + t_pt
    elif kind == "matter":
        acc_combo = t2_ptt + 0.5 * t_pt
    else:
        acc_combo = t2_ptt - t_pt
    eps_acc = abs(acc_combo) / p_val

    return {
        "status": ESTABLISHED,
        "background": kind,
        "eps_friedmann": eps_f,
        "eps_acceleration": eps_acc,
        "eps_omega_friedmann": eps_omega,
        "Pdot_over_HP": pdot_over_hp,
        "note": (
            "ε_F is the relative size of the 3 H Ṗ term against 3 P H².  "
            "Einstein-with-G_eff is an exact 00-equation only if ε_F = 0 "
            "and ω = 0."
        ),
    }


def extras_for_project_ansatz(
    n_nodes: int,
    temperature_gev: float,
    omega: float = 0.0,
    background: str = "radiation",
    coherence_coefficient: float = DEFAULT_C,
    gut_scale_gev: float = DEFAULT_TGUT_GEV,
) -> dict[str, Any]:
    """Combine the TCD ansatz with the established extra-term algebra."""

    coherence = project_coherence_p(
        n_nodes,
        temperature_gev,
        coherence_coefficient=coherence_coefficient,
        gut_scale_gev=gut_scale_gev,
    )
    extras = friedmann_extra_fractions(
        coherence["P"],
        coherence["dP_dT_GeV_inv"],
        coherence["d2P_dT2_GeV_inv2"],
        temperature_gev,
        omega=omega,
        background=background,
    )
    # Closed form for the ansatz, used as a cross-check.
    x = coherence["x_T_over_TGUT"]
    prefactor = coherence["c"] / math.sqrt(float(coherence["N"]))
    p_val = coherence["P"]
    analytic_eps_f = prefactor * (x * x) / (math.sqrt(1.0 + x * x) * p_val)
    return {
        **coherence,
        "extras": extras,
        "analytic_eps_friedmann": analytic_eps_f,
        "omega": float(omega),
    }


# ---------------------------------------------------------------------------
# Frozen epochs and Gate 3
# ---------------------------------------------------------------------------

def _epoch_table() -> tuple[dict[str, Any], ...]:
    return (
        {
            "id": "today",
            "T_GeV": DEFAULT_TODAY_GEV,
            "background": "matter",
            "note": "CMB temperature; Ḣ taken as matter-like for ε_acc only",
        },
        {
            "id": "BBN",
            "T_GeV": DEFAULT_BBN_GEV,
            "background": "radiation",
            "note": "T = 1 MeV, radiation era",
        },
        {
            "id": "QCD",
            "T_GeV": DEFAULT_QCD_GEV,
            "background": "radiation",
            "note": "HotQCD crossover temperature used only as a clock",
        },
        {
            "id": "GUT",
            "T_GeV": DEFAULT_TGUT_GEV,
            "background": "radiation",
            "note": "declared T_GUT; not a derived unification temperature",
        },
        {
            "id": "Planck",
            "T_GeV": DEFAULT_PLANCK_GEV,
            "background": "radiation",
            "note": "T = M_Pl; the ansatz is near or past its domain wall",
        },
    )


def evaluate_epochs(
    n_nodes: int = DEFAULT_N,
    omega: float = 0.0,
    coherence_coefficient: float = DEFAULT_C,
    gut_scale_gev: float = DEFAULT_TGUT_GEV,
    epochs: Iterable[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate extra-term sizes at the frozen temperature list."""

    rows = []
    for epoch in epochs if epochs is not None else _epoch_table():
        ident = str(epoch["id"])
        temperature = float(epoch["T_GeV"])
        background = str(epoch.get("background", "radiation"))
        try:
            result = extras_for_project_ansatz(
                n_nodes,
                temperature,
                omega=omega,
                background=background,
                coherence_coefficient=coherence_coefficient,
                gut_scale_gev=gut_scale_gev,
            )
            extras = result["extras"]
            rows.append(
                {
                    "id": ident,
                    "T_GeV": temperature,
                    "background": background,
                    "P": result["P"],
                    "G_eff_over_G0": result["G_eff_over_G0"],
                    "eps_friedmann": extras["eps_friedmann"],
                    "eps_acceleration": extras["eps_acceleration"],
                    "eps_omega_friedmann": extras["eps_omega_friedmann"],
                    "ir_ok": extras["eps_friedmann"] < NOGO_IR_EPS,
                    "inside_domain": True,
                    "note": epoch.get("note", ""),
                }
            )
        except JacobsonInputError as exc:
            rows.append(
                {
                    "id": ident,
                    "T_GeV": temperature,
                    "background": background,
                    "P": None,
                    "G_eff_over_G0": None,
                    "eps_friedmann": None,
                    "eps_acceleration": None,
                    "eps_omega_friedmann": None,
                    "ir_ok": False,
                    "inside_domain": False,
                    "note": f"outside_ansatz_domain: {exc}",
                }
            )
    return rows


def geff_substitution_verdict() -> dict[str, Any]:
    """Analytic no-go: G_eff = G0/P is not the field equation for variable P."""

    return {
        "status": REJECTED,
        "id": "JC-GEFF",
        "claim": (
            "The modified Clausius law S = η P A implies Einstein gravity "
            "with G_eff = G0/P."
        ),
        "decision": "NO-GO",
        "nogo_rule": (
            "Reject the identification as a general field equation whenever "
            "P is allowed to vary.  The prescribed-P metric equation always "
            "contains (g_μν □ − ∇_μ ∇_ν) P."
        ),
        "holds_iff": "∇P = 0",
        "preregistered": True,
    }


def ir_approximation_verdict(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Numeric gate on whether extras are small at today and BBN.

    Preregistered rule: the IR substitution G_eff = G0/P is an acceptable
    *approximation* (not a field equation) if ε_F < NOGO_IR_EPS at both
    today and BBN.  Passing this gate does not validate P.
    """

    needed = {row["id"]: row for row in rows if row["id"] in {"today", "BBN"}}
    if "today" not in needed or "BBN" not in needed:
        raise JacobsonInputError("IR verdict requires today and BBN rows")
    today_ok = bool(needed["today"]["ir_ok"] and needed["today"]["inside_domain"])
    bbn_ok = bool(needed["BBN"]["ir_ok"] and needed["BBN"]["inside_domain"])
    passed = today_ok and bbn_ok
    return {
        "status": ESTABLISHED if passed else REJECTED,
        "id": "JC-IR",
        "decision": "IR_OK" if passed else "NO-GO",
        "nogo_rule": (
            f"reject the IR G_eff≈G0/P approximation if ε_F ≥ {NOGO_IR_EPS} "
            "at today or at BBN"
        ),
        "threshold": NOGO_IR_EPS,
        "preregistered": True,
        "today_ok": today_ok,
        "bbn_ok": bbn_ok,
        "validates_P": False,
        "validates_toe": False,
        "note": (
            "A pass means only that the extra terms of the prescribed-P "
            "action are numerically negligible at the two IR clocks.  "
            "It is not a derivation of P and not an observational validation."
        ),
    }


def temperature_sweep(
    n_nodes: int = DEFAULT_N,
    omega: float = 0.0,
    points: int = 80,
    t_min_gev: float = 1.0e-13,
    t_max_gev: float | None = None,
    coherence_coefficient: float = DEFAULT_C,
    gut_scale_gev: float = DEFAULT_TGUT_GEV,
) -> dict[str, Any]:
    """Log-spaced sweep of ε_F(T) for the lab chart."""

    n_points = _positive_int(points, "points")
    if n_points < 8:
        raise JacobsonInputError("points must be at least 8")
    t_lo = _positive_finite(t_min_gev, "t_min_gev")
    domain = p_domain_wall(
        n_nodes,
        coherence_coefficient=coherence_coefficient,
        gut_scale_gev=gut_scale_gev,
    )
    if t_max_gev is None:
        if domain["P_positive_anywhere"]:
            t_hi = min(float(domain["T_max_GeV"]) * 0.8, 10.0 * DEFAULT_PLANCK_GEV)
        else:
            raise JacobsonInputError("ansatz has no positive-P domain")
    else:
        t_hi = _positive_finite(t_max_gev, "t_max_gev")
    if t_hi <= t_lo:
        raise JacobsonInputError("t_max must exceed t_min")

    log_lo = math.log(t_lo)
    log_hi = math.log(t_hi)
    temperatures: list[float] = []
    eps: list[float] = []
    p_vals: list[float] = []
    for i in range(n_points):
        temperature = math.exp(log_lo + (log_hi - log_lo) * i / (n_points - 1))
        try:
            result = extras_for_project_ansatz(
                n_nodes,
                temperature,
                omega=omega,
                background="radiation",
                coherence_coefficient=coherence_coefficient,
                gut_scale_gev=gut_scale_gev,
            )
        except JacobsonInputError:
            continue
        temperatures.append(temperature)
        eps.append(result["extras"]["eps_friedmann"])
        p_vals.append(result["P"])
    return {
        "status": HYPOTHESIS,
        "T_GeV": temperatures,
        "eps_friedmann": eps,
        "P": p_vals,
        "domain": domain,
        "n_nodes": int(n_nodes),
        "omega": float(omega),
    }


def verify_flrw_chain_rule(
    n_nodes: int = DEFAULT_N,
    t_ref_gev: float = DEFAULT_TGUT_GEV,
    steps: int = 5,
) -> dict[str, Any]:
    """Finite-difference check that ε_F = T |dP/dT| / P on a radiation clock.

    Uses H = 1/(2t), T ∝ t^{−1/2}.  This tests the algebra, not nature.
    """

    nodes = _positive_int(n_nodes, "n_nodes")
    t_ref = _positive_finite(t_ref_gev, "t_ref_gev")
    n_steps = _positive_int(steps, "steps")
    # Pick a fiducial time t0 = 1 (GeV^{−1}) so H = 1/2, T(t0) = t_ref.
    t0 = 1.0
    delta = 1.0e-5

    def temperature(time: float) -> float:
        return t_ref * math.sqrt(t0 / time)

    def p_of_time(time: float) -> float:
        return project_coherence_p(nodes, temperature(time))["P"]

    analytic = extras_for_project_ansatz(
        nodes, t_ref, background="radiation"
    )
    p_plus = p_of_time(t0 + delta)
    p_minus = p_of_time(t0 - delta)
    p_dot = (p_plus - p_minus) / (2.0 * delta)
    hubble = 0.5 / t0
    p0 = p_of_time(t0)
    numeric_eps = abs(p_dot) / (hubble * p0)
    # A few neighbouring times, to make the check less of a single point.
    residuals = []
    for k in range(n_steps):
        time = t0 * (0.7 + 0.15 * k)
        temp = temperature(time)
        p_here = p_of_time(time)
        p_u = p_of_time(time + delta)
        p_d = p_of_time(time - delta)
        pdot = (p_u - p_d) / (2.0 * delta)
        h_here = 0.5 / time
        num = abs(pdot) / (h_here * p_here)
        ana = extras_for_project_ansatz(nodes, temp)["extras"]["eps_friedmann"]
        residuals.append(abs(num - ana) / max(ana, 1.0e-30))
    max_rel = max(residuals)
    return {
        "status": ESTABLISHED,
        "protocol": "radiation clock H=1/(2t), T∝t^{−1/2}, central differences",
        "analytic_eps_friedmann": analytic["extras"]["eps_friedmann"],
        "numeric_eps_friedmann": numeric_eps,
        "max_relative_residual": max_rel,
        "pass_threshold": 1.0e-4,
        "passed": bool(max_rel < 1.0e-4),
        "note": "A pass validates the chain-rule identity, not the P ansatz.",
    }


def what_would_derive_p() -> dict[str, Any]:
    """Checklist for an actual derivation of P.  All items are open."""

    return {
        "status": INCOMPLETE,
        "id": "JC-DERIVE-P",
        "statement": (
            "P(N,T) would be derived only from a microscopic entropy "
            "S_graph(A, N, T) with a controlled continuum limit that matches "
            "η P A, using inputs that do not contain the target function."
        ),
        "required": [
            "a normalized graph ensemble and a continuum limit",
            "an independent area / bipartition entropy, not assigned by hand",
            "a scale map from graph temperature to a physical T",
            "a proof that S / (η A) → 1 − c/√N_eff rather than another function",
            "a frozen likelihood or a preregistered no-go on that function",
        ],
        "jacobson_supplies_this": False,
        "current_ansatz": "P = 1 − 0.33/√N_eff is a project parametrization",
    }


def gate3_jacobson_action(
    n_nodes: int = DEFAULT_N,
    omega: float = 0.0,
    coherence_coefficient: float = DEFAULT_C,
    gut_scale_gev: float = DEFAULT_TGUT_GEV,
    run_identity_check: bool = True,
) -> dict[str, Any]:
    """Gate 3 — covariant action for any prescribed P, extras, no derivation of P."""

    jacobson = jacobson_1995_einstein()
    naive = naive_clausius_with_variable_p()
    action = prescribed_p_action()
    dynamical = dynamical_scalar_tensor_action()
    domain = p_domain_wall(
        n_nodes,
        coherence_coefficient=coherence_coefficient,
        gut_scale_gev=gut_scale_gev,
    )
    rows = evaluate_epochs(
        n_nodes=n_nodes,
        omega=omega,
        coherence_coefficient=coherence_coefficient,
        gut_scale_gev=gut_scale_gev,
    )
    geff = geff_substitution_verdict()
    ir_ok = ir_approximation_verdict(rows)
    identity = verify_flrw_chain_rule(n_nodes=n_nodes) if run_identity_check else None
    missing = what_would_derive_p()
    return {
        "title": "Gate 3 — Jacobson–Clausius and the covariant action for P",
        "version": "16.1",
        "status": ESTABLISHED,
        "scientific_status": (
            "internally closed specification of the prescribed-P action; "
            "P(N,T) underived; not a validated TOE"
        ),
        "validated_observational_predictions": 0,
        "jacobson_1995": jacobson,
        "naive_variable_p": naive,
        "prescribed_action": action,
        "dynamical_action": dynamical,
        "domain": domain,
        "epochs": rows,
        "geff_substitution": geff,
        "ir_approximation": ir_ok,
        "identity_check": identity,
        "p_derivation": missing,
        "inputs": {
            "N": int(n_nodes),
            "c": float(coherence_coefficient),
            "T_GUT_GeV": float(gut_scale_gev),
            "omega": float(omega),
            "omega_is_derived": False,
        },
        "decisions": {
            "jacobson_derives_P": "NO-GO",
            "geff_is_the_field_equation": geff["decision"],
            "ir_geff_approximation": ir_ok["decision"],
            "p_ansatz": "HOLD",
        },
        "nogo_rule": geff["nogo_rule"],
        "note": (
            "Gate 3 closes the covariant-action specification for any "
            "prescribed P > 0.  It rejects Einstein-with-G_eff as the "
            "exact field equation and leaves P(N,T) as a project hypothesis."
        ),
    }


def extras_callable(
    p_fn: Callable[[float], float],
    temperature_gev: float,
    delta: float = 1.0e-4,
    background: str = "radiation",
    omega: float = 0.0,
) -> dict[str, Any]:
    """Extra-term sizes for an arbitrary prescribed P(T).

    Used so the algebra is not tied to the TCD ansatz.  Derivatives are
    taken by central differences in log T.
    """

    temperature = _positive_finite(temperature_gev, "temperature_gev")
    step = _positive_finite(delta, "delta")
    p0 = _positive_finite(float(p_fn(temperature)), "P(T)")
    p_plus = float(p_fn(temperature * math.exp(step)))
    p_minus = float(p_fn(temperature * math.exp(-step)))
    if p_plus <= 0.0 or p_minus <= 0.0:
        raise JacobsonInputError("P(T) must stay positive in the difference stencil")
    # dP/d ln T = T dP/dT ≈ (P+ − P−) / (2 step)
    dpdlnT = (p_plus - p_minus) / (2.0 * step)
    dpdT = dpdlnT / temperature
    # d²P / d(ln T)² ≈ P+ − 2 P0 + P− over step²
    d2pdlnT2 = (p_plus - 2.0 * p0 + p_minus) / (step * step)
    # d²P/dT² = (1/T²) (d²P/d(ln T)² − dP/d ln T)
    d2pdT2 = (d2pdlnT2 - dpdlnT) / (temperature * temperature)
    extras = friedmann_extra_fractions(
        p0, dpdT, d2pdT2, temperature, omega=omega, background=background
    )
    return {"P": p0, "dP_dT_GeV_inv": dpdT, "d2P_dT2_GeV_inv2": d2pdT2, "extras": extras}
