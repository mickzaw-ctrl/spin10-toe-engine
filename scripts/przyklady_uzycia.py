"""
Usage examples for SHZSpin10QuantumEngine v8.0
=============================================
Complete collection of examples demonstrating various aspects of the engine.
"""

from spin10_engine import (
    SHZSpin10QuantumEngine, 
    Spin10Graph, 
    Spin10Predictions,
    Spin10Remedies,
    Spin10Tests,
    Spin10Observables
)
import numpy as np


def example_1_basic_simulation():
    """Example 1: Podstawowa simulation"""
    print("\n" + "="*60)
    print("PRZYKLAD 1: Podstawowa simulation")
    print("="*60)
    
    engine = SHZSpin10QuantumEngine(N=120, k_target=4)
    print(f"\nPoczatkowe Var(k) = {engine.graph.degree_variance():.3f}")
    
    engine.run_simulation(n_steps=500)
    
    obs = engine.compute_observables()
    print(f"\nPo {500} krokach MC:")
    for k, v in obs.items():
        if isinstance(v, float):
            print(f"  {k} = {v:.4f}")
        else:
            print(f"  {k} = {v}")


def example_2_inflation_predictions():
    """Example 2: Predictions inflation α-Attractor"""
    print("\n" + "="*60)
    print("PRZYKLAD 2: α-Attractor Spin(10)")
    print("="*60)
    
    infl = Spin10Predictions.inflation_spectrum()
    
    print(f"\nα = dim(Spin(10))/12 = {infl['alpha']:.4f}")
    print(f"n_s = 1 - 2/N = {infl['n_s']:.4f}")
    print(f"r = 12α/N² = {infl['r']:.4f}")
    
    print(f"\nComparison z danymi:")
    print(f"  n_s (Planck):  0.9649 ± 0.0042")
    print(f"  n_s (model):   {infl['n_s']:.4f}")
    print(f"  σ odchylenie:  {abs(infl['n_s'] - 0.9649)/0.0042:.2f}")
    
    print(f"\n  r (BICEP limit): < 0.036")
    print(f"  r (model):       {infl['r']:.4f}")
    print(f"  Pass: {infl['r'] < 0.036}")


def example_3_sgwb_spectrum():
    """Example 3: SGWB Spectrum (three sources)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: SGWB - Three sources")
    print("="*60)
    
    frequencies = [1e-9, 1e-7, 1e-5, 1e-3, 1e-1, 1e0, 1e1, 1e2, 1e3]
    detectors = {
        1e-9: "PTA",
        1e-7: "PTA/LISA",
        1e-3: "LISA ★",
        1e-1: "LISA",
        1e0: "DECIGO",
        1e2: "Einstein T. ★",
        1e3: "Einstein T."
    }
    
    print(f"\n{'f [Hz]':<10} | {'Ω_GW':<12} | {'Detector':<20}")
    print("-" * 50)
    for f in frequencies:
        Omega = Spin10Predictions.sgwb_spectrum(f)
        det = detectors.get(f, "—")
        star = " ★" if abs(np.log10(f) - np.log10(1e-3)) < 0.5 else ""
        print(f"  {f:<10.0e} | {Omega:<12.2e} | {det}{star}")
    
    # Comparison with sensitivities
    print(f"\nCzulosci detectors:")
    print(f"  LISA (1 mHz):     ~10^-14")
    print(f"  Spin(10) (1 mHz): ~10^-7  (7 dekad powyzej progu)")


def example_4_remedies():
    """Example 4: 5 kluczowych remedies"""
    print("\n" + "="*60)
    print("PRZYKLAD 4: 5 KLUCZOWYCH REMEDIES")
    print("="*60)
    
    remedies = Spin10Remedies.apply_all_remedies()
    
    print("\n1. SPLIT-SUSY (m_gluino):")
    r1 = remedies['remedy_1_split_susy']
    print(f"   M_SUSY = {r1['M_SUSY']} GeV")
    print(f"   m_gluino = {r1['m_gluino_TeV']:.1f} TeV")
    print(f"   Pass LHC: {r1['passes_LHC']}")
    
    print("\n2. 3-FLAVOUR BOLTZMANN (η_B):")
    r2 = remedies['remedy_2_3flavour_boltzmann']
    print(f"   η_B (total) = {r2['eta_B_total']:.2e}")
    print(f"   η_B (obs)   = {r2['eta_B_obs']:.2e}")
    print(f"   Zgodnosc: {r2['agrees_with_obs']}")
    
    print("\n3. HIDDEN SUSY SECTOR (a_4):")
    r3 = remedies['remedy_3_hidden_susy']
    print(f"   a_4 (bare) = {r3['a_4_bare']}")
    print(f"   N_hidden_chirals = {r3['N_hidden_chirals']}")
    print(f"   a_4 (after) = {r3['a_4_after_remedy']}")
    print(f"   Anomalia anulowana: {r3['anomaly_cancelled']}")
    
    print("\n4-5. SKALOWANIE SIECI:")
    r45 = remedies['remedy_4_5_network_scaling']
    print(f"   N = {r45['N']:.0e}")
    print(f"   P(holographia) = {r45['P_holography']:.2%}")
    print(f"   d_S: {r45['d_S_UV']:.1f} -> {r45['d_S_IR']:.1f}")
    print(f"   d_S CDT-compat: {r45['d_S_compatible_CDT']}")


def example_5_full_tests():
    """Example 5: Full test suite"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Full suite of experimental tests")
    print("="*60)
    
    tests = Spin10Tests.run_all_tests()
    
    print("\n1. INFLACJA (Planck + BICEP):")
    print(f"   n_s sigma: {tests['inflation_n_s_r']['n_s_sigma']:.2f}")
    print(f"   r pass: {tests['inflation_n_s_r']['r_passes']}")
    
    print("\n2. SGWB (LISA 2035):")
    print(f"   Dekad powyzej szumu: {tests['SGWB_LISA']['decades_above']:.1f}")
    print(f"   Detekowalne: {tests['SGWB_LISA']['detectable']}")
    
    print("\n3. f_NL (CMB-S4 2035):")
    print(f"   SNR: {tests['f_NL_CMB_S4']['SNR']:.1f}")
    print(f"   Detekowalne: {tests['f_NL_CMB_S4']['detectable']}")
    
    print("\n4. AXION (CASPEr 2028):")
    print(f"   m_a = {tests['axion_CASPEr']['m_a_eV']*1e9:.1f} neV")
    print(f"   W zasiegu CASPEr: {tests['axion_CASPEr']['in_CASPEr_range']}")
    
    print("\n5. PROTON DECAY (Hyper-K 2027+):")
    print(f"   τ(p->e+π⁰) = {tests['proton_decay_HyperK']['tau_e_pi0']:.2e} years")
    print(f"   Visible 2030: {tests['proton_decay_HyperK']['visible_2030']}")
    
    print("\n6. THREE GENERATIONS:")
    print(f"   N_gen (topology) = {tests['three_generations']['N_gen_pred']}")
    print(f"   Matches SM: {tests['three_generations']['matches']}")


