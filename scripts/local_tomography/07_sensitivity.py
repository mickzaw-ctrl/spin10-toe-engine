#!/usr/bin/env python3
"""
Krok H — Analiza wrażliwości
- Powtórz z dwiema niezależnymi metodami rekonstrukcji pola (Wiener vs NN) — wynik ma być zgodny między nimi, inaczej nie ufaj mu
- Powtórz przy założeniu promienia struktury ~70 Mpc vs ~300 Mpc
- Dyskusja: dynamicznie preferowana skala z CosmicFlows-4 to ≤70 Mpc, nie pełna fotometryczna pustka KBC 300 Mpc

Implementacja:
- Porównanie C15 vs L24 (już zrobione w Krok F)
- Toy model dla R=70 vs R=300: v_edge = (1/3) f H0 delta R, oblicz przewidywany dipol i H0_local
- Test wrażliwości na bias b, f, H0
"""
import numpy as np, pathlib, json

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results" / "local_tomography"

H0 = 70.0
Om0 = 0.3
f = Om0**0.55
c_kms = 299792.458

def toy_v_edge(R, delta=-0.2):
    return (1/3) * f * H0 * delta * R

def H_local_from_void(R, delta=-0.2, H_bg=67.4):
    """
    Szacunkowy lokalny H0 z outflow z pustki
    H_local ≈ H_bg * (1 - (1/3) f delta * (R/r) ???)
    Uproszczony: v_outflow = (1/3) f H0 delta R, H_local = H_bg + v/R
    Dla top-hat, wewnątrz pustki H_local = H_bg * (1 - delta/3 * f?) - przybliżenie
    Użyjemy: H_local = H_bg - (1/3) f H_bg delta ??? 
    Dla delta negative (underdense), H_local > H_bg
    """
    # v_edge = (1/3) f H0 delta R, delta negative => v negative = outflow? Actually outflow positive if delta negative? 
    # v_edge = (1/3) f H0 delta R, delta negative => v_edge negative (infall? sign confusion)
    # We want outflow: v = -(1/3) f H0 delta R for delta negative gives positive
    v_out = -toy_v_edge(R, delta)  # positive outflow for underdensity
    # H_local = H_bg + v_out / R
    H_local = H_bg + v_out / R
    return H_local, v_out

def load_comparison():
    path = RESULT_DIR / "comparison.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def load_dipole_pred():
    # Load both methods
    results = {}
    for method in ['C15', 'L24']:
        path = RESULT_DIR / f"dipole_pred_{method}_nside16.json"
        if path.exists():
            with open(path) as f:
                results[method] = json.load(f)
    return results

