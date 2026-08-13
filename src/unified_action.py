"""Single-dynamics candidate: one classical action for gravity + Spin(10).

T2 of the TOE checklist requires gravity and the Standard Model to sit
in one action or measure.  A stack of imported LQC, α-attractors and
SM/MSSM RGE is not that action.

This module writes the unique *classical* candidate compatible with
axiom A1 and Gate 3, then inventories which programme outputs are
consequences of that action and which are imported extras.

It does not quantize the action (T3), does not derive P, N_gen or
Yukawas, and does not make T2 MET.
"""

from __future__ import annotations

from typing import Any

ESTABLISHED = "established_physics"
HYPOTHESIS = "project_hypothesis"
UNVERIFIED = "unverified_assumption"
REJECTED = "rejected_as_stated"
INCOMPLETE = "incomplete_prediction"
IMPORTED = "imported_effective"

# T2 stays UNMET until every claimed fundamental prediction is a
# consequence of S and the quantum measure exists.  Do not flip this
# by adding more documentation.
T2_MET = False


def continuum_candidate_action() -> dict[str, Any]:
    """Einstein–Yang–Mills–Dirac–Higgs with gauge group Spin(10).

    This is standard GUT + GR.  It is one action.  It is not a TOE.
    """

    return {
        "status": ESTABLISHED,
        "id": "S-EYM-SPIN10",
        "reading": "classical continuum candidate; quantum measure is T3 and is missing",
        "action": (
            "S[g, A, ψ, Φ] = S_grav[g; P] + S_YM[A, g] + S_16[ψ, A, g] + S_H[Φ, A, g, ψ]"
        ),
        "terms": [
            {
                "id": "S_grav",
                "formula": "S_grav = (1/16π G0) ∫ d⁴x √−g P(x) R[g]",
                "status": ESTABLISHED,
                "note": (
                    "P ≡ 1 is Einstein–Hilbert. Prescribed P(x) is Gate 3. "
                    "P(N,T) is not derived. Dynamical P needs ω(P), V(P)."
                ),
            },
            {
                "id": "S_YM",
                "formula": (
                    "S_YM = −1/(2 g_10²) ∫ d⁴x √−g Tr(F_μν F^{μν}), "
                    "A ∈ Ω¹(spin(10))"
                ),
                "status": ESTABLISHED,
                "note": "45 gauge bosons. After breaking, 12 remain massless (SM).",
            },
            {
                "id": "S_16",
                "formula": (
                    "S_16 = Σ_{a=1}^{N_gen} ∫ d⁴x √−g ψ̄_a i D̸[A,g] ψ_a, "
                    "ψ ∈ 16"
                ),
                "status": ESTABLISHED,
                "note": (
                    "One 16 is A1. N_gen=3 is axiom A2 (input). "
                    "The 16 contains ν_R. Masses are not fixed here."
                ),
            },
            {
                "id": "S_H",
                "formula": (
                    "S_H = |D Φ_10|² + |D Φ_126|² + |D Φ_210|² − V(Φ) "
                    "+ Y(ψ, Φ) + h.c."
                ),
                "status": ESTABLISHED,
                "note": (
                    "Standard Spin(10) Higgs system. V and the Yukawa tensors Y "
                    "are free. They are not derived from the graph."
                ),
            },
        ],
        "not_in_S": [
            {
                "module": "LQC bounce H² ∝ ρ(1−ρ/ρ_c)",
                "status": IMPORTED,
                "reason": "Holonomy-corrected Friedmann algebra is not a term in S.",
            },
            {
                "module": "α-attractor potential with α = 45/12",
                "status": IMPORTED,
                "reason": "α is not a coupling of S. n_s=1−2/N is not a consequence of S.",
            },
            {
                "module": "SM/MSSM RGE from M_Z",
                "status": IMPORTED,
                "reason": (
                    "Beta functions are the IR effective theory of S after "
                    "breaking, but M_Z couplings are inputs to the solver, "
                    "not outputs of S."
                ),
            },
            {
                "module": "TCD P = 1 − 0.33/√N_eff",
                "status": HYPOTHESIS,
                "reason": "Not a stationary point or a derived solution of S.",
            },
        ],
        "free_data": [
            "G0",
            "g_10 (or α_GUT)",
            "P(x) unless identically 1",
            "N_gen",
            "Yukawa tensors Y",
            "Higgs potential V",
            "vacuum energy / Λ",
        ],
        "derived_from_S": [
            "SM gauge algebra and hypercharge from Spin(10)",
            "existence of ν_R in each 16",
            "sin²θ_W = 3/8 at an unbroken Spin(10) point",
            "dimension-6 baryon-number violation after breaking (M_X from ⟨Φ⟩)",
            "type-I seesaw structure once Y and ⟨Φ_126⟩ exist",
        ],
        "note": (
            "Writing this action satisfies the *syntax* of T2 (one formula). "
            "T2 for a TOE claim also requires that claimed fundamental "
            "predictions be consequences of S. They are not, while C1 uses "
            "α-attractors and C3 uses an RGE-input M_GUT."
        ),
    }


