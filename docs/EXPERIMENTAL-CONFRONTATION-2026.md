# Confrontation with experimental data — run report (2026-09-16)

Everything below was produced by running the engine in this repository, not by
reading its documentation. Reproduce with:

```bash
python -m pytest tests -q                                                        # 96 passed
python scripts/run_experimental_confrontation.py --json results/experimental_confrontation.json
```

Engine: `SHZSpin10QuantumEngineV9(N=200, k_target=4)`, 400 Monte Carlo steps,
plus the Mukhanov-Sasaki, 2-loop RGE and emcee MCMC solvers. Runtime ~8 s.
Machine-readable copy: [`results/experimental_confrontation.json`](../results/experimental_confrontation.json).

The pre-existing confrontation script,
[`scripts/konfrontacja_dane_2026.py`](../scripts/konfrontacja_dane_2026.py),
printed its verdict columns as literal strings (`'ZGODNE'`, `'UNIFIKACJA ✓✓✓'`,
`'MODEL JEST W 100% NIEOBALONY I PERFEKCYJNIE ZGODNY Z DANYMI'`). Those were not
computed from anything, and the script did not even parse on Python 3.11. The new
runner computes every verdict at run time from the engine report and a frozen
data table, and the old script now imports it for its summary panel.

## Result table (current state)

| Observable | Engine | Data / limit | Deviation | Verdict | Origin of the number |
|---|---|---|---|---|---|
| n_s (numeric MS solver) | 0.96288 | 0.9649 ± 0.0042 | −0.48σ | AGREE | computed |
| n_s (analytic α-attractor) | 0.96667 | 0.9649 ± 0.0042 | +0.42σ | AGREE | computed |
| n_s vs ACT DR6 | 0.96288 | 0.9660 ± 0.0046 | −0.68σ | AGREE | computed |
| **A_s (MS solver)** | **1.867e-9** | **2.099e-9 ± 0.029e-9** | **−7.88σ** | **EXCLUDED** | computed |
| r (k = 0.05 Mpc⁻¹) | 0.0125 | < 0.036 (95% CL) | ×2.9 margin | AGREE | computed |
| f_NL^equil | 0.4608 | −26 ± 47 | +0.56σ | AGREE | computed |
| η_B | 6.185e-10 | 6.104e-10 ± 0.041e-10 | +1.98σ | AGREE | **tuned to data** |
| Ω_a h² | 0.1200 | 0.1200 ± 0.0012 | 0.00σ | AGREE | **tuned to data** |
| τ(p→e⁺π⁰) | 4.88e36 yr | > 2.4e34 yr (90% CL) | ×204 margin | AGREE | hard-coded norm |
| m_gluino (MCMC) | 12.4 TeV | > 2.30 TeV (95% CL) | ×5.4 margin | AGREE | prior-driven fit |
| m_a (axion) | 2.85e-10 eV | 5.7 μeV·(1e12 GeV/f_a) | ×1.000 | AGREE | computed |
| τ(p) vs Hyper-K 2030 reach | 4.88e36 yr | needs < 1e35 yr | ×48.8 beyond | NO-DATA | hard-coded norm |
| M_GUT | 1.031e16 GeV | no measurement | g_i spread 0.28% | NO-DATA | computed from PDG inputs |
| sin²θ_W(M_GUT) | 0.37788 | 3/8 boundary cond. | +0.77% | NO-DATA | computed |
| d_S (UV → IR) | 3.398 → 3.081 | no measurement | — | NO-DATA | measured on the graph |
| CF (causal fraction) | 0.866 | no measurement | — | NO-DATA | graph observable |
| **ρ_Λ** | **5.09e114 J/m³** | **5.31e-10 J/m³** | **×9.6e123** | **EXCLUDED** | Planck-unit sum |

17 rows; χ² over the 7 with a real measurement: **67.20 / 7 = 9.60**, of which
92% comes from A_s alone. Verdicts: AGREE 10, EXCLUDED 2, NO-DATA 5.

Data sources: Planck 2018 VI (arXiv:1807.06209) for n_s, A_s, η_B, Ω_c h²;
Planck 2018 IX (arXiv:1905.05697) for f_NL; BICEP/Keck BK18 (PRL 127, 151301)
for r; ACT DR6 for the second n_s data set; Super-Kamiokande I–IV, 450 kton·yr
(PRD 102, 112011) for τ_p; ATLAS 13 TeV 139 fb⁻¹ (JHEP 02 (2021) 143) for
m_gluino; PDG 2024 for the couplings that seed the RGE; PDG axion review for
m_a·f_a.

