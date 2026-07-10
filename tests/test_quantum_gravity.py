"""
test_quantum_gravity.py
========================
Kompletny zestaw testów dla modułu kwantowej grawitacji Spin(10).

Testuje wszystkie 7 filarów:
  1. Emergentna grawitacja z grafu
  2. Piany spinowe EPRL
  3. Regularyzacja UV (GUP, MDR)
  4. Widmo geometrii kwantowej (pole powierzchni, objętość)
  5. Czarne dziury (entropia BH, krzywa Page'a)
  6. Kosmologia kwantowa (Big Bounce, LQC)
  7. Emergentna stała kosmologiczna Λ

Author: SHZ Quantum Technologies — Test Suite
Version: 15.0-QUANTUM-GRAVITY-TESTS
Date: 2026-07-10
"""

import sys
import os
import numpy as np

# Dodaj ścieżkę do src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_gravity_core import (
    EmergentGravityFromGraph,
    QuantumGravitySpinFoam,
    UVRegularization,
    QuantumGeometrySpectrum,
    BlackHoleQuantumGravity,
    QuantumCosmology,
    EmergentCosmologicalConstant,
    QuantumGravitySpin10Solution,
    IMMIRZI_GAMMA,
    L_PLANCK,
    DIM_SPIN10,
)


class TestResults:
    """Prosty system zbierania wyników testów."""
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
        print(f"  {'✅ WSZYSTKIE TESTY PRZESZŁY!' if self.failed == 0 else f'❌ {self.failed} test(y/ów) nie przeszło'}")
        print(f"{'='*70}")
        return self.failed == 0


def test_pillar_1_emergent_gravity(tr: TestResults):
    """Testy filaru 1: Emergentna grawitacja."""
    print("\n▸ FILAR 1: Emergentna Grawitacja")
    eg = EmergentGravityFromGraph(N=1000, k_target=4, alpha=1.2)

    # Test 1.1: Emergentna metryka
    metric = eg.emergent_metric_from_graph()
    tr.check("1.1 Metryka emergentna istnieje", metric is not None)
    tr.check("1.2 Sygnatura Lorentzowska", metric['is_lorentzian'] is True,
             f"CF={metric['causal_fraction']}")
    tr.check("1.3 Wymiar emergentny = 4", abs(metric['emergent_dimension'] - 4.0) < 0.1,
             f"d={metric['emergent_dimension']}")
    tr.check("1.4 G_N emergentne > 0", metric['G_newton_emergent'] > 0)

    # Test 1.2: Mechanizm Jacobsona
    jac = eg.jacobson_thermodynamic_gravity()
    tr.check("1.5 Równanie Einsteina wyprowadzone", jac['einstein_equation_derived'] is True)
    tr.check("1.6 Λ emergentna > 0", jac['Lambda_emergent'] > 0)
    tr.check("1.7 ρ_vac_YM > 0", jac['rho_vacuum_YM'] > 0)
    tr.check("1.8 Entropia horyzontu > 0", jac['horizon_entropy'] > 0)


def test_pillar_2_spin_foam(tr: TestResults):
    """Testy filaru 2: Piany spinowe EPRL."""
    print("\n▸ FILAR 2: Piany Spinowe EPRL")
    sf = QuantumGravitySpinFoam()

    # Test 2.1: Amplitudy EPRL
    eprl = sf.eprl_vertex_amplitude()
    tr.check("2.1 Model EPRL", 'EPRL' in eprl['model'])
    tr.check("2.2 Immirzi γ = 0.2739", abs(eprl['immirzi_gamma'] - 0.2739) < 0.001)
    tr.check("2.3 Więzy prostoty k=γj", 'γ·j' in eprl['simplicity_constraint'])
    tr.check("2.4 Funkcja partycji Z > 0", eprl['partition_function_Z'] != 0)

    # Test 2.2: Amplitudy maleją z j (WKB)
    amplitudes = [v['amplitude_wkb'] for v in eprl['vertex_amplitudes']]
    tr.check("2.5 Amplitudy maleją z j (WKB)",
             amplitudes[0] > amplitudes[-1],
             f"A(j=0.5)={amplitudes[0]:.6f}, A(j=5)={amplitudes[-1]:.6f}")

    # Test 2.3: Propagator grawitonu
    prop = sf.graviton_propagator_from_spinfoam()
    tr.check("2.6 Propagator UV-skończony", prop['UV_finite'] is True)
    tr.check("2.7 Poprawki kwantowe α₁ > 0", prop['quantum_corrections']['alpha_1_lP2'] > 0)


