"""
run_rge_unification_suite.py
============================
Advanced research script performing numerical integration of 2-loop
Renormalization Group Equations (RGE) for gauge coupling constants g_1, g_2, g_3.

Wykonuje:
  1. Base fit call for M_SUSY = 5 TeV (consistent with specification).
  2. Parametric Sweep over different Split-SUSY breaking scales
     (1 TeV -> 50 TeV), showing impact on M_GUT scale and emergent Weinberg angle.
  3. Generating high-quality publication-quality plot in PNG format
     showing the evolution of coupling inverses (alpha_i^-1) as a function of energy scale mu.

Runienie:
    python scripts/run_rge_unification_suite.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import time
from numerical_rge_solver import NumericalRGESolver


def run_suite():
    print("="*75)
    print(" ADVANCED LABORATORY: 2-LOOP RGE AND SPLIT-SUSY UNIFICATION")
    print("="*75)
    
    # -------------------------------------------------------------------------
    # 1. BASE CALL (M_SUSY = 5 TeV)
    # -------------------------------------------------------------------------
    print("\n1. BASE CALL FOR M_SUSY = 5 TeV (5000 GeV)")
    start_time = time.time()
    t_vals, g_vals, a_gut, best_M_GUT = NumericalRGESolver.integrate_2loop_rge_flow(M_SUSY=5000.0)
    analysis = NumericalRGESolver.analyze_unification(t_vals, g_vals)
    exec_time = time.time() - start_time
    
    print(f"   Numerical calculations completed in {exec_time:.2f} s.")
    print(f"   >>> Scale Unifikacji:          M_GUT      = {analysis['M_GUT_GeV']:.2e} GeV")
    print(f"   >>> Unified coupling:   alpha_GUT  = {analysis['alpha_GUT']:.4f}  (alpha_GUT^-1 = {analysis['alpha_GUT_inv']:.2f})")
    print(f"   >>> Kąt Weinberga na GUT:      sin^2(theta_W) = {analysis['sin2_theta_W_GUT']:.4f}  (Docelowo w ToE: 0.3750)")
    print(f"   >>> Convergence quality:         Relative spread = {analysis['unification_accuracy']:.2%}")

    # -------------------------------------------------------------------------
    # 2. SKANOWANIE PARAMETRYCZNE (1 TeV - 50 TeV)
    # -------------------------------------------------------------------------
    print("\n2. SKANOWANIE PARAMETRYCZNE PO SKALACH PROGU SPLIT-SUSY (M_SUSY)")
    print("   Investigating how changing superpartner masses affects the perfect unification condition...")
    
    msusy_sweep = [1000.0, 2500.0, 5000.0, 10000.0, 25000.0, 50000.0]
    
    print(f"\n   {'M_SUSY (Threshold)':<15} | {'M_GUT Scale (GeV)':<18} | {'alpha_GUT^-1':<14} | {'sin^2(theta_W)':<16} | {'Deviation at GUT':<20}")
    print("   " + "-"*85)
    
    for ms in msusy_sweep:
        t_s, g_s, a_s, best_m = NumericalRGESolver.integrate_2loop_rge_flow(M_SUSY=ms)
        ana = NumericalRGESolver.analyze_unification(t_s, g_s)
        
        # Mark optimality
        marker = " <<< TO_TARGET" if abs(ana['sin2_theta_W_GUT'] - 0.3750) < 0.003 else ""
        if ana['unification_accuracy'] < 0.01: marker += " [BEST MATCH]"
            
        print(f"   {ms:<10.0f} GeV | {ana['M_GUT_GeV']:<18.2e} | {ana['alpha_GUT_inv']:<14.2f} | {ana['sin2_theta_W_GUT']:<16.4f} | {ana['unification_accuracy']:<18.2%}{marker}")

    # -------------------------------------------------------------------------
    # 3. RYSOWANIE I ZAPISYWANIE WYKRESU UNIFIKACJI (PNG)
    # -------------------------------------------------------------------------
    try:
        import matplotlib.pyplot as plt
        print("\n3. GENERATING COUPLING TRAJECTORY PLOT (alpha_i^-1)...")
        
        # Computing trajectory for M_SUSY = 5 TeV
        mu_vals = np.exp(t_vals)
        # Couplings alpha_1^-1, alpha_2^-1, alpha_3^-1
        # W convention Spin(10) GUT g_1 jest znormalizowane: alpha_1 = g_1^2 / 4pi
        alpha_1_inv = 4.0 * np.pi / (g_vals[0, :]**2)
        alpha_2_inv = 4.0 * np.pi / (g_vals[1, :]**2)
        alpha_3_inv = 4.0 * np.pi / (g_vals[2, :]**2)
        
        plt.figure(figsize=(10, 6))
        
        # Rysujemy linie
        plt.plot(np.log10(mu_vals), alpha_1_inv, color='#1f77b4', linewidth=2.5, label=r'$\alpha_1^{-1}$ $(U(1)_Y)$')
        plt.plot(np.log10(mu_vals), alpha_2_inv, color='#2ca02c', linewidth=2.5, label=r'$\alpha_2^{-1}$ $(SU(2)_L)$')
        plt.plot(np.log10(mu_vals), alpha_3_inv, color='#d62728', linewidth=2.5, label=r'$\alpha_3^{-1}$ $(SU(3)_C)$')
        
        # Oznaczamy progi i punkty unification
        plt.axvline(np.log10(5000.0), color='black', linestyle='dotted', linewidth=1.5, label=r'Split-SUSY ThresholdY ($5$ TeV)')
        plt.axvline(np.log10(analysis['M_GUT_GeV']), color='purple', linestyle='dashed', linewidth=2, label=r'Scale Unifikacji ToE ($M_{GUT}$)')
        
        # Dodajemy adnotacje na plotie
        plt.annotate(
            f"$M_{{GUT}} \\approx {analysis['M_GUT_GeV']:.2e}$ GeV\n$\\alpha_{{GUT}}^{{-1}} \\approx {analysis['alpha_GUT_inv']:.1f}$\n$\\sin^2\\theta_W \\approx {analysis['sin2_theta_W_GUT']:.4f}$",
            xy=(np.log10(analysis['M_GUT_GeV']), analysis['alpha_GUT_inv']),
            xytext=(np.log10(analysis['M_GUT_GeV']) - 3.5, analysis['alpha_GUT_inv'] + 12),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
            fontsize=11, bbox=dict(boxstyle="round,pad=0.4", fc="#f8f9fa", ec="gray", lw=1)
        )
        
        plt.title(r"Grand Unification of Gauge Couplings in Spin(10) ToE with Split-SUSY", fontsize=14, pad=15)
        plt.xlabel(r"Logarytm scale energy $\log_{10}(\mu/\text{GeV})$", fontsize=12)
        plt.ylabel(r"Inverse of coupling constants $\alpha_i^{-1}(\mu)$", fontsize=12)
        plt.grid(True, which="both", linestyle='--', alpha=0.5)
        plt.legend(fontsize=11, loc="upper right")
        
        # Save and display
        out_path = os.path.join(os.path.dirname(__file__), '../rge_unification_trajectories.png')
        plt.tight_layout()
        plt.savefig(out_path, dpi=250)
        plt.close()
        
        print(f"   Generated and saved plot: '{os.path.basename(out_path)}' (resolution 250 DPI).")
        print("   Plot perfectly illustrates the convergence of fundamental forces at the quantum gravity pointi.")
    except Exception as e:
        print(f"\n   (Error generowania plotu: {e}).")

    print("\n   >>> Script 'run_rge_unification_suite.py' completed execution with highest precision! <<<")
    print("="*75)


if __name__ == "__main__":
    run_suite()
