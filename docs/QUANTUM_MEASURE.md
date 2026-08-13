# Gate 5 — quantum measure (T3)

**Status:** checklist written; T3 **UNMET**.  
**Validated observational predictions:** 0.  
**This is not a Theory of Everything.**

T3 requires a Hilbert space or a Euclidean measure, handling of gauge
orbits, a continuum / refinement limit, and either reflection positivity
or a Lorentzian reconstruction.

Implementation: [`src/quantum_measure.py`](../src/quantum_measure.py).

---

## Two formulae, one of them defined

**Continuum (notation only)**

\[
Z_{\mathrm{cont}}
=
\frac{1}{\mathrm{Vol}(\mathrm{Diff}\ltimes\mathrm{Gauge})}
\int\mathcal D g\,\mathcal D A\,\mathcal D\psi\,\mathcal D\Phi\;
\mathrm{e}^{i S[g,A,\psi,\Phi]}.
\]

\(\mathcal D g\) is not a defined measure. This line does not construct T3.

**Discrete (intended programme measure)**

\[
Z_{\mathrm{disc}}
=
\sum_{\Gamma}\mu(\Gamma)
\int\prod_e\mathrm{d}\mu_{\mathrm{Haar}}(U_e)
\prod_v\mathrm{d}\psi_v\,\mathrm{d}\Phi_v
\;
\exp\bigl(-S_E[U,\psi,\Phi;\Gamma]+i\theta Q[U]\bigr).
\]

| Ingredient | Status |
|---|---|
| Haar measure on compact Spin(10) | **Established.** Unique bi-invariant probability measure. |
| Wilson integral on a *fixed* finite Γ | **Exists** (bounded integrand, probability Haar). Lattice YM, not gravity. |
| Graph measure \(\mu(\Gamma)\) | **Missing.** |
| Discrete \(S_{16}\) and \(S_H\) | **Missing.** |
| Refinement / continuum with a stable observable | **Missing.** Gate 1 is graphs without gauge fields. |
| Osterwalder–Schrader or a causal reconstruction | **Missing.** A finite partial-order audit is necessary, not sufficient. |

---

## Clauses M1–M6

T3 is MET only if all six are MET.

| ID | Clause | Now |
|---|---|---|
| M1 | Configuration space of Gate 4 is named | MET (syntax) |
| M2 | Normalised measure or projective family | UNMET |
| M3 | Gauge / diffeomorphism orbits | UNMET |
| M4 | Refinement continuum, one stable observable | UNMET |
| M5 | OS positivity or Lorentzian reconstruction | UNMET |
| M6 | Matter (16 + Higgs) in the same \(Z\) | UNMET |

Haar-on-fixed-Γ is not a loophole. It is lattice gauge theory on a frozen
graph. Quantum gravity is the sum over \(\Gamma\) and the continuum.

---

## The four holes, named

| Hole | Candidate | Status |
|---|---|---|
| \(\mu(\Gamma)\) | Boltzmann weight on the finite Gate-1 rewiring class, \(S_{\mathrm{graph}}=\sum \ell_{\mathrm{Manhattan}}\) | Normalisable combinatorics. **Not** a sum over geometries. |
| \(S_H\) | \(\sum_{\langle ij\rangle}\|U_{ij}\Phi_j-\Phi_i\|^2+V(\Phi)\) | Established lattice Higgs on a graph. \(V\) free. |
| \(S_{16}\) | hopping \(\bar\psi_i P_{ij} U_{ij}\psi_j\) | **Incomplete:** no Clifford / soldering form on a random graph. |
| Continuum | freeze one gauge-invariant \(O\), refine twice, demand stability | Protocol only. Not done. Gate 1 is not this limit. |
| OS / Lorentz | OS for cubic compact YM (Osterwalder–Seiler); causal kernel on a poset | OS **does not** apply to a rewired graph. A diamond poset with zero violation is necessary, not a reconstruction. |

---

## What this does not do

- It does not define \(Z\).
- It does not promote Gate 1 to a quantum gravity measure.
- It does not identify GFT quanta with isolated-horizon punctures.
- It does not make T3, or a TOE, true.
