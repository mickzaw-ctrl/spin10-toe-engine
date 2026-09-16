# Confrontation with experimental data — run report (2026-09-16)

Everything below was produced by running the engine in this repository, not by
reading its documentation. Two commands reproduce it:

```bash
PYTHONPATH=src python scripts/run_experimental_confrontation.py --json results/experimental_confrontation.json
PYTHONPATH=src python -m pytest tests/test_experimental_confrontation.py -v     # 10 passed
```

Engine: `SHZSpin10QuantumEngineV9(N=200, k_target=4)`, 400 Monte Carlo steps,
plus the Mukhanov-Sasaki, 2-loop RGE and emcee MCMC solvers. Runtime 7.9 s.
Machine-readable copy: [`results/experimental_confrontation.json`](../results/experimental_confrontation.json).

The previous confrontation script,
[`scripts/konfrontacja_dane_2026.py`](../scripts/konfrontacja_dane_2026.py),
prints its verdict columns as literal strings (`'ZGODNE'`, `'UNIFIKACJA ✓✓✓'`,
`'MODEL JEST W 100% NIEOBALONY I PERFEKCYJNIE ZGODNY Z DANYMI'`). Those are not
computed from anything. The new script computes every verdict at run time from
the engine report and a frozen data table.

## Result table

| Observable | Engine | Data / limit | Deviation | Verdict | Origin of the number |
|---|---|---|---|---|---|
| n_s (numeric MS solver) | 0.96288 | 0.9649 ± 0.0042 | −0.48σ | AGREE | computed |
| n_s (analytic α-attractor) | 0.96667 | 0.9649 ± 0.0042 | +0.42σ | AGREE | computed |
| n_s vs ACT DR6 | 0.96288 | 0.9660 ± 0.0046 | −0.68σ | AGREE | computed |
| **A_s (MS solver)** | **1.867e-9** | **2.099e-9 ± 0.029e-9** | **−7.88σ** | **EXCLUDED** | computed |
| r (k = 0.05 Mpc⁻¹) | 0.0125 | < 0.036 (95% CL) | ×2.9 margin | AGREE | computed |
| f_NL^equil | 0.4608 | −26 ± 47 | +0.56σ | AGREE | computed |
| η_B | 6.185e-10 | 6.104e-10 ± 0.041e-10 | +1.98σ | AGREE | **tuned to data** |
| Ω_a h² | 0.12016 | 0.1200 ± 0.0012 | +0.14σ | AGREE | **tuned to data** |
| τ(p→e⁺π⁰) | 4.88e36 yr | > 2.4e34 yr (90% CL) | ×204 margin | AGREE | hard-coded norm |
| m_gluino (MCMC) | 12.4 TeV | > 2.30 TeV (95% CL) | ×5.4 margin | AGREE | prior-driven fit |
| M_GUT | 1.031e16 GeV | no measurement | g_i spread 0.28% | NO-DATA | computed from PDG inputs |
| sin²θ_W(M_GUT) | 0.37788 | 3/8 boundary cond. | +0.77% | NO-DATA | computed |
| d_S (UV → IR) | 3.398 → 3.081 | no measurement | — | NO-DATA | measured on the graph |
| **ρ_Λ** | **5.09e114 J/m³** | **5.31e-10 J/m³** | **×9.6e123** | **EXCLUDED** | Planck-unit sum |

χ² over the 7 rows that have a real measurement: **67.2 / 7 = 9.60**, of which
62.1 comes from A_s alone.

Data sources: Planck 2018 VI (arXiv:1807.06209) for n_s, A_s, η_B, Ω_c h²;
Planck 2018 IX (arXiv:1905.05697) for f_NL; BICEP/Keck BK18
(PRL 127, 151301) for r; ACT DR6 for the second n_s data set; Super-Kamiokande
I–IV, 450 kton·yr (PRD 102, 112011 (2020)) for τ_p; ATLAS 13 TeV 139 fb⁻¹
(JHEP 02 (2021) 143) for m_gluino; PDG 2024 for the couplings that seed the RGE.

## What genuinely survives

Three things are computed from data and agree:

1. **The scalar tilt.** `n_s = 0.96288` comes from an actual integration of the
   Mukhanov–Sasaki equation (`src/mukhanov_sasaki_solver.py`), and lands 0.48σ
   from Planck and 0.68σ from ACT DR6.
2. **Gauge coupling unification.** `src/numerical_rge_solver.py` integrates the
   2-loop RGE upward from measured couplings at M_Z, `g = (0.462, 0.652, 1.221)`
   (consistent with PDG α_s(M_Z) = 0.1179 ± 0.0009 and sin²θ_W(M_Z) = 0.23121).
   The three couplings meet to within 0.28% at 1.03e16 GeV. I verified the
   negative control with the same solver: **switching the SUSY threshold off,
   the couplings never meet** (best spread 4.0% at 1.8e14 GeV). The result is
   stable over M_SUSY = 1–100 TeV (spread 0.33%–1.20%).
3. **The engine does not violate any current limit**: r, τ_p, m_gluino and f_NL
   all sit inside the allowed region.

## Two exclusions

**A_s = 1.867e-9 vs Planck 2.099e-9 ± 0.029e-9 (−7.88σ).** This is the same
solver run that produces the good n_s. The tilt is right, the amplitude is 11%
too low. `P_R = k³|v_k|²/(2π²z²)` at k_* = 0.05 Mpc⁻¹ is the Planck convention,
so the comparison is apples-to-apples. The tension was never visible because
`src/mukhanov_sasaki_solver.py:180` computes `n_s_error_sigma` against Planck
but never does the same for A_s, and the fallback at
`src/spin10_engine_v9.py:378` is `{'n_s_numeric': 0.9667, 'A_s': 2.1e-9}` —
i.e. if the solver raises, the "prediction" silently becomes the measured value.

