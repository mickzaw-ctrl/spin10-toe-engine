"""
demo_explicit_spin10_gauge.py
=============================
Script demonstrating newly implemented full non-Abelian
zmiennych krawędziowych (Link Variables) w grupie cechowania SO(10).

Compares Wilson loop relaxation in the non-Abelian model with simplified U(1) model.

Runienie:
    python scripts/demo_explicit_spin10_gauge.py
"""

import sys
import os

# Add main directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import time
from explicit_spin10_gauge import ExplicitSpin10GaugeGraph, ExplicitSpin10Simulator


def run_demo():
    print("="*75)
    print(" DEMONSTRACJA: PEŁNA NIEABELOWA DYNAMIKA CECHOWANIA SPIN(10) / SO(10)")
    print("="*75)
    
    # 1. Initialization
    N_nodes = 50
    k_target = 4
    beta = 2.5
    
    print(f"\n1. INICJALIZACJA GRAFU Z MACIERZAMI LINKOWYMI SO(10)")
    print(f"   Number of nodes N = {N_nodes}, Target degree <k> = {k_target}")
    
    start_time = time.time()
    gauge_graph = ExplicitSpin10GaugeGraph(N=N_nodes, k_target=k_target, seed=101)
    sim = ExplicitSpin10Simulator(gauge_graph, beta=beta)
    init_time = time.time() - start_time
    
    obs_init = sim.compute_observables()
    
    print(f"   Initialization zakończona w {init_time:.2f} s.")
    print(f"   Wygenerowano 45 generatorów SO(10) w 10-wym. rep. fundamentalnej.")
    print(f"   Przypisano {gauge_graph.G.number_of_edges()} macierzy krawędziowych (10x10).")
    print(f"   Found {obs_init['N_plaquettes']} elementary triangles (plaquettes).")
    print(f"   Początkowa mean loop Wilsona <W> = {obs_init['wilson_loop']:.4f} ± {obs_init['wilson_loop_std']:.4f}")
    
    # 2. Simulation Monte Carlo
    print(f"\n2. RELAKSACJA MONTE CARLO (METROPOLIS-HASTINGS)")
    print(f"   Parametr odwrotnej temperatury beta = {beta}")
    print(f"   Performing 10 full sweeps (updating all edges in each sweep)...")
    
    n_sweeps = 10
    history = {
        'sweep': [0],
        'wilson_loop': [obs_init['wilson_loop']],
        'ym_action': [obs_init['ym_action']],
        'acceptance_rate': [0.0]
    }
    
    print(f"\n   {'Sweep':<6} | {'<W> (Wilson Loop)':<20} | {'S_YM (Akcja)':<15} | {'Akceptacja':<12} | {'Czas (s)':<10}")
    print("   " + "-"*70)
    
    print(f"   {0:<6} | {obs_init['wilson_loop']:<20.4f} | {obs_init['ym_action']:<15.3f} | {'---':<12} | {'---':<10}")
    
    total_accepted = 0
    total_trials = 0
    sim_start_time = time.time()
    
    for sweep in range(1, n_sweeps + 1):
        s_time = time.time()
        acc, trials = sim.run_sweep(step_sigma=0.15)
        sweep_time = time.time() - s_time
        
        total_accepted += acc
        total_trials += trials
        
        obs = sim.compute_observables()
        acc_rate = acc / trials if trials > 0 else 0
        
        history['sweep'].append(sweep)
        history['wilson_loop'].append(obs['wilson_loop'])
        history['ym_action'].append(obs['ym_action'])
        history['acceptance_rate'].append(acc_rate)
        
        print(f"   {sweep:<6} | {obs['wilson_loop']:<20.4f} | {obs['ym_action']:<15.3f} | {acc_rate:<12.2%} | {sweep_time:<10.2f}")

    total_sim_time = time.time() - sim_start_time
    
    print("\n   " + "="*70)
    print(f"   PODSUMOWANIE RELAKSACJI")
    print(f"   - Czas całkowity symulacji: {total_sim_time:.2f} s")
    print(f"   - Mean akceptacja:       {total_accepted / total_trials:.2%}")
    print(f"   - Ewolucja pętli Wilsona:   {history['wilson_loop'][0]:.4f}  --->  {history['wilson_loop'][-1]:.4f}")
    
    print(f"\n3. PORÓWNANIE Z MODELEM SKALARNYM U(1) (Wersja v8.0 / v9.0)")
    print(f"   Stary model U(1) operował na pojedynczej fazie phi in [0, 2pi].")
    print(f"   New SO(10) model operates in 45-dimensional gauge space, fully accounting for:")
    print(f"   - Gauge invariance: W = Re(Tr(U1 U2 U3))/10")
    print(f"   - Algebra non-commutativity (Non-Abelian fingerprint)")
    print(f"   - Much richer spectrum of microscopic fluctuations around the vacuum state.")
    
    print("\n   >>> Nowy moduł 'ExplicitSpin10GaugeGraph' jest gotowy do integracji z mainm silnikiem ToE! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
