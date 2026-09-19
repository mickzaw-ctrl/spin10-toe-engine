#!/usr/bin/env python3
"""
Krok G — Testy null i systematyki
- Mock z zadanym znanym dipolem — weryfikacja że pipeline go odtwarza
- Oszacowanie ile fałszywego dipolu generuje samo nierównomierne pokrycie nieba przez katalog SN

"""
import numpy as np, pathlib, json, pandas as pd
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"

def generate_mock_sn_with_dipole(n=1701, dipole_amp=0.02, ra_dip=166, dec_dip=-27, S=0.05, seed=0):
    """Generate mock SN catalog with known dipole"""
    np.random.seed(seed)
    # RA/DEC uniform but with northern bias like Pantheon+
    ra = np.random.uniform(0,360,size=n)
    dec = np.random.uniform(-90,90,size=n)
    # Add northern bias 54%
    # For mock, use same as observed distribution: sample from real RA/DEC?
    # Load real
    real_path = RESULT_DIR / "pantheon_processed.csv"
    if real_path.exists():
        real = pd.read_csv(real_path)
        # Sample RA/DEC from real
        idx = np.random.choice(len(real), size=n, replace=True)
        ra = real['RA'].values[idx]
        dec = real['DEC'].values[idx]
        z = real['zHD'].values[idx] if 'zHD' in real.columns else np.random.exponential(0.1, size=n)
    else:
        z = np.random.exponential(0.1, size=n)
        z = np.clip(z, 0.001, 2.0)

    # Compute dipole model
    ra_rad = np.deg2rad(ra)
    dec_rad = np.deg2rad(dec)
    ra_d_rad = np.deg2rad(ra_dip)
    dec_d_rad = np.deg2rad(dec_dip)
    cos_theta = np.sin(dec_rad)*np.sin(dec_d_rad) + np.cos(dec_rad)*np.cos(dec_d_rad)*np.cos(ra_rad-ra_d_rad)
    delta_m = dipole_amp * cos_theta * np.exp(-z/S)
    # Add noise
    delta_m += np.random.normal(0, 0.15, size=n)

    return pd.DataFrame({'RA':ra, 'DEC':dec, 'zHD':z, 'Delta_m':delta_m}), (ra_dip, dec_dip, dipole_amp)

def build_map_and_dipole(df, nside=16, col='Delta_m'):
    npix = hp.nside2npix(nside)
    theta = np.deg2rad(90.0 - df['DEC'].values)
    phi = np.deg2rad(df['RA'].values)
    pix = hp.ang2pix(nside, theta, phi)
    map_sum = np.zeros(npix)
    map_count = np.zeros(npix)
    for p, dm in zip(pix, df[col].values):
        map_sum[p] += dm
        map_count[p] += 1
    healpix_map = np.full(npix, hp.UNSEEN)
    mask = map_count>0
    healpix_map[mask] = map_sum[mask]/map_count[mask]
    map_for_fit = healpix_map.copy()
    map_for_fit[map_for_fit==hp.UNSEEN]=0
    try:
        mono, dip_vec = hp.fit_dipole(map_for_fit)[:2]
        # Actually fit_dipole returns (monopole, dipole_vector)
        # In newer healpy, it returns dipole vector and monopole separately? Let's handle
        if isinstance(mono, (list, np.ndarray)) and len(mono)==2:
            # Actually first return is dipole vector?
            pass
    except:
        # Use older API
        dip = hp.fit_dipole(map_for_fit)
        mono = dip[0]
        dip_vec = dip[1]

    # Re-evaluate with correct unpacking
    try:
        result = hp.fit_dipole(map_for_fit)
        # result is (monopole, dipole_vector) or (dipole_vector, monopole)?
        # Check docs: fit_dipole returns (dipole_vector, monopole) or (monopole, dipole_vector) depending on version
        # We'll assume first is monopole if scalar, second is vector
        if np.isscalar(result[0]):
            mono = result[0]
            dip_vec = result[1]
        else:
            dip_vec = result[0]
            mono = result[1]
    except Exception as e:
        print(f"fit_dipole failed {e}")
        mono=0
        dip_vec=np.array([0,0,0])

    amp = np.linalg.norm(dip_vec)
    if amp>0:
        unit = dip_vec/amp
        x,y,z = unit
        dec = np.rad2deg(np.arcsin(z))
        ra = np.rad2deg(np.arctan2(y,x))%360
    else:
        ra,dec=0,0
    return {'RA':ra, 'DEC':dec, 'amp':amp, 'vec':dip_vec, 'mono':mono}

