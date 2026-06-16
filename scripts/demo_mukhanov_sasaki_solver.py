"""
demo_mukhanov_sasaki_solver.py
==============================
Demo script presenting numerical quantum solution of the equation
Mukanova-Sasakiego dla fluktuacji krzywizny w modelu Spin(10) alpha-Attractor.

Compares numerically obtained primordial power spectrum P_R(k) and spectral index n_s
z oczekiwaniami teoretycznymi oraz pomiarami satelity Planck.

Runienie:
    python scripts/demo_mukhanov_sasaki_solver.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import time
from mukhanov_sasaki_solver import MukhanovSasakiSolver


def run_demo():
    print("="*75)
    print(" DEMONSTRATION: MUKHANOV-SASAKI QUANTUM EQUATION SOLVER (ToE INFLATION)")
    print("="*75)
    
    alpha = 3.75     # Value algebry ToE (SPIN10_DIM / 12 = 45 / 12)
    N_efolds = 60    # Default number of simulation efolds
    
    print(f"\n1. GENERATING INFLATIONARY BACKGROUND (alpha-Attractor Model)")
    print(f"   Parametr algebry:  alpha    = {alpha}")
    print(f"   Liczba e-folds:    N_efolds = {N_efolds}")
    
    start_time = time.time()
    eta_vals, a_eta, z_eta = MukhanovSasakiSolver.generate_inflationary_background(
        alpha=alpha, N_efolds=N_efolds, n_points=1200
    )
    bg_time = time.time() - start_time
    
    print(f"   Conformal time eta grid generated in {bg_time:.2f} s ({len(eta_vals)} punktów).")
    print(f"   Evolution range eta: from {eta_vals[0]:.1f} (far past) to {eta_vals[-1]:.4f} (freezing).")
    
    # 2. k-mode grid
    # Defining wavenumber vectors k near the reference scale k_* = 0.05 Mpc^-1
    k_modes = np.geomspace(0.005, 0.5, 15)
    
    print(f"\n2. NUMERICAL SOLVING OF MUKHANOV-SASAKI QUANTUM EQUATIONS")
    print(f"   Solving R_k(eta) evolution for {len(k_modes)} k-modes on non-uniform grid...")
    print(f"   Initial conditions: Bunch-Davies asymptotic vacuum (Minkowski).")
    
    sim_start = time.time()
    power_spectrum = MukhanovSasakiSolver.solve_mukhanov_sasaki(
        k_modes=k_modes, eta_vals=eta_vals, a_eta=a_eta, z_eta=z_eta
    )
    sim_time = time.time() - sim_start
    
    print(f"   Quantum solver completed calculations in {sim_time:.2f} s.")
    
    # 3. Analysis i dopasowanie
    print(f"\n3. ANALIZA I DOPASOWANIE WIDMA MOCY P_R(k)")
    analysis = MukhanovSasakiSolver.analyze_power_spectrum(
        k_modes=k_modes, power_spectrum=power_spectrum, alpha=alpha, N_efolds=N_efolds
    )
    
    print(f"   - Dopasowana amplituda A_s:        A_s = {analysis['A_s']:.2e}   (Dla k_* = {analysis['k_pivot']} Mpc^-1)")
    print(f"   - Otrzymany numerycznie indeks n_s: n_s = {analysis['n_s_numeric']:.4f}")
    print(f"   - Theoretical analytical formula:    n_s = {analysis['n_s_theoretical']:.4f}   (Formula 1 - 2/N)")
    print(f"   - Przewidywany ratio r:         r   = {analysis['r_theoretical']:.4f}   (LiteBIRD target)")
    print(f"   - Consistency with Planck satellite:      {analysis['n_s_error_sigma']:.2f}σ from Planck measurementcka (0.9649 ± 0.0042)")
    print(f"   - Numerical consistency with ToE theory:  {'PERFECT AGREEMENT ✓✓✓' if analysis['excellent_agreement'] else 'TENSION'}")
    
    # 4. Mode sample table
    print(f"\n4. MODE TABLE (Sample of primordial perturbation spectrum)")
    print(f"   {'Wektor falowy k':<18} | {'P_R(k) (Widmo Mocy)':<22} | {'Deviation od scale A_s':<25}")
    print("   " + "-"*70)
    
    for i, k in enumerate(k_modes):
        ratio = power_spectrum[i] / analysis['A_s']
        print(f"   {k:<18.3f} | {power_spectrum[i]:<22.2e} | {ratio:<25.3f}")

    print("\n   >>> Module 'MukhanovSasakiSolver' ready for full research integration! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
