"""
Characterisation tests for the confrontation of the Spin(10) engine with
published experimental data (see scripts/run_experimental_confrontation.py and
docs/EXPERIMENTAL-CONFRONTATION-2026.md).

These tests record the CURRENT state of the model against data.  Some of them
assert that a quantity is IN TENSION - that is deliberate: they exist so that
the tension cannot silently disappear (for example by defaulting a solver
output to the measured value) without a test changing state.
"""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

# Planck 2018 VI: ln(10^10 A_s) = 3.044 +- 0.014
AS_OBS = math.exp(3.044) * 1e-10
AS_SIGMA = AS_OBS * 0.014
NS_OBS, NS_SIGMA = 0.9649, 0.0042
ETA_B_OBS, ETA_B_SIGMA = 6.104e-10, 0.041e-10
TAU_P_LIMIT = 2.4e34          # Super-Kamiokande, 450 kton.yr, 90% CL
HYPERK_2030_REACH = 1e35      # Hyper-Kamiokande design reach for p -> e+ pi0
RHO_LAMBDA_J_M3 = 5.31e-10
RHO_PLANCK_J_M3 = 4.633e113


@pytest.fixture(scope='module')
def report():
    from spin10_engine_v9 import SHZSpin10QuantumEngineV9
    engine = SHZSpin10QuantumEngineV9(N=120, k_target=4)
    engine.run_simulation(n_steps=150, verbose=False)
    return engine.full_report_v7()


def test_engine_report_is_complete(report):
    for key in ('observables', 'predictions', 'predictions_v7', 'tests_v7'):
        assert key in report


def test_numeric_n_s_agrees_with_planck_within_2sigma(report):
    n_s = report['predictions_v7']['mukhanov_sasaki_spectrum']['n_s_numeric']
    assert abs(n_s - NS_OBS) / NS_SIGMA < 2.0


def test_amplitude_is_an_input_and_the_solver_reproduces_it(report):
    """A_s fixes the Hubble scale (P_R scales exactly as H^2); it is not predicted.

    Regression test: the background generator used to hard-set H = 1e-5, which is
    6.3% below the value implied by the measured A_s and produced a spurious
    -7.9 sigma "tension" with Planck.
    """
    ms = report['predictions_v7']['mukhanov_sasaki_spectrum']
    assert ms['A_s_is_an_input_not_a_prediction'] is True
    assert abs(ms['A_s'] - AS_OBS) / AS_SIGMA < 2.0
    scale = ms['inflationary_energy_scale']
    assert scale['H_over_M_Pl'] == pytest.approx(1.0661e-05, rel=1e-3)
    assert scale['A_s_input'] == pytest.approx(AS_OBS, rel=1e-9)


def test_mukhanov_sasaki_solver_matches_the_exact_hankel_solution():
    """Guards the numerics: for constant nu the BD solution is known in closed
    form.  The solver must reproduce it, otherwise any amplitude it reports is
    meaningless."""
    from scipy.special import gamma as _gamma
    from mukhanov_sasaki_solver import MukhanovSasakiSolver as MS

    alpha, n_efolds, H = 3.75, 60, 1.0e-5
    eps = 3.0 * alpha / (4.0 * n_efolds ** 2)
    nu = 1.5 + eps - 0.5 * (-2.0 / n_efolds)
    analytic = MS.analytic_amplitude(H, eps, nu, k_pivot=0.05)

    eta, a, z = MS.generate_inflationary_background(alpha, n_efolds, n_points=4000)
    k = np.geomspace(0.005, 0.5, 15)
    numeric = MS.analyze_power_spectrum(k, MS.solve_mukhanov_sasaki(k, eta, a, z))['A_s']
    assert numeric / analytic == pytest.approx(1.0, abs=0.02)
    assert _gamma(nu) > 0


def test_inflation_scale_from_A_s_matches_the_rge_unification_scale(report):
    """Two independent computations: the energy scale implied by the measured
    amplitude, and the gauge-coupling unification scale from the 2-loop RGE."""
    ms = report['predictions_v7']['mukhanov_sasaki_spectrum']
    scale = ms['inflationary_energy_scale']
    m_gut = report['predictions_v7']['two_loop_rge']['M_GUT']
    ratio = scale['V_quarter_GeV'] / m_gut
    assert 0.95 < ratio < 1.05, 'V^(1/4)/M_GUT = {:.4f}'.format(ratio)
    # the same slow-roll parameters must reproduce the engine's r and n_s
    assert scale['r_consistency_16_epsilon'] == pytest.approx(
        report['predictions']['inflation']['r'], rel=1e-9)
    assert abs(scale['n_s_consistency_4_minus_2nu'] - 0.9649) / 0.0042 < 2.0


def test_f_NL_from_code_is_the_small_value_not_14_5():
    """Documents quote f_NL^equil = 14.5 (a '14.5 sigma CMB-S4 detection').
    The implemented formula 45 * phi_rms^2 * 0.1 gives 0.46, i.e. undetectable."""
    from spin10_engine import Spin10Predictions
    f_nl = Spin10Predictions.f_NL_equilateral()
    assert f_nl == pytest.approx(45 * 0.32 ** 2 * 0.1, rel=1e-12)
    assert f_nl == pytest.approx(0.4608, abs=1e-4)
    assert f_nl < 5.0


