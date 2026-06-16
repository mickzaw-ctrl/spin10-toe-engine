"""
Wyprowadzenie stalej cosmological Lambda w modelu Spin(10)
Report: M. Slusarczyk, Sieciowy Model Grawitacji Kwantowej Spin(10)

Formula:
    Lambda_eff = (3 * 8*pi * G_N)/(4 * g^2 * a^4) * (1 - <cos Phi_triangle>)
                + (8*pi * G_N * alpha)/(a^4) * <Var(k)>

    G_N = 3/(2*pi*N*a^2)    [z dualnosci graph->4-dimensionowa rozmaitosc]
"""
import math
import numpy as np

# ---------------------------------------------------------------------------
# 1.  Parameters z report (rownowaga, krok 3000)
# ---------------------------------------------------------------------------
N            = 150            # liczba wezlow
k_mean       = 4              # docelowy stopien graph
alpha        = 1.0            # kara topologiczna (parametr modelu)
g2           = 1.0            # sprzezenie YM (Spin(10) ~ unitarne w tych jedn.)
a            = 1.0            # krok network (w jednostkach a; fizycznie ~ l_P)

# Obserwable z simulation
W_eq         = 0.688          # <W> = <cos Phi_plakiett>
Var_k_eq     = 0.262          # wariancja stopni w equilibrium

# ---------------------------------------------------------------------------
# 2.  Stala Newtona (wylaniajaca sie z network)
# ---------------------------------------------------------------------------
#  G_N = 3 / (2 * pi * N * a^2)   [wzor Jacobsa-Tesedera analog]
G_N = 3.0 / (2.0 * math.pi * N * a**2)

# ---------------------------------------------------------------------------
# 3.  Gestosc energy prozniowej - dwa przyczynki
# ---------------------------------------------------------------------------
# (a) Przyczynek YM (Spin(10) - field cechowania)
eps_YM = (3.0 / (4.0 * g2 * a**4)) * (1.0 - W_eq)

# (b) Przyczynek topologiczny (defekty network)
eps_top = (alpha / a**4) * Var_k_eq

eps_vac = eps_YM + eps_top

# ---------------------------------------------------------------------------
# 4.  Lambda effective
# ---------------------------------------------------------------------------
Lambda_eff = 8.0 * math.pi * G_N * eps_vac

# ---------------------------------------------------------------------------
# 5.  Lambda po uwglednieniu tlumienia Spin(10)
# ---------------------------------------------------------------------------
# W ranku Spin(10) = 5, dim alg = 45. Tlumienie 1/rank(G):
Lambda_tl = Lambda_eff / 5.0

# W pelni skonfined prozni (cos Phi -> 1), Lambda redukuje sie do
# wylacznie topologicznego:
eps_vac_conf = eps_top           # YM = 0
Lambda_conf = 8.0 * math.pi * G_N * eps_vac_conf

# ---------------------------------------------------------------------------
# 6.  Wydruk
# ---------------------------------------------------------------------------
print("=" * 70)
print("  W Y P R O W A D Z E N I E   S T A L E J   K O S M O L O G I C Z N E J")
print("=" * 70)
print(f"  Parameters:  N = {N},  <k> = {k_mean},  alpha = {alpha},  g^2 = {g2}")
print(f"  Obserwable: <cos Phi> = {W_eq},  Var(k) = {Var_k_eq}")
print("-" * 70)
print(f"  Stala Newtona   G_N               = {G_N:.6f}")
print(f"  epsilon_YM      = (3/4g^2)(1-<cos>) = {eps_YM:.6f}")
print(f"  epsilon_top     = alpha * Var(k)   = {eps_top:.6f}")
print(f"  epsilon_vac     = suma             = {eps_vac:.6f}")
print("-" * 70)
print(f"  Lambda_eff (bare, Spin(10))       = {Lambda_eff:.6f}  * l_P^-4")
print(f"  Lambda_tl  (z tlumieniem rank=5)  = {Lambda_tl:.6f}   * l_P^-4")
print(f"  Lambda_conf (full GUT vacuum)     = {Lambda_conf:.6f}  * l_P^-4")
print("=" * 70)

# ---------------------------------------------------------------------------
# 7.  Zaleznosc Lambda od <cos Phi> (faza kondensacji)
# ---------------------------------------------------------------------------
print("\n  Zaleznosc Lambda_eff od stopnia kondensacji field Spin(10):")
print("  " + "-" * 60)
print(f"  {'<cos Phi>':>12} | {'eps_YM':>10} | {'eps_vac':>10} | {'Lambda':>10}")
print("  " + "-" * 60)
for cos_phi in np.linspace(-1.0, 1.0, 11):
    eps_ym = (3.0 / (4.0 * g2)) * (1.0 - cos_phi)
    eps = eps_ym + eps_top
    Lam = 8.0 * math.pi * G_N * eps
    print(f"  {cos_phi:>12.3f} | {eps_ym:>10.4f} | {eps:>10.4f} | {Lam:>10.4f}")
print("  " + "-" * 60)
print("\n  Uwaga: <cos Phi> = +1 -> pelna kondensacja, Lambda minimalne")
print("         <cos Phi> = -1 -> pelna dekondensacja, Lambda maksymalne")
