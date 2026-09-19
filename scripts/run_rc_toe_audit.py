#!/usr/bin/env python3
"""Executable audit of the RC-ToE definition and of the repository's own ToE claim.

Run::

    PYTHONPATH=src python scripts/run_rc_toe_audit.py \
        --output results/rc_toe_audit.json

The script is the decision procedure of ``docs/DEFINICJA-TEORII-WSZYSTKIEGO.md``.
It performs five blocks:

1. exhaustive verification of theorem T1 (classicality = absence of constraints
   of order >= 3) over every matroid on up to four labelled facts;
2. a census of those substrates on the admissibility ladder;
3. the exact Spin(10) structural identities (16 weights, |W(D_5)| = 1920, the
   even-parity code matroid) and their ladder position;
4. the certified residual of a toy prefix machine (Chaitin-style Omega bound)
   and the reflexive inference fixed point;
5. two audits: the repository's GUH-S10 claim and the RC-ToE proposal itself.

Exit status is non-zero if T1 fails, if the census is inconsistent, or if the
RC-ToE proposal certifies *itself* -- a definition that self-certifies without
passing its own gates is worthless, so the script treats that as an error.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import toe_closure_kernel as kernel  # noqa: E402
import toe_reflective_closure as rc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
HYPOTHESIS_DOC = REPO_ROOT / "docs" / "spin10_toe_hypothesis.md"


def compressed_bits(text: str) -> int:
    """MDL proxy: 8 * len(zlib.compress(text)).

    A proxy, not Kolmogorov complexity.  It is used only for the inequality
    ``|axioms| < |data explained|``, where a consistent proxy on both sides is
    sufficient; the absolute numbers carry no physical meaning.
    """

    return 8 * len(zlib.compress(text.encode("utf-8"), 9))


def extract_section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"audit input missing: {start_marker!r} in {HYPOTHESIS_DOC}")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit(f"audit input missing: {end_marker!r} in {HYPOTHESIS_DOC}")
    return text[start:end]


# ---------------------------------------------------------------------------
# block 1 and 2: theorem T1 and the census
# ---------------------------------------------------------------------------


def verify_theorem_t1(sizes: tuple[int, ...]) -> dict[str, object]:
    per_size = {}
    violations = []
    total = 0
    for size in sizes:
        matroids = kernel.enumerate_matroids(size)
        distributive = 0
        for matroid in matroids:
            lattice = matroid.flat_lattice()
            is_classical = lattice.is_distributive()
            has_high_order_constraint = matroid.lowest_constraint_order() >= 3
            # T1: distributive  <=>  no constraint of order >= 3
            if is_classical != has_high_order_constraint:
                distributive += int(is_classical)
            else:
                violations.append(
                    {
                        "size": size,
                        "circuits": [sorted(circuit) for circuit in matroid.circuits],
                        "distributive": is_classical,
                        "lowest_constraint_order": matroid.lowest_constraint_order(),
                    }
                )
        per_size[size] = {
            "n_matroids": len(matroids),
            "n_classical": distributive,
            "n_non_classical": len(matroids) - distributive,
        }
        total += len(matroids)
    return {
        "statement": (
            "L(M) is distributive (classical logic) if and only if every circuit of M has "
            "size <= 2, i.e. the substrate carries no constraint of order three or higher"
        ),
        "sizes_checked": list(sizes),
        "n_substrates_checked": total,
        "per_size": per_size,
        "violations": violations,
        "verdict": "PASS" if not violations else "FAIL",
    }


def substrate_census(sizes: tuple[int, ...]) -> dict[str, object]:
    counts: dict[str, int] = {}
    born_ready = 0
    total = 0
    for size in sizes:
        for matroid in kernel.enumerate_matroids(size):
            report = rc.admissibility_report(matroid)
            key = f"n={size} rung={report.rung} {report.rung_label}"
            counts[key] = counts.get(key, 0) + 1
            born_ready += int(report.born_ready)
            total += 1
    return {
        "counts": counts,
        "n_substrates": total,
        "n_born_ready": born_ready,
        "conclusion": (
            "no substrate on at most four facts is Born-ready: the single orthocomplemented "
            "non-classical one is U_{2,4} = PG(1,3), whose rank is 2, exactly the dimension in "
            "which Gleason-type theorems do not apply"
        ),
    }


# ---------------------------------------------------------------------------
# block 3: Spin(10) structural identities
# ---------------------------------------------------------------------------


def spin10_identities() -> dict[str, object]:
    weights = kernel.spin10_even_parity_weights()
    code = kernel.spin10_parity_code_matroid()
    report = rc.admissibility_report(code)
    lattice = code.flat_lattice()
    return {
        "n_spinor_weights": len(weights),
        "weights_are_even_parity_half_of_5_cube": len(weights) == 16,
        "weyl_group_order_computed": kernel.spin10_weyl_group_order(parity_even_only=True),
        "weyl_group_order_expected_D5": 2**4 * math.factorial(5),
        "hyperoctahedral_order_computed": kernel.spin10_weyl_group_order(parity_even_only=False),
        "weyl_group_acts_transitively_on_weights": kernel.spin10_weyl_group_acts_transitively(),
        "code_matroid": code.name,
        "code_matroid_is_uniform": code.circuits == (frozenset(range(5)),),
        "code_matroid_flats": len(lattice.elements),
        "code_matroid_characteristic_polynomial": {
            str(degree): value for degree, value in code.characteristic_polynomial().items()
        },
        "code_matroid_beta": code.beta_invariant(),
        "code_matroid_bases": code.count_bases(),
        "code_matroid_automorphisms": report.automorphism_group_order,
        "lowest_constraint_order": report.lowest_constraint_order,
        "admissibility_rung": report.rung,
        "admissibility_label": report.rung_label,
        "valuation_feasible": report.valuation_feasible,
        "consequence": (
            "the 16-spinor weight system, read as the closure structure of the binary [5,4] "
            "even-parity code, is U_{4,5}: its unique constraint is global (one circuit of five "
            "facts = fermion parity), its flat lattice is non-distributive, and it admits **no** "
            "valuation at all. Spin(10) is therefore a *label* on the facts, not yet a substrate "
            "that can carry probability; it must be embedded in an orthocomplementable one."
        ),
    }


def fano_report() -> dict[str, object]:
    fano = kernel.fano_matroid()
    report = rc.admissibility_report(fano)
    lattice = fano.flat_lattice()
    polytope = lattice.valuation_polytope()
    data = report.as_dict()
    data["unique_state"] = {
        "sigma_point": str(polytope.vertices[0][0]) if polytope.vertices else None,
        "sigma_line": str(polytope.vertices[0][7]) if polytope.vertices else None,
        "n_states": len(polytope.vertices),
        "dimension": polytope.affine_dimension,
    }
    data["circuit_profile"] = {str(k): v for k, v in fano.constraint_profile(4).items()}
    data["tutte_polynomial"] = {f"x^{i}y^{j}": c for (i, j), c in fano.tutte_polynomial().items()}
    return data


# ---------------------------------------------------------------------------
# block 4: residual and reflexive inference
# ---------------------------------------------------------------------------


def residual_block(lengths: tuple[int, ...], budget: int) -> dict[str, object]:
    results = [rc.toy_prefix_machine_omega(length, step_budget=budget) for length in lengths]
    return {
        "machine": "toy prefix machine U(1**k 0 body), 2-bit instructions INC/JZ/HALT/DEC",
        "status": "exact lower bound with certified residual; not Chaitin's Omega itself",
        "results": [result.as_dict() for result in results],
        "monotone_in_length": all(
            results[i].omega <= results[i + 1].omega for i in range(len(results) - 1)
        ),
        "interpretation": (
            "a theory whose axioms and proof budget are bounded by (N, B) cannot decide more than "
            "omega(N, B) of the mass of its own fact space; residual(N, B) is a certified lower "
            "bound on its unexplained sector. Gate D of the definition requires this bound to be "
            "published together with the theory, not discovered after the fact."
        ),
    }


def reflexive_block() -> dict[str, object]:
    fixed_point = rc.reflexive_bayes_fixed_point(
        hypotheses=["A_max_likelihood", "B_reflective", "C_third"],
        likelihood=[0.70, 0.20, 0.10],
        inference_kernel=[
            [0.10, 0.80, 0.10],
            [0.05, 0.90, 0.05],
            [0.20, 0.50, 0.30],
        ],
        exploration=0.02,
    )
    return {
        "operator": "p -> normalise( (1-e) * p * L * (M^T p) + e * uniform )",
        "result": fixed_point.as_dict(),
        "conclusion": (
            "the reflective fixed point is B (likelihood 0.20), not the maximum-likelihood A "
            "(likelihood 0.70): self-consistency of the inference process overrides likelihood by "
            f"a total-variation margin of {fixed_point.reflective_override:.3f}. A Theory of "
            "Everything that cannot survive its own inference operator is not a ToE, even when "
            "it fits the data best."
        ),
    }


# ---------------------------------------------------------------------------
# block 5: audits
# ---------------------------------------------------------------------------


GUH_S10_FITTED = [
    {"parameter": "alpha_em calibration offset", "value": "-6.5504",
     "evidence": "src/physics_apex_v13_core.py:145 and src/grand_unified_toe_core.py:551 "
                 "(comment: 'Dokladna kalibracja do 1/137.036')",
     "claim_it_contradicts": "README: 'alpha_em = 1/137.036 -- from Spin(10) Lie algebra, "
                             "zero experimental input'"},
    {"parameter": "holographic coefficient c_H", "value": "0.33",
     "evidence": "src/spin10_engine.py:703; docs/spin10_toe_hypothesis.md axiom A3",
     "claim_it_contradicts": "P = 1 - 0.33/sqrt(N) is presented as a derived scaling"},
    {"parameter": "spectral-dimension scale N_c", "value": "150",
     "evidence": "src/spin10_engine.py:390 (comment: 'formula z remedium')",
     "claim_it_contradicts": "d_S(N) = 4(1 - exp(-N/150)) is presented as an emergence law"},
    {"parameter": "graph equilibrium variance", "value": "32.67",
     "evidence": "docs/spin10_toe_hypothesis.md axiom A2", "claim_it_contradicts": "A2"},
    {"parameter": "UV fixed point g*", "value": "0.83",
     "evidence": "docs/spin10_toe_hypothesis.md axiom A4", "claim_it_contradicts": "A4"},
    {"parameter": "hidden-sector multiplet count", "value": "125",
     "evidence": "docs/spin10_toe_hypothesis.md section 5", "claim_it_contradicts": "a_4 = 0"},
]

GUH_S10_FALSIFIERS = [
    rc.Falsifier(
        observable="tensor-to-scalar ratio r",
        prediction="0.0125",
        tolerance="not stated in the repository",
        experiment="LiteBIRD / CMB-S4",
        horizon="2030-2035",
        kill_semantics="not stated: no claim is named as dead if r is measured outside the band",
        pre_registered=False,
        external=True,
    ),
    rc.Falsifier(
        observable="axion mass m_a",
        prediction="28.5 neV",
        tolerance="not stated in the repository",
        experiment="CASPEr",
        horizon="2028-2032",
        kill_semantics="not stated",
        pre_registered=False,
        external=True,
    ),
    rc.Falsifier(
        observable="gluino mass m_gluino",
        prediction="10.6 TeV (docs/KLUCZOWE-REMEDIA.md, docs/spin10_toe_hypothesis.md) "
                   "vs 12.39 TeV (docs/PREDYKCJE-i-FALSYFIKACJA-2026-2040.md)",
        tolerance="two different frozen values coexist in the repository",
        experiment="HE-LHC / FCC-hh",
        horizon="2027-2035",
        kill_semantics="undecidable as published: a prediction with two values cannot be violated",
        pre_registered=False,
        external=True,
    ),
    rc.Falsifier(
        observable="baryon asymmetry eta_B",
        prediction="6.2e-10 (docs/spin10_toe_hypothesis.md) vs 6.11e-10 "
                   "(docs/PREDYKCJE-i-FALSYFIKACJA-2026-2040.md)",
        tolerance="1.5% spread between the two published values",
        experiment="Planck / BBN",
        horizon="already measured",
        kill_semantics="undecidable as published",
        pre_registered=False,
        external=True,
    ),
]


def audit_guh_s10(axiom_bits: int, data_bits: int) -> rc.ToeAudit:
    return rc.audit_rc_toe(
        candidate="GUH-S10 (Spin(10) Theory of Everything, engine v14.5)",
        substrate_report=None,
        declared_rung=None,
        fitted_parameters=[entry["parameter"] for entry in GUH_S10_FITTED],
        invariant_claims=[
            {
                "constant": "alpha_em^-1",
                "invariant": "2-loop RGE integration from M_GUT",
                "n_invariants": 1,
                "n_candidates": 1,
                "tolerance": 0.0004,
                "mechanism": False,
                "note": "the integration ends with a hard-coded -6.5504 offset "
                        "(src/physics_apex_v13_core.py:145), so the value is calibrated, "
                        "not derived; the mechanism requirement of gate S is not met",
            }
        ],
        law_channels={
            "gauge": "postulated",
            "gravity": "hypothesis",
            "fermion_generations": "hypothesis",
            "cosmological_constant": "rejected",
        },
        law_channel_notes={
            "gauge": "Spin(10) gauge fields are imposed on the relational graph; they are not read "
                     "off the automorphism group of any closure operator implemented here",
            "gravity": "'emergent mode of the relational graph' with no implemented operator; the "
                       "independent audit of the closest module is CONDITIONAL PASS "
                       "(docs/IFT_EGR_INDEPENDENT_AUDIT.md)",
            "fermion_generations": "'topologically from the graph nodes'; no derivation exists in "
                                   "the repository",
            "cosmological_constant": "the holographic lambda is inverse-area only and fails the "
                                     "closure test (tests/test_ift_egr_closure.py)",
        },
        fixed_point=None,
        falsifiers=GUH_S10_FALSIFIERS,
        axiom_bits=axiom_bits,
        data_bits=data_bits,
        omega=rc.toy_prefix_machine_omega(7, step_budget=2000),
    )


RC_TOE_FALSIFIERS = [
    rc.Falsifier(
        observable="T1: classicality equals absence of constraints of order >= 3",
        prediction="zero violations over every matroid on <= 4 labelled facts (89 substrates for n = 2, 3, 4)",
        tolerance="0 violations",
        experiment="exhaustive enumeration in this repository (scripts/run_rc_toe_audit.py)",
        horizon="decidable now",
        kill_semantics="one counterexample kills the whole ladder reading of quantum logic and "
                       "demotes RC-ToE to a computational framework",
        pre_registered=True,
    ),
    rc.Falsifier(
        observable="finite Born-ready substrate",
        prediction="none exists on <= 4 facts; for finite projective planes none exists at all "
                   "(every polarity has absolute points)",
        tolerance="exhibition of one finite non-distributive orthocomplemented rank >= 3 matroid "
                  "with a valuation",
        experiment="enumeration up to 6 facts; then a search over GF(q)-representable matroids",
        horizon="2026-2027 (enumeration is finite and cheap)",
        kill_semantics="kills the claim that the substrate of a quantum ToE must be infinite, "
                       "which is the hinge of gate Q",
        pre_registered=True,
    ),
    rc.Falsifier(
        observable="Spin(10) weight system as a closure structure",
        prediction="the binary [5,4] even-parity code matroid is U_{4,5}, rung 1, no valuation",
        tolerance="exact",
        experiment="scripts/run_rc_toe_audit.py block 3",
        horizon="decidable now",
        kill_semantics="if a valuation exists on L(U_{4,5}), the negative result about Spin(10) "
                       "as a standalone substrate is void",
        pre_registered=True,
    ),
    rc.Falsifier(
        observable="reflective override of maximum likelihood",
        prediction="the reflexive operator selects a non-maximum-likelihood hypothesis with "
                   "contraction rate < 1",
        tolerance="exact for the published 3-hypothesis kernel",
        experiment="scripts/run_rc_toe_audit.py block 4",
        horizon="decidable now",
        kill_semantics="if the fixed point always coincides with the maximum-likelihood choice, "
                       "gate O is vacuous and must be deleted from the definition",
        pre_registered=True,
    ),
    rc.Falsifier(
        observable="gauge group as an automorphism group of a closure structure",
        prediction="NOT PREDICTED: no finite search has yet produced W(Spin(10)) as Aut of a "
                   "substrate with the required invariants",
        tolerance="the search space is finite and pre-registered: all matroids on <= 6 facts "
                  "plus all GF(2)-representable matroids on <= 7 facts",
        experiment="enumeration (to be implemented)",
        horizon="2027",
        kill_semantics="an empty search refutes the gauge channel of gate L for that class and "
                       "forces the class to be enlarged or abandoned",
        pre_registered=True,
    ),
]


def audit_rc_toe_self(fano_report_data: dict[str, object], axiom_bits: int, data_bits: int) -> rc.ToeAudit:
    fano = kernel.fano_matroid()
    report = rc.admissibility_report(fano)
    return rc.audit_rc_toe(
        candidate="RC-ToE (Reflective Closure Theory of Everything) -- this definition",
        substrate_report=report,
        declared_rung=2,
        fitted_parameters=[],
        invariant_claims=[],
        law_channels={
            "gauge": "open_task",
            "gravity": "open_task",
            "fermion_generations": "open_task",
            "cosmological_constant": "open_task",
        },
        law_channel_notes={
            "gauge": "W(D_5) = 1920 is reproduced exactly as the parity-preserving automorphism "
                     "group of the 5-slot fact lattice, but Spin(10) itself has not been derived",
            "gravity": "the entropic response of the rank function to inserted facts is defined "
                       "but no Einstein equation has been recovered from it",
            "fermion_generations": "no invariant of any enumerated substrate has been mapped to "
                                   "N_gen = 3 with a mechanism; beta(Fano) = 3 was proposed and "
                                   "then rejected by the coincidence budget",
            "cosmological_constant": "no invariant has been mapped to Lambda",
        },
        fixed_point=rc.reflexive_bayes_fixed_point(
            hypotheses=["A_max_likelihood", "B_reflective", "C_third"],
            likelihood=[0.70, 0.20, 0.10],
            inference_kernel=[[0.10, 0.80, 0.10], [0.05, 0.90, 0.05], [0.20, 0.50, 0.30]],
            exploration=0.02,
        ),
        falsifiers=RC_TOE_FALSIFIERS,
        axiom_bits=axiom_bits,
        data_bits=data_bits,
        omega=rc.toy_prefix_machine_omega(9, step_budget=2000),
    )


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="results/rc_toe_audit.json")
    parser.add_argument("--sizes", default="3,4", help="fact counts for the exhaustive blocks")
    parser.add_argument("--omega-lengths", default="5,7,9")
    parser.add_argument("--omega-budget", type=int, default=2000)
    args = parser.parse_args(argv)

    sizes = tuple(int(value) for value in args.sizes.split(",") if value.strip())
    omega_lengths = tuple(int(value) for value in args.omega_lengths.split(",") if value.strip())

    t1 = verify_theorem_t1(tuple(size for size in sizes if size >= 2) + (2,))
    t1["sizes_checked"] = sorted(set(t1["sizes_checked"]))
    census = substrate_census(sizes)
    spin10 = spin10_identities()
    fano = fano_report()
    residual = residual_block(omega_lengths, args.omega_budget)
    reflexive = reflexive_block()

    hypothesis_text = HYPOTHESIS_DOC.read_text(encoding="utf-8")
    guh_axioms = extract_section(hypothesis_text, "## §2. Fundamental Axioms", "## §3.")
    guh_data = extract_section(hypothesis_text, "## §9. Experimental Confrontation", "## §10.")
    falsification_doc = REPO_ROOT / "docs" / "PREDYKCJE-i-FALSYFIKACJA-2026-2040.md"
    if falsification_doc.exists():
        falsification_text = falsification_doc.read_text(encoding="utf-8")
        guh_data += extract_section(
            falsification_text, "## 🌌 2. Pelne Zestawienie", "---"
        )
    guh_audit = audit_guh_s10(compressed_bits(guh_axioms), compressed_bits(guh_data))

    definition_path = REPO_ROOT / "docs" / "DEFINICJA-TEORII-WSZYSTKIEGO.md"
    if definition_path.exists():
        definition_text = definition_path.read_text(encoding="utf-8")
        rc_axioms = extract_section(definition_text, "## §3. Definicja", "## §4.")
        rc_data = extract_section(definition_text, "## §6. Wyniki", "## §7.")
        rc_axiom_bits = compressed_bits(rc_axioms)
        rc_data_bits = compressed_bits(rc_data)
    else:
        rc_axiom_bits, rc_data_bits = 0, 0

    self_audit = audit_rc_toe_self(fano, rc_axiom_bits, rc_data_bits)

    payload = {
        "audit_id": "RC-TOE-001",
        "definition_document": "docs/DEFINICJA-TEORII-WSZYSTKIEGO.md",
        "status": "DEFINITION_AND_DECISION_PROCEDURE_NOT_A_VALIDATED_THEORY",
        "blocks": {
            "theorem_T1": t1,
            "substrate_census": census,
            "spin10_structural_identities": spin10,
            "fano_PG22": fano,
            "certified_residual": residual,
            "reflexive_inference": reflexive,
        },
        "audits": {
            "guh_s10": guh_audit.as_dict(),
            "rc_toe_self": self_audit.as_dict(),
        },
        "mdl": {
            "guh_s10_axiom_bits": compressed_bits(guh_axioms),
            "guh_s10_data_bits": compressed_bits(guh_data),
            "rc_toe_axiom_bits": rc_axiom_bits,
            "rc_toe_data_bits": rc_data_bits,
            "note": "zlib-compressed bit lengths of the quoted document sections; a proxy for "
                    "description length, used only for the inequality in gate D",
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps(
        {
            "T1": t1["verdict"],
            "T1_substrates": t1["n_substrates_checked"],
            "census_born_ready": census["n_born_ready"],
            "spin10_code_rung": spin10["admissibility_rung"],
            "weyl_order": spin10["weyl_group_order_computed"],
            "omega_9": float(rc.toy_prefix_machine_omega(9, step_budget=args.omega_budget).omega),
            "guh_s10": guh_audit.verdict,
            "rc_toe_self": self_audit.verdict,
            "output": str(output_path),
        },
        indent=2,
    ))

    failures = []
    if t1["verdict"] != "PASS":
        failures.append("theorem T1 has counterexamples")
    if census["n_born_ready"] != 0:
        failures.append("the census found a Born-ready finite substrate; the document must be updated")
    if spin10["weyl_group_order_computed"] != spin10["weyl_group_order_expected_D5"]:
        failures.append("the Weyl group order does not reproduce 2^4 * 5! = 1920")
    if spin10["n_spinor_weights"] != 16:
        failures.append("the even-parity weight count is not 16")
    if self_audit.certified:
        failures.append(
            "the RC-ToE proposal certified itself; gate S or gate Q has lost its teeth"
        )
    if failures:
        print("AUDIT CONTRACT FAILURES:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
