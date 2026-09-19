"""RC-ToE combinatorial kernel: closure operators, matroids, lattices of flats.

This module implements the substrate of the **Reflective Closure Theory of
Everything** (RC-ToE) definition in
``docs/DEFINICJA-TEORII-WSZYSTKIEGO.md``.

Design rules (identical to the isolated IFT-EGR closure module):

* pure standard library -- no NumPy, no JAX, no network, no fitted constants;
* exact integer/rational arithmetic wherever a closed form exists;
* fail-closed: every routine that would silently extrapolate beyond its
  validated domain raises :class:`ToeKernelError` instead of returning a
  plausible-looking number;
* the module claims **mathematics only**.  Nothing here derives a Standard
  Model coupling, a cosmological constant, or a particle mass.  The physical
  dictionary lives in the document and every entry there is classified as
  ``established``, ``theorem_of_the_dictionary``, ``project_hypothesis`` or
  ``open_task``.

Central objects
---------------
``E``           finite set of *facts* (events, propositions about the world);
``cl``          closure operator on ``E`` (extensive, monotone, idempotent,
                plus the exchange axiom => a **matroid** ``M``);
``L(M)``        lattice of closed sets (*flats*) = the pre-geometric spacetime;
``r``           rank function = number of independent facts;
``C(A)``        constraint charge ``|A| - r(A)`` = redundancy of facts;
``sigma``       a valuation (generalised probability) on ``L(M)``.

Every interaction in the RC-ToE dictionary is a channel of one object, the
rank function; every constant is an invariant of it (Tutte polynomial,
Whitney numbers, Moebius values, automorphism-group order, beta invariant).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations, permutations, product
import math
import random
from typing import Iterable, Iterator, Mapping, Sequence

__all__ = [
    "ToeKernelError",
    "Matroid",
    "Lattice",
    "ValuationPolytope",
    "RankFlowStep",
    "SpectralDimensionCurve",
    "uniform_matroid",
    "free_matroid",
    "matroid_from_gf2_columns",
    "enumerate_matroids",
    "spin10_even_parity_weights",
    "spin10_weyl_group_order",
    "spin10_parity_code_matroid",
    "subspace_matroid_gf2",
    "fano_matroid",
]

_MAX_BRUTE_FORCE_ELEMENTS = 12
_MAX_STATE_LATTICE_ELEMENTS = 40
_MAX_SPECTRAL_ELEMENTS = 4000
_MAX_ORTHO_ELEMENTS = 20


class ToeKernelError(ValueError):
    """Raised when a kernel computation would leave its validated domain."""


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _subsets(ground: Sequence[int]) -> Iterator[frozenset[int]]:
    for size in range(len(ground) + 1):
        for combo in combinations(ground, size):
            yield frozenset(combo)


def _guard_brute_force(size: int, what: str) -> None:
    if size > _MAX_BRUTE_FORCE_ELEMENTS:
        raise ToeKernelError(
            f"{what} requires exhaustive enumeration over 2**{size} subsets; "
            f"the kernel fails closed above {_MAX_BRUTE_FORCE_ELEMENTS} elements"
        )


# ---------------------------------------------------------------------------
# matroids
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Matroid:
    """A finite matroid given by its ground set and its circuit family.

    ``circuits`` must satisfy the circuit axioms (no circuit contains another,
    and the circuit-elimination property).  :meth:`validate` checks the weaker
    but decisive conditions the kernel relies on; the exchange axiom itself is
    verified indirectly through the rank axioms in :meth:`validate_rank_axioms`.
    """

    name: str
    ground: tuple[int, ...]
    circuits: tuple[frozenset[int], ...]

    # -- construction ----------------------------------------------------

    @staticmethod
    def from_circuits(name: str, ground: Iterable[int], circuits: Iterable[Iterable[int]]) -> "Matroid":
        ground_tuple = tuple(sorted(set(ground)))
        circuit_tuple = tuple(sorted({frozenset(c) for c in circuits}, key=_circuit_sort_key))
        matroid = Matroid(name=name, ground=ground_tuple, circuits=circuit_tuple)
        matroid.validate()
        return matroid

    @staticmethod
    def from_gf2_columns(name: str, columns: Sequence[Sequence[int]]) -> "Matroid":
        """Build the vector matroid of columns over GF(2).

        Circuits are the minimal linearly dependent column sets.  Fails closed
        above :data:`_MAX_BRUTE_FORCE_ELEMENTS` columns.
        """

        size = len(columns)
        _guard_brute_force(size, "matroid_from_gf2_columns")
        if size == 0:
            raise ToeKernelError("at least one column is required")
        width = len(columns[0])
        vectors = []
        for index, column in enumerate(columns):
            if len(column) != width:
                raise ToeKernelError(f"column {index} has inconsistent width")
            bits = tuple(int(bit) % 2 for bit in column)
            if any(bit not in (0, 1) for bit in bits):
                raise ToeKernelError(f"column {index} is not a GF(2) vector")
            vectors.append(bits)
        ground = tuple(range(size))
        circuits = []
        for card in range(1, size + 1):
            for combo in combinations(ground, card):
                if _gf2_rank([vectors[i] for i in combo]) < card:
                    circuits.append(frozenset(combo))
        # keep only minimal dependent sets
        minimal = [c for c in circuits if not any(d < c for d in circuits)]
        return Matroid.from_circuits(name, ground, minimal)

    # -- validation ------------------------------------------------------

    def validate(self) -> None:
        if not self.ground:
            raise ToeKernelError("the ground set must be non-empty")
        if len(set(self.ground)) != len(self.ground):
            raise ToeKernelError("the ground set must not contain duplicates")
        for circuit in self.circuits:
            if not circuit:
                continue
            if not circuit <= set(self.ground):
                raise ToeKernelError(f"circuit {sorted(circuit)} leaves the ground set")
        for first, second in combinations(self.circuits, 2):
            if first < second:
                raise ToeKernelError(
                    f"circuit {sorted(first)} is properly contained in {sorted(second)}"
                )

    def validate_rank_axioms(self) -> bool:
        """Check R0-R3 for the derived rank function (implies the exchange axiom)."""

        _guard_brute_force(len(self.ground), "validate_rank_axioms")
        rank_cache: dict[frozenset[int], int] = {}
        for subset in _subsets(self.ground):
            rank_cache[subset] = self.rank(subset)
        for subset, value in rank_cache.items():
            if value < 0 or value > len(subset):
                return False
        for first, second in product(rank_cache, repeat=2):
            if not first <= second:
                continue
            if rank_cache[first] > rank_cache[second]:
                return False
            if second - first and rank_cache[second] - rank_cache[first] > len(second - first):
                return False
        for first, second in product(rank_cache, repeat=2):
            if rank_cache[first] + rank_cache[second] < rank_cache[first | second] + rank_cache[first & second]:
                return False
        return True

    # -- core operations -------------------------------------------------

    def is_independent(self, subset: Iterable[int]) -> bool:
        wanted = frozenset(subset)
        if not wanted <= set(self.ground):
            raise ToeKernelError("subset leaves the ground set")
        return not any(circuit <= wanted for circuit in self.circuits)

    def rank(self, subset: Iterable[int]) -> int:
        """Rank via greedy augmentation -- maximal independent subsets all
        have the same size in a matroid, so greedy is exact."""

        wanted = sorted(frozenset(subset))
        chosen: list[int] = []
        for element in wanted:
            if self.is_independent(chosen + [element]):
                chosen.append(element)
        return len(chosen)

    def closure(self, subset: Iterable[int]) -> frozenset[int]:
        base = frozenset(subset)
        if not base <= set(self.ground):
            raise ToeKernelError("subset leaves the ground set")
        rank = self.rank(base)
        spanned = set(base)
        for element in self.ground:
            if element in spanned:
                continue
            if self.rank(base | {element}) == rank:
                spanned.add(element)
        return frozenset(spanned)

    def loops(self) -> tuple[int, ...]:
        return tuple(element for element in self.ground if element in self.closure(frozenset()))

    def parallel_classes(self) -> tuple[tuple[int, ...], ...]:
        groups: dict[frozenset[int], list[int]] = {}
        for element in self.ground:
            if self.rank({element}) == 0:
                continue
            groups.setdefault(self.closure({element}), []).append(element)
        return tuple(tuple(sorted(group)) for group in groups.values() if len(group) > 1)

    def full_rank(self) -> int:
        return self.rank(self.ground)

    # -- flats and lattice ----------------------------------------------

    def flats(self) -> tuple[frozenset[int], ...]:
        _guard_brute_force(len(self.ground), "flats")
        return tuple(
            sorted(
                (subset for subset in _subsets(self.ground) if self.closure(subset) == subset),
                key=lambda flat: (len(flat), sorted(flat)),
            )
        )

    def flat_lattice(self) -> "Lattice":
        return Lattice.from_flats(self)

    # -- constraint charge and dependence spectrum -----------------------

    def constraint_charge(self, subset: Iterable[int]) -> int:
        """C(A) = |A| - r(A): the number of constraints among the facts of A."""

        wanted = frozenset(subset)
        return len(wanted) - self.rank(wanted)

    def dependence_spectrum(self, max_card: int | None = None) -> dict[int, Fraction]:
        """delta_k = fraction of k-subsets that are dependent.

        ``delta_3`` is the **interaction density** of the RC-ToE dictionary:
        ``delta_3 = 0`` if and only if no three facts constrain each other,
        which (theorem T1 below) is equivalent to the flat lattice being
        distributive, i.e. to classical logic.
        """

        limit = max_card if max_card is not None else min(len(self.ground), 5)
        if limit > 5:
            raise ToeKernelError("dependence_spectrum fails closed above k = 5")
        spectrum: dict[int, Fraction] = {}
        for card in range(1, limit + 1):
            subsets = list(combinations(self.ground, card))
            if not subsets:
                spectrum[card] = Fraction(0)
                continue
            dependent = sum(0 if self.is_independent(subset) else 1 for subset in subsets)
            spectrum[card] = Fraction(dependent, len(subsets))
        return spectrum

    @property
    def interaction_density(self) -> Fraction:
        return self.dependence_spectrum(3)[3]

    def is_free_up_to_parallelism(self) -> bool:
        """True iff no circuit has three or more elements."""

        return all(len(circuit) < 3 for circuit in self.circuits)

    def lowest_constraint_order(self) -> int:
        """Size of the smallest circuit of length >= 3, or 0 when there is none.

        This is the invariant that governs theorem T1, *not* ``delta_3``: the
        kernel computes U_{3,4} with ``delta_3 = 0`` (no dependent triple) whose
        flat lattice is nevertheless non-distributive, because its single
        circuit has four elements.  A density of dependent triples can therefore
        vanish while the substrate is genuinely quantum; the lowest constraint
        order cannot.
        """

        orders = [len(circuit) for circuit in self.circuits if len(circuit) >= 3]
        return min(orders) if orders else 0

    def constraint_profile(self, max_card: int = 6) -> dict[int, int]:
        """Number of dependent k-subsets, for k = 1..max_card."""

        if len(self.ground) < max_card:
            max_card = len(self.ground)
        profile = {}
        for card in range(1, max_card + 1):
            profile[card] = sum(
                1 for combo in combinations(self.ground, card) if not self.is_independent(combo)
            )
        return profile

    # -- automorphisms ---------------------------------------------------

    def automorphisms(self, limit: int | None = None) -> tuple[tuple[int, ...], ...]:
        """Permutations of the ground set preserving the circuit family."""

        _guard_brute_force(len(self.ground), "automorphisms")
        if limit is not None and limit < len(self.ground):
            raise ToeKernelError("the automorphism search cannot prune below the ground size")
        ground = self.ground
        circuit_sets = [frozenset(circuit) for circuit in self.circuits]
        found = []
        for permutation in permutations(ground):
            mapping = dict(zip(ground, permutation))
            images = {frozenset(mapping[element] for element in circuit) for circuit in circuit_sets}
            if images == set(circuit_sets):
                found.append(permutation)
        return tuple(found)

    def automorphism_group_order(self) -> int:
        return len(self.automorphisms())

    # -- polynomials -----------------------------------------------------

    def tutte_polynomial(self) -> dict[tuple[int, int], int]:
        """Exact Tutte polynomial T_M(x, y) = sum_A (x-1)^(r-r(A)) (y-1)^(|A|-r(A))."""

        _guard_brute_force(len(self.ground), "tutte_polynomial")
        full_rank = self.full_rank()
        coefficients: dict[tuple[int, int], int] = {}
        for subset in _subsets(self.ground):
            rank = self.rank(subset)
            internal = full_rank - rank
            external = len(subset) - rank
            key = (internal, external)
            coefficients[key] = coefficients.get(key, 0) + 1
        return {key: value for key, value in sorted(coefficients.items()) if value}

    def characteristic_polynomial(self) -> dict[int, int]:
        """chi_M(q) = sum_{F flat} mu(0, F) q^(r - r(F)) as exact coefficients."""

        lattice = self.flat_lattice()
        top_rank = self.full_rank()
        coefficients: dict[int, int] = {}
        bottom = frozenset()
        for flat in lattice.elements:
            value = lattice.mobius(bottom, flat)
            degree = top_rank - lattice.rank_of[flat]
            coefficients[degree] = coefficients.get(degree, 0) + value
        return {degree: value for degree, value in sorted(coefficients.items(), reverse=True) if value}

    def beta_invariant(self) -> int:
        """Crapo's beta invariant, convention beta = (-1)^(r+1) chi'(1).

        Reproduces the textbook values beta(U_2,4) = 2, beta(U_1,2) = 1 and
        beta(free) = 0, and is positive exactly on connected matroids.  It is
        used in RC-ToE as a **connectivity certificate** of the substrate.
        """

        coefficients = self.characteristic_polynomial()
        derivative_at_one = sum(degree * value for degree, value in coefficients.items())
        rank = self.full_rank()
        beta = (-1) ** (rank + 1) * derivative_at_one
        if beta < 0:
            raise ToeKernelError(f"negative beta invariant for {self.name}: sign convention broken")
        return beta

    def invariant_vector(self) -> dict[str, int]:
        """The finite, exactly computable invariant signature of a substrate.

        Gate S of the RC-ToE definition (substance closure) is executed against
        this vector: a candidate ToE must map *these* numbers onto the observed
        dimensionless constants with zero fitted parameters.
        """

        spectrum = self.dependence_spectrum(5)
        tutte = self.tutte_polynomial()
        lattice = self.flat_lattice()
        bottom = frozenset()
        return {
            "n_elements": len(self.ground),
            "rank": self.full_rank(),
            "n_circuits": len(self.circuits),
            "min_circuit_size": min((len(c) for c in self.circuits), default=0),
            "max_circuit_size": max((len(c) for c in self.circuits), default=0),
            "n_flats": len(lattice.elements),
            "mobius_top": lattice.mobius(bottom, lattice.top),
            "chi_at_0": self.characteristic_polynomial().get(0, 0),
            "beta": self.beta_invariant(),
            "n_bases": self.count_bases(),
            "n_independent_sets": self.count_independent_sets(),
            "n_spanning_sets": sum(coeff for (i, _), coeff in tutte.items() if i == 0),
            "tutte_at_2_2": sum(tutte.values()),
            "automorphism_group_order": self.automorphism_group_order(),
            "n_parallel_classes": len(self.parallel_classes()),
            "n_loops": len(self.loops()),
            "delta_2_numerator": spectrum[2].numerator,
            "delta_2_denominator": spectrum[2].denominator,
            "delta_3_numerator": spectrum[3].numerator,
            "delta_3_denominator": spectrum[3].denominator,
            "distributive": int(lattice.is_distributive()),
            "modular": int(lattice.is_modular()),
        }

    def count_bases(self) -> int:
        _guard_brute_force(len(self.ground), "count_bases")
        rank = self.full_rank()
        return sum(
            1 for combo in combinations(self.ground, rank) if self.is_independent(combo)
        )

    def count_independent_sets(self) -> int:
        _guard_brute_force(len(self.ground), "count_independent_sets")
        return sum(1 for subset in _subsets(self.ground) if self.is_independent(subset))

    def frontier(self, actualized: Iterable[int]) -> tuple[int, ...]:
        """Facts not yet forced: the only place where the rank flow can branch."""

        closed = self.closure(actualized)
        return tuple(element for element in self.ground if element not in closed)

    def rank_flow(self, choices: Sequence[int], seed: Iterable[int] = ()) -> list["RankFlowStep"]:
        """A_{t+1} = cl(A_t | {x_t}) with x_t drawn from the frontier.

        This is the single dynamical law of the RC-ToE substrate: no action, no
        metric, no coupling constant.  A choice outside the frontier is an
        error -- the flow fails closed rather than silently accepting an
        already-forced fact.
        """

        actualized = self.closure(seed)
        trajectory = [
            RankFlowStep(
                step=0,
                actualized=actualized,
                forced=frozenset(),
                frontier=self.frontier(actualized),
                constraint_charge=self.constraint_charge(actualized),
                rank=self.rank(actualized),
            )
        ]
        for index, choice in enumerate(choices, start=1):
            if choice not in self.ground:
                raise ToeKernelError(f"choice {choice} is not a fact of {self.name}")
            if choice not in self.frontier(actualized):
                raise ToeKernelError(
                    f"step {index}: fact {choice} is already forced by the closure"
                )
            previous = actualized
            actualized = self.closure(previous | {choice})
            trajectory.append(
                RankFlowStep(
                    step=index,
                    actualized=actualized,
                    forced=actualized - previous - {choice},
                    frontier=self.frontier(actualized),
                    constraint_charge=self.constraint_charge(actualized),
                    rank=self.rank(actualized),
                )
            )
        return trajectory


@dataclass(frozen=True)
class RankFlowStep:
    step: int
    actualized: frozenset[int]
    forced: frozenset[int]
    frontier: tuple[int, ...]
    constraint_charge: int
    rank: int

    @property
    def forced_ratio(self) -> Fraction:
        if not self.actualized:
            return Fraction(0)
        return Fraction(len(self.actualized) - len(self.frontier), len(self.actualized))


def _circuit_sort_key(circuit: frozenset[int]) -> tuple[int, tuple[int, ...]]:
    return (len(circuit), tuple(sorted(circuit)))


def _gf2_rank(vectors: Sequence[Sequence[int]]) -> int:
    rows = [list(vector) for vector in vectors]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = None
        for index in range(rank, len(rows)):
            if rows[index][column]:
                pivot = index
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index][column]:
                rows[index] = [(a + b) % 2 for a, b in zip(rows[index], rows[rank])]
        rank += 1
    return rank


def uniform_matroid(rank: int, size: int, name: str | None = None) -> Matroid:
    """U_{r,n}: every (r+1)-subset is a circuit."""

    if not 0 <= rank <= size:
        raise ToeKernelError("uniform matroid requires 0 <= r <= n")
    _guard_brute_force(size, "uniform_matroid")
    ground = tuple(range(size))
    circuits = [frozenset(combo) for combo in combinations(ground, rank + 1)]
    return Matroid.from_circuits(name or f"U_{rank}_{size}", ground, circuits)


def free_matroid(size: int, name: str | None = None) -> Matroid:
    """The Boolean matroid: no constraints at all, hence no law at all."""

    if size < 1:
        raise ToeKernelError("the free matroid needs at least one element")
    return Matroid.from_circuits(name or f"F_{size}", tuple(range(size)), [])


def matroid_from_gf2_columns(name: str, columns: Sequence[Sequence[int]]) -> Matroid:
    return Matroid.from_gf2_columns(name, columns)


def enumerate_matroids(size: int, max_rank: int | None = None) -> tuple[Matroid, ...]:
    """Exhaustive enumeration of every matroid on ``size`` labelled elements.

    Rank functions are grown subset by subset in increasing cardinality and
    pruned by R0 (bounds), R1 (monotonicity), R2 (unit increase) and R3
    (submodularity).  R0-R3 are equivalent to the exchange axiom, so every
    survivor is a matroid and every matroid is reached.  Fails closed above
    ``size = 5`` because the search is exhaustive.
    """

    if size < 1 or size > 5:
        raise ToeKernelError("enumerate_matroids is exhaustive and fails closed above 5 elements")
    ground = tuple(range(size))
    subsets = sorted(_subsets(ground), key=lambda s: (len(s), sorted(s)))
    index_of = {subset: position for position, subset in enumerate(subsets)}
    upper_rank = max_rank if max_rank is not None else size

    results: list[Matroid] = []
    assignment: list[int | None] = [None] * len(subsets)
    assignment[index_of[frozenset()]] = 0

    def consistent(position: int, value: int) -> bool:
        subset = subsets[position]
        if value < 0 or value > min(len(subset), upper_rank):
            return False
        for other_position in range(position):
            other_value = assignment[other_position]
            if other_value is None:
                continue
            other = subsets[other_position]
            if other <= subset:
                if other_value > value:
                    return False
                if value - other_value > len(subset - other):
                    return False
            if subset <= other:
                if value > other_value:
                    return False
                if other_value - value > len(other - subset):
                    return False
            union_value = assignment[index_of[subset | other]]
            intersection_value = assignment[index_of[subset & other]]
            if union_value is None or intersection_value is None:
                continue
            if value + other_value < union_value + intersection_value:
                return False
        # submodularity for every pair of proper subsets whose union *is* the
        # subset being assigned: both members of the pair are already known, but
        # their union is the new value, so the generic loop above cannot see it
        proper = [
            subsets[other_position]
            for other_position in range(position)
            if assignment[other_position] is not None and subsets[other_position] < subset
        ]
        for first, second in combinations(proper, 2):
            if first | second != subset:
                continue
            if (
                assignment[index_of[first]] + assignment[index_of[second]]
                < value + assignment[index_of[first & second]]
            ):
                return False
        return True

    def circuits_from_ranks() -> tuple[frozenset[int], ...]:
        circuits = []
        for subset in subsets:
            value = assignment[index_of[subset]]
            if value is None or value == len(subset):
                continue
            if all(
                (assignment[index_of[subset - {element}]] or 0) == len(subset) - 1
                for element in subset
            ):
                circuits.append(subset)
        return tuple(sorted(circuits, key=_circuit_sort_key))

    def recurse(position: int) -> None:
        while position < len(subsets) and assignment[position] is not None:
            position += 1
        if position >= len(subsets):
            circuits = circuits_from_ranks()
            candidate = Matroid(f"M{len(results)}", ground, circuits)
            candidate.validate()
            if not candidate.validate_rank_axioms():
                raise ToeKernelError(
                    f"enumeration produced a rank function violating R0-R3: {sorted(circuits)}"
                )
            results.append(candidate)
            return
        subset = subsets[position]
        lower = 0
        for element in subset:
            smaller = assignment[index_of[subset - {element}]]
            if smaller is not None:
                lower = max(lower, smaller)
        for value in range(lower, min(len(subset), upper_rank) + 1):
            if consistent(position, value):
                assignment[position] = value
                recurse(position + 1)
                assignment[position] = None

    recurse(0)
    unique: dict[tuple[frozenset[int], ...], Matroid] = {}
    for matroid in results:
        key = tuple(sorted(matroid.circuits, key=_circuit_sort_key))
        if key in unique:
            raise ToeKernelError("enumeration produced duplicate matroids")
        unique[key] = matroid
    return tuple(unique.values())


# ---------------------------------------------------------------------------
# lattices
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Lattice:
    """The lattice of flats L(M): RC-ToE's pre-geometric spacetime."""

    name: str
    elements: tuple[frozenset[int], ...]
    covers: tuple[tuple[frozenset[int], frozenset[int]], ...]
    rank_of: Mapping[frozenset[int], int] = field(compare=False, default=None)  # type: ignore[assignment]

    @staticmethod
    def from_flats(matroid: Matroid) -> "Lattice":
        flats = matroid.flats()
        covers = []
        for lower, upper in combinations(flats, 2):
            if not lower < upper:
                continue
            if any(lower < middle < upper for middle in flats):
                continue
            covers.append((lower, upper))
        rank_of = {flat: matroid.rank(flat) for flat in flats}
        return Lattice(name=f"L({matroid.name})", elements=flats, covers=tuple(covers), rank_of=rank_of)

    # -- order -----------------------------------------------------------

    @property
    def bottom(self) -> frozenset[int]:
        return min(self.elements, key=len)

    @property
    def top(self) -> frozenset[int]:
        return max(self.elements, key=len)

    def meet(self, first: frozenset[int], second: frozenset[int]) -> frozenset[int]:
        return first & second

    def join(self, first: frozenset[int], second: frozenset[int]) -> frozenset[int]:
        union = first | second
        candidates = [element for element in self.elements if union <= element]
        if not candidates:
            raise ToeKernelError(f"{self.name}: no upper bound for {sorted(union)}")
        return min(candidates, key=lambda flat: (len(flat), sorted(flat)))

    def hasse_adjacency(self) -> dict[frozenset[int], tuple[frozenset[int], ...]]:
        adjacency: dict[frozenset[int], list[frozenset[int]]] = {element: [] for element in self.elements}
        for lower, upper in self.covers:
            adjacency[lower].append(upper)
            adjacency[upper].append(lower)
        return {element: tuple(sorted(neighbours, key=len)) for element, neighbours in adjacency.items()}

    # -- Moebius ---------------------------------------------------------

    def mobius(self, lower: frozenset[int], upper: frozenset[int]) -> int:
        if not lower <= upper:
            raise ToeKernelError("mobius requires lower <= upper")
        interval = [element for element in self.elements if lower <= element <= upper]
        interval.sort(key=lambda flat: (len(flat), sorted(flat)))
        values: dict[frozenset[int], int] = {}
        for element in interval:
            total = 0
            for smaller in interval:
                if smaller < element:
                    total += values[smaller]
            values[element] = 1 if element == lower else -total
        return values[upper]

    # -- structure tests -------------------------------------------------

    def is_modular(self) -> bool:
        """Rank-modularity: r(x) + r(y) = r(meet) + r(join) for all pairs."""

        for first, second in product(self.elements, repeat=2):
            if self.rank_of[first] + self.rank_of[second] != (
                self.rank_of[self.meet(first, second)] + self.rank_of[self.join(first, second)]
            ):
                return False
        return True

    def is_distributive(self) -> bool:
        for first, second, third in product(self.elements, repeat=3):
            if self.meet(first, self.join(second, third)) != self.join(
                self.meet(first, second), self.meet(first, third)
            ):
                return False
        return True

    def distributive_defect_witnesses(self, limit: int = 5) -> list[tuple[frozenset[int], ...]]:
        witnesses = []
        for first, second, third in product(self.elements, repeat=3):
            left = self.meet(first, self.join(second, third))
            right = self.join(self.meet(first, second), self.meet(first, third))
            if left != right:
                witnesses.append((first, second, third))
                if len(witnesses) >= limit:
                    break
        return witnesses

    def distributive_quotient(self) -> tuple[int, tuple[frozenset[int], ...]]:
        """The classical limit: quotient by the congruence generated by all
        distributivity failures.

        Returns ``(n_blocks, blocks)``.  The construction is the reflector from
        lattices to distributive lattices, so the classical limit of a
        substrate is *canonical* -- it is not an ``hbar -> 0`` extrapolation.
        For a Boolean lattice the quotient is the lattice itself; for the
        diamond M3 it collapses to the two-element lattice (one classical bit).
        """

        blocks: dict[frozenset[int], frozenset[int]] = {element: frozenset([element]) for element in self.elements}

        def find(element: frozenset[int]) -> frozenset[int]:
            return blocks[element]

        def merge(first: frozenset[int], second: frozenset[int]) -> None:
            left, right = find(first), find(second)
            if left == right:
                return
            merged = left | right
            for element in left | right:
                blocks[element] = merged

        changed = True
        while changed:
            changed = False
            for first, second, third in product(self.elements, repeat=3):
                left = self.meet(first, self.join(second, third))
                right = self.join(self.meet(first, second), self.meet(first, third))
                if find(left) != find(right):
                    merge(left, right)
                    changed = True
        grouped: dict[frozenset[int], frozenset[int]] = {}
        for element in self.elements:
            grouped[find(element)] = find(element)
        return (len(grouped), tuple(sorted(grouped, key=lambda block: (len(block), sorted(block)))))

    def classicality_defect(self) -> float:
        """kappa = log|L| / log|L/theta_D|, >= 1, infinite when the quotient is
        trivial.  kappa = 1 exactly for distributive (lawless) substrates."""

        blocks, _ = self.distributive_quotient()
        if blocks <= 1:
            raise ToeKernelError(
                f"{self.name}: the distributive quotient is trivial; classicality defect diverges"
            )
        return math.log(len(self.elements)) / math.log(blocks)

    # -- states ----------------------------------------------------------

    def valuation_equations(self) -> tuple[list[list[Fraction]], list[Fraction], list[frozenset[int]]]:
        """Exact linear system ``A sigma = b`` encoding the valuation identity.

        ``sigma`` is restricted to the non-trivial lattice elements;
        ``sigma(bottom) = 0`` and ``sigma(top) = 1`` are normalisation, and the
        box ``0 <= sigma <= 1`` is imposed separately.  Duplicate rows are
        removed so the solver stays exact and small.
        """

        if len(self.elements) > _MAX_STATE_LATTICE_ELEMENTS:
            raise ToeKernelError(
                f"valuation_equations fails closed above {_MAX_STATE_LATTICE_ELEMENTS} lattice elements"
            )
        trivial = {self.bottom, self.top}
        variables = [element for element in self.elements if element not in trivial]
        index = {element: position for position, element in enumerate(variables)}
        dimension = len(variables)

        def coefficient_vector(element: frozenset[int]) -> list[Fraction]:
            vector = [Fraction(0)] * dimension
            if element in trivial:
                return vector
            vector[index[element]] = Fraction(1)
            return vector

        seen: set[tuple[tuple[Fraction, ...], Fraction]] = set()
        rows: list[list[Fraction]] = []
        rhs: list[Fraction] = []
        for first, second in product(self.elements, repeat=2):
            join = self.join(first, second)
            meet = self.meet(first, second)
            vector = [
                coefficient_vector(join)[k]
                + coefficient_vector(meet)[k]
                - coefficient_vector(first)[k]
                - coefficient_vector(second)[k]
                for k in range(dimension)
            ]
            # sigma(x) = [x == top] + coef(x) . sigma, hence the right-hand side
            # collects the normalisation of the three top occurrences
            constant = Fraction(0)
            if first == self.top:
                constant += Fraction(1)
            if second == self.top:
                constant += Fraction(1)
            if join == self.top:
                constant -= Fraction(1)
            if meet == self.top:
                constant -= Fraction(1)
            if not any(vector) and constant == 0:
                continue
            key = (tuple(vector), constant)
            if key in seen:
                continue
            seen.add(key)
            rows.append(vector)
            rhs.append(constant)
        return rows, rhs, variables

    def valuation_polytope(self, max_vertex_search_rank: int = 3) -> "ValuationPolytope":
        """Exact state space of the substrate: valuations on the flat lattice.

        A valuation obeys ``sigma(a v b) + sigma(a ^ b) = sigma(a) + sigma(b)``.
        On a Boolean lattice this is classical probability; on a non-distributive
        lattice it is a generalised probability.  Three outcomes are possible
        and all three are physically meaningful:

        ``no``            the equality system is inconsistent -- the substrate
                          admits **no** probability measure at all;
        ``yes``           at least one state exists; ``vertices`` lists the exact
                          extreme states whenever the solution space has
                          dimension <= ``max_vertex_search_rank``;
        ``undetermined``  states exist in the affine solution space but the
                          vertex search is refused (fail closed) because it
                          would be exponential.
        """

        rows, rhs, variables = self.valuation_equations()
        dimension = len(variables)
        status, particular, basis = _solve_linear(rows, rhs, dimension)
        if status == "empty" or dimension == 0:
            feasible = "no" if status == "empty" else "undetermined"
            return ValuationPolytope(
                lattice_name=self.name,
                n_variables=dimension,
                n_equalities=len(rows),
                vertices=(),
                affine_dimension=-1 if status == "empty" else 0,
                is_boolean=self.is_distributive(),
                feasible=feasible,
                witness=None,
                solution_rank=dimension - len(basis),
            )
        free_dimension = len(basis)

        def in_box(point: Sequence[Fraction]) -> bool:
            return all(Fraction(0) <= value <= Fraction(1) for value in point)

        if free_dimension == 0:
            if not in_box(particular):
                return ValuationPolytope(
                    lattice_name=self.name,
                    n_variables=dimension,
                    n_equalities=len(rows),
                    vertices=(),
                    affine_dimension=-1,
                    is_boolean=self.is_distributive(),
                    feasible="no",
                    witness=None,
                    solution_rank=dimension,
                )
            return ValuationPolytope(
                lattice_name=self.name,
                n_variables=dimension,
                n_equalities=len(rows),
                vertices=(tuple(particular),),
                affine_dimension=0,
                is_boolean=self.is_distributive(),
                feasible="yes",
                witness=tuple(particular),
                solution_rank=dimension,
            )
        if free_dimension > max_vertex_search_rank:
            witness = _search_feasible_point(particular, basis, dimension, free_dimension)
            return ValuationPolytope(
                lattice_name=self.name,
                n_variables=dimension,
                n_equalities=len(rows),
                vertices=(),
                affine_dimension=-2,
                is_boolean=self.is_distributive(),
                feasible="yes" if witness is not None else "undetermined",
                witness=witness,
                solution_rank=dimension - free_dimension,
            )
        vertices: list[tuple[Fraction, ...]] = []
        for columns in combinations(range(dimension), free_dimension):
            for values in product((Fraction(0), Fraction(1)), repeat=free_dimension):
                extra_rows = [list(row) for row in rows]
                extra_rhs = list(rhs)
                for column, value in zip(columns, values):
                    unit = [Fraction(0)] * dimension
                    unit[column] = Fraction(1)
                    extra_rows.append(unit)
                    extra_rhs.append(value)
                status, point, remaining = _solve_linear(extra_rows, extra_rhs, dimension)
                if status == "empty" or remaining or not in_box(point):
                    continue
                candidate = tuple(point)
                if candidate not in vertices:
                    vertices.append(candidate)
        if not vertices:
            witness = _search_feasible_point(particular, basis, dimension, free_dimension)
            return ValuationPolytope(
                lattice_name=self.name,
                n_variables=dimension,
                n_equalities=len(rows),
                vertices=(),
                affine_dimension=-1 if witness is None else -2,
                is_boolean=self.is_distributive(),
                feasible="no" if witness is None else "undetermined",
                witness=witness,
                solution_rank=dimension - free_dimension,
            )
        return ValuationPolytope(
            lattice_name=self.name,
            n_variables=dimension,
            n_equalities=len(rows),
            vertices=tuple(sorted(vertices)),
            affine_dimension=_affine_dimension(vertices),
            is_boolean=self.is_distributive(),
            feasible="yes",
            witness=vertices[0],
            solution_rank=dimension - free_dimension,
        )

    def orthocomplementation(self) -> dict[frozenset[int], frozenset[int]] | None:
        """Exact search for an orthocomplementation of the lattice.

        An orthocomplementation is an involutive, order-reversing map
        ``x -> x_perp`` with ``x ^ x_perp = bottom`` and ``x v x_perp = top``.
        Its existence is the missing hypothesis of Gleason-type theorems: only
        with it does a generalised probability become a Born rule.  The search
        is exhaustive backtracking over the rank-complementary pairs and fails
        closed above :data:`_MAX_ORTHO_ELEMENTS` elements.
        """

        if len(self.elements) > _MAX_ORTHO_ELEMENTS:
            raise ToeKernelError(
                f"orthocomplementation fails closed above {_MAX_ORTHO_ELEMENTS} lattice elements"
            )
        top_rank = max(self.rank_of.values())
        by_rank: dict[int, list[frozenset[int]]] = {}
        for element in self.elements:
            by_rank.setdefault(self.rank_of[element], []).append(element)
        ordered = sorted(self.elements, key=lambda element: (self.rank_of[element], sorted(element)))
        assignment: dict[frozenset[int], frozenset[int]] = {}

        def compatible(candidate: frozenset[int], image: frozenset[int]) -> bool:
            if self.meet(candidate, image) != self.bottom:
                return False
            if self.join(candidate, image) != self.top:
                return False
            for done, done_image in assignment.items():
                if done <= candidate and not (image <= done_image):
                    return False
                if candidate <= done and not (done_image <= image):
                    return False
            return True

        def backtrack(position: int) -> bool:
            if position >= len(ordered):
                return True
            element = ordered[position]
            if element in assignment:
                return backtrack(position + 1)
            target_rank = top_rank - self.rank_of[element]
            for image in by_rank.get(target_rank, []):
                if image in assignment:
                    continue
                if assignment.get(image) is not None:
                    continue
                if not compatible(element, image):
                    continue
                assignment[element] = image
                assignment[image] = element
                if backtrack(position + 1):
                    return True
                del assignment[element]
                del assignment[image]
            return False

        if not backtrack(0):
            return None
        return dict(assignment)

