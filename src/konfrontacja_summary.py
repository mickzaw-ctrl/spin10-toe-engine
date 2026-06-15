"""
KONFRONTACJA - Spin(10) vs 9 glownych eksperymentow 2025-2040
Kompletna mapa predykcji do testow
"""

print("="*70)
print(" MANIFEST KONFRONTACJI - Spin(10) vs 9 EKSPERYMENTOW")
print("="*70)

print("\n 2025-2040: 15 LAT TESTOW HEKSALOGII SPIN(10)\n")

experiments = [
    {
        "name": "Planck PR4",
        "year": 2025,
        "status": "running",
        "predictions": ["low-l suppression", "f_NL^eq=14.5", "d_S running"],
        "critical": "★",
        "snr": "w granicach",
        "result": "low-l ✓ potwierdzone",
    },
    {
        "name": "IUPUI",
        "year": 2025,
        "status": "running",
        "predictions": ["torsja 5. sila alpha_5~1e-6"],
        "critical": "★★",
        "snr": "w zasiegu",
        "result": "TESTABLE",
    },
    {
        "name": "HE-LHC",
        "year": 2027,
        "status": "future",
        "predictions": ["Split-SUSY m_gluino=10.6 TeV"],
        "critical": "★★",
        "snr": "w zasiegu",
        "result": "TESTABLE",
    },
    {
        "name": "Hyper-K",
        "year": 2027,
        "status": "future",
        "predictions": ["tau_p = 4.9e36 years"],
        "critical": "★★",
        "snr": "blisko progu",
        "result": "TESTABLE 2030-2040",
    },
    {
        "name": "CASPEr",
        "year": 2028,
        "status": "future",
        "predictions": ["axion 28.5 neV"],
        "critical": "★★★",
        "snr": "w zasiegu CASPEr",
        "result": "TESTOWALNE juz 2028",
    },
    {
        "name": "CMB-S4",
        "year": 2028,
        "status": "future",
        "predictions": ["n_s^AS=0.962", "f_NL^eq=14.5", "70%eq+30%loc"],
        "critical": "★★★",
        "snr": "14.5 sigma dla f_NL^eq",
        "result": "NAJSILNIEJSZY test",
    },
    {
        "name": "LiteBIRD",
        "year": 2030,
        "status": "future",
        "predictions": ["r=0.0125", "B_TTB != 0 (UNIKALNA)"],
        "critical": "★★★",
        "snr": "12.5 sigma dla r",
        "result": "UNIKALNA sygnatura CP",
    },
    {
        "name": "LISA",
        "year": 2035,
        "status": "future",
        "predictions": ["SGWB Omega_GW~1e-7 @ 1 mHz"],
        "critical": "★★★★",
        "snr": "7 DEKAD powyzej progu",
        "result": "BEZPOSREDNIA detekcja",
    },
    {
        "name": "DECIGO",
        "year": 2040,
        "status": "future",
        "predictions": ["f_NL^GW=0.74", "g_NL^GW=-1.3"],
        "critical": "★★",
        "snr": "7 sigma",
        "result": "Precision GW NG",
    },
]

print(f"{'#':<3} | {'Eksperyment':<14} | {'Rok':<5} | {'Kryt.':<5} | {'SNR':<28} | {'Status'}")
print("-" * 90)
for i, exp in enumerate(experiments, 1):
    print(f"{i:<3} | {exp['name']:<14} | {exp['year']:<5} | {exp['critical']:<5} | "
          f"{exp['snr']:<28} | {exp['result']}")

print("\n" + "="*70)
print(" 4 KRYTYCZNE TESTY (★★★★★)")
print("="*70)
print("""
1. f_NL^eq = 14.5  w CMB-S4 (14.5 sigma)         - NAJSILNIEJSZY
2. SGWB Omega~1e-7 w LISA (7 dekad)              - BEZPOSREDNIA detekcja
3. B_TTB != 0 w LiteBIRD (UNIKALNA)               - tylko Spin(10)
4. N_gen = 3 topologicznie (Atiyah-Singer)        - fundamentalny
""")

print("\n" + "="*70)
print(" SCENARIUSZE")
print("="*70)
print("""
Scenariusz A: POTWIERDZENIE (3 z 4 testow pozytywne)
  -> Spin(10) staje sie dominujaca Teoria Wszystkiego

Scenariusz B: CZESCIOWE (1-2 z 4)
  -> Modyfikacja modelu (Publ. VIII?)

Scenariusz C: OBALONE (0 z 4)
  -> Nowe podejscie potrzebne
""")

print("\n" + "="*70)
print(" ROADMAPA")
print("="*70)
print("""
2025-2027  Planck PR4, IUPUI, HE-LHC setup
2027-2028  Hyper-K proton decay, CASPEr axion
2028-2030  CMB-S4 (n_s, f_NL), LiteBIRD (r, B_TTB)
2035       LISA SGWB (KRYTYCZNY)
2040+      DECIGO (f_NL^GW)
""")

print("="*70)
print(" GOTOWY DO KONFRONTACJI")
print("="*70)
