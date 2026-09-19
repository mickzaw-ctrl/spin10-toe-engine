"""Scientific-contract tests for the RC-ToE closure gates.

Standard library only.  These contracts pin the numbers quoted in
``docs/DEFINICJA-TEORII-WSZYSTKIEGO.md`` and, crucially, check that the audit
can both refuse and grant a certification -- an auditor that only ever refuses
would be vacuous.

Run::

    PYTHONPATH=src python -m unittest -v tests.test_toe_reflective_closure
"""

from __future__ import annotations

from fractions import Fraction
import unittest

import toe_closure_kernel as kernel
import toe_reflective_closure as rc


class AdmissibilityLadderTests(unittest.TestCase):
    def test_ladder_rungs_of_the_reference_substrates(self) -> None:
        expected = {
            "free": (kernel.free_matroid(4), 0),
            "diamond": (kernel.uniform_matroid(2, 3), 2),
            "m4": (kernel.uniform_matroid(2, 4), 3),
            "u34": (kernel.uniform_matroid(3, 4), 1),
            "u45": (kernel.uniform_matroid(4, 5), 1),
            "spin10_code": (kernel.spin10_parity_code_matroid(), 1),
            "fano": (kernel.fano_matroid(), 2),
        }
        for label, (matroid, rung) in expected.items():
            with self.subTest(substrate=label):
                self.assertEqual(rc.admissibility_report(matroid).rung, rung)

    def test_m4_is_orthocomplemented_but_not_born_ready(self) -> None:
        report = rc.admissibility_report(kernel.uniform_matroid(2, 4))
        self.assertTrue(report.orthocomplemented)
        self.assertEqual(report.rung, 3)
        self.assertFalse(report.born_ready)
        self.assertEqual(report.rank, 2)

    def test_fano_is_state_admissible_without_a_born_rule(self) -> None:
        report = rc.admissibility_report(kernel.fano_matroid())
        self.assertEqual(report.rung, 2)
        self.assertEqual(report.valuation_feasible, "yes")
        self.assertEqual(report.n_states, 1)
        self.assertFalse(report.orthocomplemented)
        self.assertFalse(report.born_ready)
        self.assertEqual(report.automorphism_group_order, 168)
        self.assertEqual(report.beta_invariant, 3)

    def test_spin10_weight_system_carries_no_probability(self) -> None:
        report = rc.admissibility_report(kernel.spin10_parity_code_matroid())
        self.assertEqual(report.rung, 1)
        self.assertEqual(report.valuation_feasible, "no")
        self.assertEqual(report.lowest_constraint_order, 5)

    def test_no_finite_substrate_up_to_four_facts_is_born_ready(self) -> None:
        checked = 0
        for size in (2, 3, 4):
            for matroid in kernel.enumerate_matroids(size):
                checked += 1
                self.assertFalse(
                    rc.admissibility_report(matroid).born_ready, msg=matroid.name
                )
        self.assertEqual(checked, 89)

    def test_census_of_substrates_on_four_facts(self) -> None:
        counts: dict[int, int] = {}
        for matroid in kernel.enumerate_matroids(4):
            rung = rc.admissibility_report(matroid).rung
            counts[rung] = counts.get(rung, 0) + 1
        self.assertEqual(counts, {0: 52, 1: 1, 2: 14, 3: 1})

    def test_report_rejects_a_non_matroid(self) -> None:
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.admissibility_report("not a matroid")  # type: ignore[arg-type]


class CertifiedResidualTests(unittest.TestCase):
    def test_omega_lower_bounds_are_exact_rationals(self) -> None:
        expected = {3: Fraction(3, 4), 5: Fraction(27, 32), 7: Fraction(57, 64), 9: Fraction(467, 512)}
        for length, value in expected.items():
            with self.subTest(length=length):
                result = rc.toy_prefix_machine_omega(length, step_budget=2000)
                self.assertEqual(result.omega, value)
                self.assertEqual(result.omega + result.residual, result.total_mass)

    def test_undecided_mass_grows_with_program_length(self) -> None:
        residuals = [
            rc.toy_prefix_machine_omega(length, step_budget=2000).residual
            for length in (3, 5, 7, 9)
        ]
        self.assertEqual(residuals[0], Fraction(0))
        self.assertTrue(all(a < b for a, b in zip(residuals, residuals[1:])))

    def test_a_larger_budget_can_only_reduce_the_residual(self) -> None:
        small = rc.toy_prefix_machine_omega(9, step_budget=8)
        large = rc.toy_prefix_machine_omega(9, step_budget=4096)
        self.assertLessEqual(large.residual, small.residual)
        self.assertGreaterEqual(large.omega, small.omega)
        self.assertEqual(small.total_mass, large.total_mass)

    def test_omega_fails_closed_outside_its_validated_domain(self) -> None:
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.toy_prefix_machine_omega(23)
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.toy_prefix_machine_omega(5, step_budget=0)