def test_known_dipole_recovery():
    print("\n=== Test 1: Known dipole recovery ===")
    # Inject known dipole
    true_ra, true_dec, true_amp = 166.0, -27.0, 0.02
    df_mock, true_params = generate_mock_sn_with_dipole(n=1701, dipole_amp=true_amp, ra_dip=true_ra, dec_dip=true_dec, S=0.05, seed=42)
    rec = build_map_and_dipole(df_mock, nside=16, col='Delta_m')
    print(f"True: RA={true_ra}, DEC={true_dec}, amp={true_amp}")
    print(f"Recovered: RA={rec['RA']:.2f}, DEC={rec['DEC']:.2f}, amp={rec['amp']:.5f}")

    # Compute angular error
    def ang_sep(ra1,dec1,ra2,dec2):
        ra1=np.deg2rad(ra1); dec1=np.deg2rad(dec1); ra2=np.deg2rad(ra2); dec2=np.deg2rad(dec2)
        cos_t = np.sin(dec1)*np.sin(dec2)+np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)
        cos_t=np.clip(cos_t,-1,1)
        return np.rad2deg(np.arccos(cos_t)), cos_t

    sep, cos_t = ang_sep(true_ra, true_dec, rec['RA'], rec['DEC'])
    print(f"Separation: {sep:.2f} deg, cosθ={cos_t:.4f}")

    # Check if recovered within 20 deg and amplitude within 50%
    amp_ok = abs(rec['amp']-true_amp)/true_amp < 0.5
    dir_ok = sep < 20
    print(f"Amplitude OK? {amp_ok}, Direction OK? {dir_ok}")

    return {'true': (true_ra,true_dec,true_amp), 'rec': rec, 'sep': sep, 'cos': cos_t, 'amp_ok': bool(amp_ok), 'dir_ok': bool(dir_ok)}

def test_sky_coverage_bias():
    print("\n=== Test 2: Sky coverage bias (null isotropy) ===")
    # Generate isotropic mocks (no dipole, only noise) with same RA/DEC as real Pantheon+
    # Then fit dipole, see distribution of recovered amplitude
    import pandas as pd
    real_path = RESULT_DIR / "pantheon_processed.csv"
    if not real_path.exists():
        real_path = ROOT / "local_structure_test" / "data" / "Pantheon+SH0ES.dat"
        # fallback
        df_real = pd.read_csv(real_path, sep=r'\s+')
    else:
        df_real = pd.read_csv(real_path)

    n_mocks = 200
    amps = []
    np.random.seed(123)
    for i in range(n_mocks):
        # Shuffle Delta_m or generate noise
        # Use real RA/DEC, random Delta_m ~ N(0,0.15)
        df_mock = df_real.copy()
        # If we have residuals, use random
        # For this test, generate isotropic noise
        noise = np.random.normal(0, 0.15, size=len(df_mock))
        df_mock['Delta_m'] = noise
        rec = build_map_and_dipole(df_mock, nside=16, col='Delta_m')
        amps.append(rec['amp'])

    amps = np.array(amps)
    print(f"Isotropic mocks: mean amp={amps.mean():.5f}, std={amps.std():.5f}, max={amps.max():.5f}, 95th percentile={np.percentile(amps,95):.5f}")

    # Compare to observed amplitude 0.113 and predicted 0.007
    obs_amp = 0.113
    pred_amp = 0.0076
    # What fraction of mocks exceed observed?
    frac_exceed_obs = (amps >= obs_amp).mean()
    frac_exceed_pred = (amps >= pred_amp).mean()
    print(f"Fraction of isotropic mocks with amp >= observed ({obs_amp}): {frac_exceed_obs:.4f}")
    print(f"Fraction with amp >= predicted ({pred_amp}): {frac_exceed_pred:.4f}")

    # If sky coverage generates dipole comparable to signal, then systematics dominate
    # Per pre-reg, stop if sky geometry generates dipole comparable to signal
    # i.e., if median mock amp ~ observed amp within 1σ

    return {
        'mean_amp': float(amps.mean()),
        'std_amp': float(amps.std()),
        'p95': float(np.percentile(amps,95)),
        'frac_exceed_obs': float(frac_exceed_obs),
        'frac_exceed_pred': float(frac_exceed_pred),
        'amps': amps.tolist()[:10],  # first 10 for brevity
    }

