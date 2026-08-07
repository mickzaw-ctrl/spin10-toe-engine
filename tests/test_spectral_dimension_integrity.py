"""Scientific-integrity contracts for spectral-dimension reporting."""

from __future__ import annotations

import unittest

import numpy as np

from spectral_dimension_random_walk import RandomWalkSpectralDimension


class SpectralDimensionIntegrityTests(unittest.TestCase):
    def test_theoretical_remedy_is_never_reported_as_observation(self) -> None:
        times = np.arange(1.0, 21.0)
        dimensions = np.linspace(1.8, 3.9, 20)
        report = RandomWalkSpectralDimension.compute_spectral_plateaux(
            times, dimensions, N_nodes=1000
        )
        self.assertIsNone(report["flow_observed"])
        self.assertEqual(
            report["theoretical_remedy_status"],
            "project_hypothesis_not_observation",
        )
        self.assertIn("not_inferred", report["flow_status"])

    def test_short_series_preserves_same_epistemic_status(self) -> None:
        report = RandomWalkSpectralDimension.compute_spectral_plateaux(
            np.arange(1.0, 6.0), np.ones(5), N_nodes=100
        )
        self.assertIsNone(report["flow_observed"])
        self.assertEqual(
            report["theoretical_remedy_status"],
            "project_hypothesis_not_observation",
        )


if __name__ == "__main__":
    unittest.main()
