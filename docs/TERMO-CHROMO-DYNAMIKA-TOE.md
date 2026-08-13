# Thermo-Chromo-Dynamics v15.0

**An audited Spin(10) research reinterpretation — Publication VIII**

**Author:** Michal Slusarczyk — SHZ Quantum Technologies
**Initial proposal:** 2026-07-20
**Audited implementation:** 2026-08-06
**Engine status:** Research prototype; not a validated Theory of Everything

## 1. Research thesis

The TCD programme asks whether Spin(10) link variables on a relational graph can support one statistical language for three sectors:

- **Thermo:** graph ensembles, entropy, and Jacobson-inspired emergent gravity;
- **Chromo:** finite-temperature non-Abelian diagnostics such as Wilson and Polyakov loops;
- **Dynamics:** renormalization-group flow and a temperature-labelled spectral-dimension ansatz.

This is a **project hypothesis**. Spin(10) contains the Standard Model gauge group, but that group-theoretic fact does not establish that Spin(10) is a “thermalization group,” that confinement equals holography, or that graph temperature is cosmic time.

## 2. Epistemic boundary

### Established physics

1. Jacobson's local Clausius argument derives Einstein's equation under local Rindler-horizon, local-equilibrium, and area-entropy assumptions.
2. Wilson loops, Polyakov loops, and finite-temperature QCD are standard gauge-theory constructs. In physical QCD with dynamical quarks, the transition near 156 MeV is a crossover and the Polyakov loop is not an exact order parameter.
3. One-loop gauge running and SM/MSSM threshold matching are standard perturbative baselines within their validity domains.
4. The KSS result `eta/s = 1/(4 pi)` applies to a class of strongly coupled holographic theories; it is not an exact universal QCD prediction.

### Project hypotheses

1. `P(N,T)=1-0.33/sqrt(N_eff)` is a graph-coherence ansatz.
2. `G_eff=G0/P` is a proposed effective mapping, not a derivation from a covariant action.
3. `CF(L)` is a toy inverse mapping from a logistic Polyakov diagnostic to graph causal fraction.
4. `d_S(T)=2+2/[1+(T/T*)^kappa]` is an interpolation, not a heat-kernel derivation.
5. The piecewise `w(T)` history is a toy schedule and cannot replace a multicomponent cosmological evolution.

### Rejected as stated

The original claims for the dark-energy scale, QCD crossover formula, fifth-force resummation, BBN Newton correction, lattice coupling normalization, Carnot efficiency, and “40/40 validation” fail dimensional, numerical, or provenance gates. Their exact audits are documented below and enforced by tests.

## 3. Thermal-gravity sector

Jacobson's established local relation is

\[
\delta Q=T\,dS,
\qquad
T=\frac{\hbar a}{2\pi k_B c}.
\]

The TCD modification

\[
S=\frac{k_B A}{4\ell_P^2}P(N,T),
\qquad
P(N,T)=1-\frac{0.33}{\sqrt{N_{\rm eff}(T)}}
\]

is a project hypothesis. Gate 3 (`src/jacobson_clausius.py`) now writes the
covariant action for *any prescribed* \(P(x)>0\),

\[
S[g;P]=\frac{1}{16\pi G_0}\int\mathrm{d}^4x\,\sqrt{-g}\,P\,R+S_{\mathrm{m}},
\]

whose metric equation contains the extra terms
\((g_{\mu\nu}\square-\nabla_\mu\nabla_\nu)P\). Pure Einstein gravity with
\(G_{\rm eff}=G_0/P\) follows only when \(\nabla P=0\). Jacobson 1995 still
does not derive the function \(P(N,T)\). See
[`JACOBSON_CLAUSIUS.md`](JACOBSON_CLAUSIUS.md).

The implementation fails closed when `P<=0` instead of clipping the result. High-temperature points outside the ansatz domain are reported as such.

## 4. Chromodynamic sector

For a representation `R`, the Wilson diagnostic is

\[
W_R(C)=\frac{1}{d_R}
\left\langle\mathrm{Tr}_R\prod_{(ij)\in C}U_{ij}\right\rangle.
\]

The code implements transparent toy area/perimeter laws with the conversion

\[
1\;\mathrm{fm}=5.0677307\;\mathrm{GeV}^{-1}.
\]

The logistic Polyakov curve and the mapping from `1-L(T)` to causal fraction are toy parametrizations. `CF` is not called the Polyakov loop: in the supplied mapping it is anti-correlated with `L`.

The QCD crossover value `156.5 MeV` is an external lattice-QCD reference input. It is not predicted by the module.

## 5. QCD crossover formula audit

The supplied formula was

\[
T_c=\Lambda_{\rm QCD}\frac{\sqrt{P(N)}}{CF}.
\]

Using `Lambda_QCD=0.217 GeV`, `P(10^6)=0.99967`, and `CF=0.738` gives

\[
T_c\simeq0.294\;\mathrm{GeV},
\]

not `0.156 GeV`. The formula is therefore rejected. The lattice value remains reference data only.

## 6. Spectral dimension

The implemented ansatz is

