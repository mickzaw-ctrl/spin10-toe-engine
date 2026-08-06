# IFT-EGR v0.3: Cosmology Closure and Falsifiability Gates

## Status

This document audits technical closure claims for the relational-graph Lambda-CDM research programme. The accompanying module `src/ift_egr_closure.py` implements algebraic and causal-order checks only. It does not claim a derivation of Lambda, a causal GFT condensate, or observational validation.

## Epistemic classification

- **Established physics:** the standard effective LQC Friedmann equation once its quantization convention is fixed; the LQG puncture-area spectrum; elementary finite partial-order axioms; dimensional consistency.
- **Project hypotheses:** horizon punctures encode the graph boundary; Bures information time has a cosmological continuum limit; a causal-order-restricted GFT kernel produces the IFT-EGR background.
- **Unverified assumptions:** GFT condensate quanta equal horizon punctures; a single-mode free GFT profile fixes the Hubble radius; the bounce fixes the late-time integration constant; graph corrections measurably alter CMB or Hubble observables.

## 1. LQC critical density

With

\[
\Delta = 4\sqrt{3}\,\pi\gamma\,\ell_{\rm Pl}^2,
\qquad
\rho_c = \frac{3}{8\pi G\gamma^2\Delta},
\]

one obtains

\[
\frac{\rho_c}{\rho_{\rm Pl}}
=\frac{3}{32\sqrt{3}\,\pi^2\gamma^3}
\approx 0.40937
\quad (\gamma=0.2375).
\]

This reproduces standard effective LQC under the stated convention. It is a consistency check, not a new prediction.

## 2. Isolated-horizon entropy

For punctures carrying spins `j_i`,

\[
\frac{A}{\ell_{\rm Pl}^2}
=8\pi\gamma\sum_i\sqrt{j_i(j_i+1)}.
\]

The independent-puncture degeneracy gives only the upper bound

\[
S_{\rm independent}=\sum_i\log(2j_i+1).
\]

The ratio `log(2j+1)/sqrt(j(j+1))` is maximal at `j=1/2` over positive half-integers. However, `N log 2` is not the complete ABCK/DL entropy: gauge-projection constraints, finite Chern-Simons level, topology, and subleading logarithmic corrections still require explicit state counting.

A topology-sensitive closure must therefore provide a sourced state-counting function

\[
S_{\rm ent}=\log \dim \mathcal H_{\rm boundary}
(A,\gamma,k_{\rm CS},g,\{j_i\}),
\]

not only an independent-puncture ansatz.

## 3. Correct horizon geometry

For a spherical Hubble or apparent horizon,

\[
A_H=4\pi L_H^2,
\]

not `pi L_H^2`. Equating the spherical area to `N_p` equal-spin punctures gives

\[
\frac{L_H}{\ell_{\rm Pl}}
=\sqrt{2\gamma N_p\sqrt{j(j+1)}}.
\]

For `j=1/2`,

\[
\frac{L_H}{\ell_{\rm Pl}}
=\sqrt{\sqrt{3}\gamma N_p}.
\]

The disk-area formula in the supplied closure text overestimates the radius by exactly a factor of two.

## 4. Dimensionally consistent Lambda ansatz

A dimensionally valid HDE-like relation can be written as

\[
\Lambda \ell_{\rm Pl}^2=\frac{\alpha}{S_{\rm ent}},
\]

where `alpha` is dimensionless. With `S_ent proportional to N_p` and `N_p proportional to A_H/l_Pl^2`, this gives `Lambda proportional to 1/L_H^2`. That scaling is an identity once the infrared horizon has been selected; it does not derive `alpha`, choose the horizon, or explain the observed value. The code therefore requires `alpha` explicitly and supplies no default.

## 5. Why the bounce does not fix the classical integration constant

The classical Padmanabhan integration yields, for flat FLRW under its standard assumptions,

\[
H^2=\frac{8\pi G}{3}\rho+C.
\]

The effective LQC equation is

\[
H^2=\frac{8\pi G}{3}\rho\left(1-\frac{\rho}{\rho_c}\right).
\]

At the bounce, the quadratic correction is order unity. Substituting `H=0` and `rho=rho_c` into the classical integrated equation would produce

\[
C=-\frac{8\pi G}{3}\rho_c,
\]

