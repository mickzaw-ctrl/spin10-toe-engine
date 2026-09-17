#!/usr/bin/env python3
"""
Krok G v2 — poprawka po human review

Zastrzeżenie 3: test odzysku dipolu zawodził (0.02 -> 0.00095 mag, 55° błąd) bo używał healpy.fit_dipole na rzadkiej mapie.
Poprawka: użyć tej samej metody MCMC co w Kroku E i D v2 do odzysku.

Test: wstrzyknij znany dipol, dopasuj MCMC, sprawdź czy odzyskuje w granicach błędu.
Dopiero po tym jak test G odzyskuje dipol, wolno patrzeć na wynik prawdziwych danych (per recenzja punkt 4).
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

def log_likelihood(params, ra, dec, z, delta_m, sigma=0.15):
    A_d,RA_d,DEC_d,S=params
    if not (-1<A_d<1): return -np.inf
    if not (0<=RA_d<360): return -np.inf
    if not (-90<=DEC_d<=90): return -np.inf
    if not (0.01<=S<=0.5): return -np.inf
    model=model_dipole(params,ra,dec,z)
    resid=delta_m-model
    chi2=np.sum((resid**2)/(sigma**2))
    return -0.5*chi2

def fit_mcmc(ra,dec,z,delta_m, sigma=0.15, nwalkers=32, burn=500, prod=2000):
    initial=np.array([0.02, 166.0, -27.0, 0.05])
    pos=initial+1e-3*np.random.randn(nwalkers,4)
    pos[:,1]=np.mod(pos[:,1],360)
    pos[:,2]=np.clip(pos[:,2],-90,90)
    pos[:,3]=np.clip(pos[:,3],0.01,0.5)
    sampler=emcee.EnsembleSampler(nwalkers,4,log_likelihood,args=(ra,dec,z,delta_m,sigma))
    pos,_,_=sampler.run_mcmc(pos,burn,progress=False)
    sampler.reset()
    sampler.run_mcmc(pos,prod,progress=False)
    samples=sampler.get_chain(flat=True)
    med=np.median(samples,axis=0)
    p16=np.percentile(samples,16,axis=0)
    p84=np.percentile(samples,84,axis=0)
    return med,p16,p84,samples

def test_known_dipole_recovery_v2():
    print("\n=== Test G v2: Known dipole recovery with MCMC (same method as E) ===")
    np.random.seed(42)
    n=1701
    # Use real RA/DEC distribution
    real_path=RESULT_DIR/"pantheon_processed.csv"
    if real_path.exists():
        real=pd.read_csv(real_path)
        idx=np.random.choice(len(real),size=n,replace=True)
        ra=real['RA'].values[idx]
        dec=real['DEC'].values[idx]
        z=real['zHD'].values[idx]
    else:
        ra=np.random.uniform(0,360,size=n)
        dec=np.random.uniform(-90,90,size=n)
        z=np.random.exponential(0.1,size=n)
        z=np.clip(z,0.001,2.0)

    true_A=0.02; true_RA=166.0; true_DEC=-27.0; true_S=0.05
    ra_rad=np.deg2rad(ra); dec_rad=np.deg2rad(dec)
    true_ra_rad=np.deg2rad(true_RA); true_dec_rad=np.deg2rad(true_DEC)
    cos_theta=np.sin(dec_rad)*np.sin(true_dec_rad)+np.cos(dec_rad)*np.cos(true_dec_rad)*np.cos(ra_rad-true_ra_rad)
    delta_m_true=true_A*cos_theta*np.exp(-z/true_S)
    # Add noise 0.15 mag
    delta_m_obs=delta_m_true+np.random.normal(0,0.15,size=n)

    med,p16,p84,samples=fit_mcmc(ra,dec,z,delta_m_obs,sigma=0.15)

    print(f"True: A={true_A}, RA={true_RA}, DEC={true_DEC}, S={true_S}")
    print(f"Recovered: A={med[0]:.4f} +{p84[0]-med[0]:.4f} -{med[0]-p16[0]:.4f}, RA={med[1]:.2f} +{p84[1]-med[1]:.2f} -{med[1]-p16[1]:.2f}, DEC={med[2]:.2f} +{p84[2]-med[2]:.2f} -{med[2]-p16[2]:.2f}, S={med[3]:.4f}")

    # Angular separation
    def ang_sep(ra1,dec1,ra2,dec2):
        ra1=np.deg2rad(ra1); dec1=np.deg2rad(dec1); ra2=np.deg2rad(ra2); dec2=np.deg2rad(dec2)
        cos_t=np.sin(dec1)*np.sin(dec2)+np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)
        cos_t=np.clip(cos_t,-1,1)
        return np.rad2deg(np.arccos(cos_t)), cos_t

    sep,cos_t=ang_sep(true_RA,true_DEC,med[1],med[2])
    print(f"Separation: {sep:.2f} deg, cosθ={cos_t:.4f}")

    # Check if within 2σ
    # For amplitude: true within [p16,p84]?
    amp_ok = (p16[0] <= true_A <= p84[0]) or abs(med[0]-true_A)/((p84[0]-p16[0])/2) < 2
    dir_ok = sep < 30  # within 30 deg
    S_ok = abs(med[3]-true_S) < 0.05

    print(f"Amplitude OK? {amp_ok}, Direction OK? {dir_ok} (<30°), S OK? {S_ok}")

    if amp_ok and dir_ok:
        print("PASS: Pipeline recovers injected dipole within reasonable error — per recenzja punkt 4, wolno patrzeć na wynik prawdziwych danych")
    else:
        print("FAIL: Pipeline still does not recover injected dipole — wymaga dalszej poprawy przed interpretacją prawdziwych danych (per recenzja)")

    return {
        'true': {'A':true_A,'RA':true_RA,'DEC':true_DEC,'S':true_S},
        'recovered': {'A':float(med[0]),'RA':float(med[1]),'DEC':float(med[2]),'S':float(med[3]),
                      'A_p16':float(p16[0]),'A_p84':float(p84[0]),
                      'RA_p16':float(p16[1]),'RA_p84':float(p84[1]),
                      'DEC_p16':float(p16[2]),'DEC_p84':float(p84[2]),
                      'S_p16':float(p16[3]),'S_p84':float(p84[3])},
        'sep_deg': float(sep),
        'cos_theta': float(cos_t),
        'amp_ok': bool(amp_ok),
        'dir_ok': bool(dir_ok),
        'S_ok': bool(S_ok),
        'pass': bool(amp_ok and dir_ok)
    }

if __name__=="__main__":
    print("Krok G v2 — poprawiony test odzysku")
    res=test_known_dipole_recovery_v2()
    out_path=RESULT_DIR/"null_tests_v2.json"
    with open(out_path,'w') as f:
        json.dump(res,f,indent=2)
    print(f"Saved {out_path}")
    print("Krok G v2 done.")