@dataclass(frozen=True)
class ValuationPolytope:
    """Exact state space of a substrate.

    ``affine_dimension`` is ``-1`` when no state exists and ``-2`` when states
    exist but the vertex search was refused (fail closed).
    """

    lattice_name: str
    n_variables: int
    n_equalities: int
    vertices: tuple[tuple[Fraction, ...], ...]
    affine_dimension: int
    is_boolean: bool
    feasible: str
    witness: tuple[Fraction, ...] | None
    solution_rank: int


def _search_feasible_point(
    particular: Sequence[Fraction],
    basis: Sequence[Sequence[Fraction]],
    dimension: int,
    free_dimension: int,
    resolution: int = 6,
) -> tuple[Fraction, ...] | None:
    """Rational grid witness for ``{A x = b} \cap [0, 1]^n`` (existence only)."""

    grid = [Fraction(step, resolution) for step in range(resolution + 1)]
    if free_dimension > 4:
        return None
    for coefficients in product(grid, repeat=free_dimension):
        point = [Fraction(particular[k]) for k in range(dimension)]
        for coefficient, direction in zip(coefficients, basis):
            for k in range(dimension):
                point[k] += coefficient * direction[k]
        if all(Fraction(0) <= value <= Fraction(1) for value in point):
            return tuple(point)
    return None




