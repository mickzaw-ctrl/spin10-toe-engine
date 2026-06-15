# Spin(10)-TOE Engine

**Computational engine for the Spin(10) Theory of Everything**

A complete Python implementation of the Spin(10) grand unification hypothesis, including synthetic test suite, comparative analysis, and the formal grand unification hypothesis document.

## Repository Structure

```
spin10-toe-engine/
├── src/
│   └── spin10_engine.py          # SHZSpin10QuantumEngine v8.0 — main engine
├── tests/
│   └── tests_synthetic_spin10_toe.py  # Synthetic test suite (35 observables)
├── scripts/
│   └── demo_engine_vs_tests.py   # Demo: engine vs test suite comparison
├── results/
│   └── test_results.json         # Full test results (JSON export)
└── docs/
    ├── README_synthetic_tests.md # Test suite documentation
    ├── comparative_brochure.md   # Model comparison brochure
    └── spin10_toe_hypothesis.md  # Grand Unification Hypothesis (GUH-S10)
```

## Quick Start

```bash
pip install numpy scipy
python3 src/spin10_engine.py
python3 tests/tests_synthetic_spin10_toe.py
python3 scripts/demo_engine_vs_tests.py
```

## Overview

The **SHZSpin10QuantumEngine v8.0** implements 8 modules:

| Module | Description |
|---|---|
| `RelationalGraph` | Pre-geometry — MCMC Metropolis-Hastings relational network |
| `Spin10Gauge` | Spin(10) gauge symmetry + RGE coupling unification |
| `SplitSUSY` | Split-type supersymmetry |
| `AsymptoticSafety` | Quantum gravity with UV fixed point g* = 0.83 |
| `AlphaAttractor` | α-attractor (CFT) inflation |
| `ResonantLeptogenesis` | Resonant leptogenesis (3-flavour) |
| `TorsionFifthForce` | Torsion as a fifth force |
| `AxionPhysics` | Axion from PQ-symmetry |

## Key Predictions (38 testable observables)

| Observable | Spin(10) | Experiment | Status |
|---|---|---|---|
| n_s (inflation) | 0.9667 | 0.9682 ± 0.0032 | ✅ 0.5σ |
| r (tensor/scalar) | 0.0125 | < 0.034 | ✅ 2.7× margin |
| f_NL^equil | 14.5 | −26 ± 47 | ✅ 0.9σ |
| τ(p→e⁺π⁰) | 4.9×10³⁶ yr | > 1.7×10³⁴ yr | ✅ testable |
| BR(μ→eγ) | 8×10⁻¹⁴ | < 3.1×10⁻¹³ | ⚠️ MEG-II 2026 |
| m_a (axion) | 28.5 neV | CASPEr 2028 | ✅ in range |
| g* (UV fixed point) | 0.83 | — | prediction |

## Related Repository

Main Spin(10)-TOE project (heptalogy, 7 publications, GitHub Pages):
👉 [mickzaw-ctrl/spin10-toe](https://github.com/mickzaw-ctrl/spin10-toe)

## Author

Michał Ślusarczyk — original concept and formulas  
Engine implementation: Synthetic engine v8.0

## License

MIT
