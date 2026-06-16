"""
demo_numerical_rge_solver.py
============================
Script demonstracyjny prezentujacy numeryczne calkowanie 2-petlowych i 1-petlowych
Rownan Grupy Renormalizacji (RGE) dla stalych sprzezenia g_1, g_2, g_3.

Pokazuje ewolucje sprzezen od scale elektroslabej (M_Z) do scale unification (M_GUT),
uwzgledniajac posredni prog Split-SUSY na scale M_SUSY = 5 TeV.

Runienie:
    python scripts/demo_numerical_rge_solver.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import time
from numerical_rge_solver import NumericalRGESolver


def run_demo():
    print("="*75)
    print(" DEMONSTRACJA: NUMERYCZNE CALKOWANIE 2-PETLOWYCH ROWNAN RGE (SPLIT-SUSY)")
    print("="*75)
    
    M_SUSY = 5000.0  # 5 TeV (Split-SUSY Remedy #1)
    M_GUT_target = 2.0e16
    
    print(f"\n1. WARUNKI POCZATKOWE I MODEL FIZYCZNY")
    print(f"   Scale elektroslaba:        M_Z    = 91.19 GeV")
    print(f"   Prog przelaczenia SUSY:    M_SUSY = {M_SUSY:.0f} GeV ({M_SUSY/1000:.1f} TeV)")
    print(f"   Docelowa scale unification: M_GUT  = {M_GUT_target:.1e} GeV")
    print(f"   Konwencja unification:      g_1(M_Z) = sqrt(5/3) g_Y(M_Z)")
    
    # -------------------------------------------------------------------------
    # 2. CALKOWANIE 1-PETLOWE
    # -------------------------------------------------------------------------
    print(f"\n2. CALKOWANIE 1-PETLOWE (Z Przelacznikiem Progowym)")
    start_1 = time.time()
    t_1, g_1_vals, a_gut_1, best_gut_1 = NumericalRGESolver.integrate_1loop_rge_flow(
        M_SUSY=M_SUSY, M_GUT_target=M_GUT_target
    )
    time_1 = time.time() - start_1
    
    res_1 = NumericalRGESolver.analyze_unification(t_1, g_1_vals)
    
    print(f"   Calkowanie 1-petlowe zakonczone w {time_1:.2f} s.")
    print(f"   - Wyznaczona scale unification: M_GUT      = {res_1['M_GUT_GeV']:.2e} GeV")
    print(f"   - Wspolna stala sprzezenia:    alpha_GUT  = {res_1['alpha_GUT']:.4f} (1/alpha_GUT = {res_1['alpha_GUT_inv']:.1f})")
    print(f"   - Dokladnosc zbieznosci:       Rozbieznosc = {res_1['unification_accuracy']:.2%}")
    
    # -------------------------------------------------------------------------
    # 3. CALKOWANIE 2-PETLOWE
    # -------------------------------------------------------------------------
    print(f"\n3. PELNE CALKOWANIE 2-PETLOWE (Wysoka Precyzja)")
    start_2 = time.time()
    t_2, g_2_vals, a_gut_2, best_gut_2 = NumericalRGESolver.integrate_2loop_rge_flow(
        M_SUSY=M_SUSY, M_GUT_target=M_GUT_target
    )
    time_2 = time.time() - start_2
    
    res_2 = NumericalRGESolver.analyze_unification(t_2, g_2_vals)
    
    print(f"   Calkowanie 2-petlowe zakonczone w {time_2:.2f} s.")
    print(f"   - Optymalna scale unification:  M_GUT      = {res_2['M_GUT_GeV']:.2e} GeV")
    print(f"   - Precyzyjne alpha_GUT:        alpha_GUT  = {res_2['alpha_GUT']:.4f} (1/alpha_GUT = {res_2['alpha_GUT_inv']:.2f})")
    print(f"   - Kat Weinberga sin^2(theta_W): {res_2['sin2_theta_W_GUT']:.4f}   (Teoria ToE: {res_2['sin2_theta_W_GUT_theoretical']:.4f})")
    print(f"   - Zgodnosc z unifikacja ToE:   {'POZYTYWNA ✓✓✓' if res_2['perfect_unification_passed'] else 'WYMAGA KOREKTY PROGU'}")
    
    # -------------------------------------------------------------------------
    # 4. TABELA TRAJEKTORII (Probka ewolucji 2-loop)
    # -------------------------------------------------------------------------
    print(f"\n4. TRAJEKTORIA SPRZEZEN (Ewolucja 2-petlowa w function scale mu)")
    print(f"   {'Scale mu (GeV)':<15} | {'g_1 (U(1))':<12} | {'g_2 (SU(2))':<12} | {'g_3 (SU(3))':<12} | {'Uwagi':<20}")
    print("   " + "-"*70)
    
    # Wybieramy konkretne punkty do zaprezentowania
    sample_scales = [91.2, 1000.0, 5000.0, 1e7, 1e11, 1e14, res_2['M_GUT_GeV'], 2.0e16]
    mu_2_vals = np.exp(t_2)
    
    for s in sample_scales:
        idx = np.argmin(abs(mu_2_vals - s))
        actual_mu = mu_2_vals[idx]
        g1, g2, g3 = g_2_vals[:, idx]
        
        remark = ""
        if abs(actual_mu - 91.2) < 10: remark = "Scale Z (SM)"
        elif abs(actual_mu - M_SUSY) < M_SUSY*0.2: remark = "Prog Split-SUSY"
        elif abs(actual_mu - res_2['M_GUT_GeV']) < res_2['M_GUT_GeV']*0.2: remark = "Scale Unifikacji ToE"
            
        print(f"   {actual_mu:<15.1e} | {g1:<12.4f} | {g2:<12.4f} | {g3:<12.4f} | {remark:<20}")

    print("\n   >>> Module 'NumericalRGESolver' gotowy do pelnej integracji z analityka ToE! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
