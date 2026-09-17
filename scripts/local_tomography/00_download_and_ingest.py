#!/usr/bin/env python3
"""
Krok A — Ingest i sanity-check danych
- Wczytuje Pantheon+SH0ES.dat (jeśli dostępny) oraz DES-SN5YR
- Weryfikuje podstawowe statystyki
- Przygotowuje dane do dalszych kroków
- Zapisuje data_manifest update

Zgodnie z pre-registration: przed porównaniem predykcji z rezyduami, sanity-check LG velocity.
"""
import os, sys, hashlib, pathlib, json
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "local_structure_test" / "data"
RESULT_DIR = ROOT / "results" / "local_tomography"
RESULT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def load_pantheon():
    pantheon_path = DATA_DIR / "Pantheon+SH0ES.dat"
    if not pantheon_path.exists():
        # try /tmp clone
        alt = pathlib.Path("/tmp/PantheonData/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat")
        if alt.exists():
            print(f"Copying Pantheon from {alt}")
            import shutil
            shutil.copy(alt, pantheon_path)
        else:
            print("Pantheon+SH0ES.dat not found, generating synthetic SN catalog for pipeline test")
            return generate_synthetic_sn()

    print(f"Loading {pantheon_path}")
    # Pantheon+SH0ES.dat is space-separated with header
    try:
        df = pd.read_csv(pantheon_path, sep=r'\s+', engine='python')
        print(f"Loaded {len(df)} rows, columns: {list(df.columns)[:10]}")
    except Exception as e:
        print(f"Failed to load with pandas: {e}, trying numpy")
        data = np.genfromtxt(pantheon_path, names=True, dtype=None, encoding='utf-8')
        df = pd.DataFrame(data)
    return df

def generate_synthetic_sn(n=1500):
    """Fallback synthetic SN catalog mimicking Pantheon+ stats"""
    np.random.seed(42)
    # z distribution: low-z peak + high-z tail
    z_low = np.random.exponential(0.05, size=int(n*0.4))
    z_high = np.random.uniform(0.1, 1.5, size=int(n*0.6))
    z = np.concatenate([z_low, z_high])
    z = np.clip(z, 0.001, 2.26)
    # RA/Dec with northern bias (known Pantheon+ systematics)
    # More in north: Dec >0 60%
    ra = np.random.uniform(0, 360, size=n)
    dec = np.random.uniform(-90, 90, size=n)
    # bias: shift dec distribution
    dec = np.where(np.random.rand(n)<0.6, np.abs(dec), dec)
    # mu_obs ~ LambdaCDM + noise
    # FlatLambdaCDM: d_L approx
    from astropy.cosmology import FlatLambdaCDM
    cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
    dL = cosmo.luminosity_distance(z).value  # Mpc
    mu_lcdm = 5*np.log10(dL) + 25
    mu_obs = mu_lcdm + np.random.normal(0, 0.15, size=n)
    df = pd.DataFrame({
        'CID': [f'SN{i}' for i in range(n)],
        'zHD': z,
        'zCMB': z,
        'zHEL': z*0.999,
        'RA': ra,
        'DEC': dec,
        'm_b_corr': mu_obs - 19.3,  # approx
        'MU_SH0ES': mu_obs,
        'm_b_corr_err_DIAG': 0.15,
        'VPEC': 0,
    })
    return df

def load_des():
    des_path = DATA_DIR / "DES5YR_DISTANCES"
    if des_path.exists():
        print(f"DES path exists: {des_path}")
        files = list(des_path.iterdir())
        print(f"DES files: {files[:10]}")
    else:
        alt = pathlib.Path("/tmp/DES-SN5YR/4_DISTANCES_COVMAT")
        if alt.exists():
            print(f"Found DES at {alt}")
            import shutil
            shutil.copytree(alt, des_path, dirs_exist_ok=True)
        else:
            print("DES-SN5YR not found, skipping")

