# TCD v15.0 — Final Numerical Audit and Research Decision

**Audit date:** 2026-08-07  
**Pinned baseline:** `bc93e27796a977a3774a62f5fa9f6e0910f6d144`  
**Scientific status:** conditional software pass; physical theory open  
**Validated TCD predictions:** 0

## Scope

This report evaluates the declared Thermo-Chromo-Dynamics equations, numerical domains, external comparisons, and falsifiability status. Software tests verify implementation contracts only. They do not establish agreement with nature.

Every conclusion is classified as **Established physics**, **Project hypothesis**, **Unverified assumption**, or **Rejected statement**.

## Reproducible experiments

The complete numerical artifact is available at [`results/tcd_v15_final_audit_experiments.json`](results/tcd_v15_final_audit_experiments.json).

| Experiment | Result | Classification | Decision |
|---|---:|---|---|
| Spectral interpolation | `d_S(0)=4`, `d_S(T*)=3`, `d_S(10^12 T*)=2.000000008`; strictly decreasing | Project hypothesis | HOLD for independent graph test |
| Coherence domain | `P>0` iff `T/T_GUT < sqrt(N/0.33^2 - 1)` | Exact consequence of project ansatz | KEEP with fail-closed domain |
| CF–Polyakov map | Polyakov diagnostic increases while CF decreases | Unverified operator mapping | HOLD |
| QCD crossover | `293.989 MeV`, not `156.5 MeV`; required `CF=1.386>1` | Rejected as stated | NO-GO |
| Dark-energy candidates | Cosmological-constant scale missed by `9.56e41`; density candidate missed by about `9.58e31` | Rejected | NO-GO |
| Thermal gravity | `DeltaG/G=2.62e-38` at BBN; `2.78` at the GUT scale | Project ansatz; invalid as a small correction at GUT | NO-GO without covariant derivation |
| One-loop RGE | `alpha_s(M_Z)` spans `0.10785–0.15771` for `M_SUSY=1–100 TeV`; fit gives `3.501 TeV` | Established baseline with declared inputs | Calibration only, not TCD prediction |
| Lattice normalization | `beta_10=1.90986` for unit normalization, not `24` | Established algebra | Corrected |
| Carnot efficiency | `0.9991557`, not `0.87` | Established thermodynamics | Corrected |

## Spectral-dimension method validation

The original helper mixed a numerical estimator with a target curve and always returned `flow_observed=True`. That behavior was scientifically invalid. The compatibility target is now labelled `project_hypothesis_not_observation`, and no physical flow is inferred without finite-size and uncertainty analysis.

The final pinned reference benchmark used periodic graphs with known dimensions:

- 1D cycle: mean estimate `0.9582`, absolute error `0.0418` — **PASS**.
- 2D periodic torus with 8,000 walkers: mean estimate `1.9954`, absolute error `0.0046` — **PASS**.

The canonical result is retained in [`results/tcd_spectral_reference_benchmark.json`](results/tcd_spectral_reference_benchmark.json).

An earlier run on a transient, uncommitted estimator revision produced a 2D error of `0.1956` and failed the `0.15` threshold. It could not be reproduced after the code state was frozen, so it is not used as evidence; it remains available for audit provenance at [`results/tcd_spectral_reference_benchmark_initial_transient_failure.json`](results/tcd_spectral_reference_benchmark_initial_transient_failure.json).

An exploratory sensitivity run with 20,000 walkers recovered `d_S=2` in all three tested fit windows with absolute errors below `0.03`. See [`results/tcd_spectral_sensitivity_followup.json`](results/tcd_spectral_sensitivity_followup.json). These results validate the numerical estimator on reference graphs, not the TCD spectral-flow hypothesis.

## Comparison with authoritative evidence

