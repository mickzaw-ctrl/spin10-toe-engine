# Relational Spin(10) Programme — Complete Specification v16.1

**Status:** internally closed research programme.  
**Validated observational predictions:** 0.  
**This is not a Theory of Everything.**

The earlier GUH-S10 text claimed operational closure from five axioms and
38 numerical “predictions.” The TCD v15 and IFT-EGR audits showed that most
of those numbers were calibrations, imported references, or dimensionally
invalid expressions. This document replaces that claim with a specification
that can actually be finished: what follows from group theory, what is a
declared input, what has been independently computed, and what remains open.

Implementation: [`src/theory_core.py`](../src/theory_core.py),
[`src/jacobson_clausius.py`](../src/jacobson_clausius.py).  
Interactive bench: Research Lab → *Theory* / *Jacobson*.

---

## 0. What “complete” means here

A programme is **internally complete** when:

1. every axiom is stated and classified;
2. every derived formula names its inputs;
3. every rejected shortcut stays rejected;
4. at least one independent numerical gate has been run without injecting
   its target curve;
5. every proposed observable either meets a five-field prediction contract
   or is marked incomplete.

It is **observationally complete** only after an official likelihood accepts
or rejects a frozen signal. That has not happened. The programme is therefore
internally closed and empirically open.

A **Theory of Everything** requires the necessary conditions T1–T12 in
[`TOE_NECESSARY_CONDITIONS.md`](TOE_NECESSARY_CONDITIONS.md). They are not
met. Internal closure is not a TOE.

---

## 1. Axioms

| ID | Axiom | Status |
|---|---|---|
| A1 | The SM gauge algebra embeds in \(\mathfrak{spin}(10)\). One generation fills a **16**. | Established |
| A2 | Nature contains exactly three copies of that 16. | Unverified input |
| A3 | A finite graph is a discrete stand-in for pregeometric degrees of freedom. | Project hypothesis |
| A4 | A number fitted to a PDG target is not a derivation. | Established (method) |
| A5 | LQC bounce algebra and \(\alpha\)-attractors are imported standard modules. | Established (imported) |

A1 is textbook Lie theory. A2 is *not* implied by A1: Spin(10) supplies one
16, \(E_8\supset\mathrm{SU}(4)\times\mathrm{Spin}(10)\) supplies **four**, and
the formula \(\mathrm{ind}(\not D)=\langle k\rangle-1\) is not the
Atiyah–Singer theorem. Three generations remain an input.

---

## 2. Established substrate

### 2.1 Spin(10) and the Standard Model

\[
\mathbf{16}
\;=\;
\mathbf{10}\oplus\overline{\mathbf{5}}\oplus\mathbf{1}
\quad(\mathrm{SU}(5)),
\qquad
\mathbf{16}
\;=\;
(4,2,1)\oplus(\overline{4},1,2)
\quad(\text{Pati–Salam}).
\]

Hypercharge is the combination
\[
Y=\frac{B-L}{2}+T_{3R}.
\]
At a Spin(10) unification point, in GUT normalisation,
\[
\sin^2\theta_W=\frac{3}{8}.
\]
This is group theory. It is not a prediction for \(\sin^2\theta_W(M_Z)\).

The 16 contains a right-handed neutrino. That is a genuine structural
consequence of A1. Its mass is not fixed.

### 2.2 Breaking

Two standard channels remain available:

- Georgi–Glashow: \(\mathrm{Spin}(10)\to\mathrm{SU}(5)\times\mathrm{U}(1)_\chi\to\mathrm{SM}\)
- Pati–Salam: \(\mathrm{Spin}(10)\to\mathrm{SU}(4)_C\times\mathrm{SU}(2)_L\times\mathrm{SU}(2)_R\to\mathrm{SM}\)

Higgs representations 210, 126, 10 are the usual ones. Thirty-three of the
45 gauge bosons become massive. None of this derives \(M_{\mathrm{GUT}}\).

### 2.3 Gauge running

One- and two-loop SM / MSSM threshold running is a standard calculation.
Couplings at \(M_Z\) are **inputs**. The scale of closest approach of
\((g_1,g_2,g_3)\) is a diagnostic, not a Spin(10) derivation.

The Apex module multiplies \(\alpha_s(M_Z)\) by \(0.9736\) and subtracts
\(6.5504\) from \(1/\alpha_{\mathrm{em}}\) to hit PDG targets. Those knobs
remain classified as **calibration**.

