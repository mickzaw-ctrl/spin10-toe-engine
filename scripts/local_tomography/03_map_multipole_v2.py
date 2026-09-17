#!/usr/bin/env python3
"""
Krok D v2 — poprawka po human review

Zastrzeżenie 3: healpy.fit_dipole na rzadkiej mapie (13.6%/3.8% pikseli) zawodzi — test odzysku dipolu 0.02 mag -> 0.00095 mag, 55° błąd.
Poprawka: zastąpić naiwny fit_dipole tym samym podejściem z pełną kowariancją/MCMC które działa w Kroku E.

Implementacja v2:
- Zamiast budować HEALPix mapę i fit_dipole, dopasuj dipol BEZPOŚREDNIO do Δm_pred per SN (tak jak w Kroku E do rezyduów)
- Użyj tego samego modelu: Δm = A_d * cosθ * exp(-z/S)
- MCMC emcee, diagonal errors (bo predykcja ma niepewność z CRs, nie z SN cov)
- Dzięki temu Krok D i Krok E mierzą dipol tą samą, zwalidowaną metodą statystyczną

Zachowuje zgodność z pre-reg: statystyka testowa cosθ i T_amp, ale metoda pomiaru spójna.
"""
import numpy as np, pathlib, json, pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
import emcee

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"

def model_dipole(params, ra, dec, z):
    A_d, RA_d, DEC_d, S = params
    ra_rad=np.deg2rad(ra); dec_rad=np.deg2rad(dec)
    ra_d_rad=np.deg2rad(RA_d); dec_d_rad=np.deg2rad(DEC_d)
    cos_theta=np.sin(dec_rad)*np.sin(dec_d_rad)+np.cos(dec_rad)*np.cos(dec_d_rad)*np.cos(ra_rad-ra_d_rad)
    return A_d * cos_theta * np.exp(-z/S)

def log_likelihood(params, ra, dec, z, delta_m, sigma=0.05):
    A_d,RA_d,DEC_d,S=params
    if not (-1<A_d<1): return -np.inf
    if not (0<=RA_d<360): return -np.inf
    if not (-90<=DEC_d<=90): return -np.inf
    if not (0.01<=S<=0.5): return -np.inf
    model=model_dipole(params,ra,dec,z)
    resid=delta_m-model
    chi2=np.sum((resid**2)/(sigma**2))
    return -0.5*chi2

def fit_dipole_mcmc(df, col='Delta_m_pred', nwalkers=32, nsteps=2000, burn=500):
    ra=df['RA'].values; dec=df['DEC'].values; z=df['zHD'].values
    delta_m=df[col].values
    # Initial guess: use previous healpy result or LG direction
    initial=np.array([0.01, 166.0, -27.0, 0.05])
    pos=initial+1e-3*np.random.randn(nwalkers,4)
    pos[:,1]=np.mod(pos[:,1],360)
    pos[:,2]=np.clip(pos[:,2],-90,90)
    pos[:,3]=np.clip(pos[:,3],0.01,0.5)

    sampler=emcee.EnsembleSampler(nwalkers,4,log_likelihood,args=(ra,dec,z,delta_m))
    print(f"Burn {burn}...")
    pos,_,_=sampler.run_mcmc(pos,burn,progress=False)
    sampler.reset()
    print(f"Prod {nsteps}...")
    sampler.run_mcmc(pos,nsteps,progress=False)
    samples=sampler.get_chain(flat=True)
    med=np.median(samples,axis=0)
    p16=np.percentile(samples,16,axis=0)
    p84=np.percentile(samples,84,axis=0)
    print(f"Fit: A={med[0]:.5f} +{p84[0]-med[0]:.5f} -{med[0]-p16[0]:.5f}, RA={med[1]:.2f}, DEC={med[2]:.2f}, S={med[3]:.4f}")
    # Galactic
    try:
        c=SkyCoord(ra=med[1]*u.deg, dec=med[2]*u.deg, frame='icrs')
        gal=c.galactic
        l_gal=gal.l.deg; b_gal=gal.b.deg
    except:
        l_gal=b_gal=0
    return {
        'median': med.tolist(),
        'p16': p16.tolist(),
        'p84': p84.tolist(),
        'A_d': float(med[0]),
        'RA_d': float(med[1]),
        'DEC_d': float(med[2]),
        'S': float(med[3]),
        'l_gal': float(l_gal),
        'b_gal': float(b_gal),
        'samples': samples,
    }

if __name__=="__main__":
    print("Krok D v2 — MCMC dipole fit do predykcji (spójna metoda z Krokiem E)")
    for method in ['C15','L24']:
        csv_path=RESULT_DIR/f"delta_per_sn_{method}.csv"
        if not csv_path.exists():
            print(f"Missing {csv_path}")
            continue
        df=pd.read_csv(csv_path)
        # low-z 0.01-0.1 as per pre-reg main
        df_low=df[(df['zHD']>0.01)&(df['zHD']<0.1)]
        print(f"\n{method}: total {len(df)}, low-z {len(df_low)}")
        df_use=df_low if len(df_low)>=10 else df

        # Fit with MCMC
        result=fit_dipole_mcmc(df_use, col='Delta_m_pred', nwalkers=32, nsteps=2000, burn=500)

        # Save
        out_json=RESULT_DIR/f"dipole_pred_{method}_v2_mcmc.json"
        # Don't save samples (large)
        save_result={k:v for k,v in result.items() if k!='samples'}
        with open(out_json,'w') as f:
            json.dump(save_result,f,indent=2)
        print(f"Saved {out_json}")

        # Also save samples npy for later
        np.save(RESULT_DIR/f"mcmc_pred_{method}_v2.npy", result['samples'])

    print("Krok D v2 done.")
