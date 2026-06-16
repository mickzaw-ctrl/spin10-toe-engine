"""
demo_numerical_rge_solver.py
============================
Demo script presenting numerical integration of 2-loop and 1-loop
Renormalization Group Equations (RGE) for coupling constants g_1, g_2, g_3.

Shows coupling evolution from the electroweak scale (M_Z) to the unification scale (M_GUT),
including the intermediate Split-SUSY threshold at M_SUSY = 5 TeV.

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
    print(" DEMONSTRATION: NUMERICAL INTEGRATION OF 2-LOOP RGE EQUATIONS (SPLIT-SUSY)")
    print("="*75)
    
    M_SUSY = 5000.0  # 5 TeV (Split-SUSY Remedy #1)
    M_GUT_target = 2.0e16
    
    print(f"\n1. WARUNKI POCZĄTKOWE I MODEL FIZYCZNY")
    print(f"   Scale elektrosłaba:        M_Z    = 91.19 GeV")
    print(f"   SUSY switching threshold:    M_SUSY = {M_SUSY:.0f} GeV ({M_SUSY/1000:.1f} TeV)")
    print(f"   Docelowa scale unifikacji: M_GUT  = {M_GUT_target:.1e} GeV")
    print(f"   Konwencja unifikacji:      g_1(M_Z) = sqrt(5/3) g_Y(M_Z)")
    
    # -------------------------------------------------------------------------
    # 2. 1-LOOP INTEGRATION
    # -------------------------------------------------------------------------
    print(f"\n2. 1-LOOP INTEGRATION (With Threshold Switching)")
    start_1 = time.time()
    t_1, g_1_vals, a_gut_1, best_gut_1 = NumericalRGESolver.integrate_1loop_rge_flow(
        M_SUSY=M_SUSY, M_GUT_target=M_GUT_target
    )
    time_1 = time.time() - start_1
    
    res_1 = NumericalRGESolver.analyze_unification(t_1, g_1_vals)
    
    print(f"   1-loop integration completed in {time_1:.2f} s.")
    print(f"   - Wyznaczona scale unifikacji: M_GUT      = {res_1['M_GUT_GeV']:.2e} GeV")
    print(f"   - Unified coupling constant:    alpha_GUT  = {res_1['alpha_GUT']:.4f} (1/alpha_GUT = {res_1['alpha_GUT_inv']:.1f})")
    print(f"   - Convergence accuracy:       Deviation = {res_1['unification_accuracy']:.2%}")
    
    # -------------------------------------------------------------------------
    # 3. 2-LOOP INTEGRATION
    # -------------------------------------------------------------------------
    print(f"\n3. FULL 2-LOOP INTEGRATION (High Precision)")
    start_2 = time.time()
    t_2, g_2_vals, a_gut_2, best_gut_2 = NumericalRGESolver.integrate_2loop_rge_flow(
        M_SUSY=M_SUSY, M_GUT_target=M_GUT_target
    )
    time_2 = time.time() - start_2
    
    res_2 = NumericalRGESolver.analyze_unification(t_2, g_2_vals)
    
    print(f"   2-loop integration completed in {time_2:.2f} s.")
    print(f"   - Optymalna scale unifikacji:  M_GUT      = {res_2['M_GUT_GeV']:.2e} GeV")
    print(f"   - Precyzyjne alpha_GUT:        alpha_GUT  = {res_2['alpha_GUT']:.4f} (1/alpha_GUT = {res_2['alpha_GUT_inv']:.2f})")
    print(f"   - Kąt Weinberga sin^2(theta_W): {res_2['sin2_theta_W_GUT']:.4f}   (Theora ToE: {res_2['sin2_theta_W_GUT_theoretical']:.4f})")
    print(f"   - Consistency with ToE unification:   {'POSITIVE ✓✓✓' if res_2['perfect_unification_passed'] else 'WYMAGA KOREKTY PROGU'}")
    
    # -------------------------------------------------------------------------
    # 4. TABELA TRAJEKTORII (Próbka ewolucji 2-loop)
    # -------------------------------------------------------------------------
    print(f"\n4. COUPLING TRAJECTORY (2-loop evolution as a function of scale mu)")
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
        elif abs(actual_mu - M_SUSY) < M_SUSY*0.2: remark = "Próg Split-SUSY"
        elif abs(actual_mu - res_2['M_GUT_GeV']) < res_2['M_GUT_GeV']*0.2: remark = "Scale Unifikacji ToE"
            
        print(f"   {actual_mu:<15.1e} | {g1:<12.4f} | {g2:<12.4f} | {g3:<12.4f} | {remark:<20}")

    print("\n   >>> Module 'NumericalRGESolver' ready for full integration with ToE analytics! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