## What genuinely survives

1. **The scalar tilt.** `n_s = 0.96288` comes from an actual integration of the
   Mukhanov–Sasaki equation (`src/mukhanov_sasaki_solver.py`), 0.48σ from Planck
   and 0.68σ from ACT DR6.
2. **Gauge coupling unification.** `src/numerical_rge_solver.py` integrates the
   2-loop RGE upward from measured couplings at M_Z, `g = (0.462, 0.652, 1.221)`
   (consistent with PDG α_s(M_Z) = 0.1179 ± 0.0009 and sin²θ_W(M_Z) = 0.23121).
   The three couplings meet to within 0.28% at 1.03e16 GeV. Negative control with
   the same solver: **with the SUSY threshold switched off the couplings never
   meet** (best spread 4.0% at 1.8e14 GeV). Stable over M_SUSY = 1–100 TeV
   (spread 0.33%–1.20%).
3. **No current limit is violated**: r, τ_p, m_gluino, f_NL and m_a all sit inside
   the allowed region.

## Two exclusions that remain

**A_s = 1.867e-9 vs Planck 2.099e-9 ± 0.029e-9 (−7.88σ).** Same solver run that
produces the good n_s: the tilt is right, the amplitude is 11% too low.
`P_R = k³|v_k|²/(2π²z²)` at k_* = 0.05 Mpc⁻¹ is the Planck convention, so the
comparison is apples-to-apples. The solver now reports this itself as
`A_s_error_sigma` / `A_s_agrees_with_Planck` (it previously compared only n_s
with Planck), and the fallback in `src/spin10_engine_v9.py` no longer substitutes
the measured `2.1e-9` when the solver fails — it returns `NaN` with
`solver_fallback: True`. Fixing the amplitude is a physics task, not a code task;
the most likely source is the assumed Hubble scale in
`generate_inflationary_background()`, which is normalised by hand rather than
from A_s.

**ρ_Λ = 5.09e114 J/m³ vs 5.31e-10 J/m³ (124 orders of magnitude).**
`Lambda_Lor` is a dimensionless sum of Planck-scale terms, and `Lambda_Lor_eq`
is still a literal `0.0` (`src/spin10_engine.py`). It also swings by two orders
of magnitude between graph realisations because `Var_k` dominates it (40.4 for
this run, 0.262 assumed in `src/oblicz_lambda.py`). Not solved.

## Bugs fixed during this pass

| Fix | Location | Before → after |
|---|---|---|
| Axion mass off by exactly 100× | `src/spin10_engine.py` `axion_mass()` | `5.7e-2·(1e10/f_a)` → `5.7e-6 eV·(1e12 GeV/f_a)`; 28.5 neV → **0.285 neV** |
| θ misalignment angle hard-coded | same | `theta_req = 0.0031` → derived from Ω_c h²; adds `Omega_h2_natural_theta` and `overclosure_factor_at_theta_1` (≈1.0e4) so the overclosure at θ ≈ 1 is visible |
| Hyper-K reach fudged ×100 | `src/spin10_engine.py` `test_proton_decay_vs_HyperK()` | `visible_2030: τ < 1e35×100` → `τ < 1e35`; 4.88e36 yr is now correctly reported as **not** visible, ×48.8 beyond reach |
| A_s never compared with data | `src/mukhanov_sasaki_solver.py` | adds `A_s_Planck`, `A_s_error_sigma`, `A_s_agrees_with_Planck` |
| Solver fallback hid failures | `src/spin10_engine_v9.py` | `{'n_s': 0.9667, 'A_s': 2.1e-9}` → `NaN` + `solver_fallback: True` |
| `warnings` not imported | `src/spin10_engine_v9.py` | missing `emcee` raised `NameError` instead of warning |
| PEP 701 nested f-strings | `scripts/konfrontacja_dane_2026.py:91`, `scripts/konfrontacja_ultima_2026.py:102,118-123` | `SyntaxError` on Python 3.11 → both run |
| Verdicts hard-coded as strings | `scripts/konfrontacja_dane_2026.py` | summary panel now computed by `run_experimental_confrontation.build_rows()`; the "100% NIEOBALONY" line is gone |
| `d_S` claim printed as fact | same | prints the measured flow (3.40 → 3.08) and flags that it is not a UV→IR reduction |
| f_NL = 14.518 in the executable | `tests/testy_eksperymentalne.py:26` | imports `Spin10Predictions.f_NL_equilateral()` = 0.4608; SNR printed as 0.46σ "BRAK DETEKCJI"; header lists which remaining constants are unverified assumptions |
| Wrong arithmetic in Publication IV | `docs/pub-IV-tetralogy.md:159` | `45·0.32·0.1 = 14.5189` → `45·0.32²·0.1 = 0.4608` (45·0.32·0.1 is 1.44); the 14.5σ detection claims in that file corrected |
| 33 pytest collection errors | `tests/conftest.py` (new) | the four script-style test modules pass a `tr` accumulator that was not a fixture; the fixture instantiates it and fails the test if any internal check failed |
| `m_a`, θ, Ω_a duplicated | `scripts/publikacja_V_obliczenia.py` | now derives both from the QCD relation; the script had already contained the correct formula next to the wrong constant |