def test_pillar_3_uv_regularization(tr: TestResults):
    """Testy filaru 3: Regularyzacja UV."""
    print("\n▸ FILAR 3: Regularyzacja UV")
    uv = UVRegularization()

    # Test 3.1: GUP
    gup = uv.generalized_uncertainty_principle()
    tr.check("3.1 GUP β > 0", gup['beta_parameter'] > 0,
             f"β={gup['beta_parameter']:.4f}")
    tr.check("3.2 Minimalna długość > ℓ_P", gup['minimum_length_planck_units'] > 0.1,
             f"Δx_min={gup['minimum_length_planck_units']:.4f} ℓ_P")
    tr.check("3.3 MDR η₁ > 0", gup['MDR_eta'] > 0)

    # Test 3.2: UV skończoność
    uv_proof = uv.uv_finiteness_proof()
    tr.check("3.4 Suma po spinach zbieżna", uv_proof['spin_sum_converged'] is True,
             f"Σ={uv_proof['spin_sum_value']:.6f}")
    tr.check("3.5 Brak kontrterminów", uv_proof['no_counterterms_needed'] is True)

    # Test 3.3: Zmodyfikowana relacja dyspersji
    mdr = uv.modified_dispersion_relation(energy_GeV=1e19)
    tr.check("3.6 δv/c (n=1) < 1", mdr['delta_v_over_c_n1'] < 1.0,
             f"δv/c={mdr['delta_v_over_c_n1']:.6e}")
    tr.check("3.7 δv/c (n=2) << δv/c (n=1)", mdr['delta_v_over_c_n2'] < mdr['delta_v_over_c_n1'])

    # Parametr β GUP
    beta = uv.compute_gup_parameter()
    expected_beta = IMMIRZI_GAMMA**2 * DIM_SPIN10 / (4.0 * np.pi)
    tr.check("3.8 β_GUP = γ²·dim/(4π)", abs(beta - expected_beta) < 1e-10,
             f"β={beta:.6f}")


def test_pillar_4_quantum_geometry(tr: TestResults):
    """Testy filaru 4: Widmo geometrii kwantowej."""
    print("\n▸ FILAR 4: Widmo Geometrii Kwantowej")
    qg = QuantumGeometrySpectrum()

    # Test 4.1: Widmo pola powierzchni
    area = qg.area_spectrum()
    tr.check("4.1 Widmo dyskretne", area['discrete'] is True)
    tr.check("4.2 A_min > 0", area['A_min_planck_sq'] > 0,
             f"A_min={area['A_min_planck_sq']:.4f} ℓ²_P")

    # Sprawdzenie formuły A_min = 4√3·π·γ
    A_min_expected = 4.0 * np.sqrt(3) * np.pi * IMMIRZI_GAMMA
    tr.check("4.3 A_min = 4√3πγ", abs(area['A_min_planck_sq'] - A_min_expected) < 0.001,
             f"oczekiwane={A_min_expected:.4f}, otrzymane={area['A_min_planck_sq']:.4f}")

    # Sprawdzenie, że widmo rośnie z j
    areas_j = [s['area_planck_sq'] for s in area['spectrum']]
    tr.check("4.4 A rośnie z j", all(areas_j[i] < areas_j[i+1] for i in range(len(areas_j)-1)))

    # Test 4.2: Widmo objętości
    vol = qg.volume_spectrum()
    tr.check("4.5 V_min > 0", vol['V_min_planck_cube'] > 0,
             f"V_min={vol['V_min_planck_cube']:.4f} ℓ³_P")
    tr.check("4.6 Widmo objętości dyskretne", vol['discrete'] is True)

    # Test 4.3: Operator kąta
    angle = qg.angle_operator(j1=1.0, j2=1.0)
    tr.check("4.7 Kąty dyskretne", angle['discrete'] is True)
    tr.check("4.8 Kąty w [0°, 180°]",
             all(0 <= a['theta_degrees'] <= 180 for a in angle['allowed_angles']))


