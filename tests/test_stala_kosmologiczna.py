# -*- coding: utf-8 -*-
"""
Kontrakty naukowe dla modułu problemu stałej kosmologicznej
(src/stala_kosmologiczna.py).

Testy pilnują trzech rzeczy:
  1. poprawności fizycznej liczb (wartości obserwowane, rzędy wielkości),
  2. rozdzielczości wniosków (co jest zmierzone / policzone / zhipotetyzowane),
  3. integralności raportowania — moduł NIE WOLNO przekroczyć werdyktu:
     problem nie jest rozwiązany (status LOCALIZED_OPEN, nigdy SOLVED).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import sys

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import stala_kosmologiczna as sk  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class WartosciObserwowaneTests(unittest.TestCase):
    """Stałe kosmologiczne zgadzają się z literaturą."""

    @classmethod
    def setUpClass(cls):
        cls.obs = sk.lambda_obserwowana()

    def test_rho_lambda_jest_meV4(self):
        # (2.24 meV)^4 z H0=67.4, Omega_L=0.6847; literatura: ~2.2-2.5 meV
        self.assertGreater(self.obs["rho_Lambda_quarter_meV"], 2.0)
        self.assertLess(self.obs["rho_Lambda_quarter_meV"], 2.6)

    def test_lambda_w_m2(self):
        # Λ = 1.09e-52 m^-2 (Planck 2018: 1.1056e-52 przy H0=67.66)
        self.assertGreater(self.obs["Lambda_m_inv2"], 0.9e-52)
        self.assertLess(self.obs["Lambda_m_inv2"], 1.3e-52)

    def test_lambda_w_jednostkach_plancka(self):
        self.assertGreater(self.obs["Lambda_planck"], 2.0e-122)
        self.assertLess(self.obs["Lambda_planck"], 4.0e-122)


class ProblemStandardowyTests(unittest.TestCase):
    """Klasyczna rozbieżność ~10^120 jest odtworzona."""

    @classmethod
    def setUpClass(cls):
        cls.tab = sk.tabela_problem_standardowy()

    def test_monotonicznosc_z_odcieciem(self):
        kappa = [t["kappa_GeV"] for t in self.tab]
        D = [t["log10_rozbieznosc"] for t in self.tab]
        self.assertEqual(kappa, sorted(kappa))
        self.assertEqual(D, sorted(D))

    def test_skala_plancka_ok_120_rzedow(self):
        planck = self.tab[-1]
        self.assertIn("Planck", planck["odciecie"])
        self.assertGreater(planck["log10_rozbieznosc"], 115.0)
        self.assertLess(planck["log10_rozbieznosc"], 125.0)

    def test_skala_ew_ok_54_rzedy(self):
        ew = [t for t in self.tab if "elektrosłaba" in t["odciecie"]][0]
        self.assertGreater(ew["log10_rozbieznosc"], 50.0)
        self.assertLess(ew["log10_rozbieznosc"], 60.0)

    def test_susu_pozostawia_ok_56_rzedow(self):
        susy = sk.rozbieznosc_po_susy(1.0e3)
        self.assertGreater(susy["log10_rozbieznosc"], 50.0)
        self.assertLess(susy["log10_rozbieznosc"], 62.0)


class ModelGrafowyTests(unittest.TestCase):
    """Formuła z docs/cosmological-constant.md odtworzona i zmierzona."""

    @classmethod
    def setUpClass(cls):
        cls.lam = sk.lambda_graf()
        cls.obs = sk.lambda_obserwowana()

    def test_stala_newtona_graf(self):
        import math
        self.assertAlmostEqual(self.lam["G_N_lat"], 3.0 / (2.0 * math.pi * 150.0))

    def test_epsilon_vac_z_raportu(self):
        # (3/4)(1-0.688) + 0.262 = 0.234 + 0.262
        self.assertAlmostEqual(self.lam["eps_vac"], 0.496, places=6)

    def test_lambda_planckowskiego_rzedu(self):
        # model daje Λ ~ O(10^-2) M_Pl^2 — odziedziczył pełny problem
        self.assertGreater(self.lam["Lambda_planck"], 1.0e-3)
        self.assertLess(self.lam["Lambda_planck"], 10.0)

    def test_luka_pozostaje_ok_120(self):
        luka = sk.luka_modelu(self.lam, self.obs)
        self.assertGreater(luka["log10_luka"], 115.0)
        self.assertLess(luka["log10_luka"], 125.0)

    def test_granica_kondensacji_zeruje_lambda(self):
        # cosΦ→1 i Var(k)→0 => Λ→0 (fizyczna jawność formuły)
        lam0 = sk.lambda_graf(cos_phi=1.0, var_k=0.0)
        self.assertEqual(lam0["Lambda_lat_a2"], 0.0)


class KanalyTlumieniaTests(unittest.TestCase):
    """Kanały z dokumentacji pilnowane: nie wolno im „zamknąć" problemu."""

    @classmethod
    def setUpClass(cls):
        cls.k5 = sk.kanaly_tlumienia()
        cls.k45 = sk.kanaly_tlumienia(uzyj_dim_zamiast_rank=True)

    def test_tlumienie_laczne_mniejsze_niz_3_rzedy(self):
        self.assertLess(self.k5["log10_tlumienie"], 3.0)
        self.assertLess(self.k45["log10_tlumienie"], 3.0)

    def test_luka_po_kanalach_pozostaje(self):
        self.assertGreater(self.k5["log10_luka_po_kanalach"], 100.0)
        self.assertGreater(self.k45["log10_luka_po_kanalach"], 100.0)

    def test_kanaly_oznaczone_niewystarczajace(self):
        self.assertFalse(self.k5["wystarczajace"])
        self.assertFalse(self.k45["wystarczajace"])

    def test_kazdy_kanal_ma_klasyfikacje_hipotezy(self):
        for kanal in self.k5["kanaly"]:
            self.assertIn("hipoteza", kanal["klasyfikacja"])