## Numbers that are still not predictions

| Quantity | What the code actually does | Location |
|---|---|---|
| η_B | `1.43e-21 × 4.27e11 = 6.1061e-10`; the enhancement factor is a constant chosen to hit the observation | `src/spin10_engine.py:570`, `:640` |
| Ω_a h² | reaches 0.12 only through the θ required by that target; at a natural θ ≈ 1 the same formula gives ≈1.25e4 (overclosure ~10⁴) — now reported explicitly | `src/spin10_engine.py` `axion_mass()` |
| Weyl anomaly | `N_hid = |a_4_bare| / 0.05`, so `a_4_total` is 0.0 by construction | `src/spin10_engine.py:595-596` |
| d_S | README claimed "2.0 (UV) → 4.0 (IR)"; the run measures 3.398 → 3.081, the wrong direction, and the analytic fallback `4(1−e^{−N/150})` is assumed, not measured | `src/spin10_engine.py:390` |
| m_t, m_b, m_τ, sin²θ₁₃ | `generate_exact_fermion_masses()` hard-codes `172.76`, `4.18`, `1.776`, `0.0220  # Planck / DUNE target` — the measured values — which `scripts/konfrontacja_ultima_2026.py` then prints as `ZGODNE ✓✓✓` against those same PDG numbers | `src/ultima_frontiers_core.py:59-69` |
| τ_p normalisation | `1.4e36 yr` constant rescaled by cos Φ and Var_k | `src/spin10_engine.py:530` |
| SGWB | peak amplitude 5.18e-7 quoted at 1 mHz, but the engine places the peak at `SGWB_LISA_freq ≈ 1e-7 Hz`, four decades below LISA's 1e-4–1e-1 Hz band; the quoted "SNR" is Ω_peak/Ω_sens | `src/spin10_engine.py`, `tests/testy_eksperymentalne.py` |
| f_NL^equil = 14.5 | still quoted in ~12 other documents (`docs/MANIFEST-konfrontacji.md`, `docs/TESTY-manifest.md`, `docs/comparative_brochure.md`, `docs/confrontation-megii-mu3e.md`, `docs/pub-V-pentalogy.md`, `docs/pub-VI-hexalogy.md`, `README.md` publication table, …). `src` and the executable test are corrected; the prose documents are not. `docs/IFT_EGR_INDEPENDENT_AUDIT.md` had already flagged the constant. |

## Test suite state

```
96 passed, 4 subtests passed in ~9 s
```

was `51 passed, 33 errors, 2 warnings`. The four script-style modules
(`test_grand_unified_toe`, `test_quantum_gravity`, `test_teleportation`,
`test_teleportation_deep`) now run under pytest through `tests/conftest.py`, so
their ~224 internal checks count towards the result; a deliberately failing check
was verified to turn the test red. `tests/test_experimental_confrontation.py`
(12 tests) pins every number in the tables above, including the A_s tension, so
it cannot silently regress.

CI: [`.github/workflows/engine-confrontation-ci.yml`](../.github/workflows/engine-confrontation-ci.yml)
byte-compiles every source (guards the PEP 701 regression), runs the suite, runs
the confrontation, and fails if the set of observables the data excludes grows
beyond the allow-list.

## Bottom line

The engine runs, and its spectral tilt and gauge unification are real,
data-driven results that survive contact with measurement. Its amplitude is
excluded at 7.9σ and its cosmological constant is 124 orders of magnitude off;
both are open physics problems now measured and reported rather than hidden.
Several "confirmed predictions" remain constants fitted to the data they are said
to predict. The claim "MODEL JEST W 100% NIEOBALONY I PERFEKCYJNIE ZGODNY Z
DANYMI" was removed from the code that printed it.
