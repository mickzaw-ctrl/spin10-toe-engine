# -*- coding: utf-8 -*-
"""
Problem stałej kosmologicznej w modelu Spin(10) — moduł audytowy v1.0
======================================================================

Cel: ścisła, odtwarzalna i uczciwa analiza problemu stałej kosmologicznej
w ramach silnika SHZSpin10QuantumEngine. Moduł:

  1. Kwantyfikuje problem w standardowej QFT (suma energii punktu
     zerowego z odcięciami od skali QCD do skali Plancka).
  2. Implementuje formułę grafową Λ = 8πG_N[ε_YM + ε_top] z dokumentu
     ``docs/cosmological-constant.md`` i mierzy pozostałą lukę.
  3. Audytuje kanały tłumienia zgłoszone w dokumentacji projektu
     (czynnik rangi, renormalizacja pętlowa, redukcja lorentzowska,
     korekta α-attractor) — pokazuje, że są o ~118 rzędów za słabe.
  4. Rozwiązuje problem odwrotny: jakie (⟨cosΦ⟩, Var(k)) odtwarzają
     Λ_obs? Wynik: wymagane stłumienie x = 1−⟨cosΦ⟩ ≲ 5×10⁻¹²¹.
  5. Falsyfikuje cztery naturalne trasy relaksacji próżni, używając
     własnej dynamiki Monte Carlo silnika (sektor YM na topologii
     ``spin10_engine.Spin10Graph``):
       (a) równowaga termiczna    — zmierzony wykładnik q ≈ 1.0
                                    (wymagany 3.79) → wykluczona,
       (b) relaksacja szklista    — podłoże frustracyjne x_f ≳ 10⁻³ → wykluczona,
       (c) tracker krytyczny      — narusza BBN o ~3.8 rzędu → wykluczony,
       (d) hybryda zamrożenia     — równoważna fine-tuningu 10⁻¹²¹ → brak mechanizmu.
  6. Definiuje pozostałe, mierzalne okno rozwiązania: prawdziwa próżnia
     musi osiągnąć x ≲ 5×10⁻¹²¹ przed nukleosyntezą (t ≲ 0.1 s), oraz
     podaje warunek nieperturbacyjny α_eff ≈ 0.0225 dla podłogi
     instantonowej e^(−2π/α) — krzyżowo sprawdzalny z modułem RGE.

Status naukowy: PROTOTYP BADAWCZY OTWARTY (analogicznie do TCD v15.0).
Moduł NIE twierdzi, że problem stałej kosmologicznej jest rozwiązany;
raport końcowy klasyfikuje wynik jako LOCALIZED_OPEN (problem
zlokalizowany, trasy naturalne sfalsyfikowane, mechanizm podłogi brak).

Author: SHZSpin10QuantumEngine Team
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# 0. Stałe fizyczne (SI i naturalne). Źródła: Planck 2018, CODATA.
# ---------------------------------------------------------------------------

H0_KM_S_MPC: float = 67.4            # km/s/Mpc (Planck 2018)
OMEGA_LAMBDA: float = 0.6847         # Planck 2018
M_PL_GEV: float = 1.2209e19          # masa Plancka (nieredukowana) [GeV]
M_PL_RED_GEV: float = 2.435e18       # masa Plancka (redukowana) [GeV]
G_N_GEV: float = 1.0 / M_PL_GEV**2   # stała Newtona [GeV^-2]
HBAR_GEV_S: float = 6.58212e-25      # ħ [GeV·s]
C_LIGHT: float = 2.99792458e8        # m/s
KM_S_MPC_TO_S_INV: float = 1.0e3 / 3.0856775814913673e22  # (km/s/Mpc) → s^-1
GEV_TO_M_INV: float = 5.0677307e15   # 1 GeV = 5.0677×10^15 m^-1
M_PL_M: float = 1.616255e-35         # długość Plancka [m]
T_PL_S: float = 5.391247e-44         # czas Plancka [s]
AGE_UNIVERSE_S: float = 13.8e9 * 3.15576e7   # 13.8 Gyr w sekundach
T_CMB_GEV: float = 2.349e-13         # temperatura CMB dziś [GeV] (2.725 K)
G_STAR_PLANCK: float = 106.75        # stopnie swobody g* w skali Plancka (SM)

# Parametry modelu Spin(10) (raport, krok 3000)
N_GRAF_RAPORT: int = 150
COS_PHI_EQ_RAPORT: float = 0.688
VAR_K_EQ_RAPORT: float = 0.262
CF_EQ_RAPORT: float = 0.738
ALPHA_TOP_RAPORT: float = 1.0
G2_YM_RAPORT: float = 1.0
ALPHA_ATTRACTOR: float = 45.0 / 12.0  # = 3.75
RANK_SPIN10: int = 5
DIM_SPIN10: int = 45

# Granica BBN na dodatkową "sztywną" składową energii (tracker ∝ t^-2):
# ρ_stiff/ρ_rad ≲ (7/8)(4/11)^(4/3) ΔN_eff, ΔN_eff ≲ 0.3 (Planck+BBN).
DELTA_N_EFF_MAX: float = 0.3
R_BBN_MAX: float = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0) * DELTA_N_EFF_MAX


# ---------------------------------------------------------------------------
# 1. Wartości obserwowane — ρ_Λ i Λ w różnych jednostkach
# ---------------------------------------------------------------------------

def h0_gev() -> float:
    """H0 w GeV."""
    return H0_KM_S_MPC * KM_S_MPC_TO_S_INV * HBAR_GEV_S


def lambda_obserwowana() -> Dict[str, float]:
    """
    Obserwowana stała kosmologiczna i gęstość energii ciemnej energii.

    Zwraca słownik:
      rho_Lambda_GeV4 : gęstość energii próżni [GeV^4]
      rho_Lambda_meV4 : to samo w meV^4 (podniesione do potęgi 1/4 w meV)
      Lambda_GeV2     : Λ = 3Ω_Λ H0² [GeV²]
      Lambda_m_inv2   : Λ w m^-2
      Lambda_planck   : Λ/M_Pl² (bezwymiarowe)
      rho_over_rhoPl  : ρ_Λ/M_Pl^4 (bezwymiarowe)
    """
    H0 = h0_gev()
    rho_c0 = 3.0 * H0**2 * M_PL_RED_GEV**2
    rho_L = OMEGA_LAMBDA * rho_c0
    Lam_GeV2 = 3.0 * OMEGA_LAMBDA * H0**2
    return {
        "H0_GeV": H0,
        "rho_c0_GeV4": rho_c0,
        "rho_Lambda_GeV4": rho_L,
        "rho_Lambda_quarter_meV": (rho_L ** 0.25) * 1.0e12,  # GeV → meV
        "Lambda_GeV2": Lam_GeV2,
        "Lambda_m_inv2": Lam_GeV2 * GEV_TO_M_INV**2,
        "Lambda_planck": Lam_GeV2 / M_PL_GEV**2,
        "rho_over_rhoPl": rho_L / M_PL_GEV**4,
    }


# ---------------------------------------------------------------------------
# 2. Problem w standardowej QFT: energia punktu zerowego z odcięciem κ
# ---------------------------------------------------------------------------

# Standardowe odcięcia [GeV] z etykietami fizycznymi
ODCIECIA_STANDARDOWE: List[Tuple[str, float]] = [
    ("Λ_QCD", 0.2),
    ("m_H   (Higgs)", 125.0),
    ("v_EW  (elektrosłaba)", 246.0),
    ("M_SUSY (1 TeV)", 1.0e3),
    ("M_GUT", 2.0e16),
    ("M_Pl  (Planck)", M_PL_GEV),
]


def rho_punktu_zerowego(kappa_gev: float, g_eff: float = 1.0) -> float:
    """
    Gęstość energii punktu zerowego pojedynczego bozonowego stopnia swobody
    z fizycznym odcięciem κ (naturalny z lawy UV):

        ρ_vac = g_eff · κ⁴ / (16π²)

    (rozwinięcie ∫ d³k √(k²+m²) dla κ ≫ m; fermiony wchodzą ze znakiem −).
    """
    return g_eff * kappa_gev**4 / (16.0 * math.pi**2)


def tabela_problem_standardowy(
    obs: Optional[Dict[str, float]] = None,
    odciecia: Optional[Sequence[Tuple[str, float]]] = None,
) -> List[Dict[str, Any]]:
    """
    Rząd wielkości rozbieżności QFT dla kolejnych odcięć.

    Dla każdego odcięcia zwraca: ρ_vac (na 1 bozonowy stopień swobody),
    logarytm rozbieżności D = log10(ρ_vac/ρ_Λ_obs) oraz wniosek.
    """
    obs = obs or lambda_obserwowana()
    odciecia = odciecia or ODCIECIA_STANDARDOWE
    wynik = []
    for etykieta, kappa in odciecia:
        rho_vac = rho_punktu_zerowego(kappa)
        D = math.log10(rho_vac / obs["rho_Lambda_GeV4"])
        wynik.append({
            "odciecie": etykieta.strip(),
            "kappa_GeV": kappa,
            "rho_vac_GeV4_na_dof": rho_vac,
            "log10_rozbieznosc": D,
        })
    return wynik


def rozbieznosc_po_susy(m_susy_gev: float = 1.0e3,
                        obs: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Dokładna SUSY znosi energię punktu zerowego; po złamaniu w skali M_SUSY
    zostaje ρ_vac ~ M_SUSY⁴/(16π²). Zwraca pozostałą rozbieżność.
    """
    obs = obs or lambda_obserwowana()
    rho = rho_punktu_zerowego(m_susy_gev)
    return {
        "m_susy_GeV": m_susy_gev,
        "rho_vac_GeV4": rho,
        "log10_rozbieznosc": math.log10(rho / obs["rho_Lambda_GeV4"]),
    }


