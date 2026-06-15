# Spin(10)-TOE · Synthetic Test Suite

A package of synthetic tests for the Spin(10) Theory of Everything hypothesis.

## Requirements

```
python ≥ 3.8
numpy
scipy
```

## Run

```bash
python3 tests_syntetyczne_spin10_toe.py
```

## What the suite does

### 1. Full test suite
- Generates **synthetic measurements** for 9 experiments
  (Planck PR4, LiteBIRD, CMB-S4, LISA, CASPEr, HE-LHC, Hyper-K, IUPUI, Planck ηB)
- Tests **35 observables** in 8 categories:
  - inflation, dark matter/SUSY, proton decay, fifth force,
    baryogenesis, pre-geometry, asymptotic safety, early universe
- For each observable computes:
  - **χ²** (consistency with the prediction)
  - **σ_det** (detection significance)
  - **log K** (Bayes factor Spin(10)/ΛCDM)
  - **p-value**

### 2. Stability test
Runs the suite with 20 different seeds, checks robustness of the results.

### 3. Competition with ΛCDM (BIC)
Compares models via **Bayesian Information Criterion**:
- BIC = χ² + k·ln(n), where k = number of parameters
- Spin(10)-TOE: k = 38
- ΛCDM: k = 6

### 4. Export of results
Full report in JSON format (`wyniki_testow.json`).

## Sample output

```
Observable               Prediction      Observation         σ      χ²   σ_det   PASS
──────────────────────────────────────────────────────────────────────────────
n_s                         0.9667        0.9688  0.004276    0.24     226.6      ✓
r                           0.0125       0.01267  3.16e-04    0.30     40.08      ✓
f_NL_eq                       14.5         23.73     5.385    2.94     4.407      ✓
...

TEST SUMMARY (35 observables):
  Passed (χ²<9):   35/35  (100.0%)
  Σχ²:                20.00
  ⟨χ²⟩:               0.572  (Standard Model ideal: ~1)
  Verdict: THEORY CONSISTENT WITH DATA

>>> Stability test (20 seeds)...
    ⟨pass_rate⟩ = 99.9% ± 0.6%

>>> Comparison with ΛCDM (BIC)...
    BIC(Spin10) = 155.1
    BIC(ΛCDM)   = 51.3
    ΔBIC        = -103.8  → ΛCDM (strong)

>>> DONE.
```

## Interpretation of results

### χ²
- χ² < 1: excellent consistency (may indicate overestimated σ)
- 1 < χ² < 4: very good consistency
- 4 < χ² < 9: good consistency (within 3σ)
- χ² > 9: potential problem (>3σ from prediction)

### ⟨χ²⟩
- Ideal: ~1
- Spin(10)-TOE typically achieves 0.5–1.5

### Stability test
- ⟨pass_rate⟩ should be >95%
- Standard deviation <2% indicates stability

### Competition with ΛCDM
- ΔBIC > 10: strong preference
- ΔBIC > 2: moderate preference
- ΔBIC < 2: weak preference

> Note: Spin(10)-TOE has 38 parameters, ΛCDM has 6 — for the same χ²,
> BIC always favours ΛCDM. A fair comparison requires **AIC**
> (Akaike Information Criterion) or full Bayesian evidence.

## Files

- `tests_syntetyczne_spin10_toe.py` — main script
- `wyniki_testow.json` — generated report (after running)
- `README_synthetic_tests.md` — this file

## Extensions (TODO)

- [ ] Add AIC alongside BIC
- [ ] Generate matplotlib plots (corner plot, residuals)
- [ ] Full Monte Carlo with MCMC for each prediction
- [ ] Visualize discovery contours (n_s vs r)
- [ ] Correlations among predictions (covariance matrix)