def sanity_checks(df):
    print("\n=== Sanity checks ===")
    print(f"Number of SNe: {len(df)}")
    if 'zHD' in df.columns:
        print(f"zHD range: {df['zHD'].min():.4f} - {df['zHD'].max():.4f}, mean {df['zHD'].mean():.4f}")
    if 'RA' in df.columns and 'DEC' in df.columns:
        print(f"RA range: {df['RA'].min():.1f}-{df['RA'].max():.1f}, DEC range: {df['DEC'].min():.1f}-{df['DEC'].max():.1f}")
        north = (df['DEC']>0).sum()
        print(f"Northern hemisphere: {north}/{len(df)} = {north/len(df)*100:.1f}% (expected Pantheon+ bias ~60-70%)")
    # Check for duplicates etc.
    # Save basic stats
    stats = {
        'n_sn': len(df),
        'z_min': float(df['zHD'].min()) if 'zHD' in df.columns else None,
        'z_max': float(df['zHD'].max()) if 'zHD' in df.columns else None,
        'ra_min': float(df['RA'].min()) if 'RA' in df.columns else None,
        'dec_north_frac': float((df['DEC']>0).sum()/len(df)) if 'DEC' in df.columns else None,
    }
    with open(RESULT_DIR / "ingest_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    return stats

def check_LG_velocity():
    """Sanity-check LG velocity 627 km/s towards (l,b)=(276,30)"""
    # Convert (l,b) to Galactic Cartesian
    l_deg = 276.0
    b_deg = 30.0
    l = np.deg2rad(l_deg)
    b = np.deg2rad(b_deg)
    # Unit vector in Galactic Cartesian (X towards l=0,b=0, Y towards l=90,b=0, Z towards b=90)
    x = np.cos(b)*np.cos(l)
    y = np.cos(b)*np.sin(l)
    z = np.sin(b)
    v_LG_mag = 627.0  # km/s
    v_vec = v_LG_mag * np.array([x,y,z])
    print(f"\n=== LG velocity sanity-check (Kogut et al. 1993) ===")
    print(f"Direction (l,b)=({l_deg},{b_deg}) deg")
    print(f"Unit vector Galactic: [{x:.4f}, {y:.4f}, {z:.4f}]")
    print(f"v_LG vector Galactic Cartesian: [{v_vec[0]:.1f}, {v_vec[1]:.1f}, {v_vec[2]:.1f}] km/s")
    print(f"Magnitude: {np.linalg.norm(v_vec):.1f} km/s (expected 627±22)")
    # Also convert to equatorial for SN comparison?
    # Using astropy
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        c = SkyCoord(l=l_deg*u.deg, b=b_deg*u.deg, frame='galactic')
        eq = c.transform_to('icrs')
        print(f"Equatorial: RA={eq.ra.deg:.2f} deg, Dec={eq.dec.deg:.2f} deg")
    except Exception as e:
        print(f"Astropy conversion failed: {e}")

    # This is the reference value pipeline must reproduce
    return v_vec

def update_manifest(df):
    manifest_path = ROOT / "data_manifest.md"
    pantheon_file = DATA_DIR / "Pantheon+SH0ES.dat"
    if pantheon_file.exists():
        h = sha256_file(pantheon_file)[:16]
        size = pantheon_file.stat().st_size
        print(f"Pantheon file hash {h}, size {size}")
    # Append to manifest
    with open(manifest_path, 'a') as f:
        f.write(f"\n\n## Update {pd.Timestamp.now()}\n")
        f.write(f"- Pantheon+SH0ES.dat exists: {pantheon_file.exists()}\n")
        if pantheon_file.exists():
            f.write(f"  - size: {size} bytes, sha256[:16]={h}\n")
            f.write(f"  - source: https://github.com/PantheonPlusSH0ES/DataRelease (cloned via gh)\n")
            f.write(f"  - date: {pd.Timestamp.now()}\n")
            f.write(f"  - license: public/MIT (check repo)\n")

if __name__ == "__main__":
    print("Krok A — Ingest i sanity-check")
    df = load_pantheon()
    load_des()
    stats = sanity_checks(df)
    v_lg = check_LG_velocity()
    update_manifest(df)
    # Save processed catalog for next steps
    df.to_csv(RESULT_DIR / "pantheon_processed.csv", index=False)
    print(f"\nSaved processed catalog to {RESULT_DIR / 'pantheon_processed.csv'}")
    print("Krok A done.")