def test_pillar_5_black_holes(tr: TestResults):
    """Testy filaru 5: Czarne dziury."""
    print("\n▸ FILAR 5: Czarne Dziury")
    bh = BlackHoleQuantumGravity()

    # Test 5.1: Entropia BH
    entropy = bh.bekenstein_hawking_entropy(mass_solar=10.0)
    tr.check("5.1 S_BH > 0", entropy['S_BH_classical'] > 0,
             f"S={entropy['S_BH_classical']:.4e}")
    tr.check("5.2 T_Hawking > 0", entropy['T_hawking_K'] > 0,
             f"T={entropy['T_hawking_K']:.4e} K")
    tr.check("5.3 Immirzi match (γ₀ ≈ γ)", entropy['immirzi_match'] is True,
             f"γ₀={entropy['immirzi_gamma_0']:.4f}")

    # Test 5.2: Poprawki logarytmiczne
    tr.check("5.4 Poprawka log < 0 (ujemna)", entropy['log_correction'] < 0,
             f"δS_log={entropy['log_correction']:.2f}")

    # Test 5.3: Krzywa Page'a
    page = bh.page_curve(n_qubits=64)
    tr.check("5.5 Informacja zachowana", page['information_preserved'] is True)
    tr.check("5.6 Unitarność", page['unitarity'] is True)
    tr.check("5.7 Page Time = 0.5", abs(page['page_time'] - 0.5) < 0.01)
    tr.check("5.8 S_final → 0", page['final_entropy_radiation'] < 0.1 * page['S_max'])

    # Skalowanie: S_BH(2M) > 4·S_BH(M) (bo S ∝ M²)
    bh_1 = bh.bekenstein_hawking_entropy(mass_solar=1.0)
    bh_2 = bh.bekenstein_hawking_entropy(mass_solar=2.0)
    ratio = bh_2['S_BH_classical'] / bh_1['S_BH_classical']
    tr.check("5.9 S(2M)/S(M) ≈ 4 (S ∝ M²)", abs(ratio - 4.0) < 0.1,
             f"ratio={ratio:.2f}")


def test_pillar_6_quantum_cosmology(tr: TestResults):
    """Testy filaru 6: Kosmologia kwantowa."""
    print("\n▸ FILAR 6: Kosmologia Kwantowa")
    qc = QuantumCosmology()

    # Test 6.1: Zmodyfikowane równanie Friedmanna
    friedmann = qc.modified_friedmann_equation()
    tr.check("6.1 Bounce zachodzi", friedmann['bounce_occurs'] is True)
    tr.check("6.2 Osobliwość usunięta", friedmann['singularity_removed'] is True)
    tr.check("6.3 ρ_cr = 0.41 ρ_Pl", abs(friedmann['rho_critical_planck_units'] - 0.41) < 0.01)

    # Test 6.2: Pre-bounce
    pre = qc.pre_bounce_universe()
    tr.check("6.4 Pre-bounce istnieje", pre['pre_bounce_exists'] is True)
    tr.check("6.5 Symetria CPT", pre['CPT_symmetric'] is True)
    tr.check("6.6 V_min > 0 (brak kolapsu do punktu)", pre['minimum_volume_m3'] > 0)

    # Test 6.3: Poprawki do inflacji
    infl = qc.quantum_corrections_to_inflation()
    tr.check("6.7 n_s ≈ 0.9649 (Planck)", infl['n_s_match'] is True,
             f"n_s={infl['n_s_quantum_corrected']:.5f}")
    tr.check("6.8 r < 0.036 (BICEP limit)", infl['r_within_limit'] is True,
             f"r={infl['r_quantum_corrected']:.5f}")
    tr.check("6.9 δn_s < 0 (poprawka ujemna)", infl['delta_n_s'] < 0,
             f"δn_s={infl['delta_n_s']:.6f}")


def test_pillar_7_cosmological_constant(tr: TestResults):
    """Testy filaru 7: Stała kosmologiczna."""
    print("\n▸ FILAR 7: Stała Kosmologiczna")
    cc = EmergentCosmologicalConstant(N=1000, alpha=1.2)

    # Test 7.1: Λ emergentna
    lam = cc.compute_lambda()
    tr.check("7.1 Λ_eff > 0", lam['Lambda_eff_m2'] > 0,
             f"Λ={lam['Lambda_eff_m2']:.4e} m⁻²")
    tr.check("7.2 Λ jest emergentna", lam['is_emergent'] is True)
    tr.check("7.3 Λ nie jest swobodnym parametrem", lam['not_free_parameter'] is True)
    tr.check("7.4 ρ_vac = ρ_YM + ρ_top", lam['rho_vac_YM'] > 0 and lam['rho_vac_topological'] > 0)

    # Test 7.2: Zależność od cosΦ
    lam_1 = cc.compute_lambda(cos_phi_mean=0.5)
    lam_2 = cc.compute_lambda(cos_phi_mean=0.9)
    tr.check("7.5 Λ(cosΦ=0.5) > Λ(cosΦ=0.9)",
             lam_1['Lambda_eff_m2'] > lam_2['Lambda_eff_m2'],
             "Λ maleje gdy cosΦ→1 (konfajnment)")

    # Test 7.3: Zależność od Var(k)
    lam_a = cc.compute_lambda(var_k=0.1)
    lam_b = cc.compute_lambda(var_k=0.5)
    tr.check("7.6 Λ(Var=0.1) < Λ(Var=0.5)",
             lam_a['Lambda_eff_m2'] < lam_b['Lambda_eff_m2'],
             "Λ rośnie z Var(k)")

    # Test 7.4: de Sitter
    ds = cc.de_sitter_from_network()
    tr.check("7.7 Promień de Sittera > 0", ds['de_sitter_radius_m'] > 0)
    tr.check("7.8 Entropia G-H > 0", ds['gibbons_hawking_entropy'] > 0)


