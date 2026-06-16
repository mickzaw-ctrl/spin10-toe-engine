"""
explicit_spin10_gauge.py
========================
Pelna, nieabelowa implementacja zmiennych edgesowych (Link Variables)
dla algebry Liego Spin(10) / SO(10) na graphie relacyjnym.

Module zastepuje uproszczone scalerne fazy U(1) rzeczywista dynamika cechowania
w 10-dimensionowej reprezentacji fundamentalnej SO(10). Umozliwia symulacje
relaksacji Monte Carlo (Metropolis-Hastings) nieliniowego dzialania Yang-Millsa.

Author: SHZSpin10QuantumEngine Team
Version: 9.1 (Explicit Gauge Dynamics)
"""

import numpy as np
import networkx as nx
from scipy.linalg import expm
from typing import Dict, List, Tuple, Optional, Any
import time


def generate_so10_generators() -> List[np.ndarray]:
    """
    Generuje 45 antysymetrycznych, czysto urojonych generatorow T^a dla SO(10)
    w 10-dimensionowej reprezentacji fundamentalnej.
    Spelniaja regule Tr(T^a T^b) = delta^{ab} (z dokladnoscia do normalizacji).
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
    Graph relacyjny z matrixowymi zmiennymi edgesowymi U_e w SO(10).
    
    Atrybuty:
        G: networkx.Graph - nieskierowany graph bazowy
        links: dict - matrixe 10x10 U_{ij} przypisane do edges (i, j) z i < j
        generators: list - 45 generatorow SO(10)
        layer: dict - warstwy temporalne nodes (dla struktury przyczynowej)
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
            
        # Initialization matrix cechowania na edgesach
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
        """Sprawdza czy krawedz jest timeowa (miedzy roznymi warstwami)."""
        return self.layer[u] < self.layer[v]

    def get_link(self, u: int, v: int) -> np.ndarray:
        r"""Pobiera matrix edgesowa, uwzgledniajac kierunek U_{vu} = U_{uv}^\dagger."""
        if u < v:
            return self.links[(u, v)]
        else:
            return self.links[(v, u)].conj().T

    def exact_wilson_loop(self, triangle: Tuple[int, int, int]) -> float:
        """
        Computea niezmiennicza petle Wilsona W_P = Re(Tr(U_ij * U_jk * U_ki)) / 10.0
        dla elementarnej plakiety (trojkata).
        """
        u, v, w = triangle
        U_ij = self.get_link(u, v)
        U_jk = self.get_link(v, w)
        U_ki = self.get_link(w, u)
        
        W = np.dot(U_ij, np.dot(U_jk, U_ki))
        return np.real(np.trace(W)) / 10.0

    def all_plaquettes(self) -> List[Tuple[int, int, int]]:
        """Znajduje wszystkie trojkaty w graphie."""
        triangles = set()
        for node in self.G.nodes():
            neighbors = list(self.G.neighbors(node))
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    n1, n2 = neighbors[i], neighbors[j]
                    if self.G.has_edge(n1, n2):
                        # Sortuj by unikac duplikatow
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
        
        # Mapowanie edges do plakiet w ktorych wystepuja (dla wydajnosci)
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
            # Uwzglednienie sygnatury Lorentza (Publ. I)
            has_causal = any(self.graph.is_causal_edge(e[0], e[1]) 
                           for e in [(t[0], t[1]), (t[1], t[2]), (t[2], t[0])])
            eta = -1.0 if has_causal else 1.0
            action += eta * W_P
        return -action

    def compute_local_action_for_edge(self, edge_key: Tuple[int, int]) -> float:
        """Computea dzialanie tylko od plakiet zawierajacych dana krawedz."""
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
        Wykonuje jeden pelny sweep MC (proba aktualizacji kazdej edges).
        Zwraca (liczba_akceptacji, liczba_prob).
        """
        accepted = 0
        trials = 0
        
        edges = list(self.graph.G.edges())
        for u, v in edges:
            edge_key = (min(u, v), max(u, v))
            if not self.edge_to_plaquettes[edge_key]:
                continue
                
            trials += 1
            
            # Compute lokalne dzialanie przed zmiana
            S_old = self.compute_local_action_for_edge(edge_key)
            
            # Zapamietaj stara matrix
            U_old = self.graph.links[edge_key]
            
            # Zaproponuj nowa matrix U_new = U_old * exp(i * sum(theta * T))
            U_shift = self.graph._random_so10_element(sigma=step_sigma)
            U_new = np.dot(U_old, U_shift)
            
            # Przejsciowy rzut na SO(10) by zapobiegac akumulacji bledow numerycznych
            U, _, Vh = np.linalg.svd(U_new)
            U_new = np.dot(U, Vh)
            
            # Zastosuj nowa matrix
            self.graph.links[edge_key] = U_new
            
            # Compute lokalne dzialanie po zmianie
            S_new = self.compute_local_action_for_edge(edge_key)
            
            delta_S = S_new - S_old
            
            # Kryterium Metropolisa
            if delta_S < 0 or np.random.random() < np.exp(-self.beta * delta_S):
                accepted += 1
            else:
                # Odrzucenie ruchu — przywrocenie starej matrix
                self.graph.links[edge_key] = U_old
                
        return accepted, trials

    def compute_observables(self) -> Dict[str, float]:
        """Computea wartosci srednie w aktualnym stanie."""
        if not self.plaquettes:
            return {'wilson_loop': 0.0, 'ym_action': 0.0}
            
        w_loops = [self.graph.exact_wilson_loop(t) for t in self.plaquettes]
        
        return {
            'wilson_loop': float(np.mean(w_loops)),
            'wilson_loop_std': float(np.std(w_loops)),
            'ym_action': self.compute_total_ym_action(),
            'N_plaquettes': len(self.plaquettes),
        }