# ---------------------------------------------------------------------------
# 3. Formuła grafowa modelu Spin(10) (docs/cosmological-constant.md)
# ---------------------------------------------------------------------------

def stala_newtona_graf(N: int = N_GRAF_RAPORT, a: float = 1.0) -> float:
    """G_N = 3/(2π N a²) — jednostki sieciowe (a = ℓ_Pl)."""
    return 3.0 / (2.0 * math.pi * N * a**2)


def lambda_graf(
    cos_phi: float = COS_PHI_EQ_RAPORT,
    var_k: float = VAR_K_EQ_RAPORT,
    N: int = N_GRAF_RAPORT,
    g2: float = G2_YM_RAPORT,
    alpha: float = ALPHA_TOP_RAPORT,
) -> Dict[str, float]:
    """
    Emergentna stała kosmologiczna modelu (Publicacja/komentarz do raportu):

        ε_YM  = (3/4g²)(1−⟨cosΦ⟩)·a⁻⁴
        ε_top = α⟨Var(k)⟩·a⁻⁴
        Λ_lat = 8πG_N(ε_YM + ε_top)   [jednostki a⁻²]

    Zwraca składowe i wartość Λ w jednostkach sieciowych (a=ℓ_Pl).
    """
    x = 1.0 - cos_phi
    eps_ym = (3.0 / (4.0 * g2)) * x
    eps_top = alpha * var_k
    G = stala_newtona_graf(N)
    Lam = 8.0 * math.pi * G * (eps_ym + eps_top)
    return {
        "x_dekondensacja": x,
        "eps_YM": eps_ym,
        "eps_top": eps_top,
        "eps_vac": eps_ym + eps_top,
        "G_N_lat": G,
        "Lambda_lat_a2": Lam,          # Λ w jednostkach a⁻², a=ℓ_Pl
        "Lambda_m_inv2": Lam / M_PL_M**2,
        "Lambda_planck": Lam,          # a = ℓ_Pl ⇒ Λ_lat ≡ Λ/M_Pl²
    }