class ReflexiveInferenceTests(unittest.TestCase):
    KERNEL = [[0.10, 0.80, 0.10], [0.05, 0.90, 0.05], [0.20, 0.50, 0.30]]
    NAMES = ["A_max_likelihood", "B_reflective", "C_third"]

    def test_reflective_stability_overrides_maximum_likelihood(self) -> None:
        result = rc.reflexive_bayes_fixed_point(
            self.NAMES, [0.70, 0.20, 0.10], self.KERNEL, exploration=0.02
        )
        self.assertEqual(result.maximum_likelihood, "A_max_likelihood")
        self.assertEqual(result.reflective_choice, "B_reflective")
        self.assertTrue(result.likelihood_overridden)
        self.assertTrue(result.converged)
        self.assertLess(result.contraction_rate, 1.0)
        self.assertLess(result.kl_residual, 1e-12)
        self.assertGreater(result.reflective_override, 0.5)
        self.assertAlmostEqual(sum(result.fixed_point), 1.0, places=12)

    def test_exploration_floor_keeps_the_fixed_point_interior(self) -> None:
        result = rc.reflexive_bayes_fixed_point(
            self.NAMES, [0.70, 0.20, 0.10], self.KERNEL, exploration=0.02
        )
        self.assertTrue(all(value > 0.0 for value in result.fixed_point))

    def test_a_self_confirming_agent_reproduces_the_maximum_likelihood_choice(self) -> None:
        identity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        result = rc.reflexive_bayes_fixed_point(self.NAMES, [0.70, 0.20, 0.10], identity)
        self.assertFalse(result.likelihood_overridden)
        self.assertEqual(result.reflective_choice, "A_max_likelihood")

    def test_operator_fails_closed_on_malformed_input(self) -> None:
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.reflexive_bayes_fixed_point(["only"], [1.0], [[1.0]])
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.reflexive_bayes_fixed_point(self.NAMES, [0.7, 0.2, 0.1], [[0.5, 0.5, 0.0]] * 2)
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.reflexive_bayes_fixed_point(self.NAMES, [-0.7, 0.2, 0.1], self.KERNEL)
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.reflexive_bayes_fixed_point(self.NAMES, [0.7, 0.2, 0.1], self.KERNEL, exploration=0.9)
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.reflexive_bayes_fixed_point(self.NAMES, [0.7, 0.2, 0.1], [[0.0] * 3] * 3)


class CoincidenceBudgetTests(unittest.TestCase):
    def test_beta_of_fano_versus_three_generations_is_numerology(self) -> None:
        # the invariant search space of the census is 89 substrates x 20 invariants
        budget = rc.coincidence_budget(
            n_invariants=20, n_candidates=89, tolerance=0.05, mechanism_supplied=False
        )
        self.assertEqual(budget.verdict, "rejected_no_mechanism")
        self.assertFalse(budget.admissible)
        with_mechanism = rc.coincidence_budget(
            n_invariants=20, n_candidates=89, tolerance=0.05, mechanism_supplied=True
        )
        self.assertEqual(with_mechanism.verdict, "rejected_numerology")
        self.assertGreater(with_mechanism.p_chance, 0.99)

    def test_a_tight_single_invariant_claim_with_a_mechanism_is_admissible(self) -> None:
        budget = rc.coincidence_budget(
            n_invariants=1, n_candidates=1, tolerance=0.001, mechanism_supplied=True
        )
        self.assertEqual(budget.verdict, "admissible")
        self.assertTrue(budget.admissible)
        self.assertLess(budget.p_chance, 0.05)

    def test_budget_fails_closed_on_nonsense(self) -> None:
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.coincidence_budget(0, 10, 0.05, True)
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.coincidence_budget(10, 10, 0.0, True)