def consequence_inventory() -> list[dict[str, Any]]:
    """Map programme outputs onto the single action."""

    return [
        {
            "id": "I1",
            "output": "sin²θ_W = 3/8 at a Spin(10) point",
            "in_S": True,
            "status": ESTABLISHED,
            "note": "Group theory of S_YM + embedding. Not a low-energy prediction.",
        },
        {
            "id": "I2",
            "output": "ν_R in the 16",
            "in_S": True,
            "status": ESTABLISHED,
            "note": "Representation content of S_16. Mass from Y and ⟨Φ⟩, not fixed.",
        },
        {
            "id": "I3",
            "output": "n_s, r from α-attractors",
            "in_S": False,
            "status": IMPORTED,
            "note": "Requires a potential that is not a term of S. C1 is not T2.",
        },
        {
            "id": "I4",
            "output": "LQC bounce",
            "in_S": False,
            "status": IMPORTED,
            "note": "Not obtained by varying S.",
        },
        {
            "id": "I5",
            "output": "τ(p→e⁺π⁰) with M_X from RGE inputs",
            "in_S": False,
            "status": INCOMPLETE,
            "note": (
                "Dim-6 operators exist after breaking S, but the implemented "
                "lifetime uses M_GUT from M_Z couplings, which are not outputs of S."
            ),
        },
        {
            "id": "I6",
            "output": "α_em = 1/137.036",
            "in_S": False,
            "status": REJECTED,
            "note": "Hidden offset −6.5504. Not a stationary condition of S.",
        },
        {
            "id": "I7",
            "output": "N_gen = 3",
            "in_S": False,
            "status": UNVERIFIED,
            "note": "S_16 is copied N_gen times. N_gen is an input.",
        },
        {
            "id": "I8",
            "output": "P(N,T) and G_eff = G0/P",
            "in_S": False,
            "status": REJECTED,
            "note": "Gate 3: extras exist unless ∇P=0. The TCD function is not in S.",
        },
    ]


def t2_verdict() -> dict[str, Any]:
    """Preregistered rule for T2. Do not mark MET while extras drive predictions."""

    inventory = consequence_inventory()
    imported_used = [row for row in inventory if not row["in_S"]]
    return {
        "id": "T2",
        "decision": "UNMET",
        "t2_met": T2_MET,
        "nogo_rule": (
            "T2 is MET only if (i) one action or measure is specified, "
            "(ii) every claimed fundamental prediction is a consequence of it, "
            "and (iii) LQC, α-attractors and M_Z-input RGE are either derived "
            "as limits or withdrawn as fundamental."
        ),
        "preregistered": True,
        "clause_i_syntax": True,
        "clause_ii_consequences": False,
        "clause_iii_no_stack": False,
        "blocking": [row["id"] for row in imported_used],
        "note": (
            "The continuum action is written. The programme still predicts "
            "with a stack. Syntax without consequences is not T2."
        ),
    }


def gate4_unified_action() -> dict[str, Any]:
    """Gate 4 — one classical action, imported stack named and excluded."""

    action = continuum_candidate_action()
    inventory = consequence_inventory()
    verdict = t2_verdict()
    return {
        "title": "Gate 4 — single dynamics (gravity + Spin(10) in one action)",
        "version": "16.1",
        "status": ESTABLISHED,
        "scientific_status": (
            "classical EYM candidate specified; T2 unmet; not a TOE"
        ),
        "validated_observational_predictions": 0,
        "is_toe": False,
        "action": action,
        "inventory": inventory,
        "t2": verdict,
        "decisions": {
            "single_classical_action_written": True,
            "t2_met": False,
            "lqc_in_S": False,
            "alpha_attractor_in_S": False,
            "rge_mz_inputs_in_S": False,
        },
        "note": (
            "Gate 4 closes the *specification* of the continuum candidate "
            "and the inventory of what does not follow from it. "
            "It does not unify dynamics at the quantum level."
        ),
    }
