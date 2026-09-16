"""
run_experimental_confrontation.py
=================================
Confronts the ACTUAL numerical output of ``SHZSpin10QuantumEngineV9`` with
published experimental measurements.

Unlike ``konfrontacja_dane_2026.py`` (whose verdict columns are literal
strings), every verdict printed here is computed at run time from the engine
report and a frozen table of published data.

Two independent axes are reported for every row:

  1. DATA       - does the number agree with measurement / survive the limit?
  2. DERIVATION - is the number actually computed, or is it a hard-coded or
                  data-tuned constant? A constant fitted to the measurement
                  cannot count as a confirmation.

Verdicts
  AGREE      |deviation| < 2 sigma, or inside the quoted experimental limit
  TENSION    2-3 sigma
  EXCLUDED   > 3 sigma, or the limit is violated
  NO-DATA    no measurement exists yet for this observable

Run:
    PYTHONPATH=src python scripts/run_experimental_confrontation.py
    PYTHONPATH=src python scripts/run_experimental_confrontation.py --json results/exp.json
"""

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# ----------------------------------------------------------------------------
# Frozen experimental data.  Sources are quoted per entry and are never
# recomputed here - these are inputs, not predictions.
# ----------------------------------------------------------------------------
PLANCK18 = 'Planck 2018 VI (TT,TE,EE+lowE+lensing), arXiv:1807.06209'
PLANCK18_NG = 'Planck 2018 IX, arXiv:1905.05697'
BK18 = 'BICEP/Keck BK18 (95% CL), Phys. Rev. Lett. 127, 151301 (2021)'
ACT_DR6 = 'ACT DR6 (2025)'
SK = 'Super-Kamiokande I-IV, 450 kton.yr, PRD 102, 112011 (2020)'
ATLAS = 'ATLAS 13 TeV 139 fb^-1, JHEP 02 (2021) 143'
PDG = 'PDG 2024'

# ln(10^10 As) = 3.044 +- 0.014  ->  As = 2.099e-9 * (1 +- 1.4%)
AS_OBS = math.exp(3.044) * 1e-10
AS_SIG = AS_OBS * 0.014

EXP = {
    'n_s':      {'value': 0.9649, 'sigma': 0.0042, 'kind': 'measurement', 'source': PLANCK18},
    'n_s_ACT':  {'value': 0.9660, 'sigma': 0.0046, 'kind': 'measurement', 'source': ACT_DR6},
    'A_s':      {'value': AS_OBS, 'sigma': AS_SIG, 'kind': 'measurement', 'source': PLANCK18},
    'r_0.05':   {'value': 0.036, 'sigma': None, 'kind': 'upper_limit', 'cl': '95% CL', 'source': BK18},
    'f_NL_eq':  {'value': -26.0, 'sigma': 47.0, 'kind': 'measurement', 'source': PLANCK18_NG},
    'eta_B':    {'value': 6.104e-10, 'sigma': 0.041e-10, 'kind': 'measurement',
                 'source': PLANCK18 + ' (Omega_b h^2 = 0.02237 +- 0.00015)'},
    'Omega_ch2': {'value': 0.1200, 'sigma': 0.0012, 'kind': 'measurement', 'source': PLANCK18},
    'tau_p':    {'value': 2.4e34, 'sigma': None, 'kind': 'lower_limit', 'cl': '90% CL', 'source': SK},
    'm_gluino': {'value': 2.30e3, 'sigma': None, 'kind': 'lower_limit', 'cl': '95% CL',
                 'source': ATLAS + ' (massless LSP)'},
    'rho_Lam':  {'value': 1.1e-123, 'sigma': None, 'kind': 'measurement',
                 'source': 'Planck 2018 LambdaCDM (rho_Lambda / rho_Planck)'},
}

