"""Scientific-contract tests for the RC-ToE combinatorial kernel.

Standard library only: these contracts must run in an environment without
NumPy, JAX or network access, because they are the decision procedure of
``docs/DEFINICJA-TEORII-WSZYSTKIEGO.md``.

Run::

    PYTHONPATH=src python -m unittest -v tests.test_toe_closure_kernel
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import math
import unittest

import toe_closure_kernel as kernel


class UniformMatroidInvariantsTests(unittest.TestCase):
    """Textbook values, recomputed exactly rather than quoted."""

    def test_u45_is_the_spin10_parity_code_matroid(self) -> None:
        code = kernel.spin10_parity_code_matroid()
        uniform = kernel.uniform_matroid(4, 5)
        self.assertEqual(code.circuits, uniform.circuits)
        self.assertEqual(code.circuits, (frozenset(range(5)),))

    def test_u45_characteristic_polynomial_and_counts(self) -> None:
        matroid = kernel.uniform_matroid(4, 5)
        self.assertEqual(matroid.characteristic_polynomial(), {4: 1, 3: -5, 2: 10, 1: -10, 0: 4})
        self.assertEqual(sum(matroid.characteristic_polynomial().values()), 0)  # chi(1) = 0, no loops
        self.assertEqual(matroid.count_bases(), 5)
        self.assertEqual(matroid.count_independent_sets(), 31)
        self.assertEqual(len(matroid.flats()), 27)
        self.assertEqual(matroid.automorphism_group_order(), 120)

    def test_beta_invariant_reproduces_the_uniform_formula(self) -> None:
        # beta(U_{r,n}) = C(n - 2, r - 1) (Crapo), with the convention
        # beta = (-1)^(r+1) chi'(1) used by the kernel
        for rank, size in [(1, 2), (2, 3), (2, 4), (3, 4), (4, 5), (3, 5), (2, 6)]:
            with self.subTest(rank=rank, size=size):
                observed = kernel.uniform_matroid(rank, size).beta_invariant()
                self.assertEqual(observed, math.comb(size - 2, rank - 1))

    def test_free_matroid_has_zero_beta_and_boolean_lattice(self) -> None:
        free = kernel.free_matroid(4)
        self.assertEqual(free.beta_invariant(), 0)
        self.assertEqual(free.characteristic_polynomial(), {4: 1, 3: -4, 2: 6, 1: -4, 0: 1})
        self.assertTrue(free.flat_lattice().is_distributive())
        self.assertEqual(len(free.flats()), 16)
        self.assertIsNotNone(free.flat_lattice().orthocomplementation())

    def test_tutte_evaluations_match_brute_force_counts(self) -> None:
        for matroid in (kernel.uniform_matroid(2, 4), kernel.fano_matroid(), kernel.free_matroid(3)):
            tutte = matroid.tutte_polynomial()
            with self.subTest(name=matroid.name):
                self.assertEqual(tutte.get((0, 0), 0), matroid.count_bases())  # T(1,1)
                self.assertEqual(
                    sum(coeff for (i, _), coeff in tutte.items() if i == 0),
                    sum(
                        1
                        for size in range(len(matroid.ground) + 1)
                        for combo in combinations(matroid.ground, size)
                        if matroid.rank(combo) == matroid.full_rank()
                    ),
                )  # T(1,2) = spanning sets
                self.assertEqual(
                    sum(coeff for (_, j), coeff in tutte.items() if j == 0),
                    matroid.count_independent_sets(),
                )  # T(2,1) = independent sets


class FanoSubstrateTests(unittest.TestCase):
    """PG(2,2): the smallest admissible non-classical substrate."""

    def setUp(self) -> None:
        self.fano = kernel.fano_matroid()
        self.lattice = self.fano.flat_lattice()

    def test_fano_counts(self) -> None:
        self.assertEqual(len(self.fano.ground), 7)
        self.assertEqual(self.fano.full_rank(), 3)
        self.assertEqual(len(self.fano.circuits), 14)
        self.assertEqual(sum(1 for c in self.fano.circuits if len(c) == 3), 7)  # its lines
        self.assertEqual(sum(1 for c in self.fano.circuits if len(c) == 4), 7)  # its affine planes
        self.assertEqual(len(self.fano.flats()), 16)
        self.assertEqual(self.fano.count_bases(), 28)
        self.assertEqual(self.fano.characteristic_polynomial(), {3: 1, 2: -7, 1: 14, 0: -8})
        self.assertEqual(self.fano.beta_invariant(), 3)

    def test_fano_automorphism_group_is_psl27(self) -> None:
        self.assertEqual(self.fano.automorphism_group_order(), 168)

    def test_fano_is_modular_not_distributive(self) -> None:
        self.assertTrue(self.lattice.is_modular())
        self.assertFalse(self.lattice.is_distributive())
        self.assertTrue(self.lattice.distributive_defect_witnesses(limit=1))

    def test_fano_has_exactly_one_generalised_probability(self) -> None:
        polytope = self.lattice.valuation_polytope()
        self.assertEqual(polytope.feasible, "yes")
        self.assertEqual(len(polytope.vertices), 1)
        self.assertEqual(polytope.affine_dimension, 0)
        state = polytope.vertices[0]
        points = [element for element in self.lattice.elements if len(element) == 1]
        lines = [element for element in self.lattice.elements if len(element) == 3]
        index = {
            element: position
            for position, element in enumerate(
                [e for e in self.lattice.elements if e not in (self.lattice.bottom, self.lattice.top)]
            )
        }
        self.assertEqual({state[index[p]] for p in points}, {Fraction(1, 3)})
        self.assertEqual({state[index[ln]] for ln in lines}, {Fraction(2, 3)})

    def test_fano_has_no_orthocomplementation_hence_no_born_rule(self) -> None:
        self.assertIsNone(self.lattice.orthocomplementation())

    def test_fano_interaction_density_is_one_fifth(self) -> None:
        self.assertEqual(self.fano.dependence_spectrum(3)[3], Fraction(1, 5))
        self.assertEqual(self.fano.lowest_constraint_order(), 3)


class TheoremT1Tests(unittest.TestCase):
    """Classicality = absence of constraints of order >= 3, exhaustively."""

    def test_enumeration_counts_match_the_hand_census(self) -> None:
        self.assertEqual(len(kernel.enumerate_matroids(1)), 2)
        self.assertEqual(len(kernel.enumerate_matroids(2)), 5)
        self.assertEqual(len(kernel.enumerate_matroids(3)), 16)
        self.assertEqual(len(kernel.enumerate_matroids(4)), 68)

    def test_theorem_t1_holds_for_every_substrate_up_to_four_facts(self) -> None:
        checked = 0
        for size in (2, 3, 4):
            for matroid in kernel.enumerate_matroids(size):
                checked += 1
                distributive = matroid.flat_lattice().is_distributive()
                constrained = matroid.lowest_constraint_order() >= 3
                self.assertNotEqual(
                    distributive,
                    constrained,
                    msg=f"T1 violated by {matroid.name} with circuits "
                    f"{[sorted(c) for c in matroid.circuits]}",
                )
        self.assertEqual(checked, 89)

    def test_exactly_one_substrate_on_three_facts_is_non_classical(self) -> None:
        non_classical = [
            matroid
            for matroid in kernel.enumerate_matroids(3)
            if not matroid.flat_lattice().is_distributive()
        ]
        self.assertEqual(len(non_classical), 1)
        self.assertEqual(non_classical[0].circuits, (frozenset({0, 1, 2}),))

    def test_rank_axioms_hold_for_every_enumerated_substrate(self) -> None:
        for size in (2, 3):
            for matroid in kernel.enumerate_matroids(size):
                self.assertTrue(matroid.validate_rank_axioms(), msg=matroid.name)

    def test_enumeration_fails_closed_above_five_facts(self) -> None:
        with self.assertRaises(kernel.ToeKernelError):
            kernel.enumerate_matroids(6)


class LatticeStateTests(unittest.TestCase):
    def test_diamond_has_a_unique_state_and_collapses_to_one_classical_bit(self) -> None:
        lattice = kernel.uniform_matroid(2, 3).flat_lattice()
        polytope = lattice.valuation_polytope()
        self.assertEqual(polytope.vertices, ((Fraction(1, 2),) * 3,))
        blocks, _ = lattice.distributive_quotient()
        self.assertEqual(blocks, 2)
        self.assertIsNone(lattice.orthocomplementation())

    def test_boolean_lattice_states_are_classical_probability(self) -> None:
        lattice = kernel.free_matroid(3).flat_lattice()
        polytope = lattice.valuation_polytope()
        self.assertTrue(polytope.is_boolean)
        self.assertEqual(polytope.affine_dimension, 2)
        self.assertEqual(len(polytope.vertices), 3)

    def test_u34_admits_no_probability_measure_at_all(self) -> None:
        polytope = kernel.uniform_matroid(3, 4).flat_lattice().valuation_polytope()
        self.assertEqual(polytope.feasible, "no")
        self.assertEqual(polytope.vertices, ())

    def test_m4_is_orthocomplemented_but_not_born_ready(self) -> None:
        lattice = kernel.uniform_matroid(2, 4).flat_lattice()
        self.assertIsNotNone(lattice.orthocomplementation())
        self.assertTrue(lattice.is_modular())
        self.assertEqual(kernel.uniform_matroid(2, 4).full_rank(), 2)

    def test_mobius_of_u24_reproduces_chi(self) -> None:
        lattice = kernel.uniform_matroid(2, 4).flat_lattice()
        self.assertEqual(lattice.mobius(lattice.bottom, lattice.top), 3)


class RankFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fano = kernel.fano_matroid()

    def test_flow_is_closure_monotone_and_counts_forced_facts(self) -> None:
        trajectory = self.fano.rank_flow([0, 1, 3])  # 3 is not on the line 0-1
        self.assertEqual(trajectory[0].actualized, frozenset())
        self.assertEqual(trajectory[1].actualized, frozenset({0}))
        # 0 and 1 span a line of PG(2,2), which contains a third point: forced
        self.assertEqual(trajectory[2].actualized, frozenset({0, 1, self.third_point_on_line(0, 1)}))
        self.assertEqual(trajectory[2].forced, frozenset({self.third_point_on_line(0, 1)}))
        # three non-collinear facts span the whole plane: the closure forces all
        # seven points, so the constraint charge jumps to 7 - 3 = 4
        self.assertEqual(trajectory[3].actualized, frozenset(range(7)))
        self.assertEqual([step.constraint_charge for step in trajectory], [0, 0, 1, 4])
        self.assertEqual([step.rank for step in trajectory], [0, 1, 2, 3])
        self.assertEqual(trajectory[3].frontier, ())

    def third_point_on_line(self, first: int, second: int) -> int:
        for circuit in self.fano.circuits:
            if len(circuit) == 3 and {first, second} <= circuit:
                return next(iter(circuit - {first, second}))
        raise AssertionError("no line through the two points")

    def test_flow_refuses_an_already_forced_choice(self) -> None:
        forced = self.third_point_on_line(0, 1)
        with self.assertRaisesRegex(kernel.ToeKernelError, "already forced"):
            self.fano.rank_flow([0, 1, forced])

    def test_flow_refuses_a_fact_outside_the_ground_set(self) -> None:
        with self.assertRaisesRegex(kernel.ToeKernelError, "not a fact"):
            self.fano.rank_flow([99])

    def test_frontier_shrinks_monotonically(self) -> None:
        trajectory = self.fano.rank_flow([0, 1, 3])
        sizes = [len(step.frontier) for step in trajectory]
        self.assertEqual(sizes, sorted(sizes, reverse=True))


class SpectralDimensionIntegrityTests(unittest.TestCase):
    def test_finite_substrate_is_refused_instead_of_publishing_a_dimension(self) -> None:
        lattice = kernel.fano_matroid().flat_lattice()
        with self.assertRaisesRegex(kernel.ToeKernelError, "finite-size guard"):
            kernel.spectral_dimension_from_graph(
                "fano", lattice.hasse_adjacency(), steps=40, window=(2, 12)
            )

    def test_walk_without_parity_fix_produces_no_slope_on_a_bipartite_hasse_diagram(self) -> None:
        lattice = kernel.free_matroid(4).flat_lattice()
        with self.assertRaises(kernel.ToeKernelError):
            kernel.spectral_dimension_from_graph(
                "B_4", lattice.hasse_adjacency(), steps=20, window=(3, 15), parity_fix=False
            )


class Spin10StructuralIdentityTests(unittest.TestCase):
    def test_even_parity_half_of_the_five_cube_has_sixteen_weights(self) -> None:
        weights = kernel.spin10_even_parity_weights()
        self.assertEqual(len(weights), 16)
        self.assertTrue(all(sum(1 for value in weight if value < 0) % 2 == 0 for weight in weights))
        self.assertTrue(all(abs(value) == Fraction(1, 2) for weight in weights for value in weight))

    def test_weyl_group_of_d5_is_the_parity_preserving_automorphism_group(self) -> None:
        self.assertEqual(kernel.spin10_weyl_group_order(parity_even_only=True), 1920)
        self.assertEqual(kernel.spin10_weyl_group_order(parity_even_only=True), 2**4 * math.factorial(5))
        self.assertEqual(kernel.spin10_weyl_group_order(parity_even_only=False), 3840)

    def test_weyl_group_acts_transitively_on_the_sixteen_weights(self) -> None:
        self.assertTrue(kernel.spin10_weyl_group_acts_transitively())


if __name__ == "__main__":
    unittest.main()
