"""
demo_mukhanov_sasaki_solver.py
==============================
Script demonstracyjny prezentujacy quantum rozwiazanie numeryczne rownania
Mukanova-Sasakiego dla fluktuacji curvature w modelu Spin(10) alpha-Attractor.

Porownuje uzyskane numerycznie pierwotne widmo mocy P_R(k) i indeks spektralny n_s
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
    print(" DEMONSTRACJA: SOLWER KWANTOWEGO ROWNANIA MUKANOVA-SASAKIEGO (INFLACJA ToE)")
    print("="*75)
    
    alpha = 3.75     # Wartosc algebry ToE (SPIN10_DIM / 12 = 45 / 12)
    N_efolds = 60    # Domyslna liczba efolds symulacji
    
    print(f"\n1. GENEROWANIE TLA INFLACYJNEGO (Model alpha-Attractor)")
    print(f"   Parametr algebry:  alpha    = {alpha}")
    print(f"   Liczba e-folds:    N_efolds = {N_efolds}")
    
    start_time = time.time()
    eta_vals, a_eta, z_eta = MukhanovSasakiSolver.generate_inflationary_background(
        alpha=alpha, N_efolds=N_efolds, n_points=1200
    )
    bg_time = time.time() - start_time
    
    print(f"   Siatka time konforemnego eta wygenerowana w {bg_time:.2f} s ({len(eta_vals)} punktow).")
    print(f"   Zakres ewolucji eta: od {eta_vals[0]:.1f} (daleka przeszlosc) do {eta_vals[-1]:.4f} (zamrozenie).")
    
    # 2. Siatka modow k
    # Definiujemy wektory falowe k w poblizu scale referencyjnej k_* = 0.05 Mpc^-1
    k_modes = np.geomspace(0.005, 0.5, 15)
    
    print(f"\n2. NUMERYCZNE ROZWIAZYWANIE KWANTOWYCH ROWNAN MUKANOVA-SASAKIEGO")
    print(f"   Rozwiazywanie ewolucji R_k(eta) dla {len(k_modes)} modow k w siatce nierownomiernej...")
    print(f"   Warunki poczatkowe: Asymptotyczna proznia Buncha-Daviesa (Minkowski).")
    
    sim_start = time.time()
    power_spectrum = MukhanovSasakiSolver.solve_mukhanov_sasaki(
        k_modes=k_modes, eta_vals=eta_vals, a_eta=a_eta, z_eta=z_eta
    )
    sim_time = time.time() - sim_start
    
    print(f"   Solwer quantum zakonczyl computations w {sim_time:.2f} s.")
    
    # 3. Analysis i dopasowanie
    print(f"\n3. ANALIZA I DOPASOWANIE WIDMA MOCY P_R(k)")
    analysis = MukhanovSasakiSolver.analyze_power_spectrum(
        k_modes=k_modes, power_spectrum=power_spectrum, alpha=alpha, N_efolds=N_efolds
    )
    
    print(f"   - Dopasowana amplituda A_s:        A_s = {analysis['A_s']:.2e}   (Dla k_* = {analysis['k_pivot']} Mpc^-1)")
    print(f"   - Otrzymany numerycznie indeks n_s: n_s = {analysis['n_s_numeric']:.4f}")
    print(f"   - Teoretyczny wzor analityczny:    n_s = {analysis['n_s_theoretical']:.4f}   (Formula 1 - 2/N)")
    print(f"   - Przewidywany stosunek r:         r   = {analysis['r_theoretical']:.4f}   (LiteBIRD target)")
    print(f"   - Zgodnosc z satelita Planck:      {analysis['n_s_error_sigma']:.2f}σ od pomiaru Plancka (0.9649 ± 0.0042)")
    print(f"   - Spojnosc numeryki z teoria ToE:  {'IDEALNA ZGODNOSC ✓✓✓' if analysis['excellent_agreement'] else 'TENSION'}")
    
    # 4. Tabela probki modow
    print(f"\n4. TABELA MODOW (Probka pierwotnego widma perturbacji)")
    print(f"   {'Wektor falowy k':<18} | {'P_R(k) (Widmo Mocy)':<22} | {'Odchylenie od scale A_s':<25}")
    print("   " + "-"*70)
    
    for i, k in enumerate(k_modes):
        ratio = power_spectrum[i] / analysis['A_s']
        print(f"   {k:<18.3f} | {power_spectrum[i]:<22.2e} | {ratio:<25.3f}")

    print("\n   >>> Module 'MukhanovSasakiSolver' gotowy do pelnej integracji badawczej! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