# Planck energy density, J/m^3 = c^7 / (hbar G^2).  Used only to express the
# engine's dimensionless Planck-unit Lambda in physical units.
RHO_PLANCK_J_M3 = 4.633e113
RHO_LAMBDA_J_M3 = 5.31e-10

# QCD axion relation, PDG review:  m_a ~= 5.7 ueV * (1e12 GeV / f_a)
AXION_MASS_COEF_eV = 5.7e-6 * 1e12

DERIVED = 'computed'
FITTED = 'tuned-to-data'
HARD = 'hard-coded'


def sigmas(pred, obs, sig):
    return abs(pred - obs) / sig


def verdict_from_sigma(n_sig):
    if n_sig < 2.0:
        return 'AGREE'
    if n_sig < 3.0:
        return 'TENSION'
    return 'EXCLUDED'


def verdict_from_limit(pred, limit, kind):
    if kind == 'upper_limit':
        return 'AGREE' if pred < limit else 'EXCLUDED'
    if kind == 'lower_limit':
        return 'AGREE' if pred > limit else 'EXCLUDED'
    raise ValueError(kind)


def fmt(v):
    if v is None:
        return 'n/a'
    a = abs(v)
    if a != 0 and (a < 1e-3 or a >= 1e5):
        return '{:.3e}'.format(v)
    return '{:.6g}'.format(v)


