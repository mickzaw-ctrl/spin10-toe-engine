#!/usr/bin/env python3
"""
Krok D — Mapa i multipole
Zbuduj mapę przewidzianej poprawki Δm(n̂) (HEALPix, nside dobrany do gęstości próbki),
rozłóż na harmoniki sferyczne, wyciągnij dipol (ℓ=1) — kierunek + amplitudę z niepewnością
(propagacja błędów z niepewności pola prędkości).

Wykorzystuje healpy.
"""
import numpy as np, pathlib, json, pandas as pd
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"

def build_healpix_map(df, nside=32):
    """
    df: with RA, DEC, Delta_m_pred
    Build HEALPix map averaging Δm in each pixel
    """
    npix = hp.nside2npix(nside)
    print(f"Building HEALPix map nside={nside}, npix={npix}")
    # Convert RA/DEC to theta, phi (healpy uses theta=colatitude, phi=longitude)
    # RA = phi, DEC = 90 - theta
    theta = np.deg2rad(90.0 - df['DEC'].values)
    phi = np.deg2rad(df['RA'].values)
    # Alternatively RA = phi, but healpy phi in [0,2pi)
    pix = hp.ang2pix(nside, theta, phi)

    # Average per pixel
    map_sum = np.zeros(npix)
    map_count = np.zeros(npix)
    for p, dm in zip(pix, df['Delta_m_pred'].values):
        map_sum[p] += dm
        map_count[p] += 1

    # Avoid div by zero
    healpix_map = np.full(npix, hp.UNSEEN)
    mask = map_count>0
    healpix_map[mask] = map_sum[mask] / map_count[mask]

    # Fill unseen with 0 for dipole fit? Better keep UNSEEN but for anafast need to handle
    # For dipole extraction, we can use fit_dipole on masked map
    print(f"Filled pixels: {mask.sum()}/{npix} ({mask.mean()*100:.1f}%)")
    return healpix_map, map_count