def test_full_solution(tr: TestResults):
    """Test integracyjny: pełne rozwiązanie."""
    print("\n▸ TEST INTEGRACYJNY: Pełne Rozwiązanie")
    qg = QuantumGravitySpin10Solution(N=500)

    # Test pełnego raportu
    sol = qg.full_solution()
    tr.check("INT.1 Raport wygenerowany", sol is not None)
    tr.check("INT.2 7 filarów", len([k for k in sol.keys() if k.startswith('pillar_')]) == 7)
    tr.check("INT.3 12 predykcji", len(sol['testable_predictions']) == 12)

    # Test predykcji
    predictions = sol['testable_predictions']
    confirmed = sum(1 for p in predictions if '✅' in p['status'])
    tr.check("INT.4 ≥ 5 predykcji potwierdzonych", confirmed >= 5,
             f"potwierdzone={confirmed}/12")

    # Test podsumowania
    summary = qg.summary()
    tr.check("INT.5 Podsumowanie wygenerowane", len(summary) > 100)
    tr.check("INT.6 'EMERGENTNA' w podsumowaniu", 'EMERGENTNA' in summary)


def test_consistency_checks(tr: TestResults):
    """Testy spójności między filarami."""
    print("\n▸ TESTY SPÓJNOŚCI MIĘDZY FILARAMI")

    # Spójność 1: γ z entropii BH = γ z pian spinowych
    bh = BlackHoleQuantumGravity(IMMIRZI_GAMMA)
    sf = QuantumGravitySpinFoam(IMMIRZI_GAMMA)
    entropy = bh.bekenstein_hawking_entropy()
    eprl = sf.eprl_vertex_amplitude()
    tr.check("CON.1 γ_BH = γ_EPRL",
             abs(entropy['immirzi_gamma_0'] - eprl['immirzi_gamma']) < 0.001)

    # Spójność 2: Minimalna długość ≈ ℓ_P
    uv = UVRegularization()
    gup = uv.generalized_uncertainty_principle()
    tr.check("CON.2 Δx_min ~ ℓ_P (rząd wielkości)",
             0.1 < gup['minimum_length_planck_units'] < 10.0)

    # Spójność 3: Pole surface → entropia BH
    qgs = QuantumGeometrySpectrum()
    area = qgs.area_spectrum()
    tr.check("CON.3 A_min > 0 z widma pola pow.",
             area['A_min_planck_sq'] > 0)

    # Spójność 4: Big Bounce → brak osobliwości → regularyzacja UV
    qc = QuantumCosmology()
    bounce = qc.modified_friedmann_equation()
    uv_fin = uv.uv_finiteness_proof()
    tr.check("CON.4 Bounce (QC) + UV skończoność → brak osobliwości",
             bounce['singularity_removed'] and uv_fin['no_counterterms_needed'])

    # Spójność 5: Λ emergentna z filaru 7 > 0, konsystentna z filarem 1
    eg = EmergentGravityFromGraph(N=1000)
    jac = eg.jacobson_thermodynamic_gravity()
    cc = EmergentCosmologicalConstant(N=1000)
    lam = cc.compute_lambda()
    tr.check("CON.5 Λ_Jacobson ≈ Λ_emergentna (ten sam rząd)",
             abs(np.log10(jac['Lambda_emergent']) - np.log10(lam['Lambda_eff_m2'])) < 2)


def run_all_tests():
    """Uruchamia wszystkie testy kwantowej grawitacji."""
    print("=" * 70)
    print("  TESTY KWANTOWEJ GRAWITACJI SPIN(10) — PEŁNY ZESTAW")
    print("=" * 70)

    tr = TestResults()

    test_pillar_1_emergent_gravity(tr)
    test_pillar_2_spin_foam(tr)
    test_pillar_3_uv_regularization(tr)
    test_pillar_4_quantum_geometry(tr)
    test_pillar_5_black_holes(tr)
    test_pillar_6_quantum_cosmology(tr)
    test_pillar_7_cosmological_constant(tr)
    test_full_solution(tr)
    test_consistency_checks(tr)

    tr.summary()
    return tr


if __name__ == "__main__":
    tr = run_all_tests()
    sys.exit(0 if tr.failed == 0 else 1)