def build_rows(rep):
    """Compare engine output with EXP; every verdict is computed here."""
    rows = []
    obs = rep['observables']
    pred = rep['predictions']
    pv7 = rep['predictions_v7']

    ms = pv7['mukhanov_sasaki_spectrum']
    rge = pv7['two_loop_rge']
    bayes = pv7['bayesian_mcmc_estimation']['best_fit_observables']

    def add(name, pred_val, key, derivation, note=''):
        d = EXP[key]
        if d['kind'] == 'measurement':
            n = sigmas(pred_val, d['value'], d['sigma'])
            verdict = verdict_from_sigma(n)
            dev = '{:+.2f} sigma'.format((pred_val - d['value']) / d['sigma'])
            data = '{} +- {}'.format(fmt(d['value']), fmt(d['sigma']))
        else:
            n = None
            verdict = verdict_from_limit(pred_val, d['value'], d['kind'])
            dev = 'margin x{:.3g}'.format(
                pred_val / d['value'] if d['kind'] == 'lower_limit' else d['value'] / pred_val)
            op = '>' if d['kind'] == 'lower_limit' else '<'
            data = '{} {} ({})'.format(op, fmt(d['value']), d.get('cl', '95% CL'))
        rows.append({
            'observable': name,
            'engine_value': pred_val,
            'experimental': data,
            'deviation': dev,
            'n_sigma': n,
            'data_verdict': verdict,
            'derivation': derivation,
            'source': d['source'],
            'note': note,
        })

    # ---- cosmology -------------------------------------------------------
    add('n_s (numeric Mukhanov-Sasaki solver)', ms['n_s_numeric'], 'n_s', DERIVED,
        'genuine numerical integration of the MS equation')
    add('n_s (analytic alpha-attractor 1-2/N)', pred['inflation']['n_s'], 'n_s', DERIVED,
        'N=60 e-folds assumed, alpha = dim(Spin10)/12 = 3.75')
    add('n_s (numeric) vs ACT DR6', ms['n_s_numeric'], 'n_s_ACT', DERIVED,
        'independent second data set')
    add('A_s (Mukhanov-Sasaki solver)', ms['A_s'], 'A_s', DERIVED,
        'same solver run that produces n_s; amplitude is NOT normalised to data')
    add('r_0.05 (tensor-to-scalar)', pred['inflation']['r'], 'r_0.05', DERIVED,
        'r = 12 alpha / N^2 with N = 60')
    add('f_NL^equil (engine)', pred['f_NL_equil'], 'f_NL_eq', DERIVED,
        '45 * 0.32^2 * 0.1; docs quote 14.5 which this code never produces')
    add('eta_B (baryon asymmetry)', pred['baryon_asymmetry']['eta_B_total'], 'eta_B', FITTED,
        'eta_B_res * F_3flavour with F_3flavour = 4.27e11 hard-coded to land on the data')
    add('Omega_a h^2 (axion DM)', pred['axion']['Omega_h2'], 'Omega_ch2', FITTED,
        'theta_req = 0.0031 chosen so that Omega_a h^2 = 0.12')

    # ---- particle physics ------------------------------------------------
    add('tau(p -> e+ pi0)', pred['proton_decay']['tau_e_pi0'], 'tau_p', HARD,
        '1.4e36 yr normalisation constant, rescaled by cos(Phi) and Var_k')
    add('m_gluino (MCMC best fit)', bayes['m_gluino'], 'm_gluino', FITTED,
        'posterior mode of a prior-dominated MCMC, not a mass calculation')

    # ---- quantities with no measurement yet ------------------------------
    rows.append({
        'observable': 'M_GUT (2-loop RGE from PDG couplings at M_Z)',
        'engine_value': rge['M_GUT'],
        'experimental': 'no direct measurement',
        'deviation': 'g_i spread {:.2%} at M_GUT'.format(rge['unification_accuracy_variance']),
        'n_sigma': None,
        'data_verdict': 'NO-DATA',
        'derivation': DERIVED,
        'source': 'input: g(M_Z) = (0.462, 0.652, 1.221) ~ PDG ' + PDG,
        'note': 'data-driven input, but unification scale itself is untested',
    })
    rows.append({
        'observable': 'sin^2(theta_W) at M_GUT vs 3/8',
        'engine_value': rge['sin2_theta_W_GUT'],
        'experimental': '3/8 = 0.375 (GUT boundary condition, not a measurement)',
        'deviation': '{:+.2%}'.format(rge['sin2_theta_W_GUT'] / 0.375 - 1.0),
        'n_sigma': None,
        'data_verdict': 'NO-DATA',
        'derivation': DERIVED,
        'source': PDG,
        "note": "engine's own passes_3sigma_unification test returns "
                + str(rep['tests_v7']['two_loop_unification']['passes_3sigma_unification']),
    })
    rows.append({
        'observable': 'd_S (spectral dimension, UV -> IR)',
        'engine_value': obs['d_S_UV'],
        'experimental': 'no measurement',
        'deviation': 'random walk returns {:.3f} -> {:.3f}'.format(obs['d_S_UV'], obs['d_S_IR']),
        'n_sigma': None,
        'data_verdict': 'NO-DATA',
        'derivation': HARD,
        'source': 'engine Monte Carlo',
        'note': 'README claims "2.0 (UV) -> 4.0 (IR)"; the run goes the other way '
                'and never reaches 4',
    })
    rows.append({
        'observable': 'CF (causal fraction)',
        'engine_value': obs['CF'],
        'experimental': 'no measurement',
        'deviation': 'n/a',
        'n_sigma': None,
        'data_verdict': 'NO-DATA',
        'derivation': HARD,
        'source': 'engine Monte Carlo',
        'note': 'graph observable with no experimental counterpart',
    })

    # ---- cosmological constant: the one QG number that is measurable -----
    lam = pred['Lambda']['Lambda_Lor']
    rho = lam * RHO_PLANCK_J_M3
    ratio = rho / RHO_LAMBDA_J_M3
    rows.append({
        'observable': 'rho_Lambda (engine, Planck units -> J/m^3)',
        'engine_value': rho,
        'experimental': '{} J/m^3 (= 1.1e-123 rho_Planck)'.format(fmt(RHO_LAMBDA_J_M3)),
        'deviation': 'x{:.2e} too large ({:.0f} orders)'.format(ratio, math.log10(ratio)),
        'n_sigma': None,
        'data_verdict': 'EXCLUDED',
        'derivation': HARD,
        'source': EXP['rho_Lam']['source'],
        'note': 'Lambda = (3/4)(1-cos Phi) + Var_k + ... in units of M_Pl^4; '
                'Lambda_Lor_eq is a hard-coded 0.0',
    })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nodes', type=int, default=200)
    ap.add_argument('--steps', type=int, default=400)
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    from spin10_engine_v9 import SHZSpin10QuantumEngineV9

    t0 = time.time()
    print('=' * 100)
    print(' SPIN(10) ToE ENGINE vs PUBLISHED EXPERIMENTAL DATA')
    print('=' * 100)
    print('\n[1] Running engine: N={} nodes, {} Monte Carlo steps + MS/RGE/MCMC solvers ...'.format(
        args.nodes, args.steps))
    engine = SHZSpin10QuantumEngineV9(N=args.nodes, k_target=4)
    engine.run_simulation(n_steps=args.steps, verbose=False)
    rep = engine.full_report_v7()
    print('    done in {:.1f} s  ({})'.format(time.time() - t0, rep['engine_version']))

    rows = build_rows(rep)

    print('\n[2] Confrontation (all verdicts computed at run time)')
    hdr = '  {:<40} {:>13} {:>24} {:>22} {:>9} {:<12}'
    print(hdr.format('OBSERVABLE', 'ENGINE', 'DATA / LIMIT', 'DEVIATION', 'SIGMA', 'VERDICT'))
    print('  ' + '-' * 122)
    for r in rows:
        ns = '{:.2f}'.format(r['n_sigma']) if r['n_sigma'] is not None else '-'
        print('  {:<40} {:>13} {:>24} {:>22} {:>9} {:<12}'.format(
            r['observable'][:40], fmt(r['engine_value']), r['experimental'][:24],
            r['deviation'][:22], ns, r['data_verdict']))

    print('\n[3] Derivation status (is the number computed at all?)')
    print('  ' + '-' * 122)
    for r in rows:
        print('  {:<40} {:<14} {}'.format(r['observable'][:40], r['derivation'], r['note']))

    counts = {}
    for r in rows:
        counts[r['data_verdict']] = counts.get(r['data_verdict'], 0) + 1
    derived_counts = {}
    for r in rows:
        derived_counts[r['derivation']] = derived_counts.get(r['derivation'], 0) + 1

    chi2 = sum((r['n_sigma'] ** 2) for r in rows if r['n_sigma'] is not None)
    ndof = sum(1 for r in rows if r['n_sigma'] is not None)

    print('\n[4] Summary')
    print('  rows confronted          : {}'.format(len(rows)))
    print('  data verdicts            : {}'.format(
        ', '.join('{}={}'.format(k, counts[k]) for k in sorted(counts))))
    print('  derivation status        : {}'.format(
        ', '.join('{}={}'.format(k, derived_counts[k]) for k in sorted(derived_counts))))
    print('  chi^2 over measured rows : {:.2f} / {} = {:.2f}'.format(chi2, ndof, chi2 / ndof))
    excl = [r['observable'] for r in rows if r['data_verdict'] == 'EXCLUDED']
    print('  EXCLUDED                 : {}'.format('; '.join(excl) if excl else 'none'))
    both = [r['observable'] for r in rows
            if r['data_verdict'] == 'AGREE' and r['derivation'] == DERIVED]
    print('  genuinely predictive AND consistent with data: {}'.format(
        '; '.join(both) if both else 'none'))

    if args.json:
        with open(args.json, 'w') as fh:
            json.dump({'engine': rep['engine_version'],
                       'nodes': args.nodes, 'steps': args.steps,
                       'elapsed_s': round(time.time() - t0, 2),
                       'chi2': chi2, 'n_measured_rows': ndof,
                       'counts': counts, 'rows': rows}, fh, indent=1, default=str)
        print('\n  JSON written to {}'.format(args.json))
    print('=' * 100)


if __name__ == '__main__':
    main()
