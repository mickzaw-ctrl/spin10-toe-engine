"""Contracts for the Jacobson–Clausius / prescribed-P action extension."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jacobson_clausius import (  # noqa: E402
    DEFAULT_C,
    DEFAULT_N,
    ESTABLISHED,
    HYPOTHESIS,
    INCOMPLETE,
    NOGO_IR_EPS,
    REJECTED,
    JacobsonInputError,
    dynamical_scalar_tensor_action,
    extras_callable,
    extras_for_project_ansatz,
    friedmann_extra_fractions,
    gate3_jacobson_action,
    geff_substitution_verdict,
    jacobson_1995_einstein,
    naive_clausius_with_variable_p,
    p_domain_wall,
    prescribed_p_action,
    project_coherence_p,
    verify_flrw_chain_rule,
    what_would_derive_p,
)


class JacobsonClausiusTests(unittest.TestCase):
    def test_jacobson_is_established_and_does_not_derive_p(self) -> None:
        result = jacobson_1995_einstein()
        self.assertEqual(result["status"], ESTABLISHED)
        self.assertTrue(any("P(N,T)" in item for item in result["does_not_derive"]))
        self.assertIn("local Rindler", " ".join(result["assumptions"]))

    def test_naive_variable_p_is_rejected(self) -> None:
        result = naive_clausius_with_variable_p()
        self.assertEqual(result["status"], REJECTED)
        self.assertIn("∇P = 0", result["holds_iff"])

    def test_prescribed_action_is_established_variation(self) -> None:
        action = prescribed_p_action()
        self.assertEqual(action["status"], ESTABLISHED)
        self.assertIn("P(x) R[g]", action["action"])
        self.assertIn("□", action["metric_equation"])
        self.assertEqual(action["extra_terms_vanish_iff"], "∇P = 0")

    def test_dynamical_reading_stays_incomplete(self) -> None:
        dynamical = dynamical_scalar_tensor_action()
        self.assertEqual(dynamical["status"], INCOMPLETE)
        self.assertFalse(dynamical["cassini_constraint"]["applies_to_prescribed_P"])
        self.assertTrue(dynamical["cassini_constraint"]["applies_to_dynamical_P"])

    def test_constant_p_has_vanishing_extras(self) -> None:
        extras = friedmann_extra_fractions(0.999, 0.0, 0.0, 1.0e-3)
        self.assertEqual(extras["eps_friedmann"], 0.0)
        self.assertEqual(extras["eps_acceleration"], 0.0)
        self.assertEqual(extras["status"], ESTABLISHED)

    def test_zero_temperature_extras_vanish_for_the_ansatz(self) -> None:
        result = extras_for_project_ansatz(DEFAULT_N, 0.0)
        self.assertAlmostEqual(result["P"], 1.0 - DEFAULT_C / math.sqrt(DEFAULT_N))
        self.assertEqual(result["extras"]["eps_friedmann"], 0.0)

    def test_analytic_friedmann_fraction_matches_closed_form(self) -> None:
        result = extras_for_project_ansatz(DEFAULT_N, 1.03e16)
        self.assertAlmostEqual(
            result["extras"]["eps_friedmann"],
            result["analytic_eps_friedmann"],
            places=12,
        )
        # At T = T_GUT, x = 1, ε_F = (c/√N) / (√2 P)
        p_val = result["P"]
        expected = (DEFAULT_C / math.sqrt(DEFAULT_N)) / (math.sqrt(2.0) * p_val)
        self.assertAlmostEqual(result["extras"]["eps_friedmann"], expected, places=12)

    def test_default_ansatz_is_ir_ok_and_large_at_planck(self) -> None:
        report = gate3_jacobson_action(n_nodes=DEFAULT_N, omega=0.0)
        by_id = {row["id"]: row for row in report["epochs"]}
        self.assertLess(by_id["today"]["eps_friedmann"], 1.0e-20)
        self.assertLess(by_id["BBN"]["eps_friedmann"], 1.0e-20)
        self.assertEqual(report["ir_approximation"]["decision"], "IR_OK")
        self.assertLess(by_id["today"]["eps_friedmann"], NOGO_IR_EPS)
        self.assertTrue(by_id["Planck"]["inside_domain"])
        self.assertGreater(by_id["Planck"]["eps_friedmann"], 0.1)
        self.assertFalse(by_id["Planck"]["ir_ok"])

    def test_geff_substitution_is_always_nogo(self) -> None:
        verdict = geff_substitution_verdict()
        self.assertEqual(verdict["status"], REJECTED)
        self.assertEqual(verdict["decision"], "NO-GO")
        self.assertTrue(verdict["preregistered"])

    def test_gate3_does_not_mint_a_toe_or_derive_p(self) -> None:
        report = gate3_jacobson_action()
        self.assertEqual(report["validated_observational_predictions"], 0)
        self.assertEqual(report["decisions"]["jacobson_derives_P"], "NO-GO")
        self.assertEqual(report["decisions"]["geff_is_the_field_equation"], "NO-GO")
        self.assertEqual(report["decisions"]["p_ansatz"], "HOLD")
        self.assertEqual(report["p_derivation"]["status"], INCOMPLETE)
        self.assertFalse(report["p_derivation"]["jacobson_supplies_this"])
        self.assertEqual(report["project_coherence" if False else "inputs"]["omega_is_derived"], False)

    def test_small_n_hits_the_domain_wall_before_planck(self) -> None:
        domain = p_domain_wall(100)
        self.assertTrue(domain["P_positive_anywhere"])
        self.assertLess(domain["T_max_GeV"], 1.22e19)
        with self.assertRaises(JacobsonInputError):
            project_coherence_p(100, 1.22e19)

    def test_fail_closed_on_nonpositive_and_boolean_inputs(self) -> None:
        with self.assertRaises(JacobsonInputError):
            project_coherence_p(True, 1.0)
        with self.assertRaises(JacobsonInputError):
            project_coherence_p(10**6, -1.0)
        with self.assertRaises(JacobsonInputError):
            friedmann_extra_fractions(0.0, 0.0, 0.0, 1.0)
        with self.assertRaises(JacobsonInputError):
            extras_for_project_ansatz(10**6, 1.0, background="klein")

    def test_identity_check_passes_on_the_radiation_clock(self) -> None:
        check = verify_flrw_chain_rule(n_nodes=DEFAULT_N, t_ref_gev=1.03e16)
        self.assertTrue(check["passed"])
        self.assertLess(check["max_relative_residual"], 1.0e-4)
        self.assertEqual(check["status"], ESTABLISHED)

    def test_generic_p_of_t_recovers_the_ansatz_fraction(self) -> None:
        def p_fn(temperature: float) -> float:
            return project_coherence_p(DEFAULT_N, temperature)["P"]

        numeric = extras_callable(p_fn, 1.03e16, delta=1.0e-4)
        analytic = extras_for_project_ansatz(DEFAULT_N, 1.03e16)
        self.assertAlmostEqual(
            numeric["extras"]["eps_friedmann"],
            analytic["extras"]["eps_friedmann"],
            places=6,
        )

    def test_p_ansatz_is_labelled_hypothesis(self) -> None:
        coherence = project_coherence_p(DEFAULT_N, 0.0)
        self.assertEqual(coherence["status"], HYPOTHESIS)
        missing = what_would_derive_p()
        self.assertIn("microscopic entropy", missing["statement"])

    def test_omega_term_scales_as_eps_f_squared(self) -> None:
        bare = extras_for_project_ansatz(DEFAULT_N, 1.03e16, omega=0.0)
        with_omega = extras_for_project_ansatz(DEFAULT_N, 1.03e16, omega=8.0)
        eps = bare["extras"]["eps_friedmann"]
        self.assertAlmostEqual(
            with_omega["extras"]["eps_omega_friedmann"],
            0.5 * 8.0 * eps * eps,
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