\[
d_S(T)=2+\frac{2}{1+(T/T_*)^\kappa},
\qquad
T_*=1.22\times10^{19}\;\mathrm{GeV},
\quad \kappa=0.7.
\]

It satisfies

\[
d_S(0)=4,
\qquad
d_S(T_*)=3,
\qquad
d_S(T\rightarrow\infty)=2.
\]

The original statement that `d_S=2` at `T=T*` was incorrect. Moreover, spectral dimension is normally defined from return probabilities versus diffusion time; identifying diffusion scale with physical temperature requires a graph heat-kernel derivation that is not yet available.

## 7. RGE treatment

The default implementation now uses a one-loop SM/MSSM threshold baseline:

\[
\alpha_i^{-1}(M_Z)=\alpha_{\rm GUT}^{-1}
+\frac{b_i^{\rm MSSM}}{2\pi}\ln\frac{M_{\rm GUT}}{M_{\rm SUSY}}
+\frac{b_i^{\rm SM}}{2\pi}\ln\frac{M_{\rm SUSY}}{M_Z}.
\]

The proposed term

\[
\beta_i^{\rm thermo}=
\frac{g_i^3}{(4\pi)^2}c_i
\left(\frac{T}{M_{\rm SUSY}}\right)^2
\]

is retained only as an isolated diagnostic. It is disabled by default because finite-temperature screening does not by itself modify the vacuum ultraviolet beta function, and the cosmological relation between `T` and renormalization scale `mu` has not been derived.

If `alpha_GUT^-1=24`, then

\[
\frac{1}{g_{\rm GUT}^2}
=\frac{1}{4\pi\alpha_{\rm GUT}}
\simeq1.91,
\]

not `24`. A lattice Wilson-action beta may contain additional group-dependent normalization, which must be declared explicitly.

## 8. Dark-energy scale audit

The original relation

\[
\frac{T_c^4}{M_{\rm Pl}^2}
\]

has units `GeV^2`, not energy-density units `GeV^4`. For the declared inputs,

```text
T_c^4                              = 5.999e-4 GeV^4
T_c^4/M_Pl^2                       = 4.030e-42 GeV^2
rho_DE/Mbar_Pl^2 reference         = 4.216e-84 GeV^2
candidate/reference Lambda ratio   = 9.559e41
T_c^4 exp(-1/alpha_GUT)            = 2.395e-15 GeV^4
instanton/reference density ratio  = 9.579e31
```

No calibration to `Omega_Lambda=0.685` is applied. The original hard-coded calibration has been removed. TCD does not currently explain dark energy.

## 9. Equation-of-state schedule

The original implementation set `w=-1` below `1 keV`, which would incorrectly make vacuum energy dominate before recombination and structure formation. The audited toy schedule is:

- `w=-0.99` only in the declared high-temperature inflationary toy branch;
- `w=1/3` through QCD, BBN, and the radiation era down to an order-of-magnitude matter-radiation equality scale;
- `w=0` in a late matter toy branch;
- `w=-1` only below a late-time dark-energy threshold.

Temperature alone is not a complete cosmic clock, and a physically valid model must evolve radiation, matter, and vacuum densities simultaneously.

## 10. Fifth-force audit

The bare ansatz gives

\[
\alpha_5^{\rm bare}=
\left(\frac{\Lambda_{\rm QCD}}{M_{\rm Pl}}\right)^2.
\]

Including the supplied `exp(CF)` and hidden-generator factor still leaves the result below approximately `1e-37`. Raising it to `1e-6` requires more than thirty orders of magnitude of unexplained enhancement. The audited engine returns `None` for the resummed value and marks the prediction incomplete.

A complete prediction requires a mediator, action, coupling to matter, range, screening mechanism, and comparison with a named experimental likelihood.

## 11. Glueball and viscosity diagnostics

The scalar-glueball reference mass and QCD crossover temperature are external inputs. Rescaling a reference mass by `1/P(N)` is a graph diagnostic, not an independent lattice prediction.

Likewise, the implemented `eta/s(T)` curve is a phenomenological interpolation above the KSS value. Without a TCD stress-tensor correlator and uncertainty model, agreement with heavy-ion inference cannot validate TCD.

## 12. Newton-coupling audit

The supplied ansatz

\[
\frac{\Delta G}{G}=
\left(\frac{T}{T_{\rm GUT}}\right)^2\frac{125}{45}
\]

gives

```text
DeltaG/G today (T=2.35e-13 GeV) = 1.446e-57
DeltaG/G at BBN (T=1 MeV)       = 2.618e-38
```

It does not yield `1e-32` today or `1e-2` at BBN. Passing a BBN upper bound with an almost-zero input ansatz is not an observational confirmation.

## 13. Carnot-cycle audit

For the declared reservoirs,

\[
\eta_{\rm Carnot}=1-\frac{T_{\rm GUT}}{M_{\rm Pl}}
\simeq0.99916,
\]

not `0.87`. A cosmological bounce is also not shown to be a reversible two-reservoir heat engine. CPT symmetry does not imply zero coarse-grained entropy production over a cycle.

The Carnot interpretation remains an unverified analogy and is not used as an engine prediction.

## 14. Statistical action