class ProblemOdwrotnyTests(unittest.TestCase):
    """Rozwiązanie odwrotne: wielkość wymaganego stłumienia."""

    @classmethod
    def setUpClass(cls):
        cls.inv = sk.wymagana_dekondensacja()
        cls.obs = sk.lambda_obserwowana()

    def test_x_req_rzedu_1e_m121(self):
        self.assertGreater(self.inv["x_req"], 1.0e-122)
        self.assertLess(self.inv["x_req"], 1.0e-119)

    def test_cos_phi_zbiega_do_1_ponizej_eps_maschyny(self):
        # x_req ≈ 5e-121 < eps float64 ⇒ 1 − x_req jest w zmiennoprzecinku
        # DOKŁADNIE równe 1 (skala fine-tuningu poniżej precyzji maszyny!)
        self.assertEqual(self.inv["cos_phi_req"], 1.0)
        self.assertLess(self.inv["x_req"], 1.0e-100)

    def test_fine_tuning_ok_120_rzedow(self):
        self.assertGreater(self.inv["log10_finetuning"], 115.0)
        self.assertLess(self.inv["log10_finetuning"], 125.0)

    def test_spojnosc_z_formula(self):
        # podstawienie x_req do formuły grafowej musi dać Λ_obs;
        # x_req przekazujemy bezpośrednio (1 − x_req nie ma reprezentacji
        # w float64 — por. test powyżej)
        import math
        G = sk.stala_newtona_graf(sk.N_GRAF_RAPORT)
        Lam = 8.0 * math.pi * G * (3.0 / (4.0 * sk.G2_YM_RAPORT)) * self.inv["x_req"]
        self.assertAlmostEqual(
            Lam / self.obs["Lambda_planck"], 1.0, places=9)


class TrasaTermicznaTests(unittest.TestCase):
    """Pomiar MC wykładnika q vs wymagany p (szybka wersja do testów)."""

    @classmethod
    def setUpClass(cls):
        mc = sk.MonteCarloWakuum(N=60, k_target=4, seed=42)
        cls.skan = mc.skan_beta([1.0, 4.0, 16.0], burn_sweeps=120,
                                meas_sweeps=120, seed=0)
        cls.fit = sk.fit_potega_xeq(cls.skan)
        cls.term = sk.trasa_termiczna(cls.fit)

    def test_x_eq_maleje_z_beta(self):
        xs = [s["x_eq"] for s in self.skan]
        self.assertEqual(xs, sorted(xs, reverse=True))

    def test_q_bliskie_harmonicznemu(self):
        # przewidywanie harmoniczne q=1; tolerancja na tryby wolne/ziarna
        self.assertGreater(self.fit["q"], 0.4)
        self.assertLess(self.fit["q"], 1.6)

    def test_q_daleko_ponizej_wymaganego(self):
        self.assertGreater(self.term["p_wymagany"], 3.4)
        self.assertLess(self.term["p_wymagany"], 4.2)
        self.assertGreater(self.term["p_wymagany"], self.fit["q"] + 2.0)

    def test_trasa_wykluczona(self):
        self.assertEqual(self.term["werdykt"], "WYKLUCZONA")
        self.assertGreater(self.term["log10_luka"], 50.0)


