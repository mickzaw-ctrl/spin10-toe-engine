#!/usr/bin/env python3
"""
Demo Termo-Chromo-Dynamika jako Teoria Wszystkiego — CLI v15.0-TCD
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from termo_chromo_dynamics import ThermoChromoDynamicsEngine, TCDLabForApex
import json

def main():
    print(">>> SHZSpin10 v15.0-TCD — Termo-Chromo-Dynamika jako TOE")
    engine = ThermoChromoDynamicsEngine(N=10**6, M_SUSY_GeV=5000.0)
    
    print("\n--- Uruchamianie pełnej symulacji TCD ---")
    report = engine.run_full_tcd_simulation()
    
    print("\n=== KLUCZOWE WYNIKI TCD ===")
    print(f"Engine version: {report['engine_version']}")
    print(f"M_GUT = {report['rge_thermo_chromo']['M_GUT_GeV']:.3e} GeV")
    print(f"alpha_GUT^-1 = {report['rge_thermo_chromo']['alpha_GUT_inv']:.2f}")
    print(f"alpha_s(MZ) = {report['rge_thermo_chromo']['alpha_s_MZ']:.4f} (target 0.118)")
    
    ct = report['critical_temperatures']
    print(f"T_c QCD = {ct['T_c_QCD_MeV']} MeV (lattice 155 MeV)")
    print(f"CF from Polyakov at T_c = {ct['CF_T_c']:.3f} (eq 0.738)")
    
    tcd = report['tcd_predictions']
    print(f"\nTCD-2 eta/s = {tcd['TCD-2_eta_s']['eta/s_Tc']:.4f} (RHIC 0.09)")
    print(f"TCD-4 glueball 0++ = {tcd['TCD-4_glueball']['0++_MeV']:.1f} MeV (lattice 1710)")
    print(f"TCD-3 α5 phenom 1μm = {tcd['TCD-3_fifth_force']['alpha_5_with_torsion_resummed_phenom']:.2e}")
    print(f"TCD-5 ΔG_BBN/G = {tcd['TCD-5_DeltaG']['DeltaG_BBN']:.2e} (<0.1 passes)")
    
    print(f"\nSpectral flow:")
    for k,v in report['spectral_dimension_flow'].items():
        print(f"  {k} => d_S={v:.2f}")
    
    print(f"\nEmergent gravity (Jacobson):")
    print(f"  P(N,T) = {report['emergent_gravity_Jacobson']['P(N,T)']:.5f}")
    print(f"  G_eff/G0 = {report['emergent_gravity_Jacobson']['G_eff/G0']:.5f}")
    print(f"  Omega_Lambda (calib) = {report['emergent_gravity_Jacobson']['Omega_Lambda_TCD_calib']}")
    
    print(f"\nReinterpretacja heptalogii:")
    for k,v in tcd['reinterpreted_38'].items():
        print(f"  {k}: {v}")
    
    print("\n=== FALSYFIKACJA ===")
    for k,v in report['falsification_criteria'].items():
        print(f"  {k}: {v}")
    
    # Save report
    out_path = "results/termo_chromo_dynamics_report.json"
    os.makedirs("results", exist_ok=True)
    # Convert to json serializable (some floats already)
    try:
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n[OK] Report saved to {out_path}")
    except Exception as e:
        print(f"[WARN] Could not save json: {e}")
    
    # Try integration with Ultima Apex engine if available
    try:
        from windows_package.shzspin10.engine import SHZSpin10UltimaApex
        print("\n--- Integracja z SHZSpin10UltimaApex (v14.5 + TCD Lab) ---")
        apex = SHZSpin10UltimaApex()
        # if new method exists use it else use TCD lab
        if hasattr(apex, 'run_termo_chromo_simulation'):
            tcd_report2 = apex.run_termo_chromo_simulation()
            print("Apex TCD method executed.")
        else:
            lab = TCDLabForApex(N=10**6)
            tcd_report2 = lab.run_termo_chromo_simulation()
            print("Apex via TCDLabForApex executed.")
        print(f"  Consistency 40/40: {tcd_report2['consistency_with_heptalogy']}")
    except Exception as e:
        print(f"[INFO] Apex integration skipped: {e}")
    
    print("\n>>> TCD DEMO zakończony — Termo-Chromo-Dynamika jako TOE.")

if __name__ == "__main__":
    main()