A minimally consistent schematic Euclidean ensemble would distinguish graph multiplicity, Euclidean gauge action, and the topological phase:

\[
Z_{\rm TCD}=\sum_{\mathcal G}e^{S_{\rm graph}[\mathcal G]}
\int\mathcal DU\;
\exp\left[-S_E[U;\mathcal G]+i\theta Q[U]\right].
\]

This expression is still incomplete. The graph measure, gauge fixing, representation content, reflection positivity, topological charge discretization, and continuum limit must be supplied before it defines a quantum theory.

## 15. Status of proposed observables

| Item | Current implementation | Epistemic status | Missing prediction fields |
|---|---|---|---|
| TCD-1 QCD crossover | External lattice reference | Incomplete | Independent TCD calculation and uncertainty |
| TCD-2 `eta/s` | Toy interpolation | Project hypothesis | Stress-tensor correlator and heavy-ion likelihood |
| TCD-3 fifth force | Bare scale audit only | Incomplete | Mediator, range, resummation, experiment likelihood |
| TCD-4 glueball | Reference-calibrated scaling | Project hypothesis | Independent spectrum calculation |
| TCD-5 `DeltaG/G` | Direct ansatz evaluation | Project hypothesis | Covariant gravity model and BBN likelihood |
| Axion, gluino, `f_NL`, `eta_B` | No derivation | Unverified | Implementing modules and immutable inputs |
| `Omega_Lambda-T_c` relation | Dimensionally rejected | Rejected | New dimensionally valid mechanism |

No item currently satisfies a complete falsifiable-prediction contract consisting of observable, frozen signal or interval, null hypothesis, target dataset, required sensitivity, implementation module, and immutable provenance.

## 16. Software architecture

- `src/termo_chromo_dynamics.py` — gated research diagnostics with preserved public classes;
- `tests/test_termo_chromo_dynamics.py` — dimensional, numerical, status, and regression contracts;
- `scripts/demo_termo_chromo_dynamics.py` — English CLI that reports scientific status;
- `src/windows_package/shzspin10/engine.py` — compatibility adapter with no fabricated fallback values;
- `docs/TCD_ASSUMPTION_LEDGER.json` — machine-readable epistemic ledger.

The public entry point remains:

```python
from termo_chromo_dynamics import ThermoChromoDynamicsEngine

report = ThermoChromoDynamicsEngine(
    N=10**6,
    M_SUSY_GeV=5000.0,
).run_full_tcd_simulation()
```

The report states `PROJECT HYPOTHESIS — NOT A VALIDATED TOE`, disables thermal RGE corrections by default, and sets the `40/40` claim to `False`.

## 17. Falsifiability roadmap

1. Derive a normalized graph ensemble and measure rather than assigning graph entropy heuristically.
2. Construct an operator map between graph causal observables and gauge-theory observables; correlation is not identity.
3. Derive `d_S` from return probabilities on generated graph ensembles and test refinement stability.
4. The prescribed-`P` action is now specified (Gate 3). Still missing: a microscopic derivation of `P(N,T)` and one frozen BBN/CMB likelihood for the extra terms.
5. Produce one independent observable without importing its target value as a constant.

Only after one item passes all five stages should it be promoted from diagnostic to prediction.

## 18. Primary references

- T. Jacobson, “Thermodynamics of Spacetime,” arXiv:`gr-qc/9504004`, DOI:`10.1103/PhysRevLett.75.1260`.
- K. G. Wilson, “Confinement of Quarks,” DOI:`10.1103/PhysRevD.10.2445`.
- A. M. Polyakov, “Thermal Properties of Gauge Fields and Quark Liberation,” DOI:`10.1016/0370-2693(78)90737-2`.
- A. Bazavov et al., “Equation of state in (2+1)-flavor QCD,” arXiv:`1908.09552`, DOI:`10.1103/PhysRevD.100.094510`.
- P. Kovtun, D. Son, and A. Starinets, “Viscosity in Strongly Interacting Quantum Field Theories,” arXiv:`hep-th/0405231`, DOI:`10.1103/PhysRevLett.94.111601`.
- Y. Chen et al., “Glueball spectrum and matrix elements on anisotropic lattices,” arXiv:`hep-lat/0510074`, DOI:`10.1103/PhysRevD.73.014516`.
- S. Carlip, “Dimension and Dimensional Reduction in Quantum Gravity,” arXiv:`1705.05417`, DOI:`10.1088/1361-6382/aa8535`.
- L. Dolan and R. Jackiw, “Symmetry Behavior at Finite Temperature,” DOI:`10.1103/PhysRevD.9.3320`.
- S. Weinberg, “The Cosmological Constant Problem,” DOI:`10.1103/RevModPhys.61.1`.

## 19. Confidence statement

- **High confidence:** dimensional audits, arithmetic corrections, API status gates, and rejection of hidden calibration.
- **Medium confidence:** usefulness of Wilson/Polyakov and spectral-flow functions as diagnostics.
- **Low confidence:** physical relation between graph thermodynamics, causal fraction, confinement, and emergent gravity.
- **Speculative:** TCD as a unified fundamental theory or source of new observational predictions.
