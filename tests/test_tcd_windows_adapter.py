"""Regression contracts for the Windows TCD adapter and PyInstaller build."""

from __future__ import annotations

from pathlib import Path
import unittest

from windows_package.shzspin10.engine import (
    SHZSpin10UltimaApex,
    ThermoChromoDynamicsLab,
)


class TCDWindowsAdapterTests(unittest.TestCase):
    def test_available_adapter_returns_scientifically_gated_report(self) -> None:
        lab = ThermoChromoDynamicsLab(N=10**6)
        self.assertTrue(lab.available, lab.import_error)
        report = lab.run_full_tcd()
        self.assertEqual(
            report["scientific_status"],
            "PROJECT HYPOTHESIS — NOT A VALIDATED TOE",
        )
        self.assertFalse(
            report["consistency_with_heptalogy"]["total_40/40_TCD"]
        )
        self.assertIsNone(
            report["tcd_predictions"]["TCD-3_fifth_force"]
            ["alpha_5_with_torsion_resummed_phenom"]
        )
        self.assertTrue(
            hasattr(SHZSpin10UltimaApex, "run_termo_chromo_simulation")
        )

    def test_unavailable_adapter_never_generates_fallback_physics(self) -> None:
        lab = ThermoChromoDynamicsLab.__new__(ThermoChromoDynamicsLab)
        lab.N = 10**6
        lab.available = False
        lab.import_error = "simulated missing optional dependency"
        lab._tcd_engine = None

        result = lab.run_full_tcd()

        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(
            result["scientific_status"],
            "no fallback physics values were generated",
        )
        self.assertNotIn("T_c_QCD_MeV", result)
        self.assertNotIn("glueball_MeV", result)
        self.assertNotIn("alpha_5_1um", result)

    def test_pyinstaller_spec_includes_tcd_module_and_source_root(self) -> None:
        build_script = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "windows_package"
            / "build_windows.py"
        ).read_text()
        self.assertIn("'termo_chromo_dynamics'", build_script)
        self.assertIn("pathex=['.', '..']", build_script)


if __name__ == "__main__":
    unittest.main()