def _rref(rows: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]) -> tuple[str, list[list[Fraction]], list[Fraction], list[int]]:
    """Rational reduced row echelon form.

    Returns ``(status, matrix, right_hand_side, pivot_columns)`` with status in
    ``{"ok", "inconsistent"}``.
    """

    matrix = [[Fraction(value) for value in row] for row in rows]
    vector = [Fraction(value) for value in rhs]
    n_columns = len(matrix[0]) if matrix else 0
    pivots: list[int] = []
    current_row = 0
    for column in range(n_columns):
        pivot_row = None
        for row in range(current_row, len(matrix)):
            if matrix[row][column] != 0:
                pivot_row = row
                break
        if pivot_row is None:
            continue
        matrix[current_row], matrix[pivot_row] = matrix[pivot_row], matrix[current_row]
        vector[current_row], vector[pivot_row] = vector[pivot_row], vector[current_row]
        scale = matrix[current_row][column]
        matrix[current_row] = [value / scale for value in matrix[current_row]]
        vector[current_row] = vector[current_row] / scale
        for row in range(len(matrix)):
            if row != current_row and matrix[row][column] != 0:
                factor = matrix[row][column]
                matrix[row] = [a - factor * b for a, b in zip(matrix[row], matrix[current_row])]
                vector[row] = vector[row] - factor * vector[current_row]
        pivots.append(column)
        current_row += 1
        if current_row == len(matrix):
            break
    for row in range(len(matrix)):
        if not any(matrix[row]) and vector[row] != 0:
            return ("inconsistent", matrix, vector, pivots)
    return ("ok", matrix, vector, pivots)


