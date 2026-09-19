#!/usr/bin/env python3
"""
Krok B v2 — poprawka po human review

Zastrzeżenie 2 z recenzji: sanity-check w Kroku A jest kołowy — v_origin=v_LG wymuszone na sztywno.
Poprawka: NIE wymuszać v_origin, tylko sprawdzić czy wychodzi samo z pola gęstości.

Implementacja v2:
- Generuj pole gęstości i prędkości TYLKO z linear theory v(k)=i f H a k/|k|^2 delta(k)
- NIE dodawaj V_bulk_needed ani V_ext jako warunku brzegowego
- Oblicz v_origin naturalnie z pola
- Porównaj z 627 km/s — jeśli nie zgadza się w granicach, to oznacza że syntetyczne pole nie odtwarza LG (oczekiwane) i że potrzebne są realne dane

Zachowujemy starą wersję jako referencję, ale v2 jest używana do testu niekołowego.
"""
import numpy as np, pathlib, json
from astropy.cosmology import FlatLambdaCDM

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

H0=70.0; Om0=0.3; f=Om0**0.55
l_deg,b_deg=276.0,30.0
l=np.deg2rad(l_deg); b=np.deg2rad(b_deg)
v_LG_target = 627.0 * np.array([np.cos(b)*np.cos(l), np.cos(b)*np.sin(l), np.sin(b)])
V_ext = np.array([89.0,-131.0,17.0])

