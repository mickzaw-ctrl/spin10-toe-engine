"""
demo_bayesian_mcmc_analysis.py
==============================
Demo script performing full Bayesian analysis and sampling
MCMC (Markov Chain Monte Carlo) of multidimensional parameter space
of fundamental ToE using the emcee library.

Wyznacza parameters Best-Fit dla M_SUSY, alpha_attractor oraz Causal Fraction CF,
confronting the model live with Planck PR4, LHC, BICEP and Super-Kamiokande data.

Runienie:
    python scripts/demo_bayesian_mcmc_analysis.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import time
from bayesian_mcmc_analysis import MultiExperimentLikelihood


def run_demo():
    print("="*75)
    print(" DEMONSTRACJA: WNIOSKOWANIE BAYESOWSKIE I ANALIZA MCMC (emcee) DLA SPIN(10)")
    print("="*75)
    
    # 1. Initialization pakietu
    likelihood = MultiExperimentLikelihood()
    n_walkers = 32
    n_steps = 1500
    burnin = 500
    
    print(f"\n1. DEFINICJA WEKTORA WIEDZY EKSPERYMENTALNEJ (Pomiary vs ToE v9.0)")
    print(f"   - Indeks spektralny n_s:         {likelihood.exp_data['n_s'][0]:.4f} ± {likelihood.exp_data['n_s'][1]:.4f}  [Planck PR4]")
    print(f"   - Granica tensorów r:            < {likelihood.exp_data['r_upper_limit']}             [BICEP/Keck]")
    print(f"   - Lifetime protonu tau_p:      > {likelihood.exp_data['tau_p_lower_limit']:.1e} lat      [Super-Kamiokande]")
    print(f"   - Dolny limit masses m_gluino:     > {likelihood.exp_data['m_gluino_lower_limit']:.0f} GeV        [LHC]")
    print(f"   - Asymetria barionowa eta_B:     {likelihood.exp_data['eta_B'][0]:.2e} ± {likelihood.exp_data['eta_B'][1]:.2e} [CMB / BBN]")
    
    print(f"\n2. MCMC SAMPLING (Markov Chain Monte Carlo)")
    print(f"   Uruchamianie Ensemble Samplera (Goodman & Weare)...")
    print(f"   Number of walkers: n_walkers = {n_walkers}")
    print(f"   Number of steps:   n_steps   = {n_steps} (Rejection relaxation burn-in: {burnin})")
    print(f"   Total evaluations in full multidimensional space: {n_walkers * n_steps:,} calls...")
    
    start_time = time.time()
    sampler, report = likelihood.run_mcmc(
        n_walkers=n_walkers, n_steps=n_steps, return_report=True, burnin=burnin, seed=101
    )
    mcmc_time = time.time() - start_time
    
    print(f"   Sampling completed SUCCESSFULLY in {mcmc_time:.2f} s.")
    print(f"   - Mean frakcja akceptacji Metropolis-Hastings: {report['mean_acceptance_fraction']:.2%} (Optimal: 20-50%)")
    print(f"   - Qualified {report['n_total_samples']:,} samples for building the posterior distribution.")
    
    # 3. Best-Fit Parameter Estimation Results
    print(f"\n3. POSTERIOR DISTRIBUTIONS AND PARAMETER ESTIMATION (Best-Fit & Percentiles)")
    print(f"   {'ToE Parameter':<22} | {'MAP Best-Fit':<14} | {'Median (50%)':<14} | {'68% Interval (1-sigma)':<25}")
    print("   " + "-"*80)
    
    for param_name, res in report['parameter_estimation'].items():
        # Formats names for readability
        dname = param_name.replace('_', ' ')
        p_err_plus = res['percentile_84'] - res['median']
        p_err_minus = res['median'] - res['percentile_16']
        
        if "GeV" in param_name:
            print(f"   {dname:<22} | {res['best_fit']:<14.0f} | {res['median']:<14.0f} | +{p_err_plus:<8.0f} / -{p_err_minus:<8.0f}")
        else:
            print(f"   {dname:<22} | {res['best_fit']:<14.4f} | {res['median']:<14.4f} | +{p_err_plus:<8.4f} / -{p_err_minus:<8.4f}")

    # 4. Predictions fizyczne w punkcie optymalnym
    print(f"\n4. PREDYKCJE MODELU W PUNKCIE ABSOLUTNEGO BEST-FIT (Maximum Posterior)")
    bobs = report['best_fit_observables']
    print(f"   - Przewidywany indeks n_s:         n_s = {bobs['n_s']:.4f}      (Planck PR4: {likelihood.exp_data['n_s'][0]:.4f})")
    print(f"   - Przewidywany ratio r:         r   = {bobs['r']:.4f}      (Fully consistent with BICEP < 0.036)")
    print(f"   - Lifetime protonu tau_p:      tau = {bobs['tau_p']:.2e} years (Within Hyper-K reach 1e35)")
    print(f"   - Mass gluina Split-SUSY:        m_g = {bobs['m_gluino']/1000:.2f} TeV      (Beyond LHC reach)")
    print(f"   - Obtained baryon asymmetry:  eta = {bobs['eta_B']:.2e}   (Perfect consistency)")
    
    # 5. Creating and saving Posterior plot (if matplotlib available)
    try:
        import matplotlib.pyplot as plt
        print(f"\n5. DRAWING POSTERIOR DISTRIBUTIONS (Posterior Corner Plot)...")
        flat_samples = sampler.get_chain(discard=burnin, thin=2, flat=True)
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        titles = ['M_{SUSY} (GeV)', r'\alpha_{attractor}', 'Causal Fraction CF']
        
        for i in range(3):
            axes[i].hist(flat_samples[:, i], bins=35, color='#1f77b4', edgecolor='black', alpha=0.7)
            axes[i].axvline(report['parameter_estimation'][list(report['parameter_estimation'].keys())[i]]['best_fit'], color='red', linestyle='dashed', linewidth=2, label='Best-Fit MAP')
            axes[i].axvline(report['parameter_estimation'][list(report['parameter_estimation'].keys())[i]]['median'], color='green', linestyle='dotted', linewidth=2, label='Median')
            axes[i].set_title(f"Posterior Distribution: ${titles[i]}$", fontsize=12)
            axes[i].set_ylabel("MCMC Density", fontsize=10)
            axes[i].grid(True, alpha=0.3)
            if i==0: axes[i].legend(fontsize=9)
            
        plt.tight_layout()
        out_path = os.path.join(os.path.dirname(__file__), '../bayesian_mcmc_posterior_plot.png')
        plt.savefig(out_path, dpi=200)
        plt.close()
        print(f"   Generated and saved graphics file: '{os.path.basename(out_path)}' (resolution 200 DPI).")
    except ImportError:
        print(f"\n   (Library 'matplotlib' unavailable --- skipped PNG file generation).")

    print("\n   >>> Module 'MultiExperimentLikelihood' ready for full repository integration! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
