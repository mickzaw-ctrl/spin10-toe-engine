# Independent Audit of the IFT-EGR Cosmology Closure

**Audit date:** 2026-08-06  
**Repository:** `mickzaw-ctrl/spin10-toe-engine`  
**Branch:** `feature/ift-egr-v0.2-stabilization`  
**Audited commit:** `b583b6e1256967efeb8e89f2bc63e00bc35f584d`  
**Verdict:** **CONDITIONAL PASS**

## Scope

This independent audit checks the scientific and numerical contracts introduced by:

- `src/ift_egr_closure.py`;
- `tests/test_ift_egr_closure.py`;
- `docs/IFT_EGR_COSMOLOGY_CLOSURE.md`;
- `docs/IFT_EGR_CLOSURE_ASSUMPTIONS.json`.

It also searches the wider repository for observational claims that are not produced by an implemented perturbation, likelihood, or matter-propagation pipeline.

A conditional pass means that the closure module correctly implements its stated algebraic and causal-order gates. It does **not** mean that IFT-EGR, causal GFT, a value of the cosmological constant, or any claimed CMB/GRB signal has been derived or experimentally validated.

## Audit method

The audit used:

1. direct inspection of equations, units, domain guards, and epistemic labels;
2. independent Python evaluation of numerical coefficients and asymptotic ratios;
3. execution of the closure contract tests;
4. repository-wide searches for unsupported observational claims;
5. comparison with the primary references listed below.

No external measurements, numerical precision, or citations were invented during this audit.

## Findings

### 1. LQC area gap and critical density — PASS

**Classification:** Established physics, conditional on the standard improved-dynamics LQC convention.  
**Confidence:** High.  
**Main uncertainty:** Quantization conventions outside the declared standard area-gap convention.

The implementation uses

\[
\frac{\Delta}{\ell_{\rm Pl}^2}=4\sqrt{3}\pi\gamma,
\qquad
\frac{\rho_c}{\rho_{\rm Pl}}=
\frac{3}{8\pi\gamma^2(\Delta/\ell_{\rm Pl}^2)}.
\]

For `gamma = 0.2375`, the independent evaluation gives:

```text
Delta/l_Pl^2 = 5.16932818806752
rho_c/rho_Pl = 0.40937381647831045
```

The implementation is located at `src/ift_egr_closure.py:48-80`. The value is inherited from standard effective LQC and is not a new IFT-EGR prediction.

### 2. Puncture area and entropy counting — CONDITIONAL PASS

**Classification:** Puncture area is established physics; the independent-puncture entropy is an upper bound; its use as IFT-EGR graph entropy is a project hypothesis.  
**Confidence:** High for the area spectrum and upper-bound status; low for a topology-sensitive IFT-EGR entropy.  
**Main uncertainty:** The boundary Hilbert space, gauge projection, Chern-Simons level, and topology have not been derived for the project graph.

The puncture area

\[
A_j=8\pi\gamma\ell_{\rm Pl}^2\sqrt{j(j+1)}
\]

is implemented at `src/ift_egr_closure.py:83-90`.

The expression

\[
S_{\rm independent}=\sum_i\log(2j_i+1)
\]

at `src/ift_egr_closure.py:93-106` is correctly documented as an upper bound before projection and topology constraints. For equal `j=1/2` punctures it reduces to `N log 2`, but this is not the complete ABCK/DL microcanonical entropy.

The ratio

\[
\frac{\log(2j+1)}{\sqrt{j(j+1)}}
\]

is maximal at `j=1/2` over the tested positive half-integers. Extending this result to an exact topology-sensitive boundary state count remains unverified.

### 3. Spherical horizon geometry — PASS

**Classification:** Established geometry combined with the declared puncture-area spectrum.  
**Confidence:** High.  
**Main uncertainty:** Whether the project boundary should physically be identified with the selected spherical apparent/Hubble horizon.

For a spherical horizon,

\[
A_H=4\pi L_H^2.
\]

Equating this to `N_p A_j` gives

\[
\frac{L_H}{\ell_{\rm Pl}}
=\sqrt{2\gamma N_p\sqrt{j(j+1)}}.
\]

For `j=1/2`,

\[
\frac{L_H}{\ell_{\rm Pl}}=
\sqrt{\sqrt{3}\gamma N_p}.
\]

The implementation at `src/ift_egr_closure.py:127-144` is correct. Using `A=pi L^2` instead would overestimate the radius by exactly a factor of two.

### 4. Dimensionally consistent Lambda ansatz — CONDITIONAL PASS