if __name__ == "__main__":
    print("Krok H — Analiza wrażliwości")

    # 1. Porównanie metod C15 vs L24
    print("\n=== 1. Porównanie metod rekonstrukcji (C15 vs L24) ===")
    preds = load_dipole_pred()
    for m, data in preds.items():
        print(f"{m}: RA={data['RA']:.2f}, DEC={data['DEC']:.2f}, amp={data['dipole_amplitude']:.5f}, l={data['l_gal']:.2f}, b={data['b_gal']:.2f}")

    if 'C15' in preds and 'L24' in preds:
        # Angular separation
        def ang_sep(ra1,dec1,ra2,dec2):
            ra1=np.deg2rad(ra1); dec1=np.deg2rad(dec1); ra2=np.deg2rad(ra2); dec2=np.deg2rad(dec2)
            cos_t = np.sin(dec1)*np.sin(dec2)+np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)
            cos_t=np.clip(cos_t,-1,1)
            return np.rad2deg(np.arccos(cos_t)), cos_t
        sep, cos_t = ang_sep(preds['C15']['RA'], preds['C15']['DEC'], preds['L24']['RA'], preds['L24']['DEC'])
        print(f"Separation C15 vs L24: {sep:.2f} deg, cosθ={cos_t:.4f}")
        if sep < 60:
            print("Zgodność między metodami w granicach 60° - OK per pre-reg")
        else:
            print("NIEZGODNOŚĆ między metodami >60° - per pre-reg, wynik wymaga dalszej weryfikacji, human review")

        # Amplitude ratio
        amp_c = preds['C15']['dipole_amplitude']
        amp_l = preds['L24']['dipole_amplitude']
        ratio = amp_c/amp_l if amp_l!=0 else 0
        print(f"Amplitude ratio C15/L24 = {ratio:.2f} (C15={amp_c:.5f}, L24={amp_l:.5f})")
        if 0.5 < ratio < 2.0:
            print("Amplitudy zgodne w factor 2 - OK")
        else:
            print("Amplitudy niezgodne >factor 2 - wymaga weryfikacji")

    # 2. Test skali R=70 vs R=300 Mpc
    print("\n=== 2. Test skali struktury: R=70 Mpc vs R=300 Mpc ===")
    print("Toy model: v_edge = (1/3) f H0 delta R")
    for R in [70, 300]:
        for delta in [-0.2, -0.3]:
            v = toy_v_edge(R, delta)
            H_loc, v_out = H_local_from_void(R, delta, H_bg=67.4)
            print(f"R={R} Mpc, delta={delta}: v_edge={v:.1f} km/s, v_out={v_out:.1f} km/s, H_local≈{H_loc:.2f} km/s/Mpc (bg 67.4)")

    print("\nInterpretacja (Boubel et al. 2025, arXiv:2506.10518):")
    print("- Dynamicznie preferowana skala z CF4 Tully-Fisher to ≤70 Mpc (≤10% fiducial KBC 300 Mpc)")
    print("- R=70 Mpc, delta=-0.2 => v_out~168 km/s, H_local~69.8 km/s/Mpc (niewielka poprawka do H0, ~2.4 km/s/Mpc)")
    print("- R=300 Mpc, delta=-0.2 => v_out~722 km/s, H_local~69.8? Wait same? Actually v_out/R = -(1/3) f H0 delta = const, so H_local independent of R in this toy? Let's compute: v_out/R = -(1/3) f H0 delta = const ~2.4 km/s/Mpc for delta=-0.2")
    print("- Bardziej realistycznie, dla R=300 Mpc, outflow nie jest stały wewnątrz, profil Gaussa/MB daje większe v w środku?")
    print("- W każdym razie, skala 300 Mpc wymagałaby głębokiej pustki niezgodnej z ΛCDM (6σ tension, Haslbauer et al.)")
    print("- Nasze testy używają R_main=70 Mpc jako głównego założenia, R=300 jako testu odporności")

    # 3. Wrażliwość na bias b
    print("\n=== 3. Wrażliwość na bias b i f ===")
    for b in [1.0, 1.1, 1.3, 1.5]:
        # delta_m = delta_g / b, v ∝ delta_m, więc v ∝ 1/b
        # Amplituda dipolu ∝ 1/b
        print(f"b={b}: v scaling ∝ 1/b = {1/b:.3f}, dla b=1.1 vs 1.3 ratio {1.1/1.3:.3f} => amplituda 15% mniejsza dla większego b")

    for Om in [0.25, 0.3, 0.35]:
        f_test = Om**0.55
        print(f"Om={Om}: f={f_test:.3f}, scaling v ∝ f")

    # 4. Wrażliwość na H0
    print("\n=== 4. Wrażliwość na H0 ===")
    for H in [67.4, 70, 73]:
        print(f"H0={H}: d_L scaling, factor [1-(1+z)^2/(H d_L)] changes, but low-z approx ∝ 1/H")

    # 5. Podsumowanie zgodności z literaturą
    print("\n=== 5. Tabela porównawcza z literaturą (szkic) ===")
    print("Colin et al. 2019: dipol q0, A~0.46, kierunek zgodny z CMB dipole (l~264,b~48), exp(-z/0.05), significance 3.9σ")
    print("Erdoğdu et al. 2006: 2MRS density, bulk flow ~300 km/s within 50 Mpc/h")
    print("Carrick et al. 2015: V_ext=[89,-131,17], beta=0.43, bulk flow 239±45 km/s within 200 Mpc/h")
    print("Boubel et al. 2025 (arXiv:2506.10518): CF4 Tully-Fisher prefers void size ≤70 Mpc, H_local=70.4±0.4 (Gaussian), 72.1±0.9 (exp), vs Planck 67.4")
    print("Lilow & Nusser 2021: CORAS, 200 Mpc/h reconstruction, bulk flow 239±45 km/s, LG velocity consistent")
    print("Lilow et al. 2024: NN reconstruction, 3.1 Mpc/h, similar")
    print("NR observer study 2026 (wspomniany '1 na 20'): nasze otoczenie nietypowe na poziomie 5% (1/20) w ΛCDM jeśli pustka 20% do 300 Mpc")
    print("Nasz wynik: predykcja ~0.002-0.009 mag, obserwacja ~0.113 mag, cosθ~0.03 (niespójne) - wskazuje że lokalna struktura ≤70 Mpc nie wyjaśnia całego obserwowanego dipolu, może być dodatkowy wkład systematyk lub większa skala")

    # Save sensitivity results
    out = {
        'toy_R70_delta02_v_edge': float(toy_v_edge(70, -0.2)),
        'toy_R300_delta02_v_edge': float(toy_v_edge(300, -0.2)),
        'H_local_R70': float(H_local_from_void(70, -0.2)[0]),
        'H_local_R300': float(H_local_from_void(300, -0.2)[0]),
        'C15_vs_L24_sep_deg': float(sep) if 'sep' in locals() else None,
        'C15_vs_L24_cos': float(cos_t) if 'cos_t' in locals() else None,
    }
    with open(RESULT_DIR / "sensitivity.json", 'w') as f:
        json.dump(out, f, indent=2)

    print("\nKrok H done.")