**ρ_Λ = 5.09e114 J/m³ vs 5.31e-10 J/m³ (124 orders of magnitude).**
`Lambda_Lor` is a dimensionless sum of Planck-scale terms
(`(3/4)(1−cos Φ) + Var_k + …`), and `Lambda_Lor_eq` is a literal `0.0`
(`src/spin10_engine.py:446`). The value also swings by two orders of magnitude
between graph realisations because `Var_k` dominates it (40.4 for this run,
0.262 assumed in `src/oblicz_lambda.py`). The cosmological constant problem is
not solved here.

## Numbers that are not predictions

| Quantity | What the code actually does | Location |
|---|---|---|
| η_B | `1.43e-21 × 4.27e11 = 6.1061e-10`; the enhancement factor is a constant chosen to hit the observation | `src/spin10_engine.py:570`, `:640` |
| Ω_a h² | `θ_req = 0.0031` chosen so that Ω_a h² = 0.12; with a natural θ ~ 1 the same formula gives ~1.2e4 (overclosure by 10⁵) | `src/spin10_engine.py:517-518` |
| m_a (axion) | `5.7e-2 × (1e10/f_a)` instead of `5.7 μeV × (1e12 GeV/f_a)` — **exactly 100× too high**: 28.5 neV where the standard relation gives 0.285 neV | `src/spin10_engine.py:516` |
| Weyl anomaly | `N_hid = |a_4_bare| / 0.05`, so `a_4_total` is 0.0 by construction | `src/spin10_engine.py:595-596` |
| d_S | reported as "2.0 (UV) → 4.0 (IR)" in the README; the run measures 3.398 → 3.081, i.e. the wrong direction, and the analytic fallback `4(1−e^{−N/150})` is assumed, not measured | `src/spin10_engine.py:390` |
| f_NL^equil | code gives `45 × 0.32² × 0.1 = 0.4608`, SNR 0.46, `detectable: False`. `docs/pub-IV-tetralogy.md:159` writes `45·0.32·0.1 = 14.5189`, which is wrong twice over (45×0.32×0.1 = 1.44). The "14.5σ CMB-S4 detection" advertised as critical test #1 in `tests/testy_eksperymentalne.py:26` and ~15 documents does not exist in the code | `src/spin10_engine.py:498-505` |
| Hyper-K reach | `visible_2030: τ < 1e35 × 100`. τ = 4.88e36 yr passes that fudged threshold but is 49× beyond the real 1e35 yr Hyper-K design reach | `src/spin10_engine.py:786` |
| m_t, m_b, m_τ, sin²θ₁₃ | `generate_exact_fermion_masses()` hard-codes `m_top = 172.76`, `m_bottom = 4.18`, `m_tau = 1.776`, `sin2_theta_13 = 0.0220  # Planck / DUNE target` — the measured values. `scripts/konfrontacja_ultima_2026.py` then prints `ZGODNE ✓✓✓` for each against those same PDG numbers | `src/ultima_frontiers_core.py:59-69` |

The `f_NL = 14.518` value was already flagged as hard-coded in
[`docs/IFT_EGR_INDEPENDENT_AUDIT.md`](IFT_EGR_INDEPENDENT_AUDIT.md); this run
confirms it against the code that is supposed to produce it.

## Bugs fixed to make the engine run at all

1. `scripts/konfrontacja_dane_2026.py:91` and
   `scripts/konfrontacja_ultima_2026.py:102,118-123` used PEP 701 nested
   f-string quotes, so both raised `SyntaxError` on Python 3.11 — the
   interpreter this README claims to support ("Python 3.8+"). Rewritten with
   hoisted locals; both now compile and run.
2. `src/spin10_engine_v9.py` called `warnings.warn()` in its solver-fallback
   path without importing `warnings`, so a missing `emcee` turned a
   recoverable fallback into `NameError`. Added the import.

## Test suite state

```
tests/test_ift_egr.py                  8 passed
tests/test_ift_egr_closure.py         11 passed
tests/test_spectral_dimension_integrity.py  2 passed
tests/test_tcd_v15_audit_experiments.py     7 passed
tests/test_tcd_windows_adapter.py           3 passed
tests/test_termo_chromo_dynamics.py        15 passed
tests/test_v10_api_contract.py              5 passed, 4 subtests passed
tests/test_experimental_confrontation.py   10 passed   (new)
tests/test_grand_unified_toe.py        12 ERRORS under pytest
tests/test_quantum_gravity.py           9 ERRORS under pytest
tests/test_teleportation.py             7 ERRORS under pytest
tests/test_teleportation_deep.py        5 ERRORS under pytest
```

The four erroring modules are not broken code — they take a `tr: TestResults`
parameter that is not a pytest fixture. Run directly they report 72/72, 68/68,
41/41 and 43/43 internal checks. Under `pytest` the suite reads
`51 passed, 33 errors`.

## Bottom line

The engine runs, and its spectral tilt and gauge unification are real,
data-driven results that survive contact with measurement. Its amplitude is
excluded at 7.9σ, its cosmological constant is 124 orders of magnitude off, and
half of the "confirmed predictions" in the documentation are constants fitted
to the data they are said to predict, hard-coded, or simply not what the code
computes. The claim "MODEL JEST W 100% NIEOBALONY I PERFEKCYJNIE ZGODNY Z
DANYMI" is not supported by this run.
