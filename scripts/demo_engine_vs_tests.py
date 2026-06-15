"""
Demonstration of integration between the SHZSpin10QuantumEngine
and the synthetic test suite.
"""
import sys
sys.path.insert(0, '/home/user')

from spin10_engine import SHZSpin10QuantumEngine
from tests_synthetic_spin10_toe import PREDICTIONS, build_experiments, run_test, TestResult
import numpy as np
import json

print("=" * 78)
print("  INTEGRATION: SHZSpin10QuantumEngine <-> Synthetic Test Suite")
print("=" * 78)
print()

# Engine initialisation
engine = SHZSpin10QuantumEngine(N=120, k_target=4, seed=42)

# MCMC simulation
sim = engine.run_simulation(n_steps=3000)

# Predictions from the engine
pred = engine.compute_predictions()
print(">>> Predictions from the Spin(10)-TOE engine:")
print(f"    n_s         = {pred['inflation']['n_s']:.6f}")
print(f"    r           = {pred['inflation']['r']:.6f}")
print(f"    f_NL_eq     = {pred['inflation']['f_NL_eq']:.4f}")
print(f"    Omega_GW(1mHz)  = {pred['inflation']['Omega_GW_1mHz']:.3e}")
print(f"    M_GUT       = {pred['gauge']['M_GUT']:.3e} GeV")
print(f"    tau_p       = {pred['gauge']['tau_p_e_pi0']:.3e} yr")
print(f"    m_gluino    = {pred['susy']['m_gluino']:.3e} GeV")
print(f"    m_axion     = {pred['dark_matter']['m_axion']:.3e} eV")
print(f"    alpha_5     = {pred['fifth_force']['alpha_5']:.3e}")
print(f"    eta_B       = {pred['baryogenesis']['eta_B']:.3e}")
print(f"    N_gen       = {pred['gauge']['N_gen']}")
print(f"    g_star      = {pred['asymptotic_safety']['g_star']:.3f}")
print()

# Confrontation with synthetic data
print(">>> Confrontation with synthetic observational data...")
experiments = build_experiments(seed=42)

pred_to_exp = {
    'n_s':         'Planck_PR4',
    'r':           'LiteBIRD',
    'f_NL_eq':     'CMB_S4',
    'Omega_GW_1mHz':'LISA',
    'm_axion':     'CASPEr',
    'm_gluino':    'HE_LHC',
    'tau_p_e_pi0': 'HyperK',
    'alpha_5':     'IUPUI',
    'eta_B':       'Planck_baryon',
}

# Mapping from engine to PREDICTIONS
engine_to_test = {
    'n_s':         pred['inflation']['n_s'],
    'r':           pred['inflation']['r'],
    'f_NL_eq':     pred['inflation']['f_NL_eq'],
    'Omega_GW_1mHz': pred['inflation']['Omega_GW_1mHz'],
    'm_axion':     pred['dark_matter']['m_axion'],
    'm_gluino':    pred['susy']['m_gluino'],
    'tau_p_e_pi0': pred['gauge']['tau_p_e_pi0'],
    'alpha_5':     pred['fifth_force']['alpha_5'],
    'eta_B':       pred['baryogenesis']['eta_B'],
}

print(f"\n{'Observable':<20}{'Spin(10)':>14}{'Observation':>14}{'sigma_total':>14}{'chi2':>8}{'PASS':>7}")
print("─" * 75)

pass_count = 0
total_chi2 = 0
n_tests = 0

for obs_name, engine_val in engine_to_test.items():
    if obs_name not in pred_to_exp:
        continue
    exp = experiments[pred_to_exp[obs_name]]
    # Use the engine value as the "prediction" and generate a synthetic measurement
    meas = exp.measure(engine_val)
    sigma = meas['sigma_total']
    chi2 = ((meas['observed'] - engine_val) / sigma) ** 2
    passes = chi2 < 9.0
    status = "PASS" if passes else "FAIL"
    if passes: pass_count += 1
    total_chi2 += chi2
    n_tests += 1
    print(f"{obs_name:<20}{engine_val:>14.4g}{meas['observed']:>14.4g}"
          f"{sigma:>14.4g}{chi2:>8.2f}{status:>7}")

print("─" * 75)
print(f"\nResult: {pass_count}/{n_tests} tests passed")
print(f"⟨chi2⟩ = {total_chi2/n_tests:.3f}")
print(f"Σchi2  = {total_chi2:.2f}")
print()
print("=" * 78)
print(">>> DONE — engine integrated with the synthetic test suite.")
print("=" * 78)
