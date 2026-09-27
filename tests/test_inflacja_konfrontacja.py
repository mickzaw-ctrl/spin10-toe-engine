# -*- coding: utf-8 -*-
"""
Kontrakty naukowe przebudowy sektora inflacji i jej konfrontacji z danymi
(src/inflacja_alpha_attractor.py, src/konfrontacja_inflacja.py).

Pilnuje:
  1. matematycznej poprawności dynamiki (tożsamość dN/dφ = V/V', ε_H(end)=1,
     atraktor u = −V'/V),
  2. spójności NLO↔LO (nowe liczby blisko starych wzorów silnika),
  3. fizyczności podgrzewania (N_⋆ skończone, monotoniczne w T_rh, zasięg
     zgodny z literaturą),
  4. integralności werdyków konfrontacji (vanilla vs ACT DR6 = TENSION,
     α_s i A_s raportowane uczciwie, napięcia H₀/S₈ tylko jako kontekst).
"""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import sys

import numpy as np

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inflacja_alpha_attractor import (  # noqa: E402
    PotencjalAlpha, TloInflacji, normalizuj_V0_dla_As, skan_podgrzewania,
    predykcje_LO, wymagane_N_dla_ns, A_S_OBS,
)
import konfrontacja_inflacja as ki  # noqa: E402


class PotencjalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pot = PotencjalAlpha(alpha=3.75)

    def test_tozsamosc_dN_dphi(self):
        for phi in (5.0, 7.0, 9.0):
            h = 1e-6
            num = (self.pot.N_analityczne(phi + h, 1.0)
                   - self.pot.N_analityczne(phi, 1.0)) / h
            an = self.pot.V(phi) / self.pot.dV(phi)
            self.assertLess(abs(num - an) / an, 1e-5, f"phi={phi}")

    def test_phi_end_z_epsilon(self):
        self.assertAlmostEqual(self.pot.eps_V(self.pot.phi_end_pot()), 1.0, places=6)

    def test_N_rosnie_z_phi(self):
        pe = self.pot.phi_end_pot()
        Ns = [self.pot.N_analityczne(pe + d, pe) for d in (1, 3, 5, 7)]
        self.assertEqual(Ns, sorted(Ns))

    def test_lambda_z_alpha(self):
        self.assertAlmostEqual(self.pot.lam, math.sqrt(2.0 / (3.0 * 3.75)))


class TloTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tlo = TloInflacji(PotencjalAlpha(alpha=3.75), n_max=100.0)

    def test_koniec_inflacji_epsilon_rowne_1(self):
        self.assertAlmostEqual(self.tlo.grid["eps1"][-1], 1.0, places=6)

    def test_atraktor_u_rowne_minus_Vp_nad_V(self):
        # na plateau (N_left=80) dokładna dynamika ≈ u = −V'/V
        N = 80.0
        idx = np.argmin(abs(self.tlo.grid["N_left"] - N))
        u = self.tlo.grid["u"][idx]
        phi = self.tlo.grid["phi"][idx]
        sr = -self.tlo.pot.dV(phi) / self.tlo.pot.V(phi)
        self.assertLess(abs(u - sr) / abs(sr), 0.02)

    def test_N_end_blisko_wymaganego(self):
        # margines startu 12 e-folds + transient ~1.5 → ~113.5 ± 2
        self.assertGreater(self.tlo.grid["N_end"], 100.0)
        self.assertLess(self.tlo.grid["N_end"], 118.0)

    def test_n_lo_zgodnosc(self):
        o60 = self.tlo.obserwable(60.0)
        self.assertLess(abs(o60["n_s"] - (1.0 - 2.0 / 60.0)), 5.0e-3)
        lo_r = 12.0 * 3.75 / 60.0 ** 2
        self.assertGreater(o60["r"] / lo_r, 0.5)
        self.assertLess(o60["r"] / lo_r, 1.2)

    def test_r_ponizej_bk18_w_wanilii(self):
        for N in (50.0, 55.0, 60.0):
            o = self.tlo.obserwable(N)
            self.assertLess(o["r"], 0.036, f"r przekracza BK18 przy N={N}")

    def test_running_znaki_i_rzed(self):
        rn = self.tlo.running(60.0)
        self.assertLess(rn["alpha_s"], 0.0)
        self.assertGreater(rn["alpha_s"], -1.2e-3)
        self.assertLess(rn["alpha_s"], -2.0e-4)
        self.assertLess(abs(rn["beta_s"]), 2.0e-4)

    def test_normalizacja_As(self):
        norm = normalizuj_V0_dla_As(self.tlo, 60.0)
        self.assertGreater(norm["V_k_quarter_GeV"], 1.0e16)
        self.assertLess(norm["V_k_quarter_GeV"], 1.2e17)

    def test_ms_solver_spread(self):
        # silnikowy solwer MS daje 0.963529 przy N=60 (artefakt pipeline);
        # nasze NLO = ~0.968 — spread konwencji ≤ 0.006 (raportowany w docs)
        o60 = self.tlo.obserwable(60.0)
        self.assertLess(abs(o60["n_s"] - 0.963529), 6.0e-3)


class PodgrzewanieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tlo = TloInflacji(PotencjalAlpha(alpha=3.75), n_max=100.0)
        Trh = np.logspace(0, 15, 16)
        cls.res = skan_podgrzewania(tlo, Trh, w_rh=0.0)

    def test_N_monotoniczne_w_Trh(self):
        Ns = self.res["N_star"]
        self.assertTrue(np.all(np.diff(Ns) > 0))

    def test_N_w_literaturowym_zasiegu(self):
        Ns = self.res["N_star"]
        self.assertGreater(Ns.min(), 40.0)     # T_rh=1 GeV
        self.assertLess(Ns.max(), 57.5)        # T_rh=1e15 GeV, w=0

    def test_n_s_maks_podgrzewania(self):
        # najlepszy fizyczny punkt vanilla: n_s ≤ 0.966
        self.assertLess(self.res["n_s"].max(), 0.9665)

    def test_tyicalny_reheat_obala_pactlb(self):
        # wniosek modułu: typowy T_rh → n_s 3.5-4σ pod P-ACT-LB
        n_s_typ = 0.5 * (self.res["n_s"].min() + self.res["n_s"].max())
        pull = (n_s_typ - 0.9743) / 0.0034
        self.assertLess(pull, -3.0)


class DaneKonfrontacjaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k = ki.pelna_konfrontacja()
        cls.w = cls.k["wiersze"]

    def _rows(self, fragment):
        return [w for w in self.w if fragment in w["obserwabla"]]

    def test_tabela_danych_kluczowe_wartosci(self):
        d = self.k["dane"]
        self.assertEqual(d["n_s_pactlb"]["value"], 0.9743)
        self.assertEqual(d["n_s_pactlb"]["sigma"], 0.0034)
        self.assertEqual(d["n_s_pact"]["value"], 0.9709)
        self.assertLess(d["r_0.05"]["value"], 0.04)

    def test_kazde_zrodlo_zidentyfikowane(self):
        for k, v in self.k["dane"].items():
            self.assertTrue(
                any(t in v["source"] for t in ("arXiv", "Planck", "ACT", "BICEP", "SH0ES", "DES", "KiDS", "P-ACT")),
                f"brak źródła w {k}")

    def test_vanilla_lo_pactlb_tension(self):
        w = [x for x in self._rows("n_s vs n_s_pactlb")
             if x["scenariusz"].startswith("I0")][0]
        self.assertEqual(w["verdict"], "TENSION")
        pull = float(w["pull"].rstrip("σ"))
        self.assertGreater(pull, -2.6)
        self.assertLess(pull, -2.0)

    def test_vanilla_nlo_najblizej(self):
        w = [x for x in self._rows("n_s vs n_s_pactlb")
             if x["scenariusz"].startswith("I1")][0]
        pull = float(w["pull"].rstrip("σ"))
        self.assertGreater(pull, -2.0)

    def test_typowy_reheat_wykluczony(self):
        w = [x for x in self._rows("n_s vs n_s_pactlb")
             if "typowe" in x["scenariusz"]][0]
        self.assertEqual(w["verdict"], "EXCLUDED")

    def test_planck_i_pact_agree(self):
        for frag in ("n_s vs n_s_planck", "n_s vs n_s_pact"):
            for x in self._rows(frag):
                if "typowe" in x["scenariusz"]:
                    continue
                self.assertIn(x["verdict"], ("AGREE", "TENSION"), frag)
        planck_rows = [x for x in self._rows("n_s vs n_s_planck")]
        self.assertTrue(all(x["verdict"] == "AGREE" for x in planck_rows))

    def test_r_zawsze_agree(self):
        for x in self._rows("r vs"):
            self.assertEqual(x["verdict"], "AGREE", x["obserwabla"])

    def test_As_uczciwie_oznaczone(self):
        x = self._rows("A_s")[0]
        self.assertEqual(x["derivation"], "measured input")

    def test_h0_kontekst(self):
        x = self._rows("Hubble tension")[0]
        self.assertEqual(x["verdict"], ki.TENSION_CONTEXT)
        self.assertIn("4.8", x["pull"])

    def test_s8_no_data(self):
        x = self._rows("S₈ tension")[0]
        self.assertEqual(x["verdict"], ki.NO_DATA)

    def test_diagnoza_delta_falsyfikowalnie(self):
        x = self._rows("wymagana zmiana")[0]
        self.assertIn("0.017", x["uwaga"])
        self.assertEqual(x["verdict"], "TENSION")

    def test_liczniki_sumuja_sie(self):
        lic = self.k["podsumowanie"]["liczniki"]
        self.assertEqual(sum(lic.values()), len(self.w))

    def test_json_serializowalne(self):
        json.dumps(self.k, ensure_ascii=False, default=str)


class SilinkCrossCheckTests(unittest.TestCase):
    def test_LO_rowne_opublikowanemu_silnikowi(self):
        self.assertAlmostEqual(predykcje_LO(60.0)["n_s_LO"], 0.966667, places=5)
        self.assertAlmostEqual(predykcje_LO(60.0)["r_LO"], 0.0125, places=6)

    def test_wymagane_N_dla_pactlb(self):
        N = wymagane_N_dla_ns(0.9743)
        self.assertGreater(N, 70.0)
        self.assertLess(N, 90.0)

    def test_wejscie_As_spojne_z_konfrontacja_silnika(self):
        # te same A_s co w run_experimental_confrontation.py (2.099e-9)
        self.assertAlmostEqual(A_S_OBS, 2.099e-9, places=12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