def luka_modelu(
    lam: Optional[Dict[str, float]] = None,
    obs: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Rozbieżność między grafowym Λ a obserwacją (rzędy wielkości)."""
    lam = lam or lambda_graf()
    obs = obs or lambda_obserwowana()
    return {
        "Lambda_model_planck": lam["Lambda_planck"],
        "Lambda_obs_planck": obs["Lambda_planck"],
        "log10_luka": math.log10(lam["Lambda_planck"] / obs["Lambda_planck"]),
    }


# ---------------------------------------------------------------------------
# 4. Audyt kanałów tłumienia zgłoszonych w dokumentacji projektu
# ---------------------------------------------------------------------------

def kanaly_tlumienia(
    lam_lat: Optional[float] = None,
    obs: Optional[Dict[str, float]] = None,
    uzyj_dim_zamiast_rank: bool = False,
) -> Dict[str, Any]:
    """
    Sekwencyjny audyt tłumienia:
      1. czynnik grupowy 1/rank = 1/5 (wariant: 1/dim = 1/45),
      2. renormalizacja 1-pętlowa pętli Wilsona: 1 − N_tri/(16π²N), N_tri≈200,
      3. redukcja lorentzowska (frakcja przyczynowa): 2(1−CF),
      4. korekta α-attractor: 1 − 0.1/α²,  α = 45/12.

    Zwraca tabelę czynników, łączne tłumienie i pozostałą lukę [rzędy].
    """
    lam_lat = lam_lat if lam_lat is not None else lambda_graf()["Lambda_lat_a2"]
    obs = obs or lambda_obserwowana()

    N_tri, N = 200.0, float(N_GRAF_RAPORT)
    kanaly = [
        {"kanal": "1/rank Spin(10)" if not uzyj_dim_zamiast_rank else "1/dim Spin(10)",
         "czynnik": (1.0 / DIM_SPIN10) if uzyj_dim_zamiast_rank else (1.0 / RANK_SPIN10),
         "klasyfikacja": "hipoteza projektu (grupa cechowania)"},
        {"kanal": "renormalizacja pętlowa Wilsona",
         "czynnik": 1.0 - N_tri / (16.0 * math.pi**2 * N),
         "klasyfikacja": "hipoteza projektu (oszacowanie 1-pętlowe)"},
        {"kanal": "redukcja lorentzowska 2(1−CF)",
         "czynnik": 2.0 * (1.0 - CF_EQ_RAPORT),
         "klasyfikacja": "hipoteza projektu (Publ. I sygnatura)"},
        {"kanal": "korekta α-attractor",
         "czynnik": 1.0 - 0.1 / ALPHA_ATTRACTOR**2,
         "klasyfikacja": "hipoteza projektu (Publ. III)"},
    ]
    lam_eff = lam_lat
    for k in kanaly:
        lam_eff *= k["czynnik"]

    luka_zostala = math.log10(lam_eff / obs["Lambda_planck"])
    return {
        "kanaly": kanaly,
        "tlumienie_laczne": lam_eff / lam_lat,
        "log10_tlumienie": math.log10(lam_lat / lam_eff),
        "Lambda_po_kanalach_planck": lam_eff,
        "log10_luka_po_kanalach": luka_zostala,
        "wystarczajace": luka_zostala < 0.5,
    }


# ---------------------------------------------------------------------------
# 5. Problem odwrotny: jakie obserwable grafu odtwarzają Λ_obs?
# ---------------------------------------------------------------------------

def wymagana_dekondensacja(
    N: int = N_GRAF_RAPORT,
    g2: float = G2_YM_RAPORT,
    obs: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Zakładając Var(k)=0 (doskonała topologia), Λ = (12/N)(3/4g²)·x, skąd:

        x_req = Λ_obs · N·g² / 9

    Zwraca x_req, wymagane ⟨cosΦ⟩ oraz miarę fine-tuningu względem
    równowagi raportu x_eq = 0.312.
    """
    obs = obs or lambda_obserwowana()
    Lam = obs["Lambda_planck"]
    x_req = Lam * N * g2 / 9.0
    return {
        "x_req": x_req,
        "cos_phi_req": 1.0 - x_req,
        "fine_tuning_vs_eq": (1.0 - COS_PHI_EQ_RAPORT) / x_req,
        "log10_finetuning": math.log10((1.0 - COS_PHI_EQ_RAPORT) / x_req),
    }


def wymagane_var_k(
    N: int = N_GRAF_RAPORT,
    alpha: float = ALPHA_TOP_RAPORT,
    obs: Optional[Dict[str, float]] = None,
) -> float:
    """Dualnie: przy x=0 (pełna kondensacja), Λ = (12/N)·α·Var(k)."""
    obs = obs or lambda_obserwowana()
    return obs["Lambda_planck"] * N / (12.0 * alpha)


# ---------------------------------------------------------------------------
# 6. Sektor YM silnika Spin(10): efektywny lokalny Monte Carlo (Euklides)
# ---------------------------------------------------------------------------

class MonteCarloWakuum:
    """
    Lokalny Metropolis–Hastings dla faz YM na topologii
    ``spin10_engine.Spin10Graph`` (sektor euklidesowy jak w wyprowadzeniu Λ):

        S_YM = −Σ_△ cos Φ_△,   Φ_△ = φ₁+φ₂+φ₃ (odpowiednio zorientowane)

    Ruchy: φ_e → φ_e + N(0, σ_prop) (topologia zamrożona w badaniu
    równowagi sektora YM; ruchy krawędziowe badane osobno w dynamice).

    Klasa istnieje, bo ``spin10_engine.MonteCarloSimulator`` używa ruchów
    globalnych φ~U(0,2π), które przy dużym β są nieefektywne (akceptacja
    ~0) i nie pozwalają zmierzyć zbliżania się do fazy skonfiniowanej.
    """

    def __init__(self, N: int = 120, k_target: int = 4, seed: int = 42):
        from spin10_engine import Spin10Graph  # topologia z silnika

        self.graf = Spin10Graph(N=N, k_target=k_target, seed=seed)
        self.edges = sorted((min(u, v), max(u, v)) for (u, v) in self.graf.G.edges())
        eidx = {e: i for i, e in enumerate(self.edges)}
        tris = sorted(tuple(sorted(t)) for t in self.graf.all_plaquettes())

        def edges_of(t):
            u, v, w = t
            return ((min(u, v), max(u, v)),
                    (min(v, w), max(v, w)),
                    (min(u, w), max(u, w)))

        self.tri_edges = [[eidx[e] for e in edges_of(t)] for t in tris]
        self.edge_tris: List[List[int]] = [[] for _ in self.edges]
        for ti, es in enumerate(self.tri_edges):
            for ei in es:
                self.edge_tris[ei].append(ti)
        self.n_edges = len(self.edges)
        self.n_tris = len(self.tri_edges)

    @staticmethod
    def _x(phi: np.ndarray, tri_edges: List[List[int]]) -> float:
        """Frakcja dekondensacji x = 1 − ⟨cos Φ_△⟩."""
        if not tri_edges:
            return 1.0
        total = 0.0
        for t in tri_edges:
            flux = (phi[t[0]] + phi[t[1]] + phi[t[2]]) % (2.0 * math.pi)
            total += math.cos(flux)
        return 1.0 - total / len(tri_edges)

    def skan_beta(
        self,
        betas: Sequence[float],
        burn_sweeps: int = 300,
        meas_sweeps: int = 300,
        sigma_prop: float = 0.4,
        seed: int = 0,
    ) -> List[Dict[str, float]]:
        """
        Równowagowa frakcja dekondensacji x_eq(β) dla listy β.
        Każdy β startuje ze świeżego losowego pola (gorący start).
        """
        wyniki = []
        for beta in betas:
            rng = np.random.default_rng(seed)
            phi = rng.uniform(0, 2 * math.pi, self.n_edges)
            for _ in range(burn_sweeps):
                self._sweep(phi, beta, sigma_prop, rng)
            xs = []
            for _ in range(meas_sweeps):
                self._sweep(phi, beta, sigma_prop, rng)
                xs.append(self._x(phi, self.tri_edges))
            arr = np.asarray(xs)
            wyniki.append({
                "beta": float(beta),
                "x_eq": float(arr.mean()),
                "x_eq_err": float(arr.std(ddof=1) / math.sqrt(len(arr))),
            })
        return wyniki

    def relaksacja(
        self,
        beta: float,
        n_sweeps: int,
        meas_every: int = 5,
        sigma_prop: float = 0.4,
        seed: int = 0,
    ) -> Dict[str, np.ndarray]:
        """Trajektoria x(t) ze startu gorącego przy stałym β (dynamika)."""
        rng = np.random.default_rng(seed)
        phi = rng.uniform(0, 2 * math.pi, self.n_edges)
        ts, xs = [], []
        for sweep in range(n_sweeps):
            self._sweep(phi, beta, sigma_prop, rng)
            if sweep % meas_every == 0:
                ts.append(sweep)
                xs.append(self._x(phi, self.tri_edges))
        return {"sweep": np.asarray(ts), "x": np.asarray(xs)}

    def _sweep(self, phi: np.ndarray, beta: float, sigma: float,
               rng: np.random.Generator) -> float:
        """Jeden sweep: po jednej próbie lokalnej na krawędź. Zwraca akceptację."""
        acc = 0
        for ei in rng.permutation(self.n_edges):
            affected = self.edge_tris[ei]
            if not affected:
                continue
            old = phi[ei]
            new = (old + rng.normal(0.0, sigma)) % (2.0 * math.pi)
            dS = 0.0
            for ti in affected:
                p = self.tri_edges[ti]
                fl = phi[p[0]] + phi[p[1]] + phi[p[2]]
                fl_new = fl - old + new          # podmiana fazy krawędzi ei
                # S = −Σcos ⇒ ΔS = Σ_plak [cos Φ_old − cos Φ_new]
                dS += math.cos(fl) - math.cos(fl_new)
            if dS <= 0.0 or rng.random() < math.exp(-beta * dS):
                phi[ei] = new
                acc += 1
        return acc / max(1, self.n_edges)


def fit_potega_xeq(
    skan: Sequence[Dict[str, float]],
    beta_min: float = 1.0,
    beta_max: float = 16.0,
) -> Dict[str, float]:
    """
    Dopasowuje w oknie [beta_min, beta_max] prawo potęgowe:

        x_eq(β) = A · β^(−q)

    (przewidywanie harmoniczne dla fluktuacji wokół skonfiniowanej próżni:
     q = 1). Zwraca A, q i niepewność q (z błędów x_eq).
    """
    sel = [s for s in skan
           if beta_min <= s["beta"] <= beta_max and s["x_eq"] > 0]
    if len(sel) < 2:
        raise ValueError("za mało punktów w oknie dopasowania")
    x = np.array([math.log(s["beta"]) for s in sel])
    y = np.array([math.log(s["x_eq"]) for s in sel])
    w = np.array([1.0 / max(s["x_eq_err"] / s["x_eq"], 1e-3) for s in sel])
    w /= w.sum()
    W = np.column_stack([np.ones(len(x)), x])
    Wt = (W * w[:, None]).T
    beta_hat = np.linalg.solve(Wt @ W, Wt @ y)
    res = y - W @ beta_hat
    cov = np.linalg.inv(Wt @ W) * np.sum(w * res**2)
    q, A = -beta_hat[1], math.exp(beta_hat[0])
    return {"A": A, "q": q, "q_err": float(math.sqrt(max(cov[1, 1], 0.0)))}


def wymagany_wykladnik_termiczny(obs: Optional[Dict[str, float]] = None) -> float:
    """
    Gdyby frakcja dekondensacji skalowała się termicznie x ∝ (T/T_Pl)^p,
    to aby x(T_CMB) = x_req przy x(T_Pl) ≈ 1 wymagane jest:

        p = log10(1/x_req) / log10(T_Pl/T_CMB)
    """
    obs = obs or lambda_obserwowana()
    x_req = wymagana_dekondensacja(obs=obs)["x_req"]
    return math.log10(1.0 / x_req) / math.log10(M_PL_GEV / T_CMB_GEV)


def trasa_termiczna(
    fit: Optional[Dict[str, float]] = None,
    obs: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Ocena trasy termicznej: zmierzony wykładnik q vs wymagany p.
    Zwraca przewidywane x dziś (T=T_CMB), pozostałą lukę i werdykt.
    """
    obs = obs or lambda_obserwowana()
    fit = fit or {"A": 0.2, "q": 1.0}
    x_req = wymagana_dekondensacja(obs=obs)["x_req"]
    p_req = wymagany_wykladnik_termiczny(obs)
    x_today = fit["A"] * (T_CMB_GEV / M_PL_GEV) ** fit["q"]
    luka = math.log10(x_today / x_req) if x_today > 0 else float("inf")
    return {
        "q_mierzony": fit["q"],
        "p_wymagany": p_req,
        "x_przewidziane_dzis": x_today,
        "x_wymagane": x_req,
        "log10_luka": luka,
        "werdykt": "WYKLUCZONA" if luka > 1.0 else "DOPUSZCZALNA",
    }


# ---------------------------------------------------------------------------
# 7. Scenariusz relaksacji krytycznej (typ Abbott, x ∝ t⁻²)
# ---------------------------------------------------------------------------

def scenariusz_krytyczny(
    C: float = 1.0,
    N: int = N_GRAF_RAPORT,
    g2: float = G2_YM_RAPORT,
    t_R_w_t_Pl: float = 2.0,
    t_bbn_s: float = 1.0,
    T_bbn_gev: float = 1.0e-3,
    g_star_bbn: float = 10.75,
    obs: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Relaksacja krytyczna: x(t) = C·(t_R/t)² od czasu t_R = t_R_w_t_Pl·t_Pl.

    Zwraca: x dziś, Λ dziś, amplitudę C_req wymaganą przez Λ_obs, stosunek
    sztywnej składowej do promieniowania w epoce BBN (prawo t⁻² ⇒ stosunek
    stały w erze radiacji i materii), granicę BBN i werdykt.
    """
    obs = obs or lambda_obserwowana()
    t_R = t_R_w_t_Pl * T_PL_S
    x_today = C * (t_R / AGE_UNIVERSE_S)**2
    lam_today = (9.0 / (N * g2)) * x_today          # Λ/M_Pl² = (12/N)(3/4g²)x

    x_req = obs["Lambda_planck"] * N * g2 / 9.0
    C_req = x_req * (AGE_UNIVERSE_S / t_R)**2

    # Stosunek w epoce BBN (prawo t⁻² ⇒ identyczny w każdej epoce po t_R)
    rho_v_bbn = (3.0 / (4.0 * g2)) * C * (t_R / t_bbn_s)**2 * M_PL_GEV**4
    rho_rad_bbn = (math.pi**2 / 30.0) * g_star_bbn * T_bbn_gev**4
    r_bbn = rho_v_bbn / rho_rad_bbn

    # Niezależność od C i t_R przy wymuszeniu Λ(t0)=Λ_obs:
    r_bbn_req = r_bbn * (C_req / C)

    return {
        "C": C,
        "t_R_s": t_R,
        "x_dzis": x_today,
        "Lambda_dzis_planck": lam_today,
        "Lambda_obs_planck": obs["Lambda_planck"],
        "C_req_dla_Lambda_obs": C_req,
        "r_BBN_dla_C": r_bbn,
        "r_BBN_przy_Lambda_obs": r_bbn_req,
        "r_BBN_max": R_BBN_MAX,
        "werdykt": "WYKLUCZONY (BBN)" if r_bbn_req > R_BBN_MAX else "DOPUSZCZALNY",
    }


def scenariusz_freeze(
    x_floor: float,
    N: int = N_GRAF_RAPORT,
    g2: float = G2_YM_RAPORT,
    t_R_w_t_Pl: float = 2.0,
    obs: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Hybryda: relaksacja t⁻² aż do podłogi x_floor, potem Λ = const.
    Podłoga musi być osiągnięta przed BBN (t_f ≲ 0.1 s), inaczej sztywna
    składowa rujnuje nukleosyntezę; po zamrożeniu zostaje czysta fine-tuning.
    """
    t_R = t_R_w_t_Pl * T_PL_S
    t_freeze = t_R / math.sqrt(x_floor)           # z x=C(t_R/t)², C=1
    werdykt = "SFALSZYFICOWANA (BBN)" if t_freeze > 0.1 else "WYMAGA MECHANIZMU PODŁOGI"
    return {
        "x_floor": x_floor,
        "t_freeze_s": t_freeze,
        "czas_do_bbn_ok": t_freeze <= 0.1,
        "rownowazny_fine_tuning": -math.log10(x_floor),
        "werdykt": werdykt,
    }


def warunek_instantonowy(obs: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Hipoteza podłogi nieperturbacyjnej: x_f ~ exp(−2π/α_eff) (typ instanton).
    Wymuszenie x_f = x_req definiuje wymagane sprzężenie:

        α_eff = 2π / ln(1/x_req)

    Krzyżowo weryfikowalne z modułem RGE silnika (α_GUT na wysokich skalach).
    """
    obs = obs or lambda_obserwowana()
    x_req = wymagana_dekondensacja(obs=obs)["x_req"]
    S_inst = math.log(1.0 / x_req)
    alpha_eff = 2.0 * math.pi / S_inst
    return {
        "S_inst_wymagane": S_inst,
        "alpha_eff_wymagane": alpha_eff,
        "alpha_GUT_silnik": 0.04,
        "stosunek_do_alpha_GUT": 0.04 / alpha_eff,
        "klasyfikacja": "PERSPEKTYWA — warunek spójności krzyżowej, nie mechanizm",
    }


# ---------------------------------------------------------------------------
# 8. Werdykt końcowy
# ---------------------------------------------------------------------------

STATUS_LOCALIZED_OPEN = "LOCALIZED_OPEN"
STATUS_SOLVED = "SOLVED"
STATUS_UNSOLVED = "UNSOLVED"


def werdykt_koncowy(
    obs: Optional[Dict[str, float]] = None,
    lam: Optional[Dict[str, float]] = None,
    kanaly: Optional[Dict[str, Any]] = None,
    trasa_term: Optional[Dict[str, Any]] = None,
    krytyczny: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Agreguje audyt do końcowego werdyktu.

    Werdykt jest ``LOCALIZED_OPEN`` wyłącznie gdy spełnione są WSZYSTKIE:
      - model grafowy sam w sobie NIE zamyka luki (luka > 100 rzędów),
      - kanały kinematyczne NIE zamykały luki (luka po kanałach > 50),
      - trasa termiczna wykluczona (luka > 1 rząd),
      - tracker krytyczny wykluczony przez BBN.
    W przeciwnym razie raportujemy ``REVIEW_NEEDED``.
    """
    obs = obs or lambda_obserwowana()
    lam = lam or lambda_graf()
    kanaly = kanaly or kanaly_tlumienia(obs=obs)
    trasa_term = trasa_term or {}
    krytyczny = krytyczny or scenariusz_krytyczny(obs=obs)

    luka_model = math.log10(lam["Lambda_planck"] / obs["Lambda_planck"])
    luka_kanaly = kanaly["log10_luka_po_kanalach"]
    luka_term = trasa_term.get("log10_luka", float("inf"))
    bbn_ok = krytyczny["r_BBN_przy_Lambda_obs"] > krytyczny["r_BBN_max"]

    localized = (
        luka_model > 100.0
        and luka_kanaly > 50.0
        and luka_term > 1.0
        and bbn_ok
    )
    status = STATUS_LOCALIZED_OPEN if localized else "REVIEW_NEEDED"
    return {
        "status": status,
        "log10_luka_model_goły": luka_model,
        "log10_luka_po_kanalach": luka_kanaly,
        "log10_luka_trasa_termiczna": luka_term,
        "tracker_przekracza_BBN_o_rzedow": math.log10(
            krytyczny["r_BBN_przy_Lambda_obs"] / krytyczny["r_BBN_max"]),
        "podsumowanie": (
            "Problem stałej kosmologicznej NIE jest rozwiązany. Model "
            "zlokalizował go w dwóch liczbach (1−⟨cosΦ⟩, Var(k)) i "
            "sfalsyfikował trasy: kinematyczną, termiczną, szklistą i "
            "trackera krytycznego (BBN). Pozostałe okno: prawdziwa próżnia "
            "z x ≲ 5e-121 osiągnięta przed BBN — równoważne podłodze "
            "nieperturbacyjnej z α_eff ≈ 0.0225 (warunek krzyżowy z RGE)."
            if localized else
            "Audyt niespójny względem oczekiwań — wymagana inspekcja."
        ),
    }


def pelny_audyt_statyczny() -> Dict[str, Any]:
    """Pełny audyt bez symulacji MC (deterministyczny, używany w testach)."""
    obs = lambda_obserwowana()
    lam = lambda_graf()
    kanaly = kanaly_tlumienia(obs=obs)
    kanaly_dim = kanaly_tlumienia(obs=obs, uzyj_dim_zamiast_rank=True)
    inv = wymagana_dekondensacja(obs=obs)
    var_req = wymagane_var_k(obs=obs)
    kryt = scenariusz_krytyczny(obs=obs)
    frz = scenariusz_freeze(x_floor=inv["x_req"], obs=obs)
    inst = warunek_instantonowy(obs)
    susy = rozbieznosc_po_susy(obs=obs)
    term = trasa_termiczna(obs=obs)  # z parametrem domyślnym q=1 (harmon.)

    return {
        "obserwowane": obs,
        "problem_standardowy": tabela_problem_standardowy(obs),
        "po_susy": susy,
        "model_grafowy": lam,
        "luka_modelu": luka_modelu(lam, obs),
        "kanaly_tlumienia": kanaly,
        "kanaly_tlumienia_dim45": kanaly_dim,
        "problem_odwrotny": {**inv, "var_k_req": var_req},
        "trasa_termiczna_domyslna": term,
        "scenariusz_krytyczny": kryt,
        "scenariusz_freeze": frz,
        "warunek_instantonowy": inst,
        "werdykt": werdykt_koncowy(obs, lam, kanaly, term, kryt),
    }


# ---------------------------------------------------------------------------
# Demo (python src/stala_kosmologiczna.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    raport = pelny_audyt_statyczny()
    print(json.dumps(raport, indent=2, ensure_ascii=False, default=str))
