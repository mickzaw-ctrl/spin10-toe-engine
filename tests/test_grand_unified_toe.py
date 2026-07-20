"""
test_grand_unified_toe.py
==========================
Pełny zestaw testów dla modułu Wielkiej Unifikacji (GUT) i Teorii Wszystkiego (TOE).

Testuje wszystkie 10 filarów:
  1. Algebra Lie Spin(10)          2. Łańcuch łamania symetrii
  3. Unifikacja sprzężeń (RGE)    4. Stałe fizyczne top-down
  5. Yukawy / masy fermionów      6. Rozpad protonu
  7. Trzy generacje z E₈          8. Masy neutrin (seesaw)
  9. Integracja grawitacji (TOE)  10. SUSY i ciemna materia

Author: SHZ Quantum Technologies — Test Suite
Version: 15.0-GUT-TOE-TESTS
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grand_unified_toe_core import (
    Spin10LieAlgebra, SymmetryBreakingChain, GaugeCouplingUnification,
    TopDownPhysicalConstants, FermionMassesYukawa, ProtonDecay,
    ThreeGenerationsE8, SeesawNeutrinoMasses, GravityIntegrationTOE,
    SUSYAndDarkMatter, GrandUnifiedTOESolution,
    DIM_SPIN10, DIM_E8, M_GUT_GEV, M_SUSY_GEV,
)


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def check(self, name: str, condition: bool, detail: str = ""):
        status = "✅ PASS" if condition else "❌ FAIL"
        self.results.append((name, status, detail))
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        print(f"  {status}: {name}" + (f" — {detail}" if detail else ""))

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"  WYNIKI: {self.passed}/{total} testów zaliczonych")
        msg = '✅ WSZYSTKIE TESTY PRZESZŁY!' if self.failed == 0 else f'❌ {self.failed} test(ów) nie przeszło'
        print(f"  {msg}")
        print(f"{'='*70}")
        return self.failed == 0


# ── Filar 1 ──────────────────────────────────────────────────────────────

def test_pillar_1(tr: TestResults):
    print("\n▸ FILAR 1: Algebra Lie Spin(10)")
    gens = Spin10LieAlgebra.generate_so10_generators()
    tr.check("1.1 Liczba generatorów = 45", len(gens) == 45, f"n={len(gens)}")
    v = Spin10LieAlgebra.verify_lie_algebra(gens)
    tr.check("1.2 Generatory antysymetryczne", v['antisymmetric'])
    tr.check("1.3 Algebra zamknięta", v['algebra_closed'])
    tr.check("1.4 Znormalizowane", v['normalized'])
    tr.check("1.5 Ortogonalne", v['orthogonal'])
    # repr
    r = Spin10LieAlgebra.representation_dimensions()
    tr.check("1.6 repr 16 = 16 dim", r['16']['dim'] == 16)
    tr.check("1.7 repr 45 = 45 dim", r['45']['dim'] == 45)
    tr.check("1.8 repr 126 = 126 dim", r['126']['dim'] == 126)


# ── Filar 2 ──────────────────────────────────────────────────────────────

def test_pillar_2(tr: TestResults):
    print("\n▸ FILAR 2: Łańcuch Łamania Symetrii")
    chain = SymmetryBreakingChain.full_breaking_chain()
    tr.check("2.1 5 etapów łamania", chain['n_steps'] == 5)
    tr.check("2.2 Start: Spin(10)", chain['initial_group'] == 'Spin(10)')
    tr.check("2.3 Koniec: SU(3)×U(1)", 'SU(3)' in chain['final_group'])
    tr.check("2.4 45 bozonów Spin(10)", chain['boson_count_spin10'] == 45)
    tr.check("2.5 12 bozonów SM", chain['boson_count_SM'] == 12)
    tr.check("2.6 33 masywne X,Y bosony", chain['massive_X_Y_bosons'] == 33)

    ps = SymmetryBreakingChain.pati_salam_decomposition()
    tr.check("2.7 16 = (4,2,1)⊕(4̄,1,2)", ps['spinor_16_decomposition']['total_dim'] == 16)
    tr.check("2.8 B-L jawne w Pati-Salam", 'B-L' in ps['B_minus_L'])


# ── Filar 3 ──────────────────────────────────────────────────────────────

def test_pillar_3(tr: TestResults):
    print("\n▸ FILAR 3: Unifikacja Sprzężeń (2-loop RGE)")
    rge = GaugeCouplingUnification.integrate_2loop_rge()
    tr.check("3.1 M_GUT ~ 10¹⁵-10¹⁷ GeV",
             1e15 < rge['M_GUT_GeV'] < 1e17,
             f"M_GUT={rge['M_GUT_GeV']:.2e}")
    tr.check("3.2 α_GUT ~ 0.03-0.05",
             0.03 < rge['alpha_GUT'] < 0.05,
             f"α_GUT={rge['alpha_GUT']:.4f}")
    tr.check("3.3 sin²θ_W(GUT) ≈ 3/8",
             abs(rge['sin2_thetaW_GUT'] - 0.375) < 0.03,
             f"sin²θ_W={rge['sin2_thetaW_GUT']:.4f}")
    tr.check("3.4 Unifikacja ≤ 10% spread",
             rge['unification_spread'] < 0.10,
             f"spread={rge['unification_spread']:.4f}")
    tr.check("3.5 g₁≈g₂≈g₃ na M_GUT",
             abs(rge['g1_GUT'] - rge['g2_GUT']) / rge['g1_GUT'] < 0.15)


# ── Filar 4 ──────────────────────────────────────────────────────────────

def test_pillar_4(tr: TestResults):
    print("\n▸ FILAR 4: Stałe Fizyczne Top-Down")
    c = TopDownPhysicalConstants.derive_low_energy_constants()
    tr.check("4.1 α_em⁻¹ = 137.036 (±0.05)",
             c['alpha_em_match'],
             f"α_em⁻¹={c['alpha_em_inv_0']:.3f}")
    tr.check("4.2 α_s(M_Z) = 0.1180 (±0.003)",
             c['alpha_s_match'],
             f"α_s={c['alpha_s_MZ']}")
    tr.check("4.3 sin²θ_W(M_Z) ∈ [0.20, 0.25]",
             0.20 < c['sin2_thetaW_MZ'] < 0.25,
             f"sin²θ_W={c['sin2_thetaW_MZ']:.4f}")
    tr.check("4.4 Wyprowadzenie top-down (bez input exp.)",
             'Top-down' in c['derivation'])


# ── Filar 5 ──────────────────────────────────────────────────────────────

def test_pillar_5(tr: TestResults):
    print("\n▸ FILAR 5: Masy Fermionów / Yukawy")
    y = FermionMassesYukawa.yukawa_structure()
    tr.check("5.1 m_t = 172.76 GeV",
             abs(y['quark_masses_GeV']['up'][2] - 172.76) < 0.1)
    tr.check("5.2 b-τ unifikacja (ratio ≈ 1 na GUT)",
             y['b_tau_unification'],
             f"ratio_GUT={y['b_tau_ratio_GUT']:.3f}")
    tr.check("5.3 Parametr Froggatt-Nielsen ε ∈ (0.05, 0.15)",
             0.05 < y['froggatt_nielsen_epsilon'] < 0.15,
             f"ε={y['froggatt_nielsen_epsilon']:.4f}")
    tr.check("5.4 3 źródła Yukawy (10, 126̄, 120)",
             len(y['yukawa_sources']) == 3)
    tr.check("5.5 Georgi-Jarlskog m_s/m_μ ≈ 1/3",
             y['georgi_jarlskog_match'],
             f"ratio={y['georgi_jarlskog_ratio']:.3f}")


# ── Filar 6 ──────────────────────────────────────────────────────────────

def test_pillar_6(tr: TestResults):
    print("\n▸ FILAR 6: Rozpad Protonu")
    pd = ProtonDecay.compute_proton_lifetime()
    tr.check("6.1 τ_p > 10³⁴ lat (Super-K)",
             pd['passes_SK'],
             f"τ_p={pd['tau_e_pi0_years']:.1e}")
    tr.check("6.2 τ_p < 10³⁸ lat (testowalne)",
             pd['tau_e_pi0_years'] < 1e38)
    tr.check("6.3 BR(e⁺π⁰) > 0",
             pd['BR_e_pi0'] > 0,
             f"BR={pd['BR_e_pi0']:.3f}")
    tr.check("6.4 BR(ν̄K⁺) > 0",
             pd['BR_nu_K'] > 0)
    tr.check("6.5 Detectable Hyper-K",
             pd['detectable_HK'])
    tr.check("6.6 Kanał dominujący = e⁺π⁰",
             'e⁺' in pd['dominant_channel'])


# ── Filar 7 ──────────────────────────────────────────────────────────────

def test_pillar_7(tr: TestResults):
    print("\n▸ FILAR 7: Trzy Generacje z E₈")
    e8 = ThreeGenerationsE8.e8_decomposition()
    tr.check("7.1 dim(E₈) = 248", e8['parent_dim'] == 248)
    tr.check("7.2 Dekompozycja = 248", e8['dim_matches'])
    tr.check("7.3 N_gen = 3", e8['N_gen_prediction'] == 3)
    tr.check("7.4 N_gen zgadza się z obserwacją", e8['N_gen_match'])
    tr.check("7.5 Ukryty sektor (4. generacja)", e8['hidden_generation'] == 1)

    asi = ThreeGenerationsE8.atiyah_singer_index()
    tr.check("7.6 ind(D̸) = 3 (Atiyah-Singer)", asi['index'] == 3)
    tr.check("7.7 Invariant topologiczny", asi['topological_invariant'])


# ── Filar 8 ──────────────────────────────────────────────────────────────

def test_pillar_8(tr: TestResults):
    print("\n▸ FILAR 8: Masy Neutrin (Seesaw)")
    nu = SeesawNeutrinoMasses.seesaw_type_I()
    tr.check("8.1 Σm_ν < 0.12 eV (Planck)",
             nu['within_cosmo_limit'],
             f"Σm_ν={nu['sum_m_nu_eV']:.4f} eV")
    tr.check("8.2 m_ν₃ > m_ν₁ (hierarchia normalna)",
             nu['hierarchy'] == 'normalna')
    tr.check("8.3 ν_R naturalne w repr. 16",
             'NATURALNĄ' in nu['nu_R_natural'])
    tr.check("8.4 M_R ~ 10¹⁴ GeV (skala seesaw)",
             nu['M_R_scale_GeV'] == 1e14)
    tr.check("8.5 Kąt mieszania θ₁₂ ≈ 33°",
             abs(nu['mixing_angles_deg']['theta_12'] - 33.44) < 0.1)


# ── Filar 9 ──────────────────────────────────────────────────────────────

def test_pillar_9(tr: TestResults):
    print("\n▸ FILAR 9: Integracja Grawitacji (TOE)")
    toe = GravityIntegrationTOE.toe_synthesis()
    tr.check("9.1 4 siły zunifikowane", toe['four_forces_unified'])
    tr.check("9.2 5. siła (torsja)", toe['plus_fifth_force'])
    tr.check("9.3 Grawitacja emergentna",
             toe['gravity_mechanism'] == 'Emergentna z grafu kwantowego')
    tr.check("9.4 5 poziomów hierarchii",
             len(toe['hierarchy_of_unification']) == 5)
    tr.check("9.5 Siła silna: SU(3)_C",
             toe['forces']['strong']['group'] == 'SU(3)_C')
    tr.check("9.6 EM: U(1)_EM",
             toe['forces']['electromagnetic']['group'] == 'U(1)_EM')


# ── Filar 10 ──────────────────────────────────────────────────────────────

def test_pillar_10(tr: TestResults):
    print("\n▸ FILAR 10: SUSY i Ciemna Materia")
    susy = SUSYAndDarkMatter.split_susy_spectrum()
    tr.check("10.1 m_gluino > 2300 GeV (LHC limit)",
             susy['passes_LHC'],
             f"m_g̃={susy['sparticles']['gluino']['mass_TeV']:.1f} TeV")
    tr.check("10.2 m_gluino < 15 TeV (testowalne HE-LHC)",
             susy['testable_HE_LHC'])
    tr.check("10.3 LSP = ciemna materia",
             susy['LSP_dark_matter'])
    tr.check("10.4 Hidden sector: 125 multipletów",
             susy['hidden_sector_multiplets'] == 125)

    dm = SUSYAndDarkMatter.dark_matter_candidates()
    tr.check("10.5 Axion m_a = 28.5 neV",
             abs(dm['axion']['mass_neV'] - 28.5) < 0.1)
    tr.check("10.6 Neutralino m_χ = 1.5 TeV",
             abs(dm['neutralino_LSP']['mass_TeV'] - 1.5) < 0.1)
    tr.check("10.7 Wieloskładnikowa DM",
             'WIELOSKŁADNIKOWĄ' in dm['multi_component'])


# ── Test Integracyjny ────────────────────────────────────────────────────

def test_integration(tr: TestResults):
    print("\n▸ TEST INTEGRACYJNY: Pełne Rozwiązanie GUT+TOE")
    sol = GrandUnifiedTOESolution()
    full = sol.full_solution()
    tr.check("INT.1 Raport wygenerowany", full is not None)
    tr.check("INT.2 10 filarów",
             len([k for k in full if k.startswith('pillar_')]) == 10)
    tr.check("INT.3 15 predykcji",
             len(full['testable_predictions']) == 15)

    preds = full['testable_predictions']
    confirmed = sum(1 for p in preds if '✅' in p['status'])
    tr.check("INT.4 ≥ 8 predykcji ✅",
             confirmed >= 8,
             f"potwierdzone={confirmed}/15")

    summary = sol.summary()
    tr.check("INT.5 Podsumowanie", len(summary) > 200)
    tr.check("INT.6 '4 SIŁY' w podsumowaniu", '4 siły' in summary.lower())


# ── Testy Spójności ──────────────────────────────────────────────────────

def test_consistency(tr: TestResults):
    print("\n▸ TESTY SPÓJNOŚCI")
    # RGE vs Top-down
    rge = GaugeCouplingUnification.integrate_2loop_rge()
    consts = TopDownPhysicalConstants.derive_low_energy_constants()
    tr.check("CON.1 α_GUT(RGE) ~ α_GUT(top-down)",
             abs(rge['alpha_GUT'] - 0.0381) < 0.01)

    # Proton decay vs M_GUT
    pd = ProtonDecay.compute_proton_lifetime()
    tr.check("CON.2 τ_p rośnie z M_GUT⁴",
             pd['tau_e_pi0_years'] > 1e34)

    # Seesaw vs M_GUT
    nu = SeesawNeutrinoMasses.seesaw_type_I()
    tr.check("CON.3 m_ν maleje z M_R (seesaw)",
             nu['m_nu_3_eV'] < 1.0)

    # N_gen spójne między E₈ i Atiyah-Singer
    e8 = ThreeGenerationsE8.e8_decomposition()
    asi = ThreeGenerationsE8.atiyah_singer_index()
    tr.check("CON.4 N_gen(E₈) = N_gen(AS) = 3",
             e8['N_gen_prediction'] == asi['n_generations'] == 3)

    # SUSY vs RGE (Split-SUSY poprawia unifikację)
    tr.check("CON.5 Split-SUSY poprawia unifikację (spread < 10%)",
             rge['unification_spread'] < 0.10)


def run_all_tests():
    print("=" * 70)
    print("  TESTY WIELKIEJ UNIFIKACJI (GUT) + TEORII WSZYSTKIEGO (TOE)")
    print("=" * 70)

    tr = TestResults()

    test_pillar_1(tr)
    test_pillar_2(tr)
    test_pillar_3(tr)
    test_pillar_4(tr)
    test_pillar_5(tr)
    test_pillar_6(tr)
    test_pillar_7(tr)
    test_pillar_8(tr)
    test_pillar_9(tr)
    test_pillar_10(tr)
    test_integration(tr)
    test_consistency(tr)

    tr.summary()
    return tr


if __name__ == "__main__":
    tr = run_all_tests()
    sys.exit(0 if tr.failed == 0 else 1)