but that substitution is outside the classical equation's validity and would generate a large negative constant rather than the observed positive late-time Lambda. The code therefore refuses to infer `C` in the `quantum_bounce` regime.

A valid closure requires a modified emergence law that reproduces the `rho^2/rho_c` term. Only then may one ask whether a remaining integration constant is fixed by a separate global boundary condition. The bounce condition alone does not do it.

## 6. E-fold gate

The intervals `N_e = 60` and `N_e in [72, 140]` do not overlap. This is a falsification gate only after the latter range is derived for the same perturbation state, pivot scale, reheating history, and likelihood. It must not be treated as universal across all LQC initial states.

Required next calculation:

1. freeze the bounce state and perturbation vacuum;
2. map every mode from the bounce through inflation and reheating;
3. compute scalar power and bispectra from the same parameter point;
4. evaluate Planck likelihoods without fitting the anomaly after unblinding;
5. reject the mechanism if no parameter point satisfies both power-spectrum and bispectrum criteria.

## 7. GFT number is not horizon puncture number

The imported single-mode free-condensate profile

\[
N_{\rm GFT}(\phi)=N_{\min}\cosh\left[
\sqrt{12\pi G}(\phi-\phi_b)\right]
\]

is symmetric and can reproduce a bounce in relational volume. It does not by itself establish

\[
N_{\rm GFT}=N_p,
\]

because bulk GFT quanta and boundary punctures count different structures. Consequently, inserting `N_GFT(phi)` directly into `L(N_p)` is an unverified mapping, and the claimed classical limit `L=1/H` does not follow without a bulk-boundary map.

## 8. Minimal causal-GFT research target

A candidate extension must retain bosonic field statistics while carrying explicit orientation and causal data. The minimal computational object is a transition kernel

