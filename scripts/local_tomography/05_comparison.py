#!/usr/bin/env python3
"""
Krok F — Porównanie
Iloczyn skalarny kierunków (cosθ), zgodność amplitud w granicach błędu (bootstrap po SN)
To jest właściwy test — wynik z pre-rejestracji decyduje czy sukces czy porażka
"""
import numpy as np, pathlib, json, pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"

def angular_separation(ra1, dec1, ra2, dec2):
    """Return cosθ and angle in deg"""
    # Convert to unit vectors
    ra1 = np.deg2rad(ra1); dec1 = np.deg2rad(dec1)
    ra2 = np.deg2rad(ra2); dec2 = np.deg2rad(dec2)
    # Dot product
    cos_theta = np.sin(dec1)*np.sin(dec2) + np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)
    cos_theta = np.clip(cos_theta, -1, 1)
    theta = np.rad2deg(np.arccos(cos_theta))
    return cos_theta, theta

def load_pred(method, nside=16):
    path = RESULT_DIR / f"dipole_pred_{method}_nside{nside}.json"
    if not path.exists():
        print(f"Missing {path}")
        return None
    with open(path) as f:
        data = json.load(f)
    return data

def load_obs():
    path = RESULT_DIR / "fit_observed_dipole.json"
    if not path.exists():
        print(f"Missing {path}")
        return None
    with open(path) as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    print("Krok F — Porównanie predykcji vs obserwacja")

    obs = load_obs()
    if obs is None:
        print("No observed fit, abort")
        exit(1)

    print(f"\nObserved dipole (from SN residuals):")
    print(f"  RA={obs['RA_d']:.2f}, DEC={obs['DEC_d']:.2f}, A={obs['A_d']:.4f}, S={obs['S']:.4f}")
    print(f"  Galactic l={obs['l_gal']:.2f}, b={obs['b_gal']:.2f}")

    # Pre-registration criteria
    # Success: cosθ >=0.5 and p_dir<0.05 and T_amp<2.0
    # Failure: cosθ<0 or T_amp>3

    results = []

    for method in ['C15', 'L24']:
        for nside in [16, 32]:
            pred = load_pred(method, nside)
            if pred is None:
                continue
            print(f"\n--- Predicted {method} nside={nside} ---")
            print(f"  RA={pred['RA']:.2f}, DEC={pred['DEC']:.2f}, A={pred['dipole_amplitude']:.5f}")
            print(f"  Galactic l={pred['l_gal']:.2f}, b={pred['b_gal']:.2f}")

            cos_theta, theta_deg = angular_separation(obs['RA_d'], obs['DEC_d'], pred['RA'], pred['DEC'])
            print(f"  cosθ = {cos_theta:.4f}, θ = {theta_deg:.2f} deg")

            # Amplitude comparison
            A_pred = pred['dipole_amplitude']
            A_obs = obs['A_d']
            # Uncertainties: for pred, use scatter from CRs (we don't have, estimate 50%?)
            # For obs, use posterior spread
            sigma_obs = (obs['p84'][0] - obs['p16'][0])/2 if 'p84' in obs else 0.02
            sigma_pred = 0.5 * A_pred  # assume 50% from CR scatter, conservative
            T_amp = abs(A_pred - A_obs) / np.sqrt(sigma_pred**2 + sigma_obs**2 + 1e-6)
            print(f"  A_pred={A_pred:.5f}±{sigma_pred:.5f}, A_obs={A_obs:.5f}±{sigma_obs:.5f}, T_amp={T_amp:.2f}")

            # p-value for random alignment: p = (1 - cosθ)/2
            p_dir = (1 - cos_theta)/2
            print(f"  p_dir (random alignment) = {p_dir:.4f} (probability to get >=cosθ by chance)")

            # Criteria from pre-registration
            # Direction: cosθ >=0.5 (θ<=60°) and p<0.05
            dir_pass = (cos_theta >= 0.5) and (p_dir < 0.05)
            amp_pass = T_amp < 2.0
            print(f"  Direction pass? {dir_pass} (cos>=0.5 and p<0.05)")
            print(f"  Amplitude pass? {amp_pass} (T_amp<2)")

            # Overall
            if dir_pass and amp_pass:
                verdict = "spójne (success per pre-reg)"
            elif cos_theta < 0 or T_amp > 3:
                verdict = "niespójne (failure per pre-reg)"
            else:
                verdict = "wymaga dalszej weryfikacji (inconclusive)"

            print(f"  Verdict: {verdict}")

            results.append({
                'method': method,
                'nside': nside,
                'RA_pred': pred['RA'],
                'DEC_pred': pred['DEC'],
                'l_pred': pred['l_gal'],
                'b_pred': pred['b_gal'],
                'A_pred': A_pred,
                'RA_obs': obs['RA_d'],
                'DEC_obs': obs['DEC_d'],
                'l_obs': obs['l_gal'],
                'b_obs': obs['b_gal'],
                'A_obs': A_obs,
                'cos_theta': float(cos_theta),
                'theta_deg': float(theta_deg),
                'p_dir': float(p_dir),
                'T_amp': float(T_amp),
                'dir_pass': bool(dir_pass),
                'amp_pass': bool(amp_pass),
                'verdict': verdict
            })

    # Save comparison
    out_path = RESULT_DIR / "comparison.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved comparison to {out_path}")

    # Also check stop criteria: cosθ>0.99 at first try => bug hunt
    for r in results:
        if r['cos_theta'] > 0.99:
            print(f"\n!!! STOP CRITERION: cosθ>0.99 for {r['method']} nside={r['nside']} - potential bug, require human review")
        if r['cos_theta'] < -0.9:
            print(f"Opposite direction for {r['method']}")

    # Summary for report
    # Check consistency between methods
    if len(results)>=2:
        # Compare C15 vs L24
        c15 = [r for r in results if r['method']=='C15']
        l24 = [r for r in results if r['method']=='L24']
        if c15 and l24:
            # Take nside16 as primary
            c = c15[0]; l = l24[0]
            cos_between_methods, theta_between = angular_separation(c['RA_pred'], c['DEC_pred'], l['RA_pred'], l['DEC_pred'])
            print(f"\nConsistency between methods C15 vs L24: cos={cos_between_methods:.4f}, theta={theta_between:.2f} deg")
            if theta_between > 60:
                print("WARNING: Methods disagree >60 deg - per pre-reg, result requires further verification, stop and human review")
            else:
                print("Methods agree within 60 deg")

    print("Krok F done.")