class DynamikaSzklistaTests(unittest.TestCase):
    """Floor frustracyjny trajektorii relaksacji."""

    @classmethod
    def setUpClass(cls):
        mc = sk.MonteCarloWakuum(N=60, k_target=4, seed=42)
        cls.traj = mc.relaksacja(beta=64.0, n_sweeps=250, meas_every=5, seed=0)
        cls.inv = sk.wymagana_dekondensacja()

    def test_x_schodzi_od_goracego_startu(self):
        x = self.traj["x"]
        self.assertLess(x[-1], x[0])

    def test_podloge_daleko_powyzej_x_req(self):
        import numpy as np
        podloge = float(np.mean(self.traj["x"][-10:]))
        self.assertGreater(podloge, 1.0e-4)          # nie schodzi do zera
        self.assertLess(podloge, 1.0e0)
        import math
        self.assertGreater(math.log10(podloge / self.inv["x_req"]), 50.0)


class ScenariuszKrytycznyTests(unittest.TestCase):
    """Tracker x ∝ t^-2: konflikt z BBN musi być wykryty."""

    @classmethod
    def setUpClass(cls):
        cls.kryt = sk.scenariusz_krytyczny()

    def test_c_req_niefizyczne(self):
        self.assertGreater(self.kryt["C_req_dla_Lambda_obs"], 1.0)

    def test_bbn_wyklucza(self):
        self.assertGreater(self.kryt["r_BBN_przy_Lambda_obs"],
                           self.kryt["r_BBN_max"])
        self.assertIn("BBN", self.kryt["werdykt"])
        self.assertIn("WYKLUCZONY", self.kryt["werdykt"])

    def test_przekroczenie_o_ponad_2_rzedy(self):
        import math
        ex = math.log10(self.kryt["r_BBN_przy_Lambda_obs"] / self.kryt["r_BBN_max"])
        self.assertGreater(ex, 2.0)


class ScenariuszFreezeTests(unittest.TestCase):
    def test_freeze_przy_x_req_po_bbn(self):
        inv = sk.wymagana_dekondensacja()
        fz = sk.scenariusz_freeze(x_floor=inv["x_req"])
        self.assertFalse(fz["czas_do_bbn_ok"])
        self.assertIn("SFALSZYFICOWANA", fz["werdykt"])


class InstantonTests(unittest.TestCase):
    def test_alpha_eff_w_sensownym_zakresie(self):
        ins = sk.warunek_instantonowy()
        self.assertGreater(ins["alpha_eff_wymagane"], 0.015)
        self.assertLess(ins["alpha_eff_wymagane"], 0.035)
        self.assertGreater(ins["S_inst_wymagane"], 200.0)
        self.assertIn("PERSPEKTYWA", ins["klasyfikacja"])


class WerdyktTests(unittest.TestCase):
    """Integralność raportowania: werdykt nigdy nie przesadza."""

    @classmethod
    def setUpClass(cls):
        cls.raport = sk.pelny_audyt_statyczny()

    def test_status_localized_open(self):
        self.assertEqual(self.raport["werdykt"]["status"], sk.STATUS_LOCALIZED_OPEN)

    def test_nigdy_solved(self):
        self.assertNotEqual(self.raport["werdykt"]["status"], sk.STATUS_SOLVED)
        tresc = json.dumps(self.raport, ensure_ascii=False, default=str)
        self.assertNotIn('"SOLVED"', tresc)

    def test_podsumowanie_uczciwe(self):
        self.assertTrue(
            self.raport["werdykt"]["podsumowanie"].startswith(
                "Problem stałej kosmologicznej NIE jest rozwiązany"))

    def test_raport_jest_json_serializowalny(self):
        json.dumps(sk.pelny_audyt_statyczny(), ensure_ascii=False, default=str)


class LedgerTests(unittest.TestCase):
    """Rejestr założeń istnieje i ma wymagane pola."""

    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "docs" / "LEDGER_STALA_KOSMOLOGICZNA.json"
        cls.ledger = json.loads(cls.path.read_text())

    def test_struktura(self):
        self.assertIn("entries", self.ledger)
        self.assertEqual(self.ledger["status"], "OPEN_RESEARCH_PROTOTYPE")

    def test_minimalna_liczba_wpisow(self):
        self.assertGreaterEqual(len(self.ledger["entries"]), 8)

    def test_klasyfikacje_obecne(self):
        klasy = {e["classification"] for e in self.ledger["entries"]}
        self.assertIn("established_physics", klasy)
        self.assertIn("project_hypothesis", klasy)
        self.assertIn("falsified_route", klasy)

    def test_kazdy_wpis_ma_pola(self):
        for e in self.ledger["entries"]:
            for pole in ("id", "classification", "statement", "impact",
                         "confidence", "provenance"):
                self.assertIn(pole, e, f"brak pola {pole} w {e.get('id')}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
