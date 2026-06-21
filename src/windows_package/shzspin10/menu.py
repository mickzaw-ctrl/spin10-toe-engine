"""
shzspin10/menu.py
=================
Interactive text-based console menu for SHZSpin10 Ultima Apex Engine.
"""
import json
import sys
import os
from .engine import SHZSpin10UltimaApex


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    clear_screen()
    print("=" * 80)
    print("    SHZSPIN10 ULTIMA APEX v14.5  —  INTERACTIVE CONSOLE MENU")
    print("    Unified Quantum Theory of Everything Engine")
    print("=" * 80)


def print_menu():
    print("""
    ┌──────────────────────────────────────────────────────────────┐
    │  [1]  Run full ULTIMA simulation (all horizons)  │
    │  [2]  Cosmology Simulation (Big Bang + FRW + CMB)      │
    │  [3]  Physics: LQG Spin Foam (EPRL) + SM RGE Derivation     │
    │  [4]  Cloud: 6 SaaS microservices                       │
    │  [5]  Enterprise: HPC + Quantum Bridge                      │
    │  [6]  Display report from JSON file                          │
    │  [7]  Export report to JSON                               │
    │  [8]  Version and engine information                         │
    │  [0]  Exit                                               │
    └──────────────────────────────────────────────────────────────┘
    """)


def run_full_simulation():
    print("\n>>> Running full ULTIMA simulation...")
    engine = SHZSpin10UltimaApex()
    report = engine.run_ultima_simulation()
    engine.display_ultima_dashboard(report)
    path = input("\nSave report to file (ENTER = default ultima_report.json): ").strip()
    if not path:
        path = "ultima_report.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    print(f">>> Saved {path}")
    input("\n[ENTER] to continue...")


def run_cosmology():
    print("\n>>> Running Cosmology Laboratory...")
    from .engine import CosmicEvolutionEngine
    cosmo = CosmicEvolutionEngine()
    inf = cosmo.simulate_inflation_reheating()
    frw = cosmo.simulate_frw_evolution(n_points=10000)
    cmb = cosmo.compute_cmb_power_spectrum(l_max=200)
    matter = cosmo.compute_matter_power_spectrum()
    cosmo.generate_cosmology_plots(frw, cmb, matter, output_prefix="cosmology_menu")

    print("\n--- INFLACJA STAROBINSKY R^2 ---")
    for k, v in inf.items():
        if not isinstance(v, list):
            print(f"  {k}: {v}")
    print(f"\n--- EWOLUCJA FRW ---")
    print(f"  Wiek Wszechświata: {frw['age_universe_Gyr']} Gyr")
    for epoch, vals in frw['key_epochs'].items():
        print(f"  {epoch}: {vals}")
    print(f"\n--- CMB ---")
    print(f"  Pierwszy pik: l={cmb['first_peak_l']}, amp={cmb['first_peak_amplitude_uK2']:.1f} uK^2")
    print(f"\n>>> Wykres zapisano: cosmology_menu_simulation.png")
    input("\n[ENTER] to continue...")


def run_physics():
    print("\n>>> Laboratorium Fizyki Fundamentalnej...")
    from .engine import SpinFoamLQGBridge, StandardModelLowEnergyDerivation
    lqg = SpinFoamLQGBridge()
    sm = StandardModelLowEnergyDerivation()
    ep = lqg.calculate_eprl_vertex_amplitude(spin_j=2.5, immirzi_gamma=0.274)
    rge = sm.integrate_rge_downwards_to_modern_constants()

    print("\n--- EPRL SPIN FOAM VERTEX ---")
    for k, v in ep.items():
        print(f"  {k}: {v}")
    print("\n--- RGE DOWNWARD DERIVATION ---")
    for k, v in rge.items():
        print(f"  {k}: {v}")
    input("\n[ENTER] to continue...")


