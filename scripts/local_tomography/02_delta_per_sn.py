#!/usr/bin/env python3
"""
Krok C — δ(z, n̂) per supernowa
Dla każdej SN interpoluj pole prędkości wzdłuż LOS do jej z, policz dominujący człon dopplerowski

Wzory:
delta(z, n) ≈ [1 - (1+z)^2 / (H(z) d_L(z))] * (v_src·n - v_LG·n)/c
Δm = -(5/ln10) * delta

Dla z>0.2 flaguj że soczewkowanie i ISW/Rees-Sciama mogą być niezaniedbywalne.
"""
import numpy as np, pathlib, json, pandas as pd
from astropy.cosmology import FlatLambdaCDM
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "local_structure_test" / "data"
RESULT_DIR = ROOT / "results" / "local_tomography"

H0 = 70.0
Om0 = 0.3
cosmo = FlatLambdaCDM(H0=H0, Om0=Om0)
c_kms = 299792.458

# LG velocity Galactic
l_deg, b_deg = 276.0, 30.0
l = np.deg2rad(l_deg); b = np.deg2rad(b_deg)
v_LG_vec = 627.0 * np.array([np.cos(b)*np.cos(l), np.cos(b)*np.sin(l), np.sin(b)])

def load_velocity_field(method='C15'):
    path = RESULT_DIR / f"velocity_field_{method}.npz"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    data = np.load(path)
    return data

def trilinear_interp(grid_data, positions):
    """
    grid_data: dict with vx, vy, vz, coords_1d, box_size, ngrid
    positions: (N,3) in Mpc/h Galactic Cartesian
    Returns interpolated velocities (N,3)
    """
    coords_1d = grid_data['coords_1d']
    ngrid = int(grid_data['ngrid'])
    box_size = float(grid_data['box_size'])
    # coords_1d is from -box/2+dx/2 to box/2-dx/2
    # Compute indices
    dx = box_size / ngrid
    # Convert positions to grid indices
    # pos in [-200,200], coords_1d[0] = -198.4 etc.
    # Use linear interpolation
    # For each dimension, find lower index
    # We have regular grid, so idx = (pos - coords_1d[0])/dx
    # coords_1d[0] = -box/2 + dx/2
    x0 = coords_1d[0]
    # positions shape (N,3)
    idx_float = (positions - x0) / dx
    # Clip to [0, ngrid-1]
    # For interpolation we need 0 <= idx <= ngrid-2
    idx_float = np.clip(idx_float, 0, ngrid-1-1e-6)
    idx0 = np.floor(idx_float).astype(int)
    idx1 = idx0 + 1
    frac = idx_float - idx0

    # Gather velocities
    vx = grid_data['vx']
    vy = grid_data['vy']
    vz = grid_data['vz']

    # For each SN, trilinear interpolation
    # Vectorized approach using advanced indexing
    N = positions.shape[0]
    v_interp = np.zeros((N,3))

    # This is a bit heavy but N~1700, okay loop
    for i in range(N):
        ix0, iy0, iz0 = idx0[i]
        ix1, iy1, iz1 = idx1[i]
        fx, fy, fz = frac[i]

        # 8 corners
        c000 = np.array([vx[ix0,iy0,iz0], vy[ix0,iy0,iz0], vz[ix0,iy0,iz0]])
        c001 = np.array([vx[ix0,iy0,iz1], vy[ix0,iy0,iz1], vz[ix0,iy0,iz1]])
        c010 = np.array([vx[ix0,iy1,iz0], vy[ix0,iy1,iz0], vz[ix0,iy1,iz0]])
        c011 = np.array([vx[ix0,iy1,iz1], vy[ix0,iy1,iz1], vz[ix0,iy1,iz1]])
        c100 = np.array([vx[ix1,iy0,iz0], vy[ix1,iy0,iz0], vz[ix1,iy0,iz0]])
        c101 = np.array([vx[ix1,iy0,iz1], vy[ix1,iy0,iz1], vz[ix1,iy0,iz1]])
        c110 = np.array([vx[ix1,iy1,iz0], vy[ix1,iy1,iz0], vz[ix1,iy1,iz0]])
        c111 = np.array([vx[ix1,iy1,iz1], vy[ix1,iy1,iz1], vz[ix1,iy1,iz1]])

        # Interpolate
        c00 = c000*(1-fx) + c100*fx
        c01 = c001*(1-fx) + c101*fx
        c10 = c010*(1-fx) + c110*fx
        c11 = c011*(1-fx) + c111*fx

        c0 = c00*(1-fy) + c10*fy
        c1 = c01*(1-fy) + c11*fy

        c = c0*(1-fz) + c1*fz
        v_interp[i] = c

    return v_interp

