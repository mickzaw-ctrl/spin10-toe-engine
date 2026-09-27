# -*- coding: utf-8 -*-
"""
Kontrakty naukowe dla konfrontacji sektora Λ z danymi
(src/konfrontacja_kosmologiczna.py).

Pilnuje:
  1. integralności zamrożonej tabeli danych (źródła arXiv przy każdym wpisie),
  2. poprawności werdyktów (scenariusze kinematyczne/trackery → EXCLUDED,
     podłoga → AGREE ale tuned-to-data),
  3. uczciwości raportowania (żaden scenariusz "computed" nie jest w pełni
     zgodny z danymi; w0wa-hint raportowany wyłącznie jako TENSION-CONTEXT).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import sys

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import stala_kosmologiczna as sk           # noqa: E402
import konfrontacja_kosmologiczna as kk   # noqa: E402


class TabelaDanychTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dane = kk.tabela_danych()

    def test_kazdy_wpis_ma_zrodlo(self):
        for k, v in self.dane.items():
            self.assertIn("source", v, k)
            self.assertTrue(
                any(t in v["source"] for t in ("arXiv", "Planck", "DESI", "BBN", "ΔN")),
                f"brak identyfikatora źródła w {k}")

    def test_w_desi_w_rozsadnym_zakresie(self):
        self.assertGreater(self.dane["w_desi"]["value"], -1.2)
        self.assertLess(self.dane["w_desi"]["value"], -0.8)

    def test_bbn_limit_zgodny_z_modulem(self):
        self.assertAlmostEqual(
            self.dane["r_bbn_stiff"]["value"], sk.R_BBN_MAX, places=6)

    def test_lambda_planck_zgodna_z_modulem_audytowym(self):
        self.assertAlmostEqual(
            self.dane["Lambda_planck"]["value"],
            sk.lambda_obserwowana()["Lambda_planck"],
            delta=1.0e-123)

    def test_liczba_wpisow_desi(self):
        klucze = list(self.dane)
        self.assertIn("Omega_m_desi", klucze)
        self.assertIn("Omega_m_desi_cmb", klucze)
        self.assertIn("w0wa_preferencja", klucze)


class ScenariuszeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sc = kk.scenariusze(q_mc=0.835, A_mc=0.1697)
        cls.po_id = {s["id"]: s for s in cls.sc}

    def test_liczba_scenariuszy(self):
        self.assertEqual(len(self.sc), 6)

    def test_w_termicznej_wynika_z_q(self):
        self.assertAlmostEqual(self.po_id["S3_termiczna"]["w0"],
                               -1.0 + 0.835 / 3.0, places=9)

    def test_tracker_req_jest_znormalizowany(self):
        self.assertAlmostEqual(self.po_id["S4_tracker_req"]["Lambda_t0_planck"],
                               sk.lambda_obserwowana()["Lambda_planck"],
                               delta=1e-123)

    def test_tracker_c1_amplituda_w_1_dex(self):
        lam = self.po_id["S4b_tracker_C1"]["Lambda_t0_planck"]
        import math
        self.assertLess(abs(math.log10(
            lam / sk.lambda_obserwowana()["Lambda_planck"])), 1.0)

    def test_bbn_bare_ogromne(self):
        self.assertGreater(self.po_id["S1_goly_model"]["r_BBN"], 1.0e50)

    def test_bbn_podlogi_bezpieczne(self):
        self.assertLess(self.po_id["S5_podloga"]["r_BBN"], sk.R_BBN_MAX)

    def test_trackeri_maja_w0_pylowe(self):
        self.assertEqual(self.po_id["S4_tracker_req"]["w0"], 0.0)
        self.assertEqual(self.po_id["S4b_tracker_C1"]["w0"], 0.0)


class KonfrontacjaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k = kk.pelna_konfrontacja(q_mc=0.835, A_mc=0.1697)
        cls.wiersze = cls.k["wiersze"]
        cls.po_sc = cls.k["podsumowanie"]["po_scenariuszach"]

    def _w(self, sid, obserwabla_fragment):
        return [w for w in self.wiersze
                if w["scenariusz"].startswith(sid)
                and obserwabla_fragment in w["obserwabla"]][0]

    def test_goly_wykluczony_o_120_rzedow(self):
        w = self._w("S1_goly_model", "Λ_t0")
        self.assertEqual(w["verdict"], "EXCLUDED")
        self.assertIn("+120", w["pull"])

    def test_kanaly_wykluczone(self):
        self.assertEqual(self.po_sc["S2_po_kanalach"]["werdykt"], "EXCLUDED")

    def test_termiczna_wykluczona_bbn(self):
        self.assertEqual(self._w("S3_termiczna", "BBN")["verdict"], "EXCLUDED")
        self.assertEqual(self.po_sc["S3_termiczna"]["werdykt"], "EXCLUDED")

    def test_tracker_wykluczony_przez_w_i_bbn(self):
        for sid in ("S4_tracker_req", "S4b_tracker_C1"):
            self.assertEqual(self._w(sid, "w(ciągłe")["verdict"], "EXCLUDED")
            self.assertEqual(self._w(sid, "BBN")["verdict"], "EXCLUDED")
            self.assertEqual(self.po_sc[sid]["werdykt"], "EXCLUDED")

    def test_tracker_w_pull_okolo_6_6_sigma(self):
        w = self._w("S4b_tracker_C1", "w(ciągłe")
        # (0 − (−0.99))/0.15 = 6.6
        self.assertIn("6.6", w["pull"])

    def test_podloga_jedyna_zgodna(self):
        self.assertEqual(self.po_sc["S5_podloga"]["werdykt"], "AGREE")
        self.assertEqual(self.k["podsumowanie"]["jedyny_zgodny"], ["S5_podloga"])

    def test_zadna_obliczona_nie_jest_w_pelni_zgodna(self):
        for sid, info in self.po_sc.items():
            if info["werdykt"] == "AGREE":
                wiersze_sc = [w for w in self.wiersze if w["scenariusz"] == sid]
                self.assertTrue(all(w["derivation"]["status"] == "tuned-to-data"
                                    for w in wiersze_sc),
                                "scenariusz computed nie może być AGREE")

    def test_w0wa_tylko_kontekst(self):
        w = [x for x in self.wiersze if "w0wa" in x["obserwabla"]][0]
        self.assertEqual(w["verdict"], kk.TENSION_CONTEXT)
        self.assertIn("DESI", w["source"])

    def test_alpha_eff_w_napieciu(self):
        w = [x for x in self.wiersze if "α_eff" in x["obserwabla"]][0]
        self.assertEqual(w["verdict"], "TENSION")
        self.assertGreater(w["model"], 0.015)
        self.assertLess(w["model"], 0.035)

    def test_desi_w_wiersz_ma_asymetryczne_sigmy(self):
        w = self._w("S1_goly_model", "w(ciągłe")
        self.assertIn("+0.15", w["data"])
        self.assertIn("−0.13", w["data"])

    def test_json_serializowalne(self):
        json.dumps(self.k, ensure_ascii=False, default=str)


class UczciwoscTests(unittest.TestCase):
    def test_uwaga_uczciwosci_obecna(self):
        uw = kk.pelna_konfrontacja()["podsumowanie"]["uwaga_uczciwosci"]
        self.assertIn("tuned-to-data", uw)
        self.assertIn("NIE jest predykcją", uw)

    def test_status_tension_context_istnieje(self):
        self.assertTrue(hasattr(kk, "TENSION_CONTEXT"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