| Topic | Authoritative result | TCD audit classification |
|---|---|---|
| QCD chiral crossover | `156.5 ± 1.5 MeV`, HotQCD, DOI `10.1103/PhysRevD.100.094510`, arXiv `1908.09552` | External reference; TCD formula rejected |
| Scalar glueball | Approximately `1.71 GeV` in quenched lattice calculations, DOI `10.1103/PhysRevD.73.014516` | Reference-calibrated, not predicted |
| QGP viscosity | Model-dependent minimum near the KSS scale; JETSCAPE DOI `10.1103/PhysRevC.103.054904` | TCD curve is an undriven interpolation |
| BBN variation of G | Percent-level cosmological constraint, DOI `10.1103/PhysRevD.101.043533` | TCD value is far below sensitivity and has no covariant derivation |
| Micron fifth force | Current limits remain many orders above the audited bare TCD scale | Claimed `1e-6` resummation rejected |
| Spectral dimension | Qualitative UV reduction toward two appears in CDT and other approaches, DOI `10.1103/PhysRevLett.95.171301` | Similar trend is not evidence for the TCD interpolation |
| Finite-temperature beta function | UV counterterm beta coefficients remain temperature-independent; DOI `10.1103/RevModPhys.53.43` | TCD thermal UV term remains disabled |

Agreement with a value supplied as an input is never counted as confirmation.

## Prediction contract

No implemented TCD observable currently provides all of the following:

1. an independently derived signal and uncertainty;
2. a null hypothesis;
3. immutable inputs excluding the target value;
4. a frozen external likelihood or independent simulation estimator;
5. required sensitivity and a preregistered falsification rule.

The correct prediction status is therefore **INCOMPLETE**.

### Near-term candidate: independent spectral-flow test

The current ansatz predicts the following values before any graph data are generated:

| `T/T*` | Predicted `d_S` |
|---:|---:|
| `0.01` | `3.92343` |
| `0.1` | `3.66732` |
| `1` | `3.00000` |
| `10` | `2.33268` |
| `100` | `2.07657` |

These numbers become falsifiable only after a thermal Spin(10) graph ensemble produces graphs without injecting the target curve. The frozen numerical estimator must use at least 20,000 walkers, declared seeds, finite-size extrapolation, and a single primary fit window selected before unblinding.

**Proposed no-go rule:** reject the interpolation if at least three of the five finite-size-extrapolated estimates differ from the frozen curve by more than `0.15` and their 95% intervals exclude it. This protocol remains incomplete until the thermal graph ensemble and scale map `T ↔ diffusion scale` are implemented.

### Longer-term candidate: scalar glueball mass ratio

A valid candidate is `R_0++ = m_0++ / sqrt(sigma)`, calculated from a graph transfer matrix and zero-momentum plaquette correlator. The external `1.71 GeV` target must be excluded from all inputs. No numerical TCD interval is reported because the required solver does not yet exist.

## Final decisions

- **KEEP:** fail-closed software architecture, assumption ledger, standard one-loop RGE baseline, raw random-walk estimator after independent benchmarking.
- **HOLD:** spectral interpolation and CF–Polyakov map pending independent ensemble derivations.
- **NO-GO:** present QCD crossover formula, dark-energy identifications, torsion-resummed fifth force, thermal UV beta-function correction, and old thermal-gravity magnitude claims.

## Verification commands

```bash
PYTHONPATH=src python3 -m unittest -v tests.test_termo_chromo_dynamics
PYTHONPATH=src python3 -m unittest -v tests.test_tcd_v15_audit_experiments
PYTHONPATH=src python3 -m unittest -v tests.test_spectral_dimension_integrity
PYTHONPATH=src python3 -m unittest -v tests.test_tcd_windows_adapter
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_ift_egr*.py' -v
PYTHONPATH=src python3 scripts/run_tcd_v15_audit_experiments.py
PYTHONPATH=src python3 scripts/run_spectral_dimension_reference_benchmark.py
PYTHONPATH=src python3 scripts/run_spectral_dimension_sensitivity.py
```

## Confidence

- **High:** arithmetic, dimensions, domain boundaries, software contracts, and detection of reference calibration.
- **Medium:** numerical spectral estimator after the 20,000-walker follow-up.
- **Low/speculative:** physical interpretation of graph coherence, CF–Polyakov correspondence, thermal gravity, and TCD as a unified fundamental theory.
