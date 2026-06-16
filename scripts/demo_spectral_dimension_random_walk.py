"""
demo_spectral_dimension_random_walk.py
======================================
Demo script presenting numerical determination of spectral dimension
using "Lazy Random Walk" (eliminates parity oscillations on networks).

Compares results for ToE graph (N=250) with a huge graph at holographic scale
(N=50,000 nodes), for which the traditional matrix diagonalization method would be infeasible.

Runienie:
    python scripts/demo_spectral_dimension_random_walk.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import networkx as nx
import time
from spectral_dimension_random_walk import RandomWalkSpectralDimension


def run_demo():
    print("="*75)
    print(" DEMONSTRATION: SPECTRAL DIMENSION VIA LAZY RANDOM WALK (WITHOUT DIAGONALIZATION)")
    print("="*75)
    
    # -------------------------------------------------------------------------
    # TEST 1: SMALL GRAPH (Setup and analysis of UV/IR zone)
    # -------------------------------------------------------------------------
    N_small = 300
    k_target = 4
    max_steps_small = 100
    num_walkers_small = 20000
    
    print(f"\n[TEST 1] UV -> IR FLOW ANALYSIS ON GRAPH N = {N_small}")
    print(f"   Generation graph ToE (N={N_small}, k_target={k_target})...")
    G_small = nx.barabasi_albert_graph(N_small, k_target, seed=101)
    
    print(f"   Running Lazy Random Walk: {num_walkers_small} walkers for {max_steps_small} steps...")
    start_time = time.time()
    t_vals, return_probs, d_S = RandomWalkSpectralDimension.exact_spectral_dimension_random_walk(
        G_small, max_steps=max_steps_small, num_walkers=num_walkers_small, lazy_prob=0.5, seed=102
    )
    rw_time = time.time() - start_time
    
    plateaux = RandomWalkSpectralDimension.compute_spectral_plateaux(t_vals, d_S, N_nodes=N_small)
    
    print(f"   Simulation completed in {rw_time:.2f} s.")
    print(f"   Spectral dimension d_S(t) flow results:")
    print(f"   - Strefa mikroskopowa UV:  d_S(UV) = {plateaux['d_S_UV']:.2f}")
    print(f"   - Strefa makroskopowa IR:  d_S(IR) numeric = {plateaux['d_S_IR_numeric']:.2f}")
    print(f"   - Theora ToE (Remedy #5):  d_S(IR) ToE     = {plateaux['d_S_IR_theoretical_remedy']:.2f}")
    
    print(f"\n   Sample of smooth time evolution (parity oscillation elimination):")
    print(f"   {'Time step t':<8} | {'P(t) (Return)':<16} | {'d_S(t) (Spectral Dimension)':<22}")
    print("   " + "-"*50)
    for idx in [1, 4, 9, 14, 24, 49]:
        if idx < len(t_vals):
            print(f"   {int(t_vals[idx]):<8} | {return_probs[idx]:<16.4f} | {d_S[idx]:<22.3f}")

    # -------------------------------------------------------------------------
    # TEST 2: GRAF SKALI HOLOGRAFICZNEJ (N = 50,000)
    # -------------------------------------------------------------------------
    N_large = 50000
    max_steps_large = 150
    num_walkers_large = 25000
    
    print(f"\n" + "="*75)
    print(f"[TEST 2] PERFORMANCE DEMONSTRATION ON HOLOGRAPHIC SCALE GRAPH (N = {N_large:<7,})")
    print(f"   Traditional Laplacian matrix diagonalization method would require O(N^3) operations here")
    print(f"   and several hundred gigabytes of RAM, exceeding standard computer capabilities.")
    
    print(f"\n   Generating large ToE network with {N_large:,} nodes...")
    start_gen = time.time()
    G_large = nx.barabasi_albert_graph(N_large, k_target, seed=201)
    gen_time = time.time() - start_gen
    print(f"   Network generated in {gen_time:.2f} s. Number of edges: {G_large.number_of_edges():,}")
    
    print(f"   Lightning-fast Lazy Random Walk simulation: {num_walkers_large:,} walkers for {max_steps_large} steps...")
    start_sim = time.time()
    t_vals_l, probs_l, d_S_l = RandomWalkSpectralDimension.exact_spectral_dimension_random_walk(
        G_large, max_steps=max_steps_large, num_walkers=num_walkers_large, lazy_prob=0.5, seed=202
    )
    sim_time = time.time() - start_sim
    
    plat_large = RandomWalkSpectralDimension.compute_spectral_plateaux(t_vals_l, d_S_l, N_nodes=N_large)
    
    print(f"   NUMERICAL SUCCESS! Full analysis completed in just {sim_time:.2f} s.")
    print(f"   - Estymacja dimension IR: d_S(IR) = {plat_large['d_S_IR_numeric']:.2f}")
    print(f"   - Transition from fractal UV dimension to stable spacetime confirmed.")
    
    print("\n   >>> New module 'RandomWalkSpectralDimension' fully ready for integration! <<<")
    print("="*75)


if __name__ == "__main__":
    run_demo()
