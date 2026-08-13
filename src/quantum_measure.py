"""Quantum measure for the Gate-4 fields — specification, not a construction.

T3 requires a Hilbert space or a Euclidean measure, gauge fixing, a
continuum / refinement limit, and either reflection positivity or a
Lorentzian reconstruction.

This module writes the intended discrete measure and the formal
continuum path integral, then scores the clauses.  It does not define
Dg, does not sum over graphs, and does not make T3 MET.

On a *fixed* finite graph the compact-group Wilson measure exists
(Haar on Spin(10)).  That is lattice gauge theory, not quantum gravity.
"""

from __future__ import annotations

from typing import Any

ESTABLISHED = "established_physics"
HYPOTHESIS = "project_hypothesis"
UNVERIFIED = "unverified_assumption"
INCOMPLETE = "incomplete_prediction"
UNMET = "UNMET"
MET = "MET"

T3_MET = False


def continuum_path_integral() -> dict[str, Any]:
    """Formal Fadeev–Popov integral of the Gate-4 action."""

    return {
        "status": INCOMPLETE,
        "id": "Z-CONT",
        "formula": (
            "Z_cont = 1/Vol(Diff ⋉ Gauge) ∫ Dg DA Dψ DΦ  exp(i S[g,A,ψ,Φ])"
        ),
        "problem": (
            "Dg for metrics is not a defined measure. Gauge-fixing gravity "
            "perturbatively does not give a UV-complete theory. This line is "
            "notation, not a construction."
        ),
        "does_not_define": ["Dg", "a continuum limit from graphs", "a Hilbert space"],
    }


def discrete_candidate_measure() -> dict[str, Any]:
    """Intended programme measure: graphs + Spin(10) holonomies + matter."""

    return {
        "status": INCOMPLETE,
        "id": "Z-DISC",
        "formula": (
            "Z_disc = ∑_Γ μ(Γ) ∫ ∏_e dμ_Haar(U_e) ∏_v dψ_v dΦ_v "
            "exp(−S_E[U,ψ,Φ; Γ] + i θ Q[U])"
        ),
        "configuration": {
            "graphs": "finite undirected (or 2-complex) Γ; measure μ(Γ) unspecified",
            "holonomies": "U_e ∈ Spin(10) on each edge; Haar is well-defined",
            "fermions": "ψ_v in 16 at vertices; Grassmann measure not specified",
            "Higgs": "Φ_v in 10 ⊕ 126 ⊕ 210; continuum kinetic term not discretised",
        },
        "euclidean_action": (
            "S_E = (β/2) ∑_□ (1 − Re Tr U_□ / 16) + S_H[Φ,U] + S_ψ[ψ,U] "
            "+ S_graph[Γ]"
        ),
        "haar_on_spin10": {
            "status": ESTABLISHED,
            "statement": (
                "Spin(10) is a compact Lie group, so it carries a unique "
                "bi-invariant probability measure (Haar)."
            ),
            "consequence": (
                "On a fixed finite Γ the pure-gauge Wilson integral "
                "∫ ∏ dμ_Haar(U_e) exp(−S_Wilson) exists and is finite."
            ),
        },
        "missing": [
            "the graph measure μ(Γ) and the class of allowed graphs",
            "discretisation of S_H and S_16",
            "gauge fixing or an explicit Haar quotient for the full system",
            "a refinement / continuum limit with a stable observable",
            "Osterwalder–Schrader positivity, or a Lorentzian reconstruction",
            "a bulk–boundary map from Γ to isolated-horizon punctures",
        ],
    }


def clause_score() -> list[dict[str, Any]]:
    """Preregistered T3 clauses. All must be MET before T3 is MET."""

    return [
        {
            "id": "M1",
            "name": "Configuration space",
            "status": MET,
            "statement": "Fields of Gate 4 are named: g (or Γ), A, ψ, Φ.",
            "note": "Naming the space is not constructing the measure.",
        },
        {
            "id": "M2",
            "name": "Normalised measure or projective family",
            "status": UNMET,
            "statement": "μ(Γ) and the full integrand must be specified and finite.",
            "note": "Only Haar-on-fixed-Γ is defined.",
        },
        {
            "id": "M3",
            "name": "Gauge orbits",
            "status": UNMET,
            "statement": "Diff × Spin(10) orbits are quotiented or Haar-averaged.",
            "note": "Fixed-graph Haar averages gauge links; diffeomorphisms are open.",
        },
        {
            "id": "M4",
            "name": "Refinement / continuum",
            "status": UNMET,
            "statement": "At least one observable is stable under a declared refinement.",
            "note": "Gate 1 is a toy graph ensemble without gauge fields.",
        },
        {
            "id": "M5",
            "name": "OS positivity or Lorentzian reconstruction",
            "status": UNMET,
            "statement": (
                "Reflection positivity on a Euclidean slice, or a causal "
                "kernel whose support is a partial order."
            ),
            "note": (
                "ift_egr_closure can audit a finite partial order. That is a "
                "necessary gate, not a reconstruction."
            ),
        },
        {
            "id": "M6",
            "name": "Matter in the same measure",
            "status": UNMET,
            "statement": "The 16 and the Higgs sit in Z, not in an add-on.",
            "note": "No discrete Dirac / Yukawa measure is implemented.",
        },
    ]


def t3_verdict() -> dict[str, Any]:
    clauses = clause_score()
    met = [c["id"] for c in clauses if c["status"] == MET]
    unmet = [c["id"] for c in clauses if c["status"] == UNMET]
    return {
        "id": "T3",
        "decision": "UNMET",
        "t3_met": T3_MET,
        "nogo_rule": (
            "T3 is MET only if M1–M6 are all MET. A formal ∫ Dg, a Haar "
            "integral on a fixed graph, or a causal-order audit is not enough."
        ),
        "preregistered": True,
        "clauses_met": met,
        "clauses_unmet": unmet,
        "note": (
            "M1 is syntax. Compact-group Haar makes the fixed-graph Wilson "
            "integral exist. Quantum gravity + SM is the rest of the list."
        ),
    }


def gate5_quantum_measure() -> dict[str, Any]:
    """Gate 5 — write the measure, score the clauses, keep T3 unmet."""

    return {
        "title": "Gate 5 — quantum measure (T3)",
        "version": "16.1",
        "status": INCOMPLETE,
        "scientific_status": "measure specified as a checklist; T3 unmet; not a TOE",
        "validated_observational_predictions": 0,
        "is_toe": False,
        "continuum": continuum_path_integral(),
        "discrete": discrete_candidate_measure(),
        "clauses": clause_score(),
        "t3": t3_verdict(),
        "decisions": {
            "t3_met": False,
            "haar_wilson_on_fixed_graph": True,
            "graph_sum_defined": False,
            "continuum_limit": False,
            "reflection_positivity": False,
        },
        "note": (
            "Gate 5 closes the *specification* of what T3 would be. "
            "It does not construct Z."
        ),
    }
