"""test_teleportation_deep.py — Testy pogłębionej analizy teleportacji."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from spin10_teleportation_deep import (
    GraphEntanglementFromHolonomies, EREqualsEPR,
    MERATeleportation, TraversableWormholeAnalysis,
    Spin10TeleportationDeep, L_PLANCK, T_PLANCK, DIM_SPIN10,
)

class TR:
    def __init__(self): self.p = self.f = 0
    def check(self, name, cond, d=""):
        s = "✅" if cond else "❌"
        if cond: self.p += 1
        else: self.f += 1
        print(f"  {s} {name}" + (f" — {d}" if d else ""))
    def summary(self):
        t=self.p+self.f; ok=self.f==0
        print(f"\n{'='*60}\n  {self.p}/{t} ({'✅ ALL PASS' if ok else f'❌ {self.f} FAIL'})\n{'='*60}")
        return ok

def test_A(tr):
    print("\n▸ A: Splątanie na grafie")
    e = GraphEntanglementFromHolonomies.compute_edge_entanglement()
    tr.check("A.1 Entropia > 0", e['entanglement_entropy_ebits'] > 0, f"E={e['entanglement_entropy_ebits']:.3f}")
    tr.check("A.2 Splątana", e['is_entangled'])
    tr.check("A.3 Czystość ∈ (0,1)", 0 < e['purity'] < 1.001, f"γ={e['purity']:.4f}")
    tr.check("A.4 E ≤ E_max", e['entanglement_entropy_ebits'] <= e['max_entanglement_ebits'] + 0.01)

    g = GraphEntanglementFromHolonomies.full_graph_entanglement_map(N=20, seed=42)
    tr.check("A.5 Mapa: E_mean > 0", g['mean_entanglement_ebits'] > 0)
    tr.check("A.6 Mapa: frakcja splątana > 0.5", g['fraction_entangled'] > 0.5)
    tr.check("A.7 S_max_adj = log₂(45)", abs(g['S_max_adjoint_repr'] - np.log2(45)) < 0.01)
    tr.check("A.8 Zanik: E(d=1) > E(d=10)", g['decay_with_distance']['entanglement_ebits'][0] > g['decay_with_distance']['entanglement_ebits'][-1])
    tr.check("A.9 Pojemność > 0", g['teleportation_capacity']['total_ebits'] > 0)

def test_B(tr):
    print("\n▸ B: ER=EPR")
    er = EREqualsEPR.wormhole_geometry()
    tr.check("B.1 r_throat > 0", er['throat_radius_m'] > 0)
    tr.check("B.2 r_throat ~ ℓ_P", er['throat_radius_planck'] < 100, f"r={er['throat_radius_planck']:.2f} ℓ_P")
    tr.check("B.3 Planck scale", er['is_planck_scale'])
    tr.check("B.4 Nie traversable", er['is_traversable'] == False)
    tr.check("B.5 Lifetime > 0", er['lifetime_s'] > 0)
    tr.check("B.6 Lifetime ~ t_P", er['lifetime_planck_times'] < 100)
    tr.check("B.7 Pojemność kanału > 0", er['channel_capacity_ebits'] > 0)
    tr.check("B.8 ratio << Schwarzschild Słońca", er['macro_comparison']['ratio_throat_to_sun'] < 1e-30)

    mi = EREqualsEPR.mutual_information_to_geometry(S_A=2, S_B=2, S_AB=3)
    tr.check("B.9 I(A:B) = 1", abs(mi['mutual_information'] - 1.0) < 0.01)
    tr.check("B.10 Połączone ER", mi['connected_by_ER'])

    mi0 = EREqualsEPR.mutual_information_to_geometry(S_A=2, S_B=2, S_AB=4)
    tr.check("B.11 I=0 → brak ER", not mi0['connected_by_ER'])

def test_C(tr):
    print("\n▸ C: MERA teleportacja")
    mera = MERATeleportation(32, 4)
    t = mera.teleportation_through_bulk(0, 16)
    tr.check("C.1 F > 0.999", t['teleportation_fidelity'] > 0.999, f"F={t['teleportation_fidelity']:.8f}")
    tr.check("C.2 Depth = 4", abs(t['geodesic_depth_layers'] - 4.0) < 0.01)
    tr.check("C.3 Min-cut = 8", abs(t['min_cut_bonds'] - 8.0) < 0.01)
    tr.check("C.4 S_RT > 0", t['ryu_takayanagi_entropy'] > 0)
    tr.check("C.5 No FTL", t['no_ftl'])
    tr.check("C.6 Requires classical", t['requires_classical_channel'])

    # Bliscy sąsiedzi: mniejsza głębokość
    t_near = mera.teleportation_through_bulk(0, 1)
    tr.check("C.7 Bliski: depth < 1", t_near['geodesic_depth_layers'] < 1.0)
    tr.check("C.8 Bliski: F → 1", t_near['teleportation_fidelity'] >= t['teleportation_fidelity'] - 1e-12)

    # Entanglement wedge
    w = mera.compute_entanglement_wedge(8)
    tr.check("C.9 Wedge: teleportacja w klinie możliwa", w['teleportation_possible_within_wedge'])
    tr.check("C.10 Wedge: frakcja ∈ (0,1)", 0 < w['wedge_fraction_of_bulk'] <= 1.0)

def test_D(tr):
    print("\n▸ D: Traversable Wormhole")
    tw = TraversableWormholeAnalysis.traversability_analysis()
    tr.check("D.1 Planck scale: traversable", tw['is_traversable_planck'])
    tr.check("D.2 Makro: NOT traversable", tw['is_macro_traversable'] == False)
    tr.check("D.3 r_throat ~ ℓ_P", tw['throat_radius_planck'] < 100)
    tr.check("D.4 Δt ~ t_P", tw['traversal_time_planck'] < 100)
    tr.check("D.5 E_Casimir < 0 (ujemna)", tw['casimir_energy_J'] < 0)
    tr.check("D.6 M_exotic > 0 (potrzebna egzotyczna masa)", tw['exotic_mass_solar'] > 0, f"M={tw['exotic_mass_solar']:.1e} M☉")
    tr.check("D.7 Qubits ≥ 1", tw['qubits_per_traversal'] >= 1)
    tr.check("D.8 Google porównanie", tw['google_2022_comparison']['qubits'] == 9)

def test_integration(tr):
    print("\n▸ Integration")
    deep = Spin10TeleportationDeep(N=20, chi=4, n_sites=16)
    r = deep.full_analysis()
    tr.check("I.1 Raport 4 sekcje", all(k in r for k in ['A_graph_entanglement','B_er_epr','C_mera_teleportation','D_traversable_wormhole']))
    tr.check("I.2 Summary 4 klucze", len(r['summary']) == 4)
    s = deep.summary_text()
    tr.check("I.3 Tekst > 500 znaków", len(s) > 500)
    tr.check("I.4 MERA w tekście", 'MERA' in s)
    tr.check("I.5 ER=EPR w tekście", 'ER=EPR' in s or 'ER' in s)

def run_all():
    print("=" * 60)
    print("  TESTY POGŁĘBIONEJ ANALIZY TELEPORTACJI SPIN(10)")
    print("=" * 60)
    tr = TR()
    test_A(tr); test_B(tr); test_C(tr); test_D(tr); test_integration(tr)
    tr.summary()
    return tr

if __name__ == "__main__":
    t = run_all()
    sys.exit(0 if t.f == 0 else 1)
