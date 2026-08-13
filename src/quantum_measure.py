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


def missing_t3_pieces() -> dict[str, Any]:
    """Name the four holes in Z_disc. None of them is filled."""

    return {
        "mu_graph": graph_measure_candidate(),
        "discrete_matter": discrete_matter_actions(),
        "refinement": refinement_protocol(),
        "os_or_lorentz": os_or_lorentzian(),
    }


def graph_measure_candidate() -> dict[str, Any]:
    """Finite-class Boltzmann weight. Normalisable; not quantum gravity."""

    return {
        "id": "μ(Γ)",
        "status": HYPOTHESIS,
        "class": (
            "C(N, torus-rewire): degree-preserving rewirings of a 3D periodic "
            "torus with N = side³ nodes (the Gate-1 class). Finite."
        ),
        "weight": "μ(Γ) = exp(−S_graph[Γ]) / Z_C,  S_graph = ∑_e ℓ_Manhattan",
        "normalisable": True,
        "reason_normalisable": "C is finite and the weights are positive, so Z_C < ∞.",
        "is_quantum_gravity": False,
        "note": (
            "A probability measure on a finite rewiring class is established "
            "as combinatorics. It is not a sum over geometries, not a GFT, "
            "and not μ on 2-complexes. M2 stays UNMET."
        ),
    }


def discrete_matter_actions() -> dict[str, Any]:
    """Lattice Higgs is standard; a Dirac 16 on a random graph is not."""

    return {
        "id": "S_16 and S_H",
        "S_H": {
            "status": ESTABLISHED,
            "formula": (
                "S_H[Φ,U] = ∑_{⟨ij⟩} ‖U_{ij}·Φ_j − Φ_i‖² + ∑_i V(Φ_i), "
                "Φ ∈ 10 ⊕ 126 ⊕ 210"
            ),
            "note": (
                "Standard lattice-Higgs kinetic term on a graph. V and the "
                "Yukawa tensors remain free. Writing S_H is not a spectrum."
            ),
        },
        "S_16": {
            "status": INCOMPLETE,
            "formula": (
                "S_16^{?} = ∑_{⟨ij⟩} ψ̄_i P_{ij} U_{ij} ψ_j + ∑_i ψ̄_i Y(Φ_i) ψ_i"
            ),
            "missing": (
                "A Clifford structure / soldering form on each edge, so that "
                "P_{ij} is a spin transport. A random graph does not supply γ^e."
            ),
            "note": "Naive hopping without frames is not the 16 of Spin(10) in curved space.",
        },
        "grassmann_measure": {
            "status": INCOMPLETE,
            "note": "∏ dψ_v is not defined until the spinor space at each vertex is.",
        },
    }


def refinement_protocol() -> dict[str, Any]:
    """What M4 would require. No continuum is claimed."""

    return {
        "id": "continuum / refinement",
        "status": UNMET,
        "protocol": (
            "Declare a refinement Γ_n → Γ_{n+1} (e.g. side → side+1 on the "
            "torus, or barycentric subdivision of a 2-complex). Freeze one "
            "gauge-invariant observable O. Require |O_n − O_{n+1}| < ε on a "
            "preregistered window before inspecting other observables."
        ),
        "nogo": (
            "Reject a claimed continuum if the frozen O is unstable under "
            "two successive refinements, or if d_S(T) is put back into the action."
        ),
        "gate1_relation": (
            "Gate 1 samples the finite class C but has no gauge field and "
            "already NO-GOs the TCD d_S curve. That is not a continuum limit "
            "of Z_disc."
        ),
        "done": False,
    }


def os_or_lorentzian() -> dict[str, Any]:
    """OS on a cube is a theorem; OS on a rewired graph is not."""

    return {
        "id": "OS or Lorentz",
        "status": UNMET,
        "euclidean": {
            "status": ESTABLISHED,
            "statement": (
                "Osterwalder–Seiler: compact lattice YM on a reflection-"
                "symmetric hypercubic lattice with β > 0 is reflection positive."
            ),
            "applies_to_rewired_torus": False,
            "reason": "A rewired graph generally has no reflection automorphism.",
        },
        "lorentzian": {
            "status": UNMET,
            "statement": (
                "A Lorentzian reconstruction needs a kernel K(x,y) supported "
                "on a partial order (x ≺ y) with zero weight on the complement."
            ),
            "necessary_gate": (
                "ift_egr_closure.audit_partial_order + "
                "causal_order_violation_fraction == 0"
            ),
            "sufficient": False,
        },
    }


def causal_kernel_necessary_check() -> dict[str, Any]:
    """Run the existing poset gate on the 4-element causal diamond."""

    from ift_egr_closure import (
        audit_partial_order,
        causal_order_violation_fraction,
    )
    import numpy as np

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
    return {
        "status": ESTABLISHED,
        "is_partial_order": audit.is_partial_order,
        "violation_causal": causal_order_violation_fraction(weights_ok, order),
        "violation_backward": causal_order_violation_fraction(weights_bad, order),
        "note": (
            "Zero violation on a diamond is necessary for a causal kernel. "
            "It is not a Lorentzian reconstruction of Z_disc."
        ),
    }
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
            "note": (
                "A Boltzmann weight on the finite Gate-1 rewiring class is "
                "normalisable combinatorics. The full integrand (graphs + "
                "Haar + 16 + Higgs) is not specified, so M2 stays UNMET."
            ),
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
                "OS holds for cubic compact YM. It does not apply to a "
                "rewired graph. A poset audit is necessary, not sufficient."
            ),
        },
        {
            "id": "M6",
            "name": "Matter in the same measure",
            "status": UNMET,
            "statement": "The 16 and the Higgs sit in Z, not in an add-on.",
            "note": "Lattice S_H is written. S_16 has no Clifford frames.",
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
        "pieces": missing_t3_pieces(),
        "causal_necessary_gate": causal_kernel_necessary_check(),
        "clauses": clause_score(),
        "t3": t3_verdict(),
        "decisions": {
            "t3_met": False,
            "haar_wilson_on_fixed_graph": True,
            "finite_rewiring_mu_normalisable": True,
            "finite_rewiring_is_quantum_gravity": False,
            "s_higgs_lattice_written": True,
            "s_16_frames_defined": False,
            "graph_sum_defined": False,
            "continuum_limit": False,
            "reflection_positivity": False,
        },
        "note": (
            "Gate 5 closes the *specification* of what T3 would be. "
            "It does not construct Z."
        ),
    }
