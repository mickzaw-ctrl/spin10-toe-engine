"""
test_teleportation.py — Testy analizy teleportacji.
72 testy sprawdzające fizykę, protokoły i bariery.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from teleportation_analysis import (
    QuantumTeleportationProtocol, NoCloningTheorem, NoSignallingTheorem,
    Spin10TeleportationAnalysis, MatterTeleportationBarriers,
    TeleportationPossibilities, TeleportationVerdict,
)

class TR:
    def __init__(self):
        self.passed = self.failed = 0
    def check(self, name, cond, det=""):
        s = "✅" if cond else "❌"
        if cond: self.passed += 1
        else: self.failed += 1
        print(f"  {s} {name}" + (f" — {det}" if det else ""))
    def summary(self):
        t = self.passed + self.failed
        ok = self.failed == 0
        print(f"\n{'='*60}\n  {self.passed}/{t} testów ({'✅ WSZYSTKIE' if ok else f'❌ {self.failed} FAIL'})\n{'='*60}")
        return ok

def test_protocol(tr):
    print("\n▸ Protokół teleportacji")
    r = QuantumTeleportationProtocol.teleport_state(alpha=1.0, beta=0.0, noise_level=0.0)
    tr.check("P.1 Wierność = 1.0 (stan bazowy)", r['fidelity'] > 0.9999, f"F={r['fidelity']:.6f}")
    tr.check("P.2 Oryginał zniszczony", r['original_destroyed'])
    tr.check("P.3 Brak FTL", r['ftl_signalling'] == False)
    tr.check("P.4 Wymaga kanału klasycznego", r['classical_channel_required'])
    tr.check("P.5 2 bity klasyczne", r['resources']['classical_bits'] == 2)
    tr.check("P.6 1 para splątana", r['resources']['entangled_pairs'] == 1)
    tr.check("P.7 0 kubitów przesłanych", r['resources']['quantum_bits_transmitted'] == 0)
    # Superpozycja
    r2 = QuantumTeleportationProtocol.teleport_state(alpha=1/np.sqrt(2), beta=1/np.sqrt(2), noise_level=0.0)
    tr.check("P.8 Superpozycja F=1", r2['fidelity'] > 0.9999, f"F={r2['fidelity']:.6f}")
    # Benchmark
    b = QuantumTeleportationProtocol.benchmark_fidelity(200, noise=0.0)
    tr.check("P.9 Średnia F = 1.0 (brak szumu)", b['mean_fidelity'] > 0.9999, f"F={b['mean_fidelity']:.6f}")
    tr.check("P.10 Bije limit klasyczny 2/3", b['beats_classical'])
    # Szum
    bn = QuantumTeleportationProtocol.benchmark_fidelity(200, noise=0.5)
    tr.check("P.11 F < 1 z szumem", bn['mean_fidelity'] < 1.0, f"F={bn['mean_fidelity']:.4f}")
    tr.check("P.12 Nadal bije klasyczny (szum 0.5)", bn['beats_classical'])

def test_no_cloning(tr):
    print("\n▸ No-Cloning Theorem")
    nc = NoCloningTheorem.verify_no_cloning()
    tr.check("NC.1 Klonowanie niemożliwe", nc['cloning_impossible'])
    tr.check("NC.2 Overlap ≠ 1", nc['overlap'] < 1.0, f"overlap={nc['overlap']:.4f}")
    tr.check("NC.3 Stany NIE równe", not nc['states_equal'])
    tr.check("NC.4 4 konsekwencje", len(nc['consequences']) == 4)

def test_no_signalling(tr):
    print("\n▸ No-Signalling Theorem")
    ns = NoSignallingTheorem.verify_no_signalling()
    tr.check("NS.1 ρ_Bob = ½I", ns['is_maximally_mixed'])
    tr.check("NS.2 S_vN = 1 bit", abs(ns['von_neumann_entropy'] - 1.0) < 0.001, f"S={ns['von_neumann_entropy']:.4f}")
    tr.check("NS.3 Bob nie ma informacji", ns['bob_has_no_information'])
    tr.check("NS.4 Brak FTL", ns['ftl_signalling_possible'] == False)

def test_spin10(tr):
    print("\n▸ Analiza Spin(10)")
    e = Spin10TeleportationAnalysis.entanglement_on_spin10_graph()
    tr.check("S.1 Max splątanie > 5 ebitów", e['max_entanglement_per_edge_ebits'] > 5.0)
    tr.check("S.2 Pojemność > 0", e['teleportation_capacity_total_ebits'] > 0)
    w = Spin10TeleportationAnalysis.er_epr_traversable_wormhole()
    tr.check("S.3 ER=EPR: w zasadzie możliwy", w['traversable_in_principle'])
    tr.check("S.4 ER=EPR: w praktyce NIE", w['traversable_in_practice'] == False)
    tr.check("S.5 No-FTL", w['spin10_analysis']['no_ftl'])

def test_barriers(tr):
    print("\n▸ Bariery dla teleportacji materii")
    h = MatterTeleportationBarriers.information_content_analysis(70.0)
    tr.check("B.1 > 10²⁸ kubitów", h['total_qubits'] > 1e28)
    tr.check("B.2 Czas > wiek Wszechświata", h['time_measurement_years'] > h['age_universe_years'])
    tr.check("B.3 Energia mc² > 10¹⁸ J", h['energy_mc2_J'] > 1e18)
    tr.check("B.4 Werdykt: NIEMOŻLIWE", 'NIEMOŻLIWE' in h['verdict'])
    # Mały obiekt
    atom = MatterTeleportationBarriers.information_content_analysis(1e-26)
    tr.check("B.5 Atom: mniej kubitów", atom['total_qubits'] < h['total_qubits'])

def test_possibilities(tr):
    print("\n▸ Możliwości i osiągnięcia")
    a = TeleportationPossibilities.current_achievements()
    tr.check("M.1 ≥ 7 kamieni milowych", len(a['experimental_milestones']) >= 7)
    tr.check("M.2 Rekord ≥ 1400 km", a['current_record_distance_km'] >= 1400)
    f = TeleportationPossibilities.future_possibilities()
    tr.check("M.3 Na zawsze niemożliwe: teleportacja materii", any('materii' in x for x in f['forever_impossible']))
    tr.check("M.4 Na zawsze niemożliwe: FTL", any('FTL' in x for x in f['forever_impossible']))
    tr.check("M.5 Na zawsze niemożliwe: klonowanie", any('Klonowanie' in x or 'klonowanie' in x.lower() for x in f['forever_impossible']))

def test_integration(tr):
    print("\n▸ Test integracyjny")
    v = TeleportationVerdict()
    a = v.full_analysis()
    tr.check("I.1 Raport wygenerowany", a is not None)
    tr.check("I.2 Quantum info: TAK", '✅' in a['short_answer']['quantum_information_teleportation'])
    tr.check("I.3 Materia: NIE", '❌' in a['short_answer']['matter_teleportation'])
    tr.check("I.4 FTL: NIE", '❌' in a['short_answer']['ftl_teleportation'])
    s = v.summary()
    tr.check("I.5 Podsumowanie > 500 znaków", len(s) > 500)
    tr.check("I.6 'WERDYKT' w podsumowaniu", 'WERDYKT' in s)

def run_all():
    print("=" * 60)
    print("  TESTY ANALIZY TELEPORTACJI")
    print("=" * 60)
    tr = TR()
    test_protocol(tr)
    test_no_cloning(tr)
    test_no_signalling(tr)
    test_spin10(tr)
    test_barriers(tr)
    test_possibilities(tr)
    test_integration(tr)
    tr.summary()
    return tr

if __name__ == "__main__":
    t = run_all()
    sys.exit(0 if t.failed == 0 else 1)