\[
K((g_I,\phi,\tau),(g'_I,\phi',\tau')),
\]

restricted so its support is future-directed with respect to a finite partial order. The current code introduces two necessary gates:

- the relation must be reflexive, antisymmetric, and transitive;
- transition weight outside the strict future relation must vanish.

These gates do not solve causal GFT. They prevent an acausal or merely symmetric kernel from being mislabeled as causal.

A complete theory still needs a sourced action, gauge/projector constraints, causal composition law, constraint algebra or amplitudes, and a controlled continuum/refinement limit.

## 9. Falsifiable prediction contract

**Observable:** joint low-multipole CMB power and bispectrum residual generated by one frozen causal-GFT bounce state.

**Signal:** a preregistered vector `Delta C_ell` for `2 <= ell < 30` and the corresponding bispectrum template/amplitude from the same model parameters.

**Null hypothesis:** base Lambda-CDM with the same foreground, calibration, and nuisance treatment describes the data; causal-GFT correction amplitudes are zero.

**Target data:** an official Planck CMB likelihood or a later official CMB likelihood with an immutable data manifest.

**Required sensitivity:** not yet derived. It must be computed from the frozen covariance and likelihood before evaluating the blind-test data.

**Implementation module still required:** `src/ift_egr_perturbations.py`, including bounce-to-recombination mode evolution and bispectrum calculation.

**Status:** `INCOMPLETE`.

## 10. Decision tree

1. **Geometry gate:** use `4 pi L^2`; otherwise stop.
2. **Entropy gate:** implement topology- and projection-aware state counting; otherwise retain only an upper bound.
3. **Bulk-boundary gate:** derive `N_GFT -> N_p`; otherwise do not infer `L(phi)`.
4. **Causality gate:** require zero causal-order violation and a sourced causal action; otherwise retain the symmetric GFT result as non-causal.
5. **Background gate:** derive a modified emergence law reproducing the LQC correction; otherwise do not infer `C` at the bounce.
6. **Perturbation gate:** compute power and bispectrum jointly from one frozen state.
7. **Likelihood gate:** preregister parameters, uncertainty model, and rejection rule before unblinding.

Only completion of all seven gates can turn the model from a consistency construction into a numerical cosmological prediction.

## Confidence and risk

- **High confidence:** the LQC numerical coefficient under the declared convention, the factor-of-four area correction, dimensional checks, and partial-order algebra.
- **Medium confidence:** `j=1/2` dominance within independent-puncture counting.
- **Low confidence:** transfer of that dominance to a complete topology-sensitive boundary Hilbert space.
- **Speculative:** a causal-GFT condensate yields observable CMB corrections or fixes late-time Lambda.

The dominant project risk is a multiple-miracle dependency: causal GFT action, bulk-boundary map, perturbation transfer, and observable signal are all presently open. The recommended fixed constraint is causality: require every candidate kernel to pass the partial-order support gate while leaving interaction details flexible.

## Primary references

- A. Ashtekar, T. Pawlowski, and P. Singh, “Quantum Nature of the Big Bang: Improved dynamics,” arXiv:`gr-qc/0607039`, DOI:`10.1103/PhysRevD.74.084003`.
- A. Ashtekar, J. Baez, A. Corichi, and K. Krasnov, “Quantum Geometry and Black Hole Entropy,” arXiv:`gr-qc/9710007`, DOI:`10.1103/PhysRevLett.80.904`.
- M. Domagala and J. Lewandowski, “Black hole entropy from Quantum Geometry,” arXiv:`gr-qc/0407051`, DOI:`10.1088/0264-9381/21/22/014`.
- T. Padmanabhan, “Emergence and Expansion of Cosmic Space as due to the Quest for Holographic Equipartition,” arXiv:`1206.4916`, DOI:`10.1007/s10714-012-1460-6`.
- D. Oriti, L. Sindoni, and E. Wilson-Ewing, “Emergent Friedmann dynamics with a quantum bounce from quantum gravity condensates,” arXiv:`1602.05881`, DOI:`10.1088/0264-9381/33/22/224001`.

## Rejected shortcuts

The following shortcuts were considered and rejected because they introduce new assumptions instead of closing the derivation:

1. Splitting `N_total = N_pre-pivot + N_pivot + N_reheating` is useful bookkeeping, but it does not prove that `72-140` e-folds are required or compatible with the same frozen perturbation state.
2. An unsourced asymptotic formula for `dim H_boundary(N,j,genus)` is not accepted as topology-sensitive entropy. The exact boundary Hilbert space and projection constraints must be declared first.
3. The Padmanabhan integration constant `C` is not silently reinterpreted as a Bianchi shear coefficient `C/a^6`; these quantities have different equations and physical meanings.
4. Unitary evolution in a scalar clock does not by itself define a causal partial order, exclude closed causal cycles, or solve Lorentzian GFT constraints.
5. A causal-order label does not imply modified photon dispersion. No gamma-ray-burst Lorentz-violation signal is claimed without a derived matter-propagation operator and continuum limit.

## Implementation provenance and reproducibility

- **Repository:** `mickzaw-ctrl/spin10-toe-engine`
- **Working branch:** `feature/ift-egr-v0.2-stabilization`
- **Pinned parent commit:** `4b2977df680dff3740429d98e07e30a158cb8804`
- **Closure implementation:** `src/ift_egr_closure.py`
- **Scientific-contract tests:** `tests/test_ift_egr_closure.py`
- **Assumption ledger:** `docs/IFT_EGR_CLOSURE_ASSUMPTIONS.json`
- **Unified patch SHA-256 before commit:** `aca32ef83d842426e5c4010058d59fb2b1f6245c3db297d1d8a4d70cd8d1e2dd`

Executed validation:

```text
python -m py_compile src/ift_egr_closure.py tests/test_ift_egr_closure.py  PASS
python -m unittest discover -s tests -p 'test_ift_egr*.py' -v             19/19 PASS
scripts/run_ift_egr_validation.py --steps 600 --nodes 32 --edge-modes 6  PASS
git diff --check                                                        PASS
English-only repository artifact scan                                  PASS
```

These results validate implementation contracts and numerical stability only. They do not validate the causal-GFT hypothesis, determine the cosmological constant, or establish agreement with CMB data.

Rollback before commit:

```bash
git restore README.md docs/IFT_EGR_VALIDATION.md
rm docs/IFT_EGR_COSMOLOGY_CLOSURE.md \
   docs/IFT_EGR_CLOSURE_ASSUMPTIONS.json \
   src/ift_egr_closure.py \
   tests/test_ift_egr_closure.py
```

Rollback after commit should use `git revert <closure-commit>` so repository history and provenance remain intact.