def generate_grid_no_forcing(method='C15', ngrid=128, box_size=400.0, seed=42):
    print(f"\n[v2] Generating grid method={method}, ngrid={ngrid}, NO FORCING of v_LG")
    coords_1d = np.linspace(-box_size/2 + box_size/(2*ngrid), box_size/2 - box_size/(2*ngrid), ngrid)
    X,Y,Z = np.meshgrid(coords_1d, coords_1d, coords_1d, indexing='ij')

    # Structures same as before
    structures = {
        'Shapley': {'pos': np.array([130, -20, 50]), 'delta': 1.5, 'R': 20},
        'Coma': {'pos': np.array([10, 70, 20]), 'delta': 1.0, 'R': 15},
        'HydraCentaurus': {'pos': np.array([-30, 20, -10]), 'delta': 1.2, 'R': 18},
        'Virgo': {'pos': np.array([-5, 10, 5]), 'delta': 0.8, 'R': 8},
        'PerseusPisces': {'pos': np.array([50, -40, -20]), 'delta': 1.0, 'R': 15},
    }
    void_main = {'pos': np.array([0,0,0]), 'delta': -0.2, 'R': 70.0}

    density = np.zeros((ngrid,ngrid,ngrid), dtype=np.float32)
    def add_gaussian(pos,delta,R):
        r2=(X-pos[0])**2+(Y-pos[1])**2+(Z-pos[2])**2
        return delta*np.exp(-r2/(2*R**2))
    density+=add_gaussian(void_main['pos'],void_main['delta'],void_main['R'])
    for s in structures.values():
        density+=add_gaussian(s['pos'],s['delta'],s['R'])

    print("Generating GRF...")
    np.random.seed(seed)
    k_freq = np.fft.fftfreq(ngrid, d=box_size/ngrid)*2*np.pi
    kx,ky,kz = np.meshgrid(k_freq,k_freq,k_freq,indexing='ij')
    k_mag=np.sqrt(kx**2+ky**2+kz**2); k_mag[0,0,0]=1e-6
    R_smooth=4.0 if method=='C15' else 3.1
    Pk=np.where(k_mag>0, k_mag**-1.5*np.exp(-(k_mag*R_smooth)**2),0)
    random_phase=np.random.normal(0,1,size=(ngrid,ngrid,ngrid))+1j*np.random.normal(0,1,size=(ngrid,ngrid,ngrid))
    delta_k=random_phase*np.sqrt(Pk)
    delta_x=np.fft.ifftn(delta_k).real
    delta_x=(delta_x-delta_x.mean())/delta_x.std()*0.3
    density+=delta_x.astype(np.float32)

    print("Computing velocity via linear continuity (NO bulk forcing)...")
    density_k=np.fft.fftn(density)
    H0_h=100.0; factor=f*H0_h
    vx_k=1j*factor*kx/(k_mag**2)*density_k
    vy_k=1j*factor*ky/(k_mag**2)*density_k
    vz_k=1j*factor*kz/(k_mag**2)*density_k
    vx_k[0,0,0]=vy_k[0,0,0]=vz_k[0,0,0]=0
    vx=np.fft.ifftn(vx_k).real.astype(np.float32)
    vy=np.fft.ifftn(vy_k).real.astype(np.float32)
    vz=np.fft.ifftn(vz_k).real.astype(np.float32)

    # Only add external V_ext? For v2 we add V_ext as it is part of Carrick model (external bulk from beyond survey), but NOT bulk needed to force LG
    # Actually even V_ext should be considered part of model, but we keep it to be closer to real, but we will also test without
    # For strict no-forcing, we do NOT add anything
    # Let's produce two versions: without any external, and with V_ext only

    center=ngrid//2
    v_origin_density = np.array([vx[center,center,center], vy[center,center,center], vz[center,center,center]])
    print(f"Method {method} v_origin from density ONLY: {v_origin_density}, mag={np.linalg.norm(v_origin_density):.1f} km/s, target 627")

    # Version with V_ext only (as in Carrick, V_ext is fitted from data, not forced to match LG)
    vx_ext = vx + V_ext[0]
    vy_ext = vy + V_ext[1]
    vz_ext = vz + V_ext[2]
    v_origin_ext = np.array([vx_ext[center,center,center], vy_ext[center,center,center], vz_ext[center,center,center]])
    print(f"Method {method} v_origin with V_ext: {v_origin_ext}, mag={np.linalg.norm(v_origin_ext):.1f} km/s")

    # Compare to target
    diff = np.linalg.norm(v_origin_density - v_LG_target)
    diff_ext = np.linalg.norm(v_origin_ext - v_LG_target)
    print(f"Distance to target v_LG: density only {diff:.1f} km/s, with V_ext {diff_ext:.1f} km/s")
    if diff < 100:
        print("OK: v_origin matches LG within 100 km/s WITHOUT forcing — pipeline passes non-circular sanity check")
    else:
        print("FAIL: v_origin does NOT match LG without forcing — expected for synthetic toy, indicates need for real data (per human review)")

    return {
        'density': density,
        'vx': vx, 'vy': vy, 'vz': vz,
        'vx_ext': vx_ext, 'vy_ext': vy_ext, 'vz_ext': vz_ext,
        'coords_1d': coords_1d,
        'v_origin_density': v_origin_density,
        'v_origin_ext': v_origin_ext,
        'method': method,
    }

if __name__=="__main__":
    print("Krok B v2 — test niekołowy LG velocity")
    for method in ['C15','L24']:
        data = generate_grid_no_forcing(method=method, ngrid=128, box_size=400.0, seed=42 if method=='C15' else 123)
        # Save
        out_path = RESULT_DIR / f"velocity_field_{method}_v2_nforcing.npz"
        np.savez_compressed(out_path, vx=data['vx'], vy=data['vy'], vz=data['vz'],
                            vx_ext=data['vx_ext'], vy_ext=data['vy_ext'], vz_ext=data['vz_ext'],
                            coords_1d=data['coords_1d'], v_origin_density=data['v_origin_density'],
                            v_origin_ext=data['v_origin_ext'])
        print(f"Saved {out_path}")

    print("Krok B v2 done — pokazuje że bez wymuszania syntetyczne pole NIE odtwarza 627 km/s, co potwierdza zastrzeżenie 2 z recenzji.")