def _solve_linear(
    rows: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction], n_columns: int
) -> tuple[str, list[Fraction], list[list[Fraction]]]:
    """Exact solution set: ``status``, one particular solution, nullspace basis."""

    status, matrix, vector, pivots = _rref(rows, rhs)
    if status == "inconsistent":
        return ("empty", [], [])
    particular = [Fraction(0)] * n_columns
    for row_index, column in enumerate(pivots):
        particular[column] = vector[row_index]
    free = [column for column in range(n_columns) if column not in pivots]
    basis = []
    for column in free:
        direction = [Fraction(0)] * n_columns
        direction[column] = Fraction(1)
        for row_index, pivot_column in enumerate(pivots):
            direction[pivot_column] = -matrix[row_index][column]
        basis.append(direction)
    return ("ok", particular, basis)


def _fourier_motzkin_vertices(
    dimension: int,
    equalities: Sequence[tuple[Sequence[Fraction], Fraction]],
    variables: Sequence[frozenset[int]],
) -> list[tuple[Fraction, ...]]:
    """Exact vertex enumeration of ``{Ax = b} \cap [0, 1]^dimension``.

    A vertex of this polytope is a feasible point at which ``k`` independent
    box constraints are active, ``k`` being the dimension of the affine
    solution space.  All such candidates are enumerated exactly, so no vertex
    is lost to numerical tolerance.
    """

    if dimension == 0:
        return []
    rows = [[Fraction(value) for value in vector] for vector, _ in equalities]
    rhs = [Fraction(constant) for _, constant in equalities]
    status, particular, basis = _solve_linear(rows, rhs, dimension)
    if status == "empty":
        return []
    if not basis:
        if all(Fraction(0) <= value <= Fraction(1) for value in particular):
            return [tuple(particular)]
        return []

    def feasible(point: Sequence[Fraction]) -> bool:
        return all(Fraction(0) <= value <= Fraction(1) for value in point)

    k = len(basis)
    vertices: set[tuple[Fraction, ...]] = set()
    if feasible(particular):
        # zero-dimensional candidates still matter when the equalities alone pin
        # a corner of the box
        pass
    for columns in combinations(range(dimension), k):
        for values in product((Fraction(0), Fraction(1)), repeat=k):
            extra_rows = list(rows)
            extra_rhs = list(rhs)
            for column, value in zip(columns, values):
                unit = [Fraction(0)] * dimension
                unit[column] = Fraction(1)
                extra_rows.append(unit)
                extra_rhs.append(value)
            status, point, remaining = _solve_linear(extra_rows, extra_rhs, dimension)
            if status == "empty" or remaining:
                continue
            if feasible(point):
                vertices.add(tuple(point))
    return sorted(vertices, key=lambda point: tuple(float(value) for value in point))