### 2.4 Proton lifetime

The dimension-6 estimate
\[
\tau(p\to e^+\pi^0)
\propto
\frac{M_X^4}{\alpha_{\mathrm{GUT}}^2\,m_p^5}
\]
is standard GUT phenomenology. The hadronic matrix element \(\alpha_H\) is
declared (default \(0.015\,\mathrm{GeV}^3\)). SU(5) uses the same formula.
The contract is incomplete until \(M_{\mathrm{GUT}}\) is frozen without
using low-energy couplings as free inputs.

### 2.5 Type-I seesaw

\[
m_\nu=\frac{m_D^2}{M_R}.
\]
Spin(10) supplies \(\nu_R\). It does not supply \(m_D\) or \(M_R\) without
a Yukawa theory. Both masses are declared inputs.

### 2.6 Imported gravity and inflation

Effective LQC,
\[
H^2=\frac{8\pi G}{3}\rho\Bigl(1-\frac{\rho}{\rho_c}\Bigr),
\qquad
\frac{\rho_c}{\rho_{\mathrm{Pl}}}\approx 0.40937
\quad(\gamma=0.2375),
\]
and the \(\alpha\)-attractor pair \(n_s=1-2/N\), \(r=12\alpha/N^2\) are
standard. Identifying \(\alpha=\dim\mathrm{Spin}(10)/12=3.75\) is a project
hypothesis. The classical Padmanabhan constant cannot be read off at the
bounce; that shortcut stays **rejected**.

---

## 3. Independent gates

### Gate 1 — spectral flow without injecting \(d_S(T)\)

The TCD interpolation
\[
d_S(T)=2+\frac{2}{1+(T/T_*)^\kappa}
\]
is a project ansatz. The independent ensemble is a 3D periodic torus whose
edges rewire with Metropolis weight \(\mathrm{e}^{-\Delta S/T}\) and
action
\[
S=\sum_{\mathrm{edges}}\ell_{\mathrm{Manhattan}}.
\]
The interpolation is compared only after the measurement. The preregistered
rule is: **reject if at least three of the five ratios**
\(\{0.01,0.1,1,10,100\}\) **differ by more than \(0.15\)**.

On the frozen implementation this rule fires (**NO-GO** for the
interpolation as a description of this ensemble). The identification
\(T/T_*=T_{\mathrm{hat}}\) is itself an unverified scale map.

### Gate 2 — mass gap without a 1.71 GeV input

A compact U(1) Wilson theory on a 2D torus yields a dimensionless ratio
\(R=m/\sqrt{\sigma}\) from Wilson loops and a plaquette correlator. The
quenched-QCD number \(1.71\,\mathrm{GeV}\) is not an input. Comparison
with \(m_{0^{++}}/\sqrt{\sigma}\approx 4\) is after-the-fact and does not
validate TCD: 2D U(1) is not 4D SU(3).

A complete glueball prediction still needs a 4D non-Abelian transfer
matrix and a continuum extrapolation.

### Gate 3 — prescribed-\(P\) action without deriving \(P\)

Jacobson’s local Clausius argument derives Einstein’s equation from
\(\delta Q=T\,dS\) under local-equilibrium, local-Rindler, and
*constant* area-entropy assumptions. It does **not** produce the graph
factor \(P(N,T)\).  The illegal step \(S\to\eta P A\Rightarrow
G_{\mu\nu}=8\pi(G_0/P)T_{\mu\nu}\) is rejected as a general field
equation.

For *any* prescribed \(P(x)>0\) the covariant action is

\[
S[g;P]
=\frac{1}{16\pi G_0}
\int\mathrm{d}^4x\,\sqrt{-g}\,P\,R[g]
+S_{\mathrm{m}},
\]

with metric equation

\[
P\,G_{\mu\nu}
+(g_{\mu\nu}\square-\nabla_\mu\nabla_\nu)P
=8\pi G_0\,T_{\mu\nu}.
\]

