"""
explicit_spin10_gauge.py
========================
Full, non-Abelian implementation of edge variables (Link Variables)
dla algebry Liego Spin(10) / SO(10) na graph relacyjnym.

Module replaces uproszczone scalerne fazy U(1) with real gauge dynamics
in the 10-dimensional fundamental representation of SO(10). Enables simulation
relaxation Monte Carlo (Metropolis-Hastings) of the nonlinear Yang-Mills action.

Autor: SHZSpin10QuantumEngine Team
Wersja: 9.1 (Explicit Gauge Dynamics)
"""

import numpy as np
import networkx as nx
from scipy.linalg import expm
from typing import Dict, List, Tuple, Optional, Any
import time


def generate_so10_generators() -> List[np.ndarray]:
    """
    Generates 45 antisymmetric, purely imaginary generators T^a for SO(10)
    w 10-wymiarowej reprezentacji fundamentalnej.
    Satisfy the rule Tr(T^a T^b) = delta^{ab} (up to normalization).
    """
    generators = []
    for i in range(10):
        for j in range(i + 1, 10):
            T = np.zeros((10, 10), dtype=complex)
            T[i, j] = -1j
            T[j, i] = 1j
            generators.append(T)
    return generators


class ExplicitSpin10GaugeGraph:
    """
    Relational graph with matrix edge variables U_e in SO(10).
    
    Atrybuty:
        G: networkx.Graph - nieskierowany graph bazowy
        links: dict - macierze 10x10 U_{ij} przypisane do edges (i, j) z i < j
        generators: list - 45 SO(10) generators
        layer: dict - temporal layers of nodes (for causal structure)
    """
    
    def __init__(self, N: int = 60, k_target: int = 4, seed: int = 42):
        self.N = N
        self.k_target = k_target
        self.seed = seed
        np.random.seed(seed)
        
        # Generatory algebry
        self.generators = generate_so10_generators()
        
        # Tworzenie graph (Barabasi-Albert)
        self.G = nx.barabasi_albert_graph(N, k_target, seed=seed)
        
        # Przypisanie warstw temporalnych (10 warstw)
        self.layer = {}
        nodes_per_layer = max(1, N // 10)
        for i, node in enumerate(self.G.nodes()):
            self.layer[node] = min(i // nodes_per_layer, 9)
            
        # Initialize gauge matrices on edges
        self.links = {}
        for u, v in self.G.edges():
            edge_key = (min(u, v), max(u, v))
            # Losowa matrix z SO(10)
            self.links[edge_key] = self._random_so10_element(sigma=0.5)

    def _random_so10_element(self, sigma: float = 0.1) -> np.ndarray:
        """Losuje element grupy exp(i * sum(theta^a * T^a))."""
        thetas = np.random.normal(0, sigma, 45)
        Lie_elem = sum(t * T for t, T in zip(thetas, self.generators))
        return expm(1j * Lie_elem)

    def is_causal_edge(self, u: int, v: int) -> bool:
        """Checks if an edge is temporal (between different layers)."""
        return self.layer[u] < self.layer[v]

    def get_link(self, u: int, v: int) -> np.ndarray:
        r"""Retrieves the edge matrix, taking into account the direction U_{vu} = U_{uv}^\dagger."""
        if u < v:
            return self.links[(u, v)]
        else:
            return self.links[(v, u)].conj().T

    def exact_wilson_loop(self, triangle: Tuple[int, int, int]) -> float:
        """
        Computes the invariant Wilson loop W_P = Re(Tr(U_ij * U_jk * U_ki)) / 10.0
        for an elementary plaquette (triangle).
        """
        u, v, w = triangle
        U_ij = self.get_link(u, v)
        U_jk = self.get_link(v, w)
        U_ki = self.get_link(w, u)
        
        W = np.dot(U_ij, np.dot(U_jk, U_ki))
        return np.real(np.trace(W)) / 10.0

    def all_plaquettes(self) -> List[Tuple[int, int, int]]:
        """Finds all triangles in the graph."""
        triangles = set()
        for node in self.G.nodes():
            neighbors = list(self.G.neighbors(node))
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    n1, n2 = neighbors[i], neighbors[j]
                    if self.G.has_edge(n1, n2):
                        # Sort to avoid duplicates
                        t = tuple(sorted([node, n1, n2]))
                        triangles.add(t)
        return list(triangles)


class ExplicitSpin10Simulator:
    """
    Symulator Monte Carlo (Metropolis-Hastings) dla nieabelowej dynamiki SO(10).
    """
    
    def __init__(self, graph: ExplicitSpin10GaugeGraph, beta: float = 2.0):
        self.graph = graph
        self.beta = beta
        self.plaquettes = graph.all_plaquettes()
        
        # Mapping edges to plaquettes they belong to (for efficiency)
        self.edge_to_plaquettes = {}
        for edge in graph.G.edges():
            ekey = (min(edge), max(edge))
            self.edge_to_plaquettes[ekey] = []
            
        for t in self.plaquettes:
            u, v, w = t
            e1, e2, e3 = (min(u,v), max(u,v)), (min(v,w), max(v,w)), (min(w,u), max(w,u))
            self.edge_to_plaquettes[e1].append(t)
            self.edge_to_plaquettes[e2].append(t)
            self.edge_to_plaquettes[e3].append(t)

    def compute_total_ym_action(self) -> float:
        r"""S_{YM} = - \sum_{\triangle} \eta(\triangle) W_P"""
        action = 0.0
        for t in self.plaquettes:
            W_P = self.graph.exact_wilson_loop(t)
            # Account for Lorentz signature (Publ. I)
            has_causal = any(self.graph.is_causal_edge(e[0], e[1]) 
                           for e in [(t[0], t[1]), (t[1], t[2]), (t[2], t[0])])
            eta = -1.0 if has_causal else 1.0
            action += eta * W_P
        return -action

    def compute_local_action_for_edge(self, edge_key: Tuple[int, int]) -> float:
        """Computes action only from plaquettes containing the given edge."""
        local_act = 0.0
        for t in self.edge_to_plaquettes[edge_key]:
            W_P = self.graph.exact_wilson_loop(t)
            has_causal = any(self.graph.is_causal_edge(e[0], e[1]) 
                           for e in [(t[0], t[1]), (t[1], t[2]), (t[2], t[0])])
            eta = -1.0 if has_causal else 1.0
            local_act += eta * W_P
        return -local_act

    def run_sweep(self, step_sigma: float = 0.1) -> Tuple[int, int]:
        """
        Performs one full MC sweep (attempted update of each edge).
        Returns (n_accepted, n_attempts).
        """
        accepted = 0
        trials = 0
        
        edges = list(self.graph.G.edges())
        for u, v in edges:
            edge_key = (min(u, v), max(u, v))
            if not self.edge_to_plaquettes[edge_key]:
                continue
                
            trials += 1
            
            # Compute local action before change
            S_old = self.compute_local_action_for_edge(edge_key)
            
            # Store old matrix
            U_old = self.graph.links[edge_key]
            
            # Propose new matrix U_new = U_old * exp(i * sum(theta * T))
            U_shift = self.graph._random_so10_element(sigma=step_sigma)
            U_new = np.dot(U_old, U_shift)
            
            # Temporary projection onto SO(10) to prevent numerical error accumulation
            U, _, Vh = np.linalg.svd(U_new)
            U_new = np.dot(U, Vh)
            
            # Apply new matrix
            self.graph.links[edge_key] = U_new
            
            # Compute lokalne działanie po zmianie
            S_new = self.compute_local_action_for_edge(edge_key)
            
            delta_S = S_new - S_old
            
            # Kryterium Metropolisa
            if delta_S < 0 or np.random.random() < np.exp(-self.beta * delta_S):
                accepted += 1
            else:
                # Reject move — restore old matrix
                self.graph.links[edge_key] = U_old
                
        return accepted, trials

    def compute_observables(self) -> Dict[str, float]:
        """Computes mean values in the current state."""
        if not self.plaquettes:
            return {'wilson_loop': 0.0, 'ym_action': 0.0}
            
        w_loops = [self.graph.exact_wilson_loop(t) for t in self.plaquettes]
        
        return {
            'wilson_loop': float(np.mean(w_loops)),
            'wilson_loop_std': float(np.std(w_loops)),
            'ym_action': self.compute_total_ym_action(),
            'N_plaquettes': len(self.plaquettes),
        }
