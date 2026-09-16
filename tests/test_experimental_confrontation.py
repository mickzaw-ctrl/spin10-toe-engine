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


def test_amplitude_A_s_is_in_tension_with_planck(report):
    """The same solver run that gets n_s right at ~0.5 sigma gets A_s ~8 sigma low."""
    A_s = report['predictions_v7']['mukhanov_sasaki_spectrum']['A_s']
    n_sigma = abs(A_s - AS_OBS) / AS_SIGMA
    assert n_sigma > 3.0, (
        'A_s tension has disappeared; re-check the Mukhanov-Sasaki normalisation '
        'and update docs/EXPERIMENTAL-CONFRONTATION-2026.md')


def test_f_NL_from_code_is_the_small_value_not_14_5():
    """Documents quote f_NL^equil = 14.5 (a '14.5 sigma CMB-S4 detection').
    The implemented formula 45 * phi_rms^2 * 0.1 gives 0.46, i.e. undetectable."""
    from spin10_engine import Spin10Predictions
    f_nl = Spin10Predictions.f_NL_equilateral()
    assert f_nl == pytest.approx(45 * 0.32 ** 2 * 0.1, rel=1e-12)
    assert f_nl == pytest.approx(0.4608, abs=1e-4)
    assert f_nl < 5.0


def test_axion_mass_is_100x_the_standard_relation():
    """m_a = 5.7e-2 * (1e10 / f_a) instead of 5.7e-6 eV * (1e12 GeV / f_a)."""
    from spin10_engine import Spin10Predictions
    ax = Spin10Predictions.axion_mass()
    standard = 5.7e-6 * 1e12 / ax['f_a_GeV']
    assert ax['m_a_eV'] / standard == pytest.approx(100.0, rel=1e-9)


def test_eta_B_matches_only_through_a_fitted_enhancement_factor(report):
    """eta_B agrees with Planck, but only because F_3flavour = 4.27e11 is a
    hard-coded constant: 1.43e-21 * 4.27e11 = 6.1061e-10."""
    assert 1.43e-21 * 4.27e11 == pytest.approx(6.1061e-10, rel=1e-9)
    eta = report['predictions']['baryon_asymmetry']['eta_B_total']
    assert abs(eta - ETA_B_OBS) / ETA_B_SIGMA < 3.0


def test_proton_decay_survives_super_k_but_is_out_of_reach_of_hyper_k_2030(report):
    tau = report['predictions']['proton_decay']['tau_e_pi0']
    assert tau > TAU_P_LIMIT, 'excluded by Super-Kamiokande'
    assert tau > HYPERK_2030_REACH, 'should be out of reach of Hyper-K in 2030'
    # ...yet the engine test reports it as visible in 2030 (its threshold is
    # HyperK_2030 * 100, i.e. 1e37 yr, not 1e35 yr).
    assert report['tests']['proton_decay_HyperK']['visible_2030'] is True


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
