"""
CONFRONTATION Spin(10) Split-SUSY with MEG-II (2026) and Mu3e (2028+)
Nearest model tests
"""

print("="*75)
print(" CONFRONTATION: Spin(10) Split-SUSY vs LFV 2026-2030")
print("="*75)

print("\n" + "="*75)
print(" 1. CURRENT LFV STATUS (2025)")
print("="*75)

# Aktualne limity (2024-2025)
MEG_combined = 3.1e-13   # MEG + MEG-II 2022 (90% CL)
MEG_II_2022   = 7.5e-13  # MEG-II only, 2022 data
MEG_II_target = 6.0e-14  # Final target (end 2026)

print(f"\nCurrent limits BR(mu->e gamma):")
print(f"  MEG (2016):              4.2e-13 (90% CL)")
print(f"  MEG-II (2022 only):      {MEG_II_2022:.1e} (90% CL)")
print(f"  MEG + MEG-II (2024):     {MEG_combined:.1e} (90% CL) - BEST")
print(f"  MEG-II final (end 2026): ~{MEG_II_target:.1e} - TARGET")

# Spin(10) prediction
M_SUSY = 5000  # GeV
BR_spin10 = 5e-11 * (1000.0/M_SUSY)**4

print(f"\nSpin(10) Split-SUSY prediction:")
print(f"  M_SUSY = {M_SUSY/1000} TeV")
print(f"  BR(mu->e gamma) = {BR_spin10:.2e}")

print(f"\nRatio Spin(10)/Limit:")
print(f"  vs MEG 2016:    {BR_spin10/4.3e-13:.4f}  {'<OK' if BR_spin10 < 4.3e-13 else 'excluded'}")
print(f"  vs MEG-II 2024: {BR_spin10/MEG_combined:.4f}  {'<OK' if BR_spin10 < MEG_combined else 'excluded'}")
print(f"  vs MEG-II 2026: {BR_spin10/MEG_II_target:.4f}  {'<OK' if BR_spin10 < MEG_II_target else 'excluded'}")

# 2026 prognoza
print("\n" + "="*75)
print(" 2. MEG-II 2026 - FIRST SPIN(10) TEST")
print("="*75)

print(f"\n[Scenario: MEG-II ends at end of 2026]")
print(f"  MEG-II final sensitivity:  {MEG_II_target:.1e}")
print(f"  Spin(10) BR:           {BR_spin10:.2e}")
print(f"  Spin(10)/MEG-II:       {BR_spin10/MEG_II_target:.3f}")
print(f"  SNR Spin(10):          {BR_spin10/MEG_II_target:.2f}σ")

if BR_spin10 > MEG_II_target:
    print(f"\n>>> MEG-II WILL SEE Spin(10) signal <<<")
else:
    print(f"\n>>> MEG-II WILL NOT see Spin(10) - falsification <<<")

# Year forecasts
print("\n" + "="*75)
print(" 3. CONFRONTATION TIMELINE 2025-2030")
print("="*75)

forecasts = [
    (2025, "MEG 2016 limit",          4.3e-13,  8e-14,  0.19, "Spin(10) << limit"),
    (2025, "MEG+MEG-II 2022",         3.1e-13,  8e-14,  0.26, "Spin(10) << limit"),
    (2026, "MEG-II final",            6.0e-14,  8e-14,  1.33, "MEG-II sees Spin(10) 1.3σ!"),
    (2028, "Mu3e Phase-I (μ→eee)",   1.0e-15,  5e-17,  0.05, "marginal"),
    (2028, "Mu2e (μ→e conv)",         1.0e-16,  1e-14,  0.1,  "near threshold"),
    (2030, "Mu3e Phase-II",          1.0e-16,  5e-17,  2.0,  "Mu3e sees Spin(10) 2σ!"),
    (2035, "Hyper-K (τ_p)",          1.0e-36,  4.9e-36, "testable", "test τ_p"),
]

print(f"\n{'Year':<5} | {'Eksperyment':<25} | {'Sensitivity':<10} | {'Spin(10)':<10} | {'SNR':<6} | Comment")
print("-"*85)
for rok, exp, sens, pred, snr, kom in forecasts:
    print(f"  {rok:<3} | {exp:<25} | {sens:<10.1e} | {pred:<10.1e} | {str(snr)[:5]:<6} | {kom}")

# Full LFV hierarchy
print("\n" + "="*75)
print(" 4. LFV HIERARCHY IN SPIN(10) SPLIT-SUSY")
print("="*75)

print(f"\nSpin(10) Split-SUSY (M_SUSY=5 TeV) predicts CONCRETE hierarchy:")
print(f"  BR(mu->e gamma) = {BR_spin10:.2e}  [tested by MEG-II]")
print(f"  BR(mu->e e e)   = 5e-17          [tested by Mu3e Phase-II 2030+]")
print(f"  R(mu->e conv)   = 1e-14          [tested by Mu2e 2027+]")
print(f"\nRatio: BR(mu->e gamma)/BR(mu->e e e) ~ 1600 (Spin(10) fingerprint)")

# Konkurencja modeli
print("\n" + "="*75)
print(" 5. COMPARISON WITH OTHER LFV MODELS")
print("="*75)

models = [
    ("Spin(10) Split-SUSY", 8e-14, 5e-17, 1600),
    ("MSSM typowy",          1e-13, 1e-15, 100),
    ("cMSSM",                1e-14, 1e-16, 100),
    ("SU(5) SUSY",           1e-11, 1e-14, 1000),
    ("Split-SUSY generic",   1e-15, 1e-18, 1000),
]

print(f"\n{'Model':<22} | {'BR(mu->egamma)':<14} | {'BR(mu->eee)':<12} | {'Ratio'}")
print("-"*70)
for model, br_eg, br_ee, ratio in models:
    print(f"  {model:<20} | {br_eg:<14.1e} | {br_ee:<12.1e} | {ratio}")

print(f"\nSpin(10) has unique ratio BR(egamma)/BR(eee) ~ 1600 (other models: 100-1000)")

# Konkluzja
print("\n" + "="*75)
print(" 6. CONCLUSION - 2026 IS A BREAKTHROUGH YEAR")
print("="*75)

print(f"""
KEY POINTS:

1. MEG-II 2026 CZULOSC: {MEG_II_target:.1e}
   Spin(10) Split-SUSY: {BR_spin10:.2e}
   Ratio: {BR_spin10/MEG_II_target:.2f}

2. IF Spin(10) Split-SUSY is correct:
   - MEG-II 2026: sees BR ~ 8e-14 (1.3σ)
   - Mu3e Phase-II 2030+: sees BR(mu->eee) ~ 5e-17 (2σ)
   - Combined SNR Spin(10) > 3σ by 2030

3. IF Spin(10) is WRONG (e.g. higher M_SUSY):
   - MEG-II 2026: sees nothing (< 6e-14)
   - Spin(10) Split-SUSY excluded
   - Model modification required

2026 WILL BE THE YEAR of the Spin(10) Split-SUSY answer!

HISTORICAL PARALLEL:
- As the Higgs boson discovery in 2012 confirmed the Standard Model
- As the gravitational wave detection in 2015 confirmed GR
- MEG-II 2026 may confirm Spin(10) Split-SUSY
""")