def test_axion_mass_follows_the_standard_QCD_relation():
    """Regression test: the mass used to be 100x too high
    (5.7e-2 * (1e10 / f_a) instead of 5.7e-6 eV * (1e12 GeV / f_a))."""
    from spin10_engine import Spin10Predictions
    ax = Spin10Predictions.axion_mass()
    standard = 5.7e-6 * 1e12 / ax['f_a_GeV']
    assert ax['m_a_eV'] == pytest.approx(standard, rel=1e-12)
    assert ax['m_a_neV'] == pytest.approx(0.285, rel=1e-3)


def test_axion_relic_density_reports_the_overclosure_factor():
    """Omega_a h^2 = 0.12 only because theta_req is derived from that target;
    with a natural theta ~ 1 the same formula overcloses by ~1e4."""
    from spin10_engine import Spin10Predictions
    ax = Spin10Predictions.axion_mass()
    assert ax['Omega_h2'] == pytest.approx(0.12, rel=1e-9)
    assert ax['theta_req_is_a_fit_to_Omega_c_h2'] is True
    assert ax['overclosure_factor_at_theta_1'] > 1e3
    assert ax['Omega_h2_natural_theta'] == pytest.approx(
        ax['Omega_h2'] / ax['theta_req'] ** 2, rel=1e-9)


def test_eta_B_matches_only_through_a_fitted_enhancement_factor(report):
    """eta_B agrees with Planck, but only because F_3flavour = 4.27e11 is a
    hard-coded constant: 1.43e-21 * 4.27e11 = 6.1061e-10."""
    assert 1.43e-21 * 4.27e11 == pytest.approx(6.1061e-10, rel=1e-9)
    eta = report['predictions']['baryon_asymmetry']['eta_B_total']
    assert abs(eta - ETA_B_OBS) / ETA_B_SIGMA < 3.0


def test_proton_decay_survives_super_k_but_is_out_of_reach_of_hyper_k(report):
    """Regression test: `visible_2030` used to compare tau with
    HyperK_2030 * 100 = 1e37 yr, which made this lifetime look reachable."""
    tau = report['predictions']['proton_decay']['tau_e_pi0']
    hk = report['tests']['proton_decay_HyperK']
    assert tau > TAU_P_LIMIT, 'excluded by Super-Kamiokande'
    assert hk['survives_SuperK'] is True
    assert tau > HYPERK_2030_REACH
    assert hk['visible_2030'] is False
    assert hk['visible_2040'] is False
    assert hk['beyond_HyperK_2030_reach_by'] == pytest.approx(tau / HYPERK_2030_REACH, rel=1e-9)


def test_mukhanov_sasaki_solver_reports_its_own_amplitude_tension(report):
    """The solver used to compare n_s with Planck but never A_s; the fallback on
    solver failure used to return the measured A_s = 2.1e-9."""
    ms = report['predictions_v7']['mukhanov_sasaki_spectrum']
    assert 'A_s_error_sigma' in ms
    assert ms['A_s_Planck'] == pytest.approx(math.exp(3.044) * 1e-10, rel=1e-12)
    assert ms['A_s_error_sigma'] == pytest.approx(
        abs(ms['A_s'] - ms['A_s_Planck']) / ms['A_s_Planck_sigma'], rel=1e-9)
    assert ms['A_s_agrees_with_Planck'] is (ms['A_s_error_sigma'] < 2.0)


def test_spectral_dimension_flow_is_not_the_documented_2_to_4(report):
    d_uv = report['observables']['d_S_UV']
    d_ir = report['observables']['d_S_IR']
    assert not (abs(d_uv - 2.0) < 0.25 and abs(d_ir - 4.0) < 0.25), (
        'the random walk now reproduces the documented 2 -> 4 flow; '
        'docs/EXPERIMENTAL-CONFRONTATION-2026.md needs updating')


def test_cosmological_constant_is_far_above_observation(report):
    """Lambda_Lor is in Planck units; the observed value is 1.1e-123 of that."""
    rho = report['predictions']['Lambda']['Lambda_Lor'] * RHO_PLANCK_J_M3
    assert rho / RHO_LAMBDA_J_M3 > 1e100


def test_rge_unification_is_data_driven_but_its_own_3sigma_test_fails(report):
    rge = report['predictions_v7']['two_loop_rge']
    assert rge['numerical_integration_passed'] is True
    assert 1e15 < rge['M_GUT'] < 1e17
    assert abs(rge['sin2_theta_W_GUT'] / 0.375 - 1.0) < 0.02
    # the engine's own gate compares M_GUT with an arbitrary 2e16 reference
    assert report['tests_v7']['two_loop_unification']['passes_3sigma_unification'] is False


def test_synthetic_suite_draws_its_data_around_the_model_itself():
    """`tests_synthetic_spin10_toe.py` builds every "measurement" as
    prediction + noise, so its 35/35 pass rate says nothing about agreement with
    the real world.  Pinned here so it cannot be mistaken for a validation."""
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'tests_synthetic_spin10_toe.py')
    spec = importlib.util.spec_from_file_location('_synthetic', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    exp = mod.SyntheticExperiment('probe', 2030, sensitivity=0.01,
                                  systematics=0.0, seed=7)
    meas = exp.measure(1.2345)
    assert meas['true'] == 1.2345
    assert abs(meas['observed'] - meas['true']) < 5 * meas['sigma_total']
    # the same generator is what feeds every one of the 35 "PASS" rows
    assert exp.measure(9.0)['true'] == 9.0