**Classification:** Dimensional identity plus project hypothesis.  
**Confidence:** High for dimensions and inverse-area scaling; speculative as a determination of the cosmological constant.  
**Main uncertainty:** The dimensionless coefficient and infrared horizon are not derived.

The function at `src/ift_egr_closure.py:147-157` implements

\[
\Lambda\ell_{\rm Pl}^2=\frac{\alpha}{S}.
\]

This is dimensionally consistent when entropy is dimensionless. If `S` is proportional to horizon area, it reproduces `Lambda proportional to 1/L_H^2`. That scaling does not determine `alpha`, select the correct horizon, or explain the observed value of Lambda. Requiring the coefficient explicitly is therefore the correct fail-closed behavior.

### 5. Padmanabhan integration constant at the LQC bounce — PASS

**Classification:** Rejection of an invalid assumption.  
**Confidence:** High.  
**Main uncertainty:** A modified emergence law reproducing the LQC correction has not been derived.

The classical integrated relation

\[
H^2=\frac{8\pi G}{3}\rho+C
\]

cannot be imposed at an LQC bounce where the correction

\[
1-\frac{\rho}{\rho_c}
\]

is order unity. The guard at `src/ift_egr_closure.py:160-187` correctly rejects non-classical regimes.

An intentionally invalid classical substitution of `H=0` and `rho=rho_c` would give, in Planck units,

```text
C_invalid = -3.4295620651207366
```

This large negative value is a diagnostic of regime misuse, not a derivation of the late-time cosmological constant. The Padmanabhan constant must not be silently reinterpreted as an anisotropic shear coefficient proportional to `a^-6`.

### 6. E-fold interval 60 versus 72-140 — OPEN

**Classification:** Unverified assumption.  
**Confidence:** High that the literal intervals do not overlap; low that they describe the same physical quantity and frozen model state.  
**Main uncertainty:** Pivot scale, bounce state, perturbation vacuum, reheating history, and likelihood are not fixed by one immutable parameter manifest.

The interval gate at `src/ift_egr_closure.py:190-205` correctly finds no overlap between the point interval `[60, 60]` and `[72, 140]`.

This is not yet a falsification result. The claimed `72-140` range must first be derived for the same definitions and model inputs as the document's `N_e=60`. Splitting total expansion into pre-pivot, observable, and reheating epochs is bookkeeping, not a derivation of either range.

### 7. Free GFT profile and bulk-boundary map — CONDITIONAL PASS

**Classification:** The free single-mode GFT condensate profile is literature-based; identifying bulk GFT quanta with horizon punctures is an unverified assumption.  
**Confidence:** Medium for the profile under its restricted approximation; speculative for `N_GFT = N_p`.  
**Main uncertainty:** Interactions, multimode effects, causal labels, and the bulk-boundary map.

The module represents the restricted profile

\[
N_{\rm GFT}(\phi)=N_{\min}\cosh
\left[\sqrt{12\pi G}(\phi-\phi_b)\right].
\]

The implementation explicitly states that this profile neither identifies GFT quanta with horizon punctures nor encodes a causal partial order. Therefore `N_GFT(phi)` cannot determine `L(phi)` until a sourced bulk-boundary map is supplied.

### 8. Partial-order and causal-kernel gates — CONDITIONAL PASS

**Classification:** Finite partial-order algebra is established mathematics; its use as a causal-GFT kernel gate is a project hypothesis.  
**Confidence:** High for the finite-matrix audit; medium that zero forbidden support is a useful necessary condition; low that it is sufficient for causal quantum gravity.  
**Main uncertainty:** Lorentzian amplitudes, composition, gauge constraints, continuum/refinement limit, and matter propagation.

The implementation checks reflexivity, antisymmetry, and transitivity at `src/ift_egr_closure.py:208-219`. It then measures transition weight outside the strict future relation at `src/ift_egr_closure.py:222-241`.

A zero violation fraction is necessary for the declared finite-kernel convention but is not sufficient to establish a causal GFT, exclude all continuum causal pathologies, or derive Lorentz-invariant matter propagation.

## Reproducible numerical checks

The independent calculations used the following Python expressions:

```python
import math

gamma = 0.2375
delta = 4.0 * math.sqrt(3.0) * math.pi * gamma
rho_c = 3.0 / (8.0 * math.pi * gamma**2 * delta)
legacy_C = -(8.0 * math.pi / 3.0) * rho_c

print(delta)
print(rho_c)
print(legacy_C)
```

Expected output:

```text
5.16932818806752
0.40937381647831045
-3.4295620651207366
```

The geometric check is:

```python
correct = math.sqrt(math.sqrt(3.0) * gamma)
legacy = 2.0 * correct
print(legacy / correct)
```