class AuditTeethTests(unittest.TestCase):
    def _falsifiers(self, external: bool) -> tuple[rc.Falsifier, ...]:
        return (
            rc.Falsifier(
                observable="test observable",
                prediction="1.000",
                tolerance="+-0.001",
                experiment="third-party experiment",
                horizon="2030",
                kill_semantics="kills claim X",
                pre_registered=True,
                external=external,
            ),
        )

    def _fixed_point(self) -> rc.ReflexiveFixedPoint:
        return rc.reflexive_bayes_fixed_point(
            ["A", "B"], [0.6, 0.4], [[0.2, 0.8], [0.1, 0.9]], exploration=0.05
        )

    def test_audit_can_certify_a_synthetic_candidate_that_passes_every_gate(self) -> None:
        substrate = kernel.uniform_matroid(2, 4)  # rung 3, orthocomplemented, rank 2
        report = rc.admissibility_report(substrate)
        audit = rc.audit_rc_toe(
            candidate="synthetic passing candidate",
            substrate_report=report,
            declared_rung=3,
            fitted_parameters=[],
            invariant_claims=[
                {
                    "constant": "c",
                    "invariant": "beta",
                    "n_invariants": 1,
                    "n_candidates": 1,
                    "tolerance": 0.001,
                    "mechanism": True,
                }
            ],
            law_channels={
                "gauge": "derived",
                "gravity": "derived",
                "fermion_generations": "implemented",
                "cosmological_constant": "derived",
            },
            law_channel_notes={"note": "synthetic"},
            fixed_point=self._fixed_point(),
            falsifiers=self._falsifiers(external=True),
            axiom_bits=1000,
            data_bits=5000,
            requires_born_rule=False,
        )
        self.assertTrue(audit.certified)
        self.assertEqual(audit.verdict, "CERTIFIED_AS_TOE")
        self.assertEqual([gate.verdict for gate in audit.gates], ["PASS"] * 5)

    def test_internal_only_falsifiers_cannot_satisfy_decision_closure(self) -> None:
        report = rc.admissibility_report(kernel.uniform_matroid(2, 4))
        audit = rc.audit_rc_toe(
            candidate="internal-only candidate",
            substrate_report=report,
            declared_rung=3,
            fitted_parameters=[],
            invariant_claims=[
                {"n_invariants": 1, "n_candidates": 1, "tolerance": 0.001, "mechanism": True}
            ],
            law_channels={
                "gauge": "derived",
                "gravity": "derived",
                "fermion_generations": "derived",
                "cosmological_constant": "derived",
            },
            law_channel_notes={},
            fixed_point=self._fixed_point(),
            falsifiers=self._falsifiers(external=False),
            axiom_bits=1000,
            data_bits=5000,
            requires_born_rule=False,
        )
        self.assertFalse(audit.certified)
        self.assertEqual(
            [gate for gate in audit.gates if gate.gate_id == "D"][0].verdict, "CONDITIONAL"
        )

    def test_a_born_rule_requirement_blocks_every_finite_substrate(self) -> None:
        report = rc.admissibility_report(kernel.uniform_matroid(2, 4))
        audit = rc.audit_rc_toe(
            candidate="finite quantum candidate",
            substrate_report=report,
            declared_rung=3,
            fitted_parameters=[],
            invariant_claims=[
                {"n_invariants": 1, "n_candidates": 1, "tolerance": 0.001, "mechanism": True}
            ],
            law_channels={
                "gauge": "derived",
                "gravity": "derived",
                "fermion_generations": "derived",
                "cosmological_constant": "derived",
            },
            law_channel_notes={},
            fixed_point=self._fixed_point(),
            falsifiers=self._falsifiers(external=True),
            axiom_bits=1000,
            data_bits=5000,
            requires_born_rule=True,
        )
        self.assertFalse(audit.certified)
        gate_q = [gate for gate in audit.gates if gate.gate_id == "Q"][0]
        self.assertEqual(gate_q.verdict, "CONDITIONAL")
        self.assertIn("infinite", str(gate_q.evidence["blocking_note"]))

    def test_a_declared_rung_that_disagrees_with_the_computation_fails(self) -> None:
        report = rc.admissibility_report(kernel.fano_matroid())
        audit = rc.audit_rc_toe(
            candidate="overclaiming candidate",
            substrate_report=report,
            declared_rung=3,
            fitted_parameters=[],
            invariant_claims=[],
            law_channels={
                "gauge": "derived",
                "gravity": "derived",
                "fermion_generations": "derived",
                "cosmological_constant": "derived",
            },
            law_channel_notes={},
            fixed_point=self._fixed_point(),
            falsifiers=self._falsifiers(external=True),
            axiom_bits=1000,
            data_bits=5000,
        )
        self.assertEqual([gate for gate in audit.gates if gate.gate_id == "Q"][0].verdict, "FAIL")
        self.assertEqual(audit.verdict, "FRAMEWORK_NOT_TOE")

    def test_unknown_law_channel_status_fails_closed(self) -> None:
        with self.assertRaises(rc.ReflectiveClosureError):
            rc.audit_rc_toe(
                candidate="bad vocabulary",
                substrate_report=None,
                declared_rung=None,
                fitted_parameters=[],
                invariant_claims=[],
                law_channels={
                    "gauge": "beautifully derived",
                    "gravity": "derived",
                    "fermion_generations": "derived",
                    "cosmological_constant": "derived",
                },
                law_channel_notes={},
                fixed_point=None,
                falsifiers=(),
                axiom_bits=1,
                data_bits=2,
            )

    def test_a_missing_substrate_report_is_refused_not_guessed(self) -> None:
        audit = rc.audit_rc_toe(
            candidate="no substrate",
            substrate_report=None,
            declared_rung=None,
            fitted_parameters=[],
            invariant_claims=[],
            law_channels={
                "gauge": "derived",
                "gravity": "derived",
                "fermion_generations": "derived",
                "cosmological_constant": "derived",
            },
            law_channel_notes={},
            fixed_point=self._fixed_point(),
            falsifiers=self._falsifiers(external=True),
            axiom_bits=1000,
            data_bits=5000,
        )
        self.assertEqual([gate for gate in audit.gates if gate.gate_id == "Q"][0].verdict, "REFUSED")
        self.assertEqual(audit.verdict, "REFUSED_MISSING_COMPUTATION")
        self.assertFalse(audit.certified)


if __name__ == "__main__":
    unittest.main()
