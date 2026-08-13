"""Necessary conditions for a Theory-of-Everything claim in this programme.

A TOE claim is allowed only if every condition below is MET.
Partial credit is not a TOE.  Satisfying the α-attractor phenomenology
contract (NS-AT-INSTANT-01) is not sufficient.

This module evaluates the frozen checklist against the current
specification.  It does not mint validations.
"""

from __future__ import annotations

from typing import Any

MET = "MET"
UNMET = "UNMET"
PARTIAL = "PARTIAL"

# A TOE claim requires every ID in this tuple to be MET.
NECESSARY = (
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "T6",
    "T7",
    "T8",
    "T9",
    "T10",
    "T11",
    "T12",
)


def _item(
    ident: str,
    name: str,
    statement: str,
    status: str,
    evidence: str,
) -> dict[str, Any]:
    return {
        "id": ident,
        "name": name,
        "statement": statement,
        "status": status,
        "necessary": ident in NECESSARY,
        "evidence": evidence,
    }


def evaluate_toe_conditions() -> dict[str, Any]:
    """Return the frozen necessary-condition checklist and the TOE verdict."""

    items = [
        _item(
            "T1",
            "Internal consistency",
            (
                "Every axiom is classified, every formula names its inputs and "
                "units, and every rejected shortcut stays rejected."
            ),
            PARTIAL,
            (
                "The v16.1 specification and ledgers exist, but imported "
                "modules and undeclared Yukawas remain. Partial ≠ MET."
            ),
        ),
        _item(
            "T2",
            "Single dynamical framework",
            (
                "One action or measure contains gravity and the SM gauge + "
                "matter content. A stack of imported LQC / α-attractor / "
                "RGE modules is not a TOE."
            ),
            UNMET,
            (
                "Gate 4 writes the classical EYM candidate S[g,A,ψ,Φ]. "
                "LQC, α-attractors and M_Z-input RGE are not terms of S. "
                "Syntax without consequences is not T2."
            ),
        ),
        _item(
            "T3",
            "Quantum definition",
            (
                "A Hilbert space or Euclidean measure is specified, with gauge "
                "fixing, a continuum / refinement limit, and either reflection "
                "positivity or a stated Lorentzian reconstruction."
            ),
            UNMET,
            (
                "Gate 5 names the four holes. A finite rewiring μ(Γ) is "
                "normalisable combinatorics, not QG. Lattice S_H is written; "
                "S_16 has no frames. Continuum and OS/Lorentz stay UNMET."
            ),
        ),
        _item(
            "T4",
            "Gravity limit",
            (
                "Einstein gravity (or a specified alternative) is recovered "
                "with controlled extra terms. G_eff = G0/P is not the field "
                "equation unless ∇P = 0."
            ),
            UNMET,
            (
                "Gate 3 writes the prescribed-P action but does not derive P. "
                "Einstein-with-G_eff is NO-GO for variable P."
            ),
        ),
        _item(
            "T5",
            "Standard Model content",
            (
                "Gauge algebra and fermion quantum numbers are derived, "
                "including hypercharge. Three generations are derived, not "
                "posted as an input."
            ),
            UNMET,
            (
                "A1 gives one 16 and sin²θ_W=3/8 at a Spin(10) point. "
                "N_gen=3 is axiom A2 (unverified input). E8 gives four 16s."
            ),
        ),
        _item(
            "T6",
            "No hidden calibration",
            (
                "A number fitted to a PDG or entropy-matching target is not "
                "sold as a derivation (A4)."
            ),
            UNMET,
            (
                "Apex multiplies α_s by 0.9736 and subtracts 6.5504 from "
                "1/α_em. Immirzi γ=0.2739 is matched to S=A/4."
            ),
        ),
        _item(
            "T7",
            "Input-independent scales",
            (
                "M_GUT, Λ, α_em, and the Yukawas (m_D, M_R) are derived "
                "without placing the target in the inputs."
            ),
            UNMET,
            (
                "M_Z couplings and M_SUSY are inputs. Λ from T_c⁴/M_Pl² is "
                "rejected. Seesaw masses are declared."
            ),
        ),
        _item(
            "T8",
            "One TOE-level prediction contract",
            (
                "At least one observable has: independent derivation from the "
                "TOE dynamics (not an imported module), inputs excluding the "
                "target, an official likelihood, and a preregistered no-go."
            ),
            UNMET,
            (
                "NS-AT-INSTANT-01 is a complete phenomenology contract for "
                "α-attractors with a chosen α. It is not a Spin(10) derivation "
                "and not an official Planck Plik/CamSpec likelihood."
            ),
        ),
        _item(
            "T9",
            "Not excluded on necessary consequences",
            (
                "No necessary consequence of the claimed TOE is excluded by a "
                "frozen published limit under the theory's own declared inputs."
            ),
            UNMET,
            (
                "The implemented dimension-6 proton lifetime at default "
                "α_H=0.015 is below Super-K 2.4e34 yr (row C3, excluded)."
            ),
        ),
        _item(
            "T10",
            "Official data products",
            (
                "Confrontations that are used to claim a TOE use official "
                "likelihoods or published limits as specified (Planck "
                "Plik/CamSpec, Super-K/Hyper-K, MEG-II), not marketing proxies."
            ),
            UNMET,
            "OBS-2026-08 n_s Gaussian is a proxy. No Plik/CamSpec or MEG-II loop.",
        ),
        _item(
            "T11",
            "Independent gates bind",
            (
                "A preregistered NO-GO on an independent ensemble cannot be "
                "overridden by putting the target curve back into the action."
            ),
            PARTIAL,
            (
                "Gate 1 NO-GO on the 3D torus is recorded. The condition is "
                "a discipline rule; it does not by itself make a TOE."
            ),
        ),
        _item(
            "T12",
            "Count stays honest",
            (
                "validated_observational_predictions increments only under T8. "
                "validated_toe is true only if T1–T11 are all MET."
            ),
            MET,
            "Both counters are implemented fail-closed and currently read 0 / false.",
        ),
    ]
    met = [item for item in items if item["status"] == MET]
    unmet = [item for item in items if item["status"] == UNMET]
    partial = [item for item in items if item["status"] == PARTIAL]
    necessary_met = all(
        item["status"] == MET for item in items if item["id"] in NECESSARY
    )
    return {
        "title": "Necessary conditions for a TOE claim",
        "version": "16.1",
        "is_toe": False,
        "validated_toe": False,
        "validated_observational_predictions": 0,
        "necessary_ids": list(NECESSARY),
        "necessary_all_met": necessary_met,
        "n_met": len(met),
        "n_partial": len(partial),
        "n_unmet": len(unmet),
        "n_necessary": len(NECESSARY),
        "items": items,
        "rule": (
            "A Theory-of-Everything claim requires every necessary condition "
            "T1–T12 to be MET. Phenomenology contracts, group-theory facts, "
            "and internal specification closure are not sufficient."
        ),
        "note": (
            "T12 being MET only means the counters refuse to lie. "
            "The programme is not a TOE."
        ),
    }


def assert_not_a_toe(report: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fail closed: raise if anyone marks a TOE while conditions are unmet."""

    payload = report if report is not None else evaluate_toe_conditions()
    if payload.get("is_toe") or payload.get("validated_toe"):
        if not payload.get("necessary_all_met"):
            raise AssertionError("TOE flag set while necessary conditions are unmet")
    if payload.get("validated_observational_predictions", 0) != 0:
        if payload.get("items") and any(
            item["id"] == "T8" and item["status"] != MET for item in payload["items"]
        ):
            raise AssertionError("TOE prediction count incremented without T8")
    return payload
