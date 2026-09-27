# -*- coding: utf-8 -*-
"""
Przebudowa sektora inflacji: E-model α-attractor z dokładną dynamiką tła
==========================================================================

Dotychczasowy silnik przewiduje inflację wyłącznie z analityk wiodącego rzędu:
n_s = 1 − 2/N, r = 12α/N² przy sztywnym N = 60 oraz α = dim Spin(10)/12 = 3.75.

Moduł zastępuje to pełną, sprawdzoną procedurą:

  1. Dokładne tło: równania Friedmanna–Klein-Gordona dla potencjału
     E-modelu α-attractor  V = V₀(1 − e^{−λφ})²,  λ = √(2/(3α)),
     całkowane numerycznie aż do końca inflacji (ε_H = 1).
  2. Parametry przepływu Hubble'a ε₁, ε₂, ε₃(N) z dokładnego tła —
     a obserwable z relacji drugiego rzędu (Lidsey i in. 1997):

         n_s = 1 − 2ε₁ − ε₂ − 2ε₁² − (3+2C)ε₁ε₂ − C ε₂ε₃,
         r   = 16 ε₁ [1 + 2C(ε₁ + ε₂)],        C = 4(ln2 + γ_E) − 5 = 0.08145,
         α_s = dn_s/dlnk,  β_s = d²n_s/dlnk²   (różniczka po tle).

  3. Sektor podgrzewania (entropia + skalowanie ρ): fizyczne N_⋆ jako
     funkcja temperatury podgrzewania T_rh i równania stanu w_rh —
     zamiast sztywnego N = 60. Zastosowana jest standardowa
     konstrukcja: ρ_end = (3/2)V_end przy ε_H=1, ρ → a^{−3(1+w_rh)},
     ρ_rh = (π²/30)g* T_rh⁴, zachowanie entropii po podgrzewaniu.

  4. Diagnostyka deformacji: ilościowe zapotrzebowanie Δn_s(N deforms)
     vs aktualne dane (patrz moduł konfrontacji) — klasyfikowane jako
     warunek, NIE mechanizm.

Wszystkie wielkości w jednostkach M_Pl = 1 (masa nieredukowana).
Status: PROTOTYP BADAWCZY — wyniki do konfrontacji w
src/konfrontacja_inflacja.py.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# ---------------------------------------------------------------------------
# Stałe fizyczne
# ---------------------------------------------------------------------------

M_PL_GEV = 1.2209e19
C_NLO = 4 * (math.log(2) + 0.5772156649015329) - 5      # = 0.0814514
G_STAR_RH = 106.75
G_STAR_S0 = 3.91
T0_GEV = 2.349e-13           # 2.725 K
EV_GEV = 1.0e-9
MPC_INV_GEV = 6.3949e-39     # 1 Mpc^-1 w GeV
K_PIVOT = 0.05 * MPC_INV_GEV # k_* = 0.05 Mpc^-1
A_S_OBS = 2.099e-9           # Planck 2018 (te same dane co w konfrontacji)


# ---------------------------------------------------------------------------
# Potencjał i pochodne (M_Pl = 1)
# ---------------------------------------------------------------------------

class PotencjalAlpha:
    def __init__(self, alpha: float = 3.75, V0: float = 1.0):
        self.alpha = float(alpha)
        self.lam = math.sqrt(2.0 / (3.0 * alpha))
        self.V0 = V0

    def _x(self, phi: float) -> float:
        return math.exp(-self.lam * phi)

    def V(self, phi: float) -> float:
        return self.V0 * (1.0 - self._x(phi)) ** 2

    def dV(self, phi: float) -> float:
        x = self._x(phi)
        return 2.0 * self.lam * self.V0 * x * (1.0 - x)

    def ddV(self, phi: float) -> float:
        x = self._x(phi)
        return 2.0 * self.lam**2 * self.V0 * x * (2.0 * x - 1.0)

    def eps_V(self, phi: float) -> float:
        return 0.5 * (self.dV(phi) / self.V(phi)) ** 2

    def eta_V(self, phi: float) -> float:
        return self.ddV(phi) / self.V(phi)

    def phi_end_pot(self) -> float:
        """φ_end z ε_V = 1 (przybliżenie potencjałowe; dokumentowane)."""
        xe = 1.0 / (1.0 + math.sqrt(2.0) * self.lam)
        return -math.log(xe) / self.lam

    def N_analityczne(self, phi: float, phi_end: float) -> float:
        """N(φ) = ∫ V/V' dφ = [e^{λφ} − λφ − (e^{λφ_end} − λφ_end)] / (2λ²).

        (Prymitywna: d/dφ[(e^{λφ} − λφ)/(2λ²)] = (e^{λφ} − 1)/(2λ) = V/V'.)
        """
        lam = self.lam
        f = lambda p: math.exp(lam * p) - lam * p
        return (f(phi) - f(phi_end)) / (2.0 * lam ** 2)

    def phi_z_N(self, N: float, phi_end: Optional[float] = None) -> float:
        """Odwracanie N(φ) (potencjałowe przybliżenie slow-roll)."""
        phi_end = phi_end if phi_end is not None else self.phi_end_pot()
        lam = self.lam
        f_phi_end = math.exp(lam * phi_end) - lam * phi_end
        target = f_phi_end + 2.0 * lam ** 2 * N

        def eq(p):
            return math.exp(lam * p) - lam * p - target

        hi = math.log(max(target, 10.0)) / lam + 10.0
        return brentq(eq, phi_end + 1e-9, hi, xtol=1e-12, rtol=1e-12)


# ---------------------------------------------------------------------------
# Dokładne tło: Friedmann–Klein-Gordon
# ---------------------------------------------------------------------------

class TloInflacji:
    """
    Całkuje  φ̈ + 3Hφ̇ = −V',  H² = (φ̇²/2 + V)/3  (M_Pl=1)
    od plateau do ε_H = 1 i zwraca parametry przepływu Hubble'a jako
    funkcję liczby e-folds do końca inflacji.
    """

    def __init__(self, pot: PotencjalAlpha, phi_start: float = None,
                 n_max: float = 130.0, n_grid: int = 4000,
                 n_margin: float = 12.0):
        self.pot = pot
        if phi_start is None:
            # start dokładnie n_max + n_margin e-folds przed (potencjałowym)
            # końcem inflacji — wystarczająco głęboko na plateau
            self.phi_start = pot.phi_z_N(n_max + n_margin)
        else:
            self.phi_start = phi_start
        # slow-rollowa prędkość początkowa u = dφ/dN ≈ −V'/V
        self.u_start = -pot.dV(self.phi_start) / pot.V(self.phi_start)
        self.n_max = n_max + n_margin + 20.0  # twardy horyzont całkowania
        self.n_grid = n_grid
        self._rozwiaz()

    def _rozwiaz(self) -> None:
        """Całkowanie w czasie e-foldów N = ln a (równania dokładne):

            φ' = u,
            u' = −(3 − u²/2)·(u + V'/V),      H² = V/(3 − u²/2).

        Warunek stopu: ε_H = u²/2 = 1. Start: slow-rollowy IC na plateau.
        """
        p = self.pot

        def rhs(N, y):
            phi, u = y
            return [u, -(3.0 - 0.5 * u * u) * (u + p.dV(phi) / p.V(phi))]

        def end_event(N, y):
            return 1.0 - 0.5 * y[1] ** 2
        end_event.terminal = True
        end_event.direction = -1

        sol = solve_ivp(rhs, [0.0, self.n_max], [self.phi_start, self.u_start],
                        events=end_event, dense_output=True,
                        rtol=1e-10, atol=1e-13, max_step=0.25)
        if not sol.t_events[0].size:
            raise RuntimeError("nie osiągnięto ε_H=1 w horyzoncie n_max")
        N_end = float(sol.t_events[0][0])

        Ns = np.linspace(0.0, N_end, self.n_grid)
        phi, u = sol.sol(Ns)
        Vv = np.array([p.V(x) for x in phi])
        H = np.sqrt(Vv / (3.0 - 0.5 * u ** 2))
        N_left = N_end - Ns
        eps1 = 0.5 * u ** 2
        eps2 = np.gradient(np.log(np.clip(eps1, 1e-300, None)), Ns)
        eps3 = np.gradient(eps2, Ns)
        self.grid = {
            "N": Ns, "phi": phi, "u": u, "H": H,
            "N_left": N_left, "eps1": eps1, "eps2": eps2, "eps3": eps3,
            "rho_end_gev4": 1.5 * p.V(phi[-1]) * M_PL_GEV ** 4,
            "N_end": N_end,
        }

    def _w_N(self, N: float, klucz: str) -> float:
        """Interpolacja pola 'klucz' jako funkcja N_left (malejącej?)."""
        Nl = self.grid["N_left"]   # maleje od Nmax do 0
        # potrzebna rosnąca wstęga N
        idx = np.argsort(Nl)
        return float(np.interp(N, Nl[idx], self.grid[klucz][idx]))

    def obserwable(self, N: float) -> Dict[str, float]:
        """Obserwable drugiego rzędu dla horyzontu wychodzącego N e-folds
        przed końcem inflacji."""
        e1 = self._w_N(N, "eps1")
        e2 = self._w_N(N, "eps2")
        e3 = self._w_N(N, "eps3")
        phi_k = self._w_N(N, "phi")
        ns = 1.0 - 2.0 * e1 - e2 - 2.0 * e1**2 - (3 + 2 * C_NLO) * e1 * e2 - C_NLO * e2 * e3
        r = 16.0 * e1 * (1.0 + 2.0 * C_NLO * (e1 + e2))
        P_R = self.pot.V(phi_k) / (24.0 * math.pi**2 * e1)   # przy V0=1
        return {"N": N, "eps1": e1, "eps2": e2, "eps3": e3,
                "phi_k_Mpl": phi_k, "n_s": ns, "r": r,
                "V_k_pot1": self.pot.V(phi_k), "P_R_V01": P_R}

    def n_s_krzywa(self, Ns: np.ndarray) -> Dict[str, np.ndarray]:
        out = {"N": Ns, "n_s": [], "r": [], "V_k": [], "eps1": [], "phi_k": []}
        for N in Ns:
            o = self.obserwable(N)
            out["n_s"].append(o["n_s"]); out["r"].append(o["r"])
            out["V_k"].append(o["V_k_pot1"]); out["phi_k"].append(o["phi_k_Mpl"])
            out["eps1"].append(o["eps1"])
        return {k: np.asarray(v) for k, v in out.items()}

    def running(self, N: float, dN: float = 0.5) -> Dict[str, float]:
        """α_s = −dn_s/dN · (dln k/dN)⁻¹, analogicznie β_s (dln k/dN ≈ 1−ε₁)."""
        o_a, o_b = self.obserwable(N - dN), self.obserwable(N + dN)
        eps1 = self._w_N(N, "eps1")
        jac = 1.0 / (1.0 - eps1)
        alpha_s = -(o_b["n_s"] - o_a["n_s"]) / (2 * dN) * jac
        # β_s: druga pochodna przez trzy punkty
        o_c = self.obserwable(N)
        beta_s = -((o_b["n_s"] - 2 * o_c["n_s"] + o_a["n_s"]) / dN ** 2) * jac ** 2
        return {"alpha_s": alpha_s, "beta_s": beta_s,
                "n_s": o_c["n_s"], "r": o_c["r"]}


def normalizuj_V0_dla_As(tlo: TloInflacji, N: float, A_s: float = A_S_OBS
                         ) -> Dict[str, float]:
    """
    V₀ nie jest predykcją — P_R ∝ V₀ dokładnie. Normalizacja do A_s:

        V₀ = 24π² ε₁,⋆ A_s / (1−e^{−λφ⋆})²

    Zwraca V₀ i skalars V_⋆^(1/4) [GeV].
    """
    o = tlo.obserwable(N)
    shape = (1.0 - math.exp(-tlo.pot.lam * o["phi_k_Mpl"])) ** 2
    V0 = 24.0 * math.pi**2 * o["eps1"] * A_s / shape
    V_k = V0 * o["V_k_pot1"]
    return {"V0_Mpl4": V0, "V_k_quarter_GeV": V_k ** 0.25 * M_PL_GEV,
            "H_star_GeV": math.sqrt(V_k / 3.0) * M_PL_GEV}


# ---------------------------------------------------------------------------
# Podgrzewanie: fizyczne N_⋆(T_rh, w_rh)
# ---------------------------------------------------------------------------

def N_z_podgrzewania(
    H_k_gev: float,
    rho_end_gev4: float,
    T_rh_gev: float,
    w_rh: float = 0.0,
    k: float = K_PIVOT,
) -> Dict[str, float]:
    """
    Standardowa relacja podgrzewania:

        N_⋆ = ln(a_end·H_⋆/k)

    z  a_end = a_rh · (ρ_rh/ρ_end)^{1/[3(1+w_rh)]},
       a_rh  = (T₀/T_rh)·(g_s0/g_s,rh)^{1/3},
       ρ_rh  = (π²/30) g_*(T_rh) T_rh⁴.

    Walidacja znana: dla w_rh=0 i wysokiego T_rh (~lρ_end-scale) daje N ~ 60.
    """
    rho_rh = (math.pi ** 2 / 30.0) * G_STAR_RH * T_rh_gev ** 4
    if rho_rh >= rho_end_gev4:
        raise ValueError("rho_rh >= rho_end: podgrzewanie natychmiastowe "
                         "(użyj N_z_rh_natychmiastowego)")
    a_rh = (T0_GEV / T_rh_gev) * (G_STAR_S0 / G_STAR_RH) ** (1.0 / 3.0)
    a_end = a_rh * (rho_rh / rho_end_gev4) ** (1.0 / (3.0 * (1.0 + w_rh)))
    N_star = math.log(a_end * H_k_gev / k)
    N_rh = math.log((rho_end_gev4 / rho_rh) ** (1.0 / (3.0 * (1.0 + w_rh))))
    return {"N_star": N_star, "N_rh": N_rh, "rho_rh_gev4": rho_rh,
            "a_end": a_end}


def skan_podgrzewania(
    tlo: TloInflacji,
    t_rh_lista: np.ndarray,
    w_rh: float = 0.0,
    N_start: float = 60.0,
    A_s: float = A_S_OBS,
) -> Dict[str, np.ndarray]:
    """
    Samozgodne rozwiązanie pętli  N → (r, A_s) → V₀ → V_⋆, H_⋆, ρ_end → N_⋆(T_rh).
    Dla każdej T_rh wyznacza fizyczne N i obserwable w tym punkcie.
    Iteracja: zaczynamy od N_start; obliczamy V/H; nowe N = N_⋆; powtarzamy aż
    do zbieżności < 1e-3.
    """
    Ns, ns_l, r_l, a_s_l = [], [], [], []
    rho_end_shape = tlo.grid["rho_end_gev4"] / M_PL_GEV ** 4   # jednostki M_Pl
    for T_rh in t_rh_lista:
        N = N_start
        for _ in range(60):
            o = tlo.obserwable(N)
            V0 = 24.0 * math.pi ** 2 * o["eps1"] * A_s / \
                (1.0 - math.exp(-tlo.pot.lam * o["phi_k_Mpl"])) ** 2
            V_k = V0 * o["V_k_pot1"]
            H_k = math.sqrt(V_k / 3.0) * M_PL_GEV
            rho_end = V0 * rho_end_shape * M_PL_GEV ** 4
            out = N_z_podgrzewania(H_k, rho_end, T_rh, w_rh)
            if abs(out["N_star"] - N) < 1e-3:
                N = out["N_star"]; break
            N = out["N_star"]
        o = tlo.obserwable(N)
        rn = tlo.running(N)
        Ns.append(N); ns_l.append(o["n_s"]); r_l.append(o["r"])
        a_s_l.append(rn["alpha_s"])
    return {"T_rh": np.asarray(t_rh_lista), "N_star": np.asarray(Ns),
            "n_s": np.asarray(ns_l), "r": np.asarray(r_l),
            "alpha_s": np.asarray(a_s_l)}


# ---------------------------------------------------------------------------
# Analityka wiodącego rzędu — do testów spójności ze starym silnikiem
# ---------------------------------------------------------------------------

def predykcje_LO(N: float, alpha: float = 3.75) -> Dict[str, float]:
    """Wzory silnika: n_s = 1 − 2/N, r = 12α/N² (wiodący rząd 1/N)."""
    return {"n_s_LO": 1.0 - 2.0 / N, "r_LO": 12.0 * alpha / N ** 2,
            "alpha_s_LO": -2.0 / N ** 2}


def wymagane_N_dla_ns(n_s_target: float, alpha: float = 3.75) -> float:
    """Vanilla: N potrzebne dla zadanego n_s (wzór LO 1−2/N)."""
    return 2.0 / (1.0 - n_s_target)
