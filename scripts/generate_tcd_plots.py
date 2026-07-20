#!/usr/bin/env python3
"""
Generate TCD plots: d_S(T), w(T), eta/s(T), Polyakov L, string tension
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from termo_chromo_dynamics import ThermoChromoDynamicsEngine

eng = ThermoChromoDynamicsEngine(N=10**6)

# temperature grid log from 1e-3 GeV to 1e19 GeV plus low
T_GeV = np.logspace(-12, 19, 200)  # 1e-12 to 1e19
T_MeV_for_eta = T_GeV*1e3

dS = [eng.coupling.spectral_dimension_T(T) for T in T_GeV]
w = [eng.coupling.equation_of_state_w_T(T) for T in T_GeV]
eta = [eng.chromo.eta_over_s(Tm) for Tm in T_MeV_for_eta if Tm<1000]  # only up to 1 GeV
T_eta = T_MeV_for_eta[T_MeV_for_eta<1000]
L_poly = [eng.chromo.polyakov_loop(T) for T in T_MeV_for_eta if T<500]
T_L = T_MeV_for_eta[T_MeV_for_eta<500]
sigma = [eng.chromo.string_tension(T) for T in T_L]

fig, axes = plt.subplots(2,2, figsize=(13,10))

ax=axes[0,0]
ax.semilogx(T_GeV, dS, 'b-', lw=2)
ax.set_xlabel('T [GeV]'); ax.set_ylabel('d_S')
ax.set_title('TCD Spectral dimension d_S(T): 2 (UV) → 4 (IR)')
ax.grid(True, alpha=0.3)
ax.set_ylim(1.9,4.1)

ax=axes[0,1]
ax.semilogx(T_GeV, w, 'r-', lw=2)
ax.set_xlabel('T [GeV]'); ax.set_ylabel('w = p/ρ')
ax.set_title('Equation of state w(T) in TCD')
ax.grid(True, alpha=0.3)
ax.set_ylim(-1.1,0.5)

ax=axes[1,0]
ax.plot(T_eta, eta, 'g-', lw=2, label='η/s TCD')
ax.axhline(1/(4*np.pi), color='k', ls='--', label='KSS bound 1/4π')
ax.axvline(155, color='r', ls='--', alpha=0.5, label='T_c 155 MeV')
ax.set_xlabel('T [MeV]'); ax.set_ylabel('η/s')
ax.set_title('Viscosity η/s — minimum at T_c (RHIC 0.09)')
ax.legend(); ax.grid(True, alpha=0.3)
ax.set_xlim(0,1000)

ax=axes[1,1]
ax.plot(T_L, L_poly, 'm-', lw=2, label='Polyakov L')
ax.plot(T_L, sigma, 'c--', lw=2, label='σ(T) [GeV²]')
ax.axvline(155, color='r', ls='--', alpha=0.5, label='T_c')
ax.set_xlabel('T [MeV]'); ax.set_ylabel('L / σ')
ax.set_title('Polyakov loop (CF analog) & string tension')
ax.legend(); ax.grid(True, alpha=0.3)

fig.suptitle('Termo-Chromo-Dynamika as TOE — v15.0-TCD — 4 key plots', fontsize=13, fontweight='bold')
fig.tight_layout(rect=[0,0.03,1,0.95])
out = 'results/tcd_plots_v15.png'
os.makedirs('results', exist_ok=True)
fig.savefig(out, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f"[PLOT] Saved {out}")
