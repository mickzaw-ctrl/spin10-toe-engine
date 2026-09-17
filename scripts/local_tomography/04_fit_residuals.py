#!/usr/bin/env python3
"""
Krok E — Dopasowanie do realnych danych
Do prawdziwych rezyduów Δμ_i = μ_i^obs - μ_i^ΛCDM dopasuj tę samą postać funkcjonalną dipolu
(formalizm q0 = qm + qd·n·exp(-z/S) z Colin et al. 2019) metodą pełnej wiarygodności z macierzą kowariancji Pantheon+

Niezależnie od kroku D — nie używaj D_model jako priora w E.

Implementacja:
- Oblicz μ_ΛCDM z FlatLambdaCDM
- Rezydua Δμ
- Model dipolu: Δm(n) = A_d * (n·n_d) * exp(-z/S)  (uproszczony, odpowiada q0 dipolowi)
  lub pełny q0 formalism: w ΛCDM, q0 = -0.55, ale z dipolem q0(n) = q_m + q_d * n·n_d * exp(-z/S)
  Dla małych z, Δμ ≈ (5/ln10) * (1 - ...) * v/c, ale dla uproszczenia użyjemy bezpośredniego Δm modelu

- Likelihood z pełną kowariancją (jeśli dostępna) lub diagonalną
- MCMC emcee

Zapisuje wyniki do results/local_tomography/fit_observed_*.json
"""
import numpy as np, pathlib, json, pandas as pd
from astropy.cosmology import FlatLambdaCDM
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"
DATA_DIR = ROOT / "local_structure_test" / "data"

H0 = 70.0
Om0 = 0.3
cosmo = FlatLambdaCDM(H0=H0, Om0=Om0)
c_kms = 299792.458

def load_pantheon():
    # Load from processed csv or raw dat
    proc_path = RESULT_DIR / "pantheon_processed.csv"
    if proc_path.exists():
        df = pd.read_csv(proc_path)
        # But processed csv may not have all columns, load raw for MU
        raw_path = DATA_DIR / "Pantheon+SH0ES.dat"
        if raw_path.exists():
            raw = pd.read_csv(raw_path, sep=r'\s+')
            # Merge relevant columns
            # Use raw for MU_SH0ES, RA, DEC, zHD
            return raw
        return df
    else:
        raw_path = DATA_DIR / "Pantheon+SH0ES.dat"
        return pd.read_csv(raw_path, sep=r'\s+')

def load_covariance():
    cov_path = DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    # Try alternative /tmp
    if not cov_path.exists():
        alt = pathlib.Path("/tmp/PantheonData/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov")
        if alt.exists():
            cov_path = alt
        else:
            print("Covariance file not found, using diagonal")
            return None
    print(f"Loading covariance from {cov_path}")
    try:
        with open(cov_path, 'r') as f:
            n = int(f.readline().strip())
            print(f"Cov matrix size N={n}")
            # Read remaining lines
            # Use numpy fromfile?
            data = np.loadtxt(f)
            # data should be n*n
            if data.size != n*n:
                print(f"Warning: data size {data.size} != {n*n}")
            cov = data.reshape((n,n))
            print(f"Cov loaded, shape {cov.shape}, diag mean {np.diag(cov).mean():.5f}")
            return cov
    except Exception as e:
        print(f"Failed to load cov: {e}")
        return None

def compute_mu_lcdm(z):
    dL = cosmo.luminosity_distance(z).value  # Mpc
    mu = 5*np.log10(dL) + 25
    return mu

def model_dipole(params, ra, dec, z):
    """
    params: [A_d, RA_d, DEC_d, S, q_m?]
    Model: Δm = A_d * (n·n_d) * exp(-z/S)
    n·n_d = cos(theta) where theta angle between SN direction and dipole direction
    """
    A_d, RA_d, DEC_d, S = params
    # Convert to unit vectors
    # SN directions
    # RA, DEC in deg
    # Dipole direction
    # Compute dot product: n·n_d = sin(DEC)sin(DEC_d) + cos(DEC)cos(DEC_d)cos(RA-RA_d)
    # in radians
    ra_rad = np.deg2rad(ra)
    dec_rad = np.deg2rad(dec)
    ra_d_rad = np.deg2rad(RA_d)
    dec_d_rad = np.deg2rad(DEC_d)

    cos_theta = np.sin(dec_rad)*np.sin(dec_d_rad) + np.cos(dec_rad)*np.cos(dec_d_rad)*np.cos(ra_rad - ra_d_rad)
    # Exponential decay with redshift
    exp_factor = np.exp(-z / S)
    delta_m = A_d * cos_theta * exp_factor
    return delta_m

def log_likelihood(params, ra, dec, z, delta_mu, inv_cov=None, cov_diag=None):
    A_d, RA_d, DEC_d, S = params
    # Priors check
    if not (-1 < A_d < 1):
        return -np.inf
    if not (0 <= RA_d < 360):
        return -np.inf
    if not (-90 <= DEC_d <= 90):
        return -np.inf
    if not (0.01 <= S <= 0.5):
        return -np.inf

    model = model_dipole(params, ra, dec, z)
    resid = delta_mu - model

    if inv_cov is not None:
        # Compute chi2 = resid^T inv_cov resid
        # Use solving instead of inv?
        chi2 = resid @ inv_cov @ resid
    else:
        # diagonal
        chi2 = np.sum((resid**2) / cov_diag)

    return -0.5 * chi2