def compute_delta_for_sn(df, method='C15'):
    print(f"\nComputing delta per SN for method {method}")
    grid_data = load_velocity_field(method)

    # SN coordinates
    # RA, DEC in degrees, convert to Galactic Cartesian unit vectors
    # Use astropy to convert ICRS to Galactic, then to Cartesian
    coords = SkyCoord(ra=df['RA'].values*u.deg, dec=df['DEC'].values*u.deg, frame='icrs')
    gal = coords.galactic
    l_sn = gal.l.rad
    b_sn = gal.b.rad
    # Unit vectors in Galactic Cartesian
    nx = np.cos(b_sn)*np.cos(l_sn)
    ny = np.cos(b_sn)*np.sin(l_sn)
    nz = np.sin(b_sn)
    n_hat = np.vstack([nx, ny, nz]).T  # (N,3)

    # Comoving distance from zHD
    z = df['zHD'].values
    # For h=0.7, comoving distance in Mpc/h = comoving in Mpc * h
    # cosmo.comoving_distance returns Mpc, convert to Mpc/h
    h = H0/100.0
    comov_mpc = cosmo.comoving_distance(z).value  # Mpc
    comov_mpc_h = comov_mpc * h  # Mpc/h

    # Positions in Mpc/h Galactic Cartesian: r = comov * n_hat
    positions = (comov_mpc_h[:, None] * n_hat)  # (N,3)

    # Interpolate v_src
    v_src = trilinear_interp(grid_data, positions)

    # Compute v·n
    v_src_dot_n = np.sum(v_src * n_hat, axis=1)
    v_LG_dot_n = np.sum(v_LG_vec * n_hat, axis=1)

    # H(z) and d_L(z)
    H_z = cosmo.H(z).value  # km/s/Mpc
    d_L = cosmo.luminosity_distance(z).value  # Mpc

    # Factor [1 - (1+z)^2 / (H d_L)] ; need H in same units: H(z) [km/s/Mpc] * d_L [Mpc] => km/s, dimensionless? Actually (1+z)^2 / (H d_L) has units: H d_L = (km/s/Mpc)*Mpc = km/s, but (1+z)^2 dimensionless, so need c? Wait formula: delta = [1 - (1+z)^2/(H d_L)] * (v·n)/c
    # So H d_L / c dimensionless? Let's compute: H d_L has km/s, divide by c km/s => dimensionless, so (1+z)^2 / (H d_L / c) ??? Let's check original formula:
    # delta(z, n) ≈ [1 - (1+z)^2 / (H(z) d_L(z))] (v_src·n - v_LG·n)/c
    # If H d_L is in same units as c, then (1+z)^2/(H d_L) is dimensionless only if H d_L in units of c? Actually H*d_L has units of velocity, so (1+z)^2/(H d_L) has 1/velocity. So there is missing c? Let's interpret: formula in task: delta ≈ [1 - (1+z)^2/(H(z) d_L(z))] (v·n)/c
    # So first bracket dimensionless if H d_L is dimensionless? Hmm. In cosmology, H d_L / c is dimensionless. So probably H(z) d_L(z) / c is meant. Let's use that.
    # Compute H d_L / c dimensionless
    HdL_over_c = H_z * d_L / c_kms
    # Then factor = 1 - (1+z)^2 / (HdL_over_c * ???) Wait need check: (1+z)^2 / (H d_L) where H d_L is in units of c? So (1+z)^2 / (H d_L / c) = (1+z)^2 * c / (H d_L)
    # So factor = 1 - (1+z)^2 * c / (H d_L) = 1 - (1+z)^2 / (H d_L / c)
    factor = 1.0 - (1+z)**2 / HdL_over_c
    # For low z, HdL_over_c ≈ z, so factor ≈ 1 - (1)/z ≈ -1/z large negative, which matches known low-z divergence? Actually Doppler term diverges at low z as 1/z.
    # Let's clip for very low z to avoid extreme
    # For z<0.01, factor large, but that's physical (peculiar velocity dominates)

    delta = factor * (v_src_dot_n - v_LG_dot_n) / c_kms

    Delta_m = -(5.0/np.log(10)) * delta

    # Flag high z
    flag_high_z = z > 0.2
    print(f"Flag high-z (>0.2): {flag_high_z.sum()}/{len(z)} ({flag_high_z.mean()*100:.1f}%) - lensing/ISW may be non-negligible")

    # Create result df
    result = pd.DataFrame({
        'CID': df['CID'] if 'CID' in df.columns else np.arange(len(df)),
        'zHD': z,
        'RA': df['RA'],
        'DEC': df['DEC'],
        'l_gal': np.rad2deg(l_sn),
        'b_gal': np.rad2deg(b_sn),
        'n_x': nx, 'n_y': ny, 'n_z': nz,
        'comov_Mpc_h': comov_mpc_h,
        'v_src_x': v_src[:,0], 'v_src_y': v_src[:,1], 'v_src_z': v_src[:,2],
        'v_src_dot_n': v_src_dot_n,
        'v_LG_dot_n': v_LG_dot_n,
        'H_z': H_z,
        'd_L': d_L,
        'factor': factor,
        'delta': delta,
        'Delta_m_pred': Delta_m,
        'flag_high_z': flag_high_z
    })

    print(f"Delta stats: mean {delta.mean():.4e}, std {delta.std():.4e}")
    print(f"Delta_m_pred stats: mean {Delta_m.mean():.4f}, std {Delta_m.std():.4f}, min {Delta_m.min():.4f}, max {Delta_m.max():.4f}")

    return result

if __name__ == "__main__":
    print("Krok C — delta per SN")
    # Load processed Pantheon
    pantheon_path = RESULT_DIR / "pantheon_processed.csv"
    if not pantheon_path.exists():
        # fallback to raw
        raw_path = ROOT / "local_structure_test" / "data" / "Pantheon+SH0ES.dat"
        import pandas as pd
        df = pd.read_csv(raw_path, sep=r'\s+')
    else:
        df = pd.read_csv(pantheon_path)

    for method in ['C15', 'L24']:
        try:
            res = compute_delta_for_sn(df, method=method)
            out_path = RESULT_DIR / f"delta_per_sn_{method}.csv"
            res.to_csv(out_path, index=False)
            print(f"Saved {out_path}")
        except Exception as e:
            print(f"Failed for {method}: {e}")
            import traceback; traceback.print_exc()

    print("Krok C done.")