Expected output:

```text
2.0
```

## Code-quality findings

1. `_positive_finite` at `src/ift_egr_closure.py:41-45` converts values with `float(value)`. Consequently, `True` is accepted as `1.0`. The public scientific scalar inputs should explicitly reject `bool`, as `spherical_horizon_radius_planck` already does for `puncture_count` at lines `138-142`.
2. The test module imports `ift_egr_closure` directly. Reproducible execution currently requires `PYTHONPATH=src`; this is acceptable when documented but should remain explicit in CI/HPC commands.
3. The wording around the legacy `A=pi L^2` expression should consistently call it a disk-area substitution, not a spherical horizon area.

These findings do not invalidate the current numerical results. The first is an input-validation defect; the other two are reproducibility and documentation issues.

## Unsupported observational claims found outside the closure module

The repository still contains observational claims that are not generated by an implemented perturbation, bispectrum, likelihood, or matter-propagation pipeline. Examples include:

- hard-coded `f_NL = 14.518` in `tests/testy_eksperymentalne.py:26` and related scripts/documents;
- an approximately `10 ms` GRB delay printed by `tests/testy_eksperymentalne.py:224`;
- claims that `B_TTB` is a unique LiteBIRD signature in `tests/testy_eksperymentalne.py:45-54`;
- the statement that this is the most testable ToE model in history at `tests/testy_eksperymentalne.py:419` and duplicated manifests.

**Classification:** Unverified assumptions presented too strongly.  
**Confidence:** High.  
**Main uncertainty:** No derived continuum matter operator, perturbation transfer solver, bispectrum estimator, immutable data manifest, covariance, or official likelihood is connected to these values.

These values must not be described as validated predictions. An unsupported causal-order label also does not imply modified photon dispersion, a GRB time delay, a CMB suppression, or a nonzero tensor bispectrum.

## Falsifiable prediction status

No complete IFT-EGR observational prediction currently satisfies all required fields.

A future prediction must provide:

- the observable and a numerically frozen signal or interval;
- the null hypothesis;
- the target experiment or immutable official dataset;
- the required sensitivity derived from a covariance/likelihood;
- the implementing simulation module;
- an assumption ledger and repository provenance.

Until those fields exist, the CMB/GRB causal-GFT prediction status is **INCOMPLETE**.

## Prioritized corrections

1. Add strict boolean rejection for all public scalar physics inputs and regression tests for `True`/`False`.
2. Quarantine or relabel hard-coded `f_NL`, GRB-delay, and `B_TTB` outputs as unverified toy diagnostics.
3. Keep `PYTHONPATH=src` explicit in every local, CI, and HPC audit command, or package the module consistently.
4. Add property-based tests for partial orders, invalid matrices, and causal-kernel support.
5. Do not implement a CMB/GRB prediction until a sourced causal-GFT action, bulk-boundary map, continuum matter operator, and frozen likelihood contract exist.

## Final verdict

**CONDITIONAL PASS.**

The audited closure module correctly encodes the LQC coefficient under its declared convention, puncture-area algebra, the spherical-horizon correction, dimensional Lambda scaling, the rejection of classical bounce matching for `C`, interval overlap, and finite partial-order gates.

The module does not solve the open causal-GFT problem and does not validate any observational signal. The most important repository-level risk is that older hard-coded toy outputs are still described as predictions or confirmations. Those claims require a separate corrective patch and provenance review.

## Primary references

- A. Ashtekar, T. Pawlowski, and P. Singh, “Quantum Nature of the Big Bang: Improved dynamics,” arXiv:`gr-qc/0607039`, DOI:`10.1103/PhysRevD.74.084003`.
- A. Ashtekar, J. Baez, A. Corichi, and K. Krasnov, “Quantum Geometry and Black Hole Entropy,” arXiv:`gr-qc/9710007`, DOI:`10.1103/PhysRevLett.80.904`.
- M. Domagala and J. Lewandowski, “Black hole entropy from Quantum Geometry,” arXiv:`gr-qc/0407051`, DOI:`10.1088/0264-9381/21/22/014`.
- T. Padmanabhan, “Emergence and Expansion of Cosmic Space as due to the Quest for Holographic Equipartition,” arXiv:`1206.4916`, DOI:`10.1007/s10714-012-1460-6`.
- D. Oriti, L. Sindoni, and E. Wilson-Ewing, “Emergent Friedmann dynamics with a quantum bounce from quantum gravity condensates,” arXiv:`1602.05881`, DOI:`10.1088/0264-9381/33/22/224001`.