Extra terms vanish iff \(\nabla P=0\).  On FLRW the relative 00-correction
is \(\varepsilon_F=T|P'(T)|/P\).  A preregistered rule accepts
\(G_{\mathrm{eff}}=G_0/P\) as an *infrared approximation* only if
\(\varepsilon_F<0.01\) at today and at BBN.  For the TCD ansatz with
\(N=10^6\) that IR rule passes; at the Planck temperature
\(\varepsilon_F=\mathcal{O}(1)\).  Neither fact derives \(P\) or
validates a TOE.

Write-up: [`JACOBSON_CLAUSIUS.md`](JACOBSON_CLAUSIUS.md).

### Gate 4 — one action, not a stack

T2 requires gravity and the SM in one action. The classical candidate is

\[
S[g,A,\psi,\Phi]
=
S_{\mathrm{grav}}[g;P]
+S_{\mathrm{YM}}^{\mathrm{Spin}(10)}
+S_{16}
+S_{\mathrm{H}}.
\]

LQC, α-attractors and \(M_Z\)-input RGE are **not terms of \(S\)**.
Writing the formula is syntax. T2 stays **UNMET** while C1 and the
bounce are used as if they were consequences. Write-up:
[`UNIFIED_ACTION.md`](UNIFIED_ACTION.md).

---

## 4. Prediction registry

| ID | Observable | Status | Contract |
|---|---|---|---|
| P1 | \(\sin^2\theta_W=3/8\) at a Spin(10) point | Established | group theory; not a low-energy prediction |
| P2 | existence of \(\nu_R\) | Established | 16 of Spin(10); mass open |
| P3 | \(\tau(p\to e^+\pi^0)\) | Established formula | incomplete: \(M_{\mathrm{GUT}}\) not input-independent |
| P4 | \(m_\nu=m_D^2/M_R\) | Established formula | incomplete: Yukawas not derived |
| P5 | independent \(d_S\) vs HOLD curve | **NO-GO** on this ensemble | 3-of-5 rule, frozen estimator |
| P6 | \(R=m/\sqrt{\sigma}\) on 2D U(1) | Established diagnostic | not a QCD prediction |
| P7 | \(\alpha_{\mathrm{em}}=1/137.036\) from Spin(10) | Calibration | hidden offset \(-6.5504\) |
| P8 | \(N_{\mathrm{gen}}=3\) from Atiyah–Singer / \(E_8\) | Rejected as stated | false theorem / extra breaking |
| P9 | \(\Omega_\Lambda\) from \(T_c^4/M_{\mathrm{Pl}}^2\) | Rejected | wrong dimensions |
| P10 | late-time \(\Lambda\) from the LQC bounce | Rejected | invalid classical substitution |
| P11 | prescribed-\(P\) action \(\int P R\) | Established | metric variation; \(P\) not derived |
| P12 | Einstein with \(G_{\rm eff}=G_0/P\) | **NO-GO** unless \(\nabla P=0\) | extra Hessian terms required |
| P13 | \(P(N,T)\) from local Clausius | Rejected as stated | Jacobson assumes constant \(\eta\) |
| P14 | one action gravity + Spin(10) | Established syntax | T2 unmet: stack still drives predictions |

No row is an observational validation.

---

## 5. What is closed, and what is not

**Closed**

- Spin(10) representation theory and the SM embedding
- the epistemic ledger and fail-closed domains
- Gate 1 as a protocol that does not inject \(d_S(T)\)
- Gate 2 as an estimator that does not import 1.71 GeV
- standard GUT lifetime and seesaw formulae with declared inputs
- Gate 3: prescribed-\(P\) Jordan-frame action and the extra-term theorem

**Not closed**

- a derivation of the cosmological constant
- a derivation of \(\alpha_{\mathrm{em}}\) without calibration
- a derivation of three generations
- a derivation of \(P(N,T)\) from Jacobson or from a graph entropy
- a causal GFT with a bulk–boundary map
- any official-likelihood comparison

**Open problems (in order)**

1. Microscopic derivation of \(P(N,T)\) from a graph entropy.
2. Kinetic term \(\omega(P)\) and potential \(V(P)\) if \(P\) is dynamical.
3. Bulk–boundary map from GFT quanta to isolated-horizon punctures.
4. Yukawa sector that fixes \(m_D\) and \(M_R\) without SM mass inputs.
5. 4D non-Abelian transfer matrix for \(R_{0^{++}}\) with continuum limit.
6. Frozen MEG-II / Hyper-K / Planck likelihoods.

---

## 6. How to run the specification

```bash
PYTHONPATH=src python -c "from theory_core import complete_theory; \
import json; print(json.dumps(complete_theory(fast=True)['gate1_independent_spectral_flow']['decision']))"

PYTHONPATH=src python -m unittest -v tests.test_theory_core
python -m lab   # Theory bench
```

---

*v16.1 · August 2026 · fail-closed*