def run_cloud():
    print("\n>>> Mikrousługi chmurowe SHZSpin10 Cloud API...")
    from .engine import (
        cloud_status, cloud_gauge_relaxation, cloud_holographic_random_walk,
        cloud_rge_unification, cloud_mukhanov_sasaki, cloud_mera_entropy, cloud_equation_discovery
    )
    print(f"\nStatus: {cloud_status()}")
    print(f"\n1. Gauge Relaxation: {cloud_gauge_relaxation()}")
    print(f"\n2. Holographic Random Walk: {cloud_holographic_random_walk()}")
    print(f"\n3. RGE Unification: {cloud_rge_unification()}")
    print(f"\n4. Mukhanov-Sasaki: {cloud_mukhanov_sasaki()}")
    print(f"\n5. MERA Entropy: {cloud_mera_entropy()}")
    print(f"\n6. AI Equation Discovery: {cloud_equation_discovery([0.1,0.5,1.0],[0.12,0.48,0.95],'x')}")
    input("\n[ENTER] to continue...")


def run_enterprise():
    print("\n>>> Enterprise HPC & Quantum Bridge...")
    from .engine import Spin10EnterpriseHPCEngine, QuantumHardwareBridge
    hpc = Spin10EnterpriseHPCEngine(N=10**6)
    qb = QuantumHardwareBridge()
    print(f"\nHPC: {hpc.batch_link_variable_relaxation_gpu(n_sweeps=5)}")
    print(f"\nQiskit Bridge: {qb.compile_toe_graph_to_qiskit_circuit(nodes=16)}")
    input("\n[ENTER] to continue...")


def display_json():
    path = input("Ścieżka do pliku JSON (ENTER = ultima_report.json): ").strip()
    if not path:
        path = "ultima_report.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for section, vals in data.items():
            print(f"\n[{section}]")
            print("-" * 40)
            for k, v in vals.items():
                print(f"  {k}: {v}")
    except FileNotFoundError:
        print(f"File not found: {path}")
    input("\n[ENTER] to continue...")


def export_json():
    engine = SHZSpin10UltimaApex()
    report = engine.run_ultima_simulation()
    path = input("Ścieżka zapisu (ENTER = ultima_export.json): ").strip() or "ultima_export.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    print(f">>> Saved {path}")
    input("\n[ENTER] to continue...")


def show_info():
    print("""
    SHZSPIN10 ULTIMA APEX v14.5 — ULTIMA COSMOS UNIFIED
    ─────────────────────────────────────────────────────
    Autor:   SHZ Quantum Technologies Unified Kernel Team
    Licencja: Proprietary / Research Use
    Python:   >= 3.9
    Zależności: numpy, scipy, matplotlib

    Horyzonty:
      1. Base Engine v13.6
      2. Ultima Frontiers (BH, Yukawa, E8, TQEC)
      3. Enterprise HPC + Quantum Bridge
      4. Physics Apex (LQG EPRL, SM RGE)
      5. Cloud SaaS API (6 microservices)
      6. Cosmology (Big Bang, Inflation, FRW, CMB, P(k))
    """)
    input("\n[ENTER] to continue...")


def main_menu():
    while True:
        print_header()
        print_menu()
        choice = input("    Select option [0-8]: ").strip()
        if choice == "1":
            run_full_simulation()
        elif choice == "2":
            run_cosmology()
        elif choice == "3":
            run_physics()
        elif choice == "4":
            run_cloud()
        elif choice == "5":
            run_enterprise()
        elif choice == "6":
            display_json()
        elif choice == "7":
            export_json()
        elif choice == "8":
            show_info()
        elif choice == "0":
            print("\n>>> Wyjście. Wszechświat pozostaje samokorygującym się komputerem kwantowym E8.")
            sys.exit(0)
        else:
            print("\n    Nieprawidłowy wybór. Naciśnij ENTER...")
            input()


if __name__ == "__main__":
    main_menu()