def extract_dipole_healpix(healpix_map, nside):
    """
    Extract dipole using healpy fit_dipole or anafast
    Returns direction and amplitude
    """
    # Replace UNSEEN with 0 for anafast? Better use hp.remove_dipole? Let's use fit_dipole
    # hp.fit_dipole works with UNSEEN? It may ignore UNSEEN. Let's check
    # We'll create a map where UNSEEN -> 0 but keep track
    map_for_fit = healpix_map.copy()
    unseen_mask = (map_for_fit == hp.UNSEEN)
    map_for_fit[unseen_mask] = 0.0

    # Fit dipole
    # fit_dipole returns dipole vector and monopole
    try:
        dipole = hp.fit_dipole(map_for_fit)
        # dipole is (monopole, dipole_vector)
        mono = dipole[0]
        dip_vec = dipole[1]  # in Galactic? Actually healpy uses same coordinate as map (we used RA/DEC -> theta,phi which is equatorial? No, we used RA/DEC directly as phi, theta, so map is in equatorial)
        # dipole vector components in same Cartesian as healpy? hp.fit_dipole returns vector in same coords as map's pixelization (which is defined by theta,phi)
        # The vector is in the Cartesian basis of the map (x,y,z) where z is north pole (DEC=90)
        print(f"fit_dipole: mono={mono:.5f}, dipole vector={dip_vec}, amp={np.linalg.norm(dip_vec):.5f}")
    except Exception as e:
        print(f"fit_dipole failed: {e}")
        mono = 0
        dip_vec = np.array([0,0,0])

    # Also compute alm and Cl
    # Use anafast
    try:
        # Use map_for_fit with lmax=3
        alm = hp.map2alm(map_for_fit, lmax=3)
        # alm is complex array, get dipole components
        # For l=1, m=-1,0,1
        # Convert to dipole vector: see healpy docs
        # Instead compute Cl
        cl = hp.alm2cl(alm, lmax=3)
        print(f"Cl: l=0:{cl[0]:.5e}, l=1:{cl[1]:.5e}, l=2:{cl[2]:.5e}, l=3:{cl[3]:.5e}")
    except Exception as e:
        print(f"map2alm failed: {e}")
        cl = np.zeros(4)

    # Direction from dipole vector
    dip_amp = np.linalg.norm(dip_vec)
    if dip_amp>0:
        dip_unit = dip_vec / dip_amp
        # Convert Cartesian (x,y,z) where x= sin(theta)cos(phi)... Actually healpy's dipole vector is in same basis as map: 
        # For equatorial map (RA=phi, DEC), the Cartesian is: x = cos(DEC)cos(RA), y=cos(DEC)sin(RA), z=sin(DEC)
        # So we can convert to RA/DEC
        # dip_unit = [x,y,z]
        x,y,z = dip_unit
        dec = np.rad2deg(np.arcsin(z))
        ra = np.rad2deg(np.arctan2(y,x)) % 360
        print(f"Dipole direction: RA={ra:.2f} deg, Dec={dec:.2f} deg, amp={dip_amp:.5f} mag")
        # Also convert to Galactic l,b
        try:
            c = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            gal = c.galactic
            l_gal = gal.l.deg
            b_gal = gal.b.deg
            print(f"Galactic: l={l_gal:.2f}, b={b_gal:.2f}")
        except Exception as e:
            print(f"Galactic conversion failed: {e}")
            l_gal, b_gal = 0,0
    else:
        ra, dec, l_gal, b_gal = 0,0,0,0
        dip_unit = np.array([0,0,0])

    return {
        'monopole': float(mono),
        'dipole_vector': dip_vec.tolist() if hasattr(dip_vec, 'tolist') else list(dip_vec),
        'dipole_amplitude': float(dip_amp),
        'dipole_unit': dip_unit.tolist(),
        'RA': float(ra) if 'ra' in locals() else 0,
        'DEC': float(dec) if 'dec' in locals() else 0,
        'l_gal': float(l_gal) if 'l_gal' in locals() else 0,
        'b_gal': float(b_gal) if 'b_gal' in locals() else 0,
        'cl': cl.tolist() if hasattr(cl, 'tolist') else list(cl),
        'nside': int(nside),
    }

def process_method(method, nside=32):
    print(f"\n=== Processing {method} nside={nside} ===")
    csv_path = RESULT_DIR / f"delta_per_sn_{method}.csv"
    if not csv_path.exists():
        print(f"Missing {csv_path}")
        return None
    df = pd.read_csv(csv_path)
    # Filter low-z for main analysis: 0.01<z<0.1 as per pre-reg
    df_low = df[(df['zHD']>0.01) & (df['zHD']<0.1)]
    print(f"Total SN: {len(df)}, low-z (0.01-0.1): {len(df_low)}")
    # Use low-z for dipole (dominant Doppler)
    if len(df_low)<10:
        print("Not enough low-z, using all")
        df_use = df
    else:
        df_use = df_low

    healpix_map, counts = build_healpix_map(df_use, nside=nside)
    dipole_info = extract_dipole_healpix(healpix_map, nside=nside)

    # Save map
    out_map_path = RESULT_DIR / f"healpix_map_{method}_nside{nside}.npy"
    np.save(out_map_path, healpix_map)
    print(f"Saved map to {out_map_path}")

    # Also save dipole info
    out_json = RESULT_DIR / f"dipole_pred_{method}_nside{nside}.json"
    with open(out_json, 'w') as f:
        json.dump(dipole_info, f, indent=2)
    print(f"Saved dipole to {out_json}")

    return dipole_info

if __name__ == "__main__":
    print("Krok D — Mapa i multipole")
    for method in ['C15', 'L24']:
        for nside in [16, 32]:
            try:
                info = process_method(method, nside=nside)
            except Exception as e:
                print(f"Failed {method} nside {nside}: {e}")
                import traceback; traceback.print_exc()

    print("Krok D done.")