def example_6_full_report():
    """Example 6: Pelen report z simulation"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Full report")
    print("="*60)
    
    engine = SHZSpin10QuantumEngine(N=120, k_target=4)
    engine.run_simulation(n_steps=500, verbose=True)
    
    report = engine.full_report()
    
    print(f"\nEngine: {report['engine_version']}")
    print(f"Simulation steps: {len(report['simulation_history']['Var_k'])}")
    
    print(f"\nObserwable (final):")
    obs = report['observables']
    print(f"  Var(k) = {obs['Var_k']:.4f}")
    print(f"  <k> = {obs['mean_degree']:.2f}")
    print(f"  CF = {obs['CF']:.4f}")
    
    print(f"\nKLUCZOWE PREDYKCJE:")
    pred = report['predictions']
    print(f"  N_generations = {pred['N_generations']} (topologiczne)")
    print(f"  n_s = {pred['inflation']['n_s']:.4f}")
    print(f"  r = {pred['inflation']['r']:.4f}")
    print(f"  f_NL^eq = {pred['f_NL_equil']:.4f}")
    print(f"  Axion m_a = {pred['axion']['m_a_neV']:.1f} neV")
    
    print(f"\nREMEDIES:")
    rem = report['remedies']
    print(f"  m_gluino = {rem['remedy_1_split_susy']['m_gluino_TeV']:.1f} TeV")
    print(f"  η_B = {rem['remedy_2_3flavour_boltzmann']['eta_B_total']:.2e}")
    print(f"  Hidden SUSY: {rem['remedy_3_hidden_susy']['N_hidden_chirals']} multipletow")


def example_7_custom_graph():
    """Example 7: Wlasna configuration graph"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Custom graph configuration")
    print("="*60)
    
    # Large network with strong target k
    engine = SHZSpin10QuantumEngine(N=500, k_target=6, alpha=2.0, beta=2.0)
    engine.run_simulation(n_steps=1000)
    
    obs = engine.compute_observables()
    print(f"\nLarge network (N=500, k=6, α=2, β=2):")
    print(f"  Var(k) = {obs['Var_k']:.4f}")
    print(f"  Wilson = {obs['wilson_loop']:.4f}")
    print(f"  d_S IR = {obs['d_S_IR']:.2f}")


def example_8_plot_results():
    """Example 8: Podstawowa wizualizacja"""
    print("\n" + "="*60)
    print("PRZYKLAD 8: Podstawowa wizualizacja")
    print("="*60)
    
    engine = SHZSpin10QuantumEngine(N=120, k_target=4)
    engine.run_simulation(n_steps=1000)
    
    history = engine.history
    print(f"\nHistoria simulation ({len(history['Var_k'])} punktow):")
    print(f"  Var(k):  start={history['Var_k'][0]:.3f}, end={history['Var_k'][-1]:.3f}")
    print(f"  cos Φ:   start={history['cos_Phi'][0]:.3f}, end={history['cos_Phi'][-1]:.3f}")
    print(f"  CF:      start={history['CF'][0]:.3f}, end={history['CF'][-1]:.3f}")
    
    # ASCII plot Var(k)
    print("\nVar(k) evolution (ASCII):")
    vals = history['Var_k']
    n_show = min(20, len(vals))
    indices = np.linspace(0, len(vals)-1, n_show).astype(int)
    max_v = max(vals)
    for i in indices:
        bar = "#" * int(50 * vals[i] / max_v)
        print(f"  step {i:4d}: {bar} ({vals[i]:.3f})")


if __name__ == "__main__":
    # Run wszystkie przyklady
    example_1_basic_simulation()
    example_2_inflation_predictions()
    example_3_sgwb_spectrum()
    example_4_remedies()
    example_5_full_tests()
    example_6_full_report()
    example_7_custom_graph()
    example_8_plot_results()
    
    print("\n" + "="*60)
    print(" Wszystkie przyklady zakonczone")
    print("="*60)