def _affine_dimension(vertices: Sequence[Sequence[Fraction]]) -> int:
    if len(vertices) <= 1:
        return 0
    dimension = len(vertices[0])
    rows = [[vertices[i][k] - vertices[0][k] for k in range(dimension)] for i in range(1, len(vertices))]
    rhs = [Fraction(0)] * len(rows)
    _, _, basis = _solve_linear(rows, rhs, dimension)
    return dimension - len(basis)


# ---------------------------------------------------------------------------
# spectral dimension from the Hasse diagram
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpectralDimensionCurve:
    name: str
    times: tuple[int, ...]
    return_probabilities: tuple[Fraction, ...]
    spectral_dimensions: tuple[float, ...]
    window: tuple[int, int]
    derived_dimension: float
    is_exact: bool
    n_walkers: int

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "times": list(self.times),
            "return_probabilities": [str(value) for value in self.return_probabilities],
            "spectral_dimensions": list(self.spectral_dimensions),
            "window": list(self.window),
            "derived_dimension": self.derived_dimension,
            "is_exact": self.is_exact,
            "n_walkers": self.n_walkers,
        }


def spectral_dimension_from_graph(
    name: str,
    adjacency: Mapping[frozenset[int], Sequence[frozenset[int]]],
    steps: int = 200,
    window: tuple[int, int] = (10, 100),
    walkers: int = 0,
    seed: int = 20260919,
    lazy: bool = False,
    parity_fix: bool = True,
) -> SpectralDimensionCurve:
    """Return-probability decay d_S(t) = -2 dlog P(t) / dlog t on the Hasse graph.

    Exact rational propagation when the number of lattice elements is small
    enough (``walkers = 0``); otherwise Monte-Carlo with the requested number
    of walkers.  The derived dimension is the mean of d_S over ``window``.

    ``parity_fix=True`` (default) takes slopes between even times only, because
    the Hasse diagram of a graded lattice is bipartite and a simple walk can
    return to its start only at even times.  ``lazy=True`` switches to
    ``P -> (I + P)/2``, which removes periodicity but also removes the whole
    transient regime of a product graph, so it is off by default.

    The routine **fails closed** when the walk has already mixed inside the
    requested window: a finite lattice has a plateau at ``1/|L|`` and a spectral
    dimension extracted from the plateau is meaningless.  This is the same
    reporting discipline the repository enforces for the graph random-walk
    spectral dimension in ``tests/test_spectral_dimension_integrity.py``.
    """

    elements = list(adjacency)
    if len(elements) > _MAX_SPECTRAL_ELEMENTS and walkers == 0:
        raise ToeKernelError(
            f"{name}: exact propagation fails closed above {_MAX_SPECTRAL_ELEMENTS} elements; "
            "pass walkers > 0 for the Monte-Carlo estimator"
        )
    for element in elements:
        if not adjacency[element]:
            raise ToeKernelError(f"{name}: element {sorted(element)} has no Hasse neighbour")
    low, high = window
    if not 1 <= low < high <= steps:
        raise ToeKernelError("window must satisfy 1 <= low < high <= steps")

    probabilities: dict[int, Fraction] = {}
    if walkers == 0:
        distributions = [
            {start: Fraction(1)} for start in elements
        ]
        for time in range(1, steps + 1):
            new_distributions = []
            total = Fraction(0)
            for start, distribution in zip(elements, distributions):
                nxt: dict[frozenset[int], Fraction] = {}
                for node, weight in distribution.items():
                    if lazy:
                        nxt[node] = nxt.get(node, Fraction(0)) + weight / 2
                        share = weight / (2 * len(adjacency[node]))
                    else:
                        share = weight / len(adjacency[node])
                    for neighbour in adjacency[node]:
                        nxt[neighbour] = nxt.get(neighbour, Fraction(0)) + share
                new_distributions.append(nxt)
                total += nxt.get(start, Fraction(0))
            distributions = new_distributions
            probabilities[time] = total / len(elements)
        exact = True
        used_walkers = len(elements)
    else:
        generator = random.Random(seed)
        counts: dict[int, int] = {time: 0 for time in range(1, steps + 1)}
        neighbours_cache = {element: list(adjacency[element]) for element in elements}
        for _ in range(walkers):
            node = generator.choice(elements)
            start = node
            for time in range(1, steps + 1):
                if not lazy or generator.random() < 0.5:
                    node = generator.choice(neighbours_cache[node])
                if node == start:
                    counts[time] += 1
        probabilities = {time: Fraction(count, walkers) for time, count in counts.items()}
        exact = False
        used_walkers = walkers

    times = tuple(sorted(probabilities))
    values = tuple(probabilities[time] for time in times)
    if parity_fix:
        # the Hasse diagram of a graded lattice is bipartite: a simple walk
        # returns only at even times, so slopes are taken between even times
        times = tuple(time for time in times if time % 2 == 0)
        values = tuple(probabilities[time] for time in times)
    if len(times) < 4:
        raise ToeKernelError(f"{name}: not enough usable return times to form a slope")
    plateau = min(values[len(values) * 9 // 10 :])
    if plateau <= 0:
        plateau = Fraction(1, len(adjacency))
    above = [time for time, value in zip(times, values) if low <= time <= high and value >= 2 * plateau]
    if len(above) < 3:
        raise ToeKernelError(
            f"{name}: finite-size guard -- the walk has already mixed (plateau {float(plateau):.3e}, "
            f"window {window}); no spectral dimension is derivable from a substrate of "
            f"{len(adjacency)} lattice elements"
        )
    local: list[float] = []
    for position in range(1, len(times)):
        previous_time, current_time = times[position - 1], times[position]
        previous_value, current_value = values[position - 1], values[position]
        if previous_value == 0 or current_value == 0:
            local.append(float("nan"))
            continue
        slope = math.log(float(current_value) / float(previous_value)) / math.log(current_time / previous_time)
        local.append(-2.0 * slope)
    selected = [
        value
        for value, time in zip(local, times[1:])
        if low <= time <= high and not math.isnan(value)
    ]
    if not selected:
        raise ToeKernelError(f"{name}: no usable return probability inside window {window}")
    derived = sum(selected) / len(selected)
    return SpectralDimensionCurve(
        name=name,
        times=times,
        return_probabilities=values,
        spectral_dimensions=tuple(local),
        window=window,
        derived_dimension=derived,
        is_exact=exact,
        n_walkers=used_walkers,
    )


# ---------------------------------------------------------------------------
# Spin(10) weight system as a closure structure
# ---------------------------------------------------------------------------


def spin10_even_parity_weights() -> tuple[tuple[Fraction, ...], ...]:
    """The 16 weights of the chiral spinor of Spin(10).

    Exact structural fact: the weights of the 16 of Spin(2n) are the points
    (+-1/2, ..., +-1/2) with an even number of minus signs.  For n = 5 this is
    the even-parity half of the 5-cube, i.e. the code words of the binary
    [5, 4] even-parity code read as signs.
    """

    weights = []
    for signs in product((1, -1), repeat=5):
        minus = sum(1 for sign in signs if sign < 0)
        if minus % 2 == 0:
            weights.append(tuple(Fraction(sign, 2) for sign in signs))
    return tuple(weights)


def spin10_weyl_group_order(parity_even_only: bool = True) -> int:
    """Order of the group of parity-preserving signed permutations of 5 slots.

    ``parity_even_only=True`` returns |W(D_5)| = 2^4 * 5! = 1920, the Weyl
    group of Spin(10); ``False`` returns the full hyperoctahedral group
    2^5 * 5! = 3840 = |W(B_5)|.  Both are computed by explicit enumeration,
    which is the RC-ToE reading of gauge symmetry: *symmetry is the
    automorphism group of the closure structure of the fact slots*.
    """

    count = 0
    for signs in product((1, -1), repeat=5):
        minus = sum(1 for sign in signs if sign < 0)
        if parity_even_only and minus % 2 != 0:
            continue
        count += math.factorial(5)
    return count


def spin10_weyl_group_acts_transitively() -> bool:
    weights = spin10_even_parity_weights()
    target = weights[0]
    reached = set()
    for signs in product((1, -1), repeat=5):
        if sum(1 for sign in signs if sign < 0) % 2 != 0:
            continue
        for permutation in permutations(range(5)):
            moved = tuple(signs[position] * target[permutation[position]] for position in range(5))
            reached.add(moved)
    return reached == set(weights)


def spin10_parity_code_matroid() -> Matroid:
    """The matroid of the generator matrix of the binary [5, 4] even-parity code.

    Columns are the five code coordinates; the unique circuit is the whole
    ground set, so the matroid is U_{4,5}.  Dual reading: the constraint of the
    Spin(10) spinor is a *single global parity charge* -- a rank-one dual, i.e.
    one Z_2 fact shared by all five slots.
    """

    columns = [
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
        (1, 1, 1, 1),
    ]
    return Matroid.from_gf2_columns("spin10_even_parity_code", columns)


def subspace_matroid_gf2(dim: int, name: str | None = None) -> Matroid:
    """The matroid whose ground set is *all* non-zero vectors of GF(2)^dim.

    Independence is linear independence, so the closure operator is the linear
    span and the flats are exactly the subspaces: ``L`` is the projective
    geometry PG(dim-1, 2).  This is the crucial difference from a finite
    generic sample such as ``U_{r,n}``: the substrate contains *every* fact of
    the vector space, and only then does the flat lattice become modular,
    orthocomplementable and state-admissible.

    Fails closed above ``dim = 3`` because the number of facts is 2**dim - 1
    and every routine here is exhaustive.
    """

    if dim < 2 or dim > 3:
        raise ToeKernelError("subspace_matroid_gf2 fails closed outside dim in {2, 3}")
    vectors = [
        tuple(int(bit) for bit in format(number, f"0{dim}b"))
        for number in range(1, 2**dim)
    ]
    return Matroid.from_gf2_columns(name or f"PG({dim - 1},2)", vectors)


def fano_matroid() -> Matroid:
    """PG(2, 2): the Fano plane -- 7 facts, rank 3, 7 circuits (its lines).

    RC-ToE significance, all of it exactly computable below:
    * it is the smallest substrate that is simultaneously non-distributive
      (there are 3-fold constraints, theorem T1) and state-admissible;
    * its automorphism group is GL(3, 2) = PSL(2, 7) of order 168;
    * it is the incidence diagram of the octonion multiplication, i.e. the
      smallest substrate whose constraint structure is non-associative.
    """

    return subspace_matroid_gf2(3, name="fano_PG2_2")