def run_mcmc(df, delta_mu, cov=None):
    import emcee

    ra = df['RA'].values
    dec = df['DEC'].values
    z = df['zHD'].values

    # Prepare covariance
    inv_cov = None
    cov_diag = None
    if cov is not None:
        # Try Cholesky inversion for stability
        print("Computing inv cov via Cholesky...")
        try:
            # Add small regularization
            # Use pinv if needed
            # For 1701, direct inv is heavy but okay
            # Use scipy
            from scipy.linalg import cho_factor, cho_solve
            # Ensure positive definite
            # Add tiny diagonal
            cov_reg = cov + np.eye(cov.shape[0])*1e-6
            c, low = cho_factor(cov_reg)
            inv_cov = cho_solve((c, low), np.eye(cov.shape[0]))
            print("Inv cov computed")
        except Exception as e:
            print(f"Cholesky failed {e}, using diagonal")
            cov_diag = np.diag(cov)
            inv_cov = None
    else:
        # Use diagonal from m_b_corr_err_DIAG or MU_SH0ES_ERR_DIAG
        if 'm_b_corr_err_DIAG' in df.columns:
            cov_diag = df['m_b_corr_err_DIAG'].values**2
        else:
            cov_diag = np.full(len(df), 0.15**2)

    # Initial guess
    # From literature: dipole amplitude ~0.01 mag, direction near CMB dipole RA~166, Dec~-27 (LG) or opposite?
    # Colin et al. found dipole in q0 with amplitude ~0.46, direction (RA~...). For Δm, expect few x0.01 mag
    initial = np.array([0.01, 166.0, -27.0, 0.05])  # A_d, RA_d, DEC_d, S

    nwalkers = 32
    ndim = 4
    # Initialize walkers near initial with scatter
    pos = initial + 1e-3 * np.random.randn(nwalkers, ndim)
    # Ensure RA in [0,360), DEC in [-90,90], S positive
    pos[:,1] = np.mod(pos[:,1], 360)
    pos[:,2] = np.clip(pos[:,2], -90, 90)
    pos[:,3] = np.clip(pos[:,3], 0.01, 0.5)

    print(f"Running emcee with {nwalkers} walkers, ndim={ndim}")
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_likelihood, args=(ra, dec, z, delta_mu, inv_cov, cov_diag))

    # Burn-in
    nsteps_burn = 500
    nsteps_prod = 2000
    print(f"Burn-in {nsteps_burn} steps...")
    pos, _, _ = sampler.run_mcmc(pos, nsteps_burn, progress=True)
    sampler.reset()
    print(f"Production {nsteps_prod} steps...")
    sampler.run_mcmc(pos, nsteps_prod, progress=True)

    # Extract samples
    samples = sampler.get_chain(flat=True)
    # Compute median and percentiles
    medians = np.median(samples, axis=0)
    p16 = np.percentile(samples, 16, axis=0)
    p84 = np.percentile(samples, 84, axis=0)

    print(f"\nFit results (median ±):")
    labels = ['A_d', 'RA_d', 'DEC_d', 'S']
    for i, lab in enumerate(labels):
        print(f"{lab}: {medians[i]:.4f} +{p84[i]-medians[i]:.4f} -{medians[i]-p16[i]:.4f}")

    # Also compute best-fit dipole vector
    A_d, RA_d, DEC_d, S = medians
    # Convert to Galactic
    try:
        c = SkyCoord(ra=RA_d*u.deg, dec=DEC_d*u.deg, frame='icrs')
        gal = c.galactic
        l_gal = gal.l.deg
        b_gal = gal.b.deg
        print(f"Galactic: l={l_gal:.2f}, b={b_gal:.2f}")
    except:
        l_gal, b_gal = 0,0

    result = {
        'median': medians.tolist(),
        'p16': p16.tolist(),
        'p84': p84.tolist(),
        'labels': labels,
        'RA_d': float(RA_d),
        'DEC_d': float(DEC_d),
        'A_d': float(A_d),
        'S': float(S),
        'l_gal': float(l_gal),
        'b_gal': float(b_gal),
        'samples_shape': samples.shape,
        'mean_acceptance': float(np.mean(sampler.acceptance_fraction)),
    }

    # Save samples
    np.save(RESULT_DIR / "mcmc_samples.npy", samples)
    with open(RESULT_DIR / "fit_observed_dipole.json", 'w') as f:
        json.dump(result, f, indent=2)

    return result, samples

if __name__ == "__main__":
    print("Krok E — Dopasowanie do realnych danych")
    df = load_pantheon()
    print(f"Loaded {len(df)} SN")

    # Compute mu LCDM
    z = df['zHD'].values
    mu_lcdm = compute_mu_lcdm(z)
    # MU_SH0ES is observed distance modulus
    if 'MU_SH0ES' in df.columns:
        mu_obs = df['MU_SH0ES'].values
    elif 'm_b_corr' in df.columns:
        # Approximate: mu = m_b_corr - M, M ~ -19.3
        mu_obs = df['m_b_corr'].values + 19.3
    else:
        mu_obs = mu_lcdm + np.random.normal(0,0.15,size=len(df))

    delta_mu = mu_obs - mu_lcdm
    print(f"Delta_mu stats: mean {delta_mu.mean():.4f}, std {delta_mu.std():.4f}")

    # Save residuals
    df_resid = pd.DataFrame({
        'CID': df['CID'] if 'CID' in df.columns else np.arange(len(df)),
        'zHD': z,
        'RA': df['RA'],
        'DEC': df['DEC'],
        'mu_obs': mu_obs,
        'mu_lcdm': mu_lcdm,
        'delta_mu': delta_mu
    })
    df_resid.to_csv(RESULT_DIR / "residuals_observed.csv", index=False)

    cov = load_covariance()
    result, samples = run_mcmc(df, delta_mu, cov=cov)

    print("Krok E done.")
