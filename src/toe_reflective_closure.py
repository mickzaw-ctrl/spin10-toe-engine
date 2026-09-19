"""RC-ToE closure gates: admissibility ladder, reflexive inference, residual.

This module implements the *decision procedure* half of the Reflective Closure
Theory of Everything definition (``docs/DEFINICJA-TEORII-WSZYSTKIEGO.md``).
It is deliberately separate from the combinatorial kernel
(:mod:`toe_closure_kernel`) because the kernel proves mathematics while this
module scores physical claims.

Everything is standard library only, exact where a closed form exists, and
fail-closed: no routine returns a certification it cannot justify.  In
particular :func:`audit_rc_toe` **refuses to certify** a Theory of Everything
unless all five gates pass, and it refuses to certify the RC-ToE proposal
itself -- see ``scripts/run_rc_toe_audit.py``.

Gates
-----
S   substance closure   -- zero fitted parameters; every constant is a
                           combinatorial invariant, and the invariant claim
                           survives the coincidence budget;
L   law closure         -- every interaction is a channel of one rank flow;
Q   logic closure       -- the substrate sits on a *declared* rung of the
                           admissibility ladder (classical / inadmissible /
                           generalised probability / orthocomplemented);
O   observer closure    -- the theory is an attractive fixed point of its own
                           inference operator, up to a certified residual;
D   decision closure    -- pre-registered falsifiers with claim-level kill
                           semantics, plus an MDL inequality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations, product
import json
import math
from typing import Iterable, Mapping, Sequence

__all__ = [
    "ReflectiveClosureError",
    "AdmissibilityReport",
    "ReflexiveFixedPoint",
    "CoincidenceBudget",
    "Gate",
    "ToeAudit",
    "admissibility_report",
    "toy_prefix_machine_omega",
    "reflexive_bayes_fixed_point",
    "coincidence_budget",
    "audit_rc_toe",
]


class ReflectiveClosureError(ValueError):
    """Raised when a gate would have to be scored outside its validated domain."""


# ---------------------------------------------------------------------------
# gate Q -- the admissibility ladder
# ---------------------------------------------------------------------------

LAW_CHANNEL_STATUS = {"derived", "implemented", "hypothesis", "open_task", "postulated", "rejected"}

LADDER = {
    0: "classical_lawless",
    1: "constrained_but_no_probability",
    2: "generalised_probability_without_born_rule",
    3: "orthocomplemented_hilbert_ready",
}


@dataclass(frozen=True)
class AdmissibilityReport:
    """Where a substrate sits on the admissibility ladder, with exact evidence.

    Rung 0: distributive lattice -- classical logic, but ``delta_3 = 0``, i.e.
            no constraint of order three or higher, i.e. no law at all.
    Rung 1: non-distributive, and the valuation system is inconsistent -- the
            substrate admits **no** probability measure.
    Rung 2: non-distributive with at least one valuation, but no
            orthocomplementation -- generalised probability without a Born rule.
    Rung 3: non-distributive, valuation exists and an orthocomplementation was
            found -- Gleason/Soller territory, i.e. a Hilbert space over a
            division ring with involution.
    """

    substrate: str
    n_facts: int
    rank: int
    interaction_density: Fraction
    distributive: bool
    modular: bool
    valuation_feasible: str
    valuation_dimension: int
    n_states: int
    orthocomplemented: bool
    automorphism_group_order: int
    beta_invariant: int
    rung: int
    rung_label: str
    lowest_constraint_order: int
    born_ready: bool
    invariant_vector: Mapping[str, int]
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "substrate": self.substrate,
            "n_facts": self.n_facts,
            "rank": self.rank,
            "interaction_density": str(self.interaction_density),
            "distributive": self.distributive,
            "modular": self.modular,
            "valuation_feasible": self.valuation_feasible,
            "valuation_dimension": self.valuation_dimension,
            "n_states": self.n_states,
            "orthocomplemented": self.orthocomplemented,
            "automorphism_group_order": self.automorphism_group_order,
            "beta_invariant": self.beta_invariant,
            "rung": self.rung,
            "rung_label": self.rung_label,
            "lowest_constraint_order": self.lowest_constraint_order,
            "born_ready": self.born_ready,
            "invariant_vector": dict(self.invariant_vector),
            "notes": list(self.notes),
        }


def admissibility_report(matroid, notes: Sequence[str] = ()) -> AdmissibilityReport:
    """Score a substrate exactly.  Requires :mod:`toe_closure_kernel`."""

    from toe_closure_kernel import Lattice, Matroid  # local import keeps this module light

    if not isinstance(matroid, Matroid):
        raise ReflectiveClosureError("admissibility_report requires a toe_closure_kernel.Matroid")
    lattice: Lattice = matroid.flat_lattice()
    polytope = lattice.valuation_polytope()
    notes = list(notes)

    ortho = None
    try:
        ortho = lattice.orthocomplementation()
    except Exception as exc:  # pragma: no cover - guard message only
        notes.append(f"orthocomplementation search refused: {exc}")
    if ortho is None and not any("orthocomplementation" in note for note in notes):
        notes.append(
            "no orthocomplementation was found; for finite projective geometries this is "
            "expected, since every polarity of a finite projective plane has absolute points"
        )

    if polytope.feasible == "no":
        rung = 1
    elif lattice.is_distributive():
        rung = 0
    elif ortho is not None:
        rung = 3
    elif polytope.feasible == "yes":
        rung = 2
    else:
        raise ReflectiveClosureError(
            f"{matroid.name}: the state space is undetermined; the ladder refuses to score it"
        )

    if rung == 0 and matroid.lowest_constraint_order() >= 3:
        raise ReflectiveClosureError(
            f"{matroid.name}: distributive lattice with a circuit of order >= 3 contradicts theorem T1"
        )
    if rung >= 1 and matroid.lowest_constraint_order() == 0:
        raise ReflectiveClosureError(
            f"{matroid.name}: non-distributive lattice without any constraint of order >= 3 "
            "contradicts theorem T1"
        )
    # Gleason-type theorems need rank >= 3, so an orthocomplemented rank-2
    # substrate (M4, the logic of a qubit over a finite field) is rung 3 but is
    # *not* Born-ready: this is exactly the well-known dimension-2 exception.
    # A distributive lattice is orthocomplemented too, but it is classical, so
    # Born-readiness is reserved for the genuinely non-classical rung 3.
    born_ready = rung == 3 and matroid.full_rank() >= 3

    return AdmissibilityReport(
        substrate=matroid.name,
        n_facts=len(matroid.ground),
        rank=matroid.full_rank(),
        interaction_density=matroid.interaction_density,
        distributive=lattice.is_distributive(),
        modular=lattice.is_modular(),
        valuation_feasible=polytope.feasible,
        valuation_dimension=polytope.affine_dimension,
        n_states=len(polytope.vertices),
        orthocomplemented=ortho is not None,
        automorphism_group_order=matroid.automorphism_group_order(),
        beta_invariant=matroid.beta_invariant(),
        rung=rung,
        rung_label=LADDER[rung],
        lowest_constraint_order=matroid.lowest_constraint_order(),
        born_ready=born_ready,
        invariant_vector=matroid.invariant_vector(),
        notes=tuple(notes),
    )


# ---------------------------------------------------------------------------
# residual -- exact Chaitin-style Omega lower bound on a toy prefix machine
# ---------------------------------------------------------------------------

# instruction alphabet of the toy machine, 2 bits per instruction
_INC = 0  # A += 1
_JZ = 1  # if A == 0: pc = 0  (loop while the register is empty)
_HALT = 2
_DEC = 3  # A = max(A - 1, 0)


@dataclass(frozen=True)
class OmegaResult:
    """Exact lower bound on the halting probability of the toy prefix machine.

    Programs use the self-delimiting code ``1**k 0 body`` with ``|body| = k``,
    so a program has length ``2k + 1`` and the code is prefix free.  The body
    is read as ``k // 2`` two-bit instructions; odd ``k`` leaves one unused
    trailing bit, which is part of the program's identity.

    ``omega`` is the exact mass of programs of length <= ``max_length`` that
    halt within ``step_budget`` steps; ``residual`` is the exact mass that the
    budget could not decide.  ``omega + residual`` equals the total program mass
    of that length bound, so the residual is a *certified* upper bound on the
    machine's undecidable sector -- the same epistemic status as published
    lower bounds on Chaitin's Omega.
    """

    max_length: int
    step_budget: int
    omega: Fraction
    residual: Fraction
    total_mass: Fraction
    n_programs: int
    n_halting: int
    n_undecided: int

    def as_dict(self) -> dict[str, object]:
        return {
            "max_length": self.max_length,
            "step_budget": self.step_budget,
            "omega": str(self.omega),
            "omega_float": float(self.omega),
            "residual": str(self.residual),
            "residual_float": float(self.residual),
            "total_mass": str(self.total_mass),
            "n_programs": self.n_programs,
            "n_halting": self.n_halting,
            "n_undecided": self.n_undecided,
        }


def _run_toy_program(instructions: Sequence[int], step_budget: int) -> bool | None:
    """Return True (halts), False (provably runs off within budget) or None."""

    register = 0
    program_counter = 0
    for _ in range(step_budget):
        if program_counter >= len(instructions):
            return True  # running off the end is halting
        instruction = instructions[program_counter]
        if instruction == _HALT:
            return True
        if instruction == _INC:
            register += 1
            program_counter += 1
        elif instruction == _DEC:
            register = max(register - 1, 0)
            program_counter += 1
        elif instruction == _JZ:
            program_counter = 0 if register == 0 else program_counter + 1
        else:  # pragma: no cover - unreachable for 2-bit instructions
            raise ReflectiveClosureError("unknown instruction")
    return None  # undecided within the budget


def toy_prefix_machine_omega(max_length: int, step_budget: int = 4096) -> OmegaResult:
    if max_length < 1:
        raise ReflectiveClosureError("max_length must be at least 1")
    if max_length > 21:
        raise ReflectiveClosureError(
            "toy_prefix_machine_omega fails closed above length 21 (exhaustive enumeration)"
        )
    if step_budget < 1:
        raise ReflectiveClosureError("step_budget must be positive")

    omega = Fraction(0)
    residual = Fraction(0)
    total = Fraction(0)
    n_programs = n_halting = n_undecided = 0
    for k in range(0, (max_length) // 2 + 1):
        length = 2 * k + 1
        if length > max_length:
            continue
        mass = Fraction(1, 2**length)
        for body in product((0, 1), repeat=k):
            n_programs += 1
            total += mass
            number = int("".join(str(bit) for bit in body), 2) if body else 0
            instructions = [(number >> (2 * position)) & 3 for position in range(k // 2)]
            outcome = _run_toy_program(instructions, step_budget)
            if outcome is True:
                omega += mass
                n_halting += 1
            elif outcome is None:
                residual += mass
                n_undecided += 1
            else:  # pragma: no cover - the toy machine never returns False
                residual += mass
                n_undecided += 1
    if omega + residual != total:
        raise ReflectiveClosureError("mass accounting is broken; refusing to report Omega")
    return OmegaResult(
        max_length=max_length,
        step_budget=step_budget,
        omega=omega,
        residual=residual,
        total_mass=total,
        n_programs=n_programs,
        n_halting=n_halting,
        n_undecided=n_undecided,
    )


# ---------------------------------------------------------------------------
# gate O -- reflexive inference fixed point
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReflexiveFixedPoint:
    """Attractive fixed point of the self-referential inference operator.

    The map is ``p -> normalise( p * L * (M^T p) )``: a candidate theory gains
    weight from the data (``L``) *and* from the probability that an agent who
    holds a theory drawn from ``p`` would infer it (``M``).  It is quadratic, so
    its fixed point is a replicator-type equilibrium on theory space and need
    not be the maximum-likelihood theory.  That difference is the content of
    gate O: a Theory of Everything must be able to predict its own discovery.
    """

    hypotheses: tuple[str, ...]
    likelihood: tuple[float, ...]
    inference_kernel: tuple[tuple[float, ...], ...]
    prior: tuple[float, ...]
    fixed_point: tuple[float, ...]
    iterations: int
    kl_residual: float
    contraction_rate: float
    converged: bool
    maximum_likelihood: str
    reflective_choice: str
    likelihood_overridden: bool
    reflective_override: float
    exploration: float

    def as_dict(self) -> dict[str, object]:
        return {
            "hypotheses": list(self.hypotheses),
            "likelihood": list(self.likelihood),
            "inference_kernel": [list(row) for row in self.inference_kernel],
            "prior": list(self.prior),
            "fixed_point": list(self.fixed_point),
            "iterations": self.iterations,
            "kl_residual": self.kl_residual,
            "contraction_rate": self.contraction_rate,
            "converged": self.converged,
            "maximum_likelihood": self.maximum_likelihood,
            "reflective_choice": self.reflective_choice,
            "likelihood_overridden": self.likelihood_overridden,
            "reflective_override": self.reflective_override,
            "exploration": self.exploration,
        }


def _normalise(values: Sequence[float]) -> list[float]:
    total = sum(values)
    if total <= 0.0 or not math.isfinite(total):
        raise ReflectiveClosureError("the inference operator produced a non-normalisable measure")
    return [value / total for value in values]


def _kl(first: Sequence[float], second: Sequence[float]) -> float:
    total = 0.0
    for p, q in zip(first, second):
        if p <= 0.0:
            continue
        if q <= 0.0:
            return math.inf
        total += p * math.log(p / q)
    return total


def reflexive_bayes_fixed_point(
    hypotheses: Sequence[str],
    likelihood: Sequence[float],
    inference_kernel: Sequence[Sequence[float]],
    prior: Sequence[float] | None = None,
    iterations: int = 500,
    tolerance: float = 1e-13,
    exploration: float = 0.0,
) -> ReflexiveFixedPoint:
    names = tuple(hypotheses)
    size = len(names)
    if size < 2:
        raise ReflectiveClosureError("reflexive inference needs at least two competing hypotheses")
    if len(likelihood) != size or len(inference_kernel) != size:
        raise ReflectiveClosureError("likelihood and inference kernel must match the hypothesis set")
    for row in inference_kernel:
        if len(row) != size:
            raise ReflectiveClosureError("the inference kernel must be square")
        if any(value < 0.0 for value in row):
            raise ReflectiveClosureError("the inference kernel must be non-negative")
        if sum(row) <= 0.0:
            raise ReflectiveClosureError("every row of the inference kernel must carry mass")
    if any(value < 0.0 for value in likelihood) or sum(likelihood) <= 0.0:
        raise ReflectiveClosureError("the likelihood must be non-negative and not identically zero")
    if iterations < 2:
        raise ReflectiveClosureError("iterations must be at least 2")

    if not 0.0 <= exploration < 0.5:
        raise ReflectiveClosureError("exploration must lie in [0, 0.5)")
    uniform = [1.0 / size] * size
    current = _normalise(prior if prior is not None else [1.0] * size)
    residuals: list[float] = []
    converged = False
    used = 0
    for index in range(iterations):
        inference_pressure = [
            sum(current[source] * inference_kernel[source][target] for source in range(size))
            for target in range(size)
        ]
        candidate = [current[h] * likelihood[h] * inference_pressure[h] for h in range(size)]
        if any(value <= 0.0 for value in candidate):
            raise ReflectiveClosureError(
                "the reflexive operator annihilated a hypothesis; the fixed point is degenerate"
            )
        nxt = _normalise(candidate)
        if exploration > 0.0:
            # a real inference device is never perfectly self-confirming; the
            # floor keeps the operator positive, hence the fixed point interior
            nxt = _normalise(
                [(1.0 - exploration) * value + exploration * uniform[h] for h, value in enumerate(nxt)]
            )
        residual = _kl(nxt, current)
        residuals.append(residual)
        current = nxt
        used = index + 1
        if residual < tolerance:
            converged = True
            break
    contraction = (
        residuals[-1] / residuals[-2]
        if len(residuals) >= 2 and residuals[-2] > 0.0
        else float("nan")
    )
    maximum_likelihood = names[max(range(size), key=lambda h: likelihood[h])]
    reflective_choice = names[max(range(size), key=lambda h: current[h])]
    likelihood_normalised = _normalise(list(likelihood))
    override = 0.5 * sum(abs(current[h] - likelihood_normalised[h]) for h in range(size))
    return ReflexiveFixedPoint(
        hypotheses=names,
        likelihood=tuple(float(value) for value in likelihood),
        inference_kernel=tuple(tuple(float(value) for value in row) for row in inference_kernel),
        prior=tuple(_normalise(prior if prior is not None else [1.0] * size)),
        fixed_point=tuple(current),
        iterations=used,
        kl_residual=residuals[-1] if residuals else math.inf,
        contraction_rate=contraction,
        converged=converged,
        maximum_likelihood=maximum_likelihood,
        reflective_choice=reflective_choice,
        likelihood_overridden=maximum_likelihood != reflective_choice,
        reflective_override=override,
        exploration=exploration,
    )


# ---------------------------------------------------------------------------
# gate S -- coincidence budget (the numerology tax)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoincidenceBudget:
    """Chance probability that an invariant-to-constant match is a coincidence.

    Searching ``n_invariants`` values over ``n_candidates`` substrates and
    accepting a match inside a relative tolerance ``tolerance`` gives, for a
    target of order one,

        p_chance = 1 - (1 - 2 * tolerance) ** (n_invariants * n_candidates)

    A claim that a physical constant *equals* a combinatorial invariant is
    admissible only if ``p_chance`` stays below ``alpha`` **and** a mechanism is
    supplied.  Without this gate, a theory with a large enough invariant search
    space can "derive" any number it likes.
    """

    n_invariants: int
    n_candidates: int
    tolerance: float
    alpha: float
    p_chance: float
    admissible: bool
    mechanism_supplied: bool
    verdict: str

    def as_dict(self) -> dict[str, object]:
        return {
            "n_invariants": self.n_invariants,
            "n_candidates": self.n_candidates,
            "tolerance": self.tolerance,
            "alpha": self.alpha,
            "p_chance": self.p_chance,
            "admissible": self.admissible,
            "mechanism_supplied": self.mechanism_supplied,
            "verdict": self.verdict,
        }


def coincidence_budget(
    n_invariants: int,
    n_candidates: int,
    tolerance: float,
    mechanism_supplied: bool,
    alpha: float = 0.05,
) -> CoincidenceBudget:
    if n_invariants < 1 or n_candidates < 1:
        raise ReflectiveClosureError("the coincidence budget needs at least one invariant and candidate")
    if not 0.0 < tolerance < 1.0:
        raise ReflectiveClosureError("tolerance must be a relative tolerance in (0, 1)")
    if not 0.0 < alpha < 1.0:
        raise ReflectiveClosureError("alpha must lie in (0, 1)")
    trials = n_invariants * n_candidates
    p_chance = 1.0 - (1.0 - 2.0 * tolerance) ** trials
    admissible = p_chance < alpha and mechanism_supplied
    if not mechanism_supplied:
        verdict = "rejected_no_mechanism"
    elif p_chance >= alpha:
        verdict = "rejected_numerology"
    else:
        verdict = "admissible"
    return CoincidenceBudget(
        n_invariants=n_invariants,
        n_candidates=n_candidates,
        tolerance=tolerance,
        alpha=alpha,
        p_chance=p_chance,
        admissible=admissible,
        mechanism_supplied=mechanism_supplied,
        verdict=verdict,
    )


# ---------------------------------------------------------------------------
# the audit
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Gate:
    gate_id: str
    name: str
    requirement: str
    verdict: str  # PASS | CONDITIONAL | FAIL | REFUSED
    evidence: Mapping[str, object]
    kill_semantics: str


@dataclass(frozen=True)
class ToeAudit:
    candidate: str
    gates: tuple[Gate, ...]
    certified: bool
    verdict: str
    residual: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "candidate": self.candidate,
            "certified": self.certified,
            "verdict": self.verdict,
            "gates": [
                {
                    "gate_id": gate.gate_id,
                    "name": gate.name,
                    "requirement": gate.requirement,
                    "verdict": gate.verdict,
                    "evidence": dict(gate.evidence),
                    "kill_semantics": gate.kill_semantics,
                }
                for gate in self.gates
            ],
            "residual": dict(self.residual),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), indent=indent, sort_keys=False, default=str)


@dataclass(frozen=True)
class Falsifier:
    """One pre-registered falsifier with claim-level kill semantics.

    ``external`` distinguishes a test that a third party can run without this
    repository (an experiment, an observation, an independent computation) from
    an internal self-check.  Gate D requires at least one complete *external*
    falsifier: a definition whose only falsifiers are its own unit tests is not
    falsifiable in the physical sense.
    """

    observable: str
    prediction: str
    tolerance: str
    experiment: str
    horizon: str
    kill_semantics: str
    pre_registered: bool
    external: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "external": self.external,
            "observable": self.observable,
            "prediction": self.prediction,
            "tolerance": self.tolerance,
            "experiment": self.experiment,
            "horizon": self.horizon,
            "kill_semantics": self.kill_semantics,
            "pre_registered": self.pre_registered,
        }


def audit_rc_toe(
    candidate: str,
    substrate_report: AdmissibilityReport | None,
    declared_rung: int | None,
    fitted_parameters: Sequence[str],
    invariant_claims: Sequence[Mapping[str, object]],
    law_channels: Mapping[str, str],
    law_channel_notes: Mapping[str, str],
    fixed_point: ReflexiveFixedPoint | None,
    falsifiers: Sequence[Falsifier],
    axiom_bits: int,
    data_bits: int,
    omega: OmegaResult | None = None,
    requires_born_rule: bool = True,
) -> ToeAudit:
    """Score a candidate Theory of Everything against the five RC-ToE gates.

    The audit is intentionally hard to pass.  ``certified`` is ``True`` only if
    every gate is ``PASS``; a single ``REFUSED`` (a computation that declined to
    produce a number) already blocks certification.
    """

    gates: list[Gate] = []

    # ---- gate S ---------------------------------------------------------
    budgets = [
        coincidence_budget(
            n_invariants=int(claim.get("n_invariants", 0)) or 1,
            n_candidates=int(claim.get("n_candidates", 0)) or 1,
            tolerance=float(claim.get("tolerance", 0.0)),
            mechanism_supplied=bool(claim.get("mechanism", False)),
        )
        for claim in invariant_claims
    ] if invariant_claims else []
    s_pass = (not fitted_parameters) and bool(invariant_claims) and all(
        budget.admissible for budget in budgets
    )
    gates.append(
        Gate(
            gate_id="S",
            name="substance closure",
            requirement=(
                "no fitted parameter may remain, and every claimed constant must be a "
                "combinatorial invariant of the substrate that survives the coincidence budget"
            ),
            verdict="PASS" if s_pass else "FAIL",
            evidence={
                "fitted_parameters": list(fitted_parameters),
                "n_invariant_claims": len(invariant_claims),
                "coincidence_budgets": [budget.as_dict() for budget in budgets],
            },
            kill_semantics=(
                "if a parameter is later shown to be fitted rather than derived, gate S fails and "
                "every 'derivation' claim that used it is void, not merely uncertain"
            ),
        )
    )

    # ---- gate L ---------------------------------------------------------
    required_channels = {"gauge", "gravity", "fermion_generations", "cosmological_constant"}
    missing = sorted(required_channels - set(law_channels))
    unknown_status = sorted(
        channel for channel, status in law_channels.items() if status not in LAW_CHANNEL_STATUS
    )
    if unknown_status:
        raise ReflectiveClosureError(
            f"law channel status must be one of {sorted(LAW_CHANNEL_STATUS)}; got {unknown_status}"
        )
    derived = sorted(c for c, s in law_channels.items() if s in {"derived", "implemented"})
    open_channels = sorted(c for c, s in law_channels.items() if s in {"open_task", "hypothesis"})
    dead_channels = sorted(c for c, s in law_channels.items() if s in {"postulated", "rejected"})
    if missing or dead_channels:
        l_verdict = "FAIL"
    elif open_channels:
        l_verdict = "CONDITIONAL"
    else:
        l_verdict = "PASS"
    gates.append(
        Gate(
            gate_id="L",
            name="law closure",
            requirement=(
                "every interaction must be a named channel of the single rank flow "
                "A_{t+1} = cl(A_t | {x_t}); a term that is merely added to the flow fails the gate"
            ),
            verdict=l_verdict,
            evidence={
                "channels": dict(law_channels),
                "channel_notes": dict(law_channel_notes),
                "missing_channels": missing,
                "derived_channels": derived,
                "open_channels": open_channels,
                "postulated_or_rejected_channels": dead_channels,
            },
            kill_semantics=(
                "any interaction that has to be added to the rank flow as an extra term falsifies "
                "law closure and demotes the candidate to a framework"
            ),
        )
    )

    # ---- gate Q ---------------------------------------------------------
    if substrate_report is None or declared_rung is None:
        q_verdict = "REFUSED"
        q_evidence: dict[str, object] = {"reason": "no substrate report was supplied"}
    elif declared_rung not in LADDER:
        raise ReflectiveClosureError(f"declared rung {declared_rung} is not on the ladder")
    elif substrate_report.rung != declared_rung:
        q_verdict = "FAIL"
        q_evidence = {
            "declared_rung": declared_rung,
            "computed_rung": substrate_report.rung,
            "computed_label": substrate_report.rung_label,
        }
    else:
        born_ok = (not requires_born_rule) or substrate_report.born_ready
        q_verdict = "PASS" if born_ok else "CONDITIONAL"
        q_evidence = {
            "declared_rung": declared_rung,
            "computed_rung": substrate_report.rung,
            "computed_label": substrate_report.rung_label,
            "born_ready": substrate_report.born_ready,
            "requires_born_rule": requires_born_rule,
            "report": substrate_report.as_dict(),
        }
        if not born_ok:
            q_evidence["blocking_note"] = (
                "the substrate is not Born-ready: either it has no orthocomplementation "
                "(rung < 3) or its rank is below 3, where Gleason-type theorems do not apply. "
                "A Theory of Everything with quantum probability therefore requires an infinite "
                "substrate; every finite one we can enumerate is refused"
            )
    gates.append(
        Gate(
            gate_id="Q",
            name="logic closure",
            requirement=(
                "the substrate's rung on the admissibility ladder must be computed exactly and "
                "must equal the declared rung; a quantum theory needs rung 3"
            ),
            verdict=q_verdict,
            evidence=q_evidence,
            kill_semantics=(
                "if the substrate is shown to be rung 1 (no valuation at all), the candidate has no "
                "probability interpretation and every prediction derived from it is void"
            ),
        )
    )

    # ---- gate O ---------------------------------------------------------
    if fixed_point is None:
        o_verdict = "FAIL"
        o_evidence: dict[str, object] = {"reason": "no reflexive inference operator was supplied"}
    else:
        attractive = fixed_point.converged and 0.0 <= fixed_point.contraction_rate < 1.0
        o_verdict = "PASS" if attractive else "FAIL"
        o_evidence = {
            "converged": fixed_point.converged,
            "kl_residual": fixed_point.kl_residual,
            "contraction_rate": fixed_point.contraction_rate,
            "maximum_likelihood": fixed_point.maximum_likelihood,
            "reflective_choice": fixed_point.reflective_choice,
            "likelihood_overridden": fixed_point.likelihood_overridden,
            "reflective_override": fixed_point.reflective_override,
            "exploration": fixed_point.exploration,
            "fixed_point": list(fixed_point.fixed_point),
        }
    gates.append(
        Gate(
            gate_id="O",
            name="observer closure",
            requirement=(
                "the theory must be an attractive fixed point of its own inference operator, i.e. "
                "it must predict the process by which it is inferred"
            ),
            verdict=o_verdict,
            evidence=o_evidence,
            kill_semantics=(
                "if the reflexive fixed point selects a different theory than the candidate, the "
                "candidate is self-refuting and must be abandoned, not adjusted"
            ),
        )
    )

    # ---- gate D ---------------------------------------------------------
    def is_complete(falsifier: Falsifier) -> bool:
        return bool(
            falsifier.pre_registered
            and falsifier.observable
            and falsifier.prediction
            and falsifier.tolerance
            and falsifier.experiment
            and falsifier.horizon
            and falsifier.kill_semantics
        )

    complete = [falsifier for falsifier in falsifiers if is_complete(falsifier)]
    complete_external = [falsifier for falsifier in complete if falsifier.external]
    mdl_ok = axiom_bits > 0 and data_bits > 0 and axiom_bits < data_bits
    if complete_external and mdl_ok:
        d_verdict = "PASS"
    elif complete or mdl_ok:
        d_verdict = "CONDITIONAL"
    else:
        d_verdict = "FAIL"
    gates.append(
        Gate(
            gate_id="D",
            name="decision closure",
            requirement=(
                "at least one fully pre-registered falsifier with claim-level kill semantics, and "
                "the axiom system must be shorter than the data it explains (MDL)"
            ),
            verdict=d_verdict,
            evidence={
                "n_falsifiers": len(falsifiers),
                "n_complete_falsifiers": len(complete),
                "n_complete_external_falsifiers": len(complete_external),
                "axiom_bits": axiom_bits,
                "data_bits": data_bits,
                "mdl_satisfied": mdl_ok,
                "falsifiers": [falsifier.as_dict() for falsifier in falsifiers],
            },
            kill_semantics=(
                "a violated falsifier kills the claim named in its kill_semantics field; the rest of "
                "the theory survives only if it does not depend on that claim"
            ),
        )
    )

    verdicts = [gate.verdict for gate in gates]
    certified = all(verdict == "PASS" for verdict in verdicts)
    if certified:
        verdict = "CERTIFIED_AS_TOE"
    elif any(verdict == "REFUSED" for verdict in verdicts):
        verdict = "REFUSED_MISSING_COMPUTATION"
    else:
        verdict = "FRAMEWORK_NOT_TOE"

    residual: dict[str, object] = {
        "definition": "certified lower bound on the sector the candidate cannot decide",
        "omega": omega.as_dict() if omega is not None else None,
        "n_gates_passed": sum(1 for verdict in verdicts if verdict == "PASS"),
        "n_gates_total": len(verdicts),
        "blocking_gates": [gate.gate_id for gate in gates if gate.verdict not in {"PASS"}],
    }

    return ToeAudit(
        candidate=candidate,
        gates=tuple(gates),
        certified=certified,
        verdict=verdict,
        residual=residual,
    )