def test_random_directions_null():
    print("\n=== Test 3: Random direction null for cosθ ===")
    # Under H0 (random orientation), cosθ uniform in [-1,1]
    # Generate 10000 random directions, compute cosθ vs observed
    np.random.seed(456)
    n = 10000
    # Random uniform on sphere: RA uniform 0-360, sin(DEC) uniform
    ra_rand = np.random.uniform(0,360,size=n)
    sin_dec_rand = np.random.uniform(-1,1,size=n)
    dec_rand = np.rad2deg(np.arcsin(sin_dec_rand))

    # Observed direction from fit
    obs_ra, obs_dec = 211.89, -47.93
    # Predicted C15
    pred_ra, pred_dec = 7.16, -41.58

    def cos_theta(ra1,dec1,ra2,dec2):
        ra1=np.deg2rad(ra1); dec1=np.deg2rad(dec1); ra2=np.deg2rad(ra2); dec2=np.deg2rad(dec2)
        return np.sin(dec1)*np.sin(dec2)+np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)

    cos_vals = cos_theta(obs_ra, obs_dec, ra_rand, dec_rand)
    # p-value for observed cos vs predicted
    cos_obs_pred = cos_theta(obs_ra, obs_dec, pred_ra, pred_dec)
    p_val = (cos_vals >= cos_obs_pred).mean()
    print(f"cosθ obs vs pred C15 = {cos_obs_pred:.4f}, p-value (random >=) = {p_val:.4f}")
    # Also for L24
    pred_ra2, pred_dec2 = 325.75, -15.49
    cos_obs_pred2 = cos_theta(obs_ra, obs_dec, pred_ra2, pred_dec2)
    p_val2 = (cos_vals >= cos_obs_pred2).mean()
    print(f"cosθ obs vs pred L24 = {cos_obs_pred2:.4f}, p={p_val2:.4f}")

    return {
        'cos_C15': float(cos_obs_pred),
        'p_C15': float(p_val),
        'cos_L24': float(cos_obs_pred2),
        'p_L24': float(p_val2),
    }

if __name__ == "__main__":
    print("Krok G — Testy null i systematyki")

    res1 = test_known_dipole_recovery()
    res2 = test_sky_coverage_bias()
    res3 = test_random_directions_null()

    # Save
    out = {
        'known_dipole_recovery': res1,
        'sky_coverage_bias': res2,
        'random_direction_null': res3,
    }
    # Convert numpy types
    import json
    def convert(o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.integer):
            return int(o)
        return o

    with open(RESULT_DIR / "null_tests.json", 'w') as f:
        json.dump(out, f, indent=2, default=convert)

    print("\n=== Summary ===")
    print(f"Known dipole recovery: dir_ok={res1['dir_ok']}, amp_ok={res1['amp_ok']}")
    print(f"Sky bias: mean amp isotropic {res2['mean_amp']:.5f} vs observed 0.113, pred 0.0076")
    if res2['mean_amp'] > 0.5*0.113:
        print("WARNING: Sky coverage generates dipole comparable to observed signal - per pre-reg, require human review, possible systematics dominate")
    else:
        print("Sky coverage bias not dominant vs observed")

    print("Krok G done.")
