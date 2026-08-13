# Gate 3 — Local Jacobson–Clausius construction and the action for \(P\)

**Status:** internally closed specification of a *prescribed* graph
correction.  
**Validated observational predictions:** 0.  
**This is not a Theory of Everything.**

Implementation: [`src/jacobson_clausius.py`](../src/jacobson_clausius.py).  
Interactive bench: Research Lab → *Jacobson*.

---

## 1. What was open

The TCD ledger entry TCD-E001 is established physics:

> Jacobson's local Clausius construction derives the Einstein equation
> under local-equilibrium, area-entropy, and local-Rindler-horizon
> assumptions.

Its impact was also correct:

> Provides motivation only; it does not derive the graph correction
> \(P(N,T)\).

Open problem 1 of the v16 specification asked for a covariant action
*for any* such correction.  Gate 3 answers that question and nothing
else.  In particular it does **not** produce

\[
P(N,T)=1-\frac{0.33}{\sqrt{N_{\rm eff}(T)}}
\]

from \(\delta Q=T\,dS\).

---

## 2. Established local Clausius (Jacobson 1995)

On every local Rindler horizon, with Unruh temperature \(T=\kappa/2\pi\)
and area entropy \(S=\eta A\) at *constant* \(\eta\), local equilibrium
implies

\[
G_{\mu\nu}+\Lambda g_{\mu\nu}
=\frac{2\pi}{\eta}\,T_{\mu\nu}.
\]

For \(\eta=1/(4G)\) this is Einstein’s equation.  The assumptions are
those of Jacobson, *Phys. Rev. Lett.* **75**, 1260 (1995),
arXiv:`gr-qc/9504004`.

Eling, Guedens and Jacobson (PRL **96**, 121301 (2006),
arXiv:`gr-qc/0602001`) showed that a *non-constant* entropy density
requires a non-equilibrium entropy-production term before the Clausius
argument recovers the correct field equations.  The substitution
\(S\to\eta P A\) inside the 1995 argument is therefore **not** a
derivation of Einstein gravity with \(G_{\rm eff}=G_0/P\).

That illegal step is classified `rejected_as_stated` (TCD-R007 / P12).

---

## 3. Covariant action for any prescribed \(P(x)\)

If a graph correction is given as a positive scalar field that is
**not** varied, the unique diffeomorphism-covariant completion of
“put \(P\) in front of the Einstein–Hilbert / area term” is

\[
S[g;P]
=\frac{1}{16\pi G_0}
\int\mathrm{d}^4x\,\sqrt{-g}\,P(x)\,R[g]
+S_{\mathrm{m}}[g,\psi].
\]

Metric variation (mostly-plus signature, matter minimally coupled) yields

\[
P\,G_{\mu\nu}
+(g_{\mu\nu}\square-\nabla_\mu\nabla_\nu)P
=8\pi G_0\,T_{\mu\nu}.
\]

This is ordinary scalar-tensor algebra with the Brans–Dicke scalar held
fixed.  It holds for **every** \(P>0\).  It does not select the TCD
ansatz.

The algebraic piece \(P G_{\mu\nu}\) is Einstein gravity with
\(G_{\rm eff}=G_0/P\).  The extra terms vanish if and only if
\(\nabla P=0\).

### Dynamical reading (incomplete)

If \(P\) is promoted to an independent scalar one must also specify
\(\omega(P)\) and \(V(P)\):

\[
S[g,P]
=\frac{1}{16\pi G_0}
\int\mathrm{d}^4x\,\sqrt{-g}
\Bigl[
P R-\frac{\omega(P)}{P}(\nabla P)^2-V(P)
\Bigr]
+S_{\mathrm{m}}.
\]

The graph supplies neither function.  A *light* Brans–Dicke field with
constant \(\omega\) is constrained by Cassini/VLBI to
\(\omega\gtrsim 4\times 10^4\).  That bound applies only to the
dynamical reading; it does not constrain a prescribed background
\(P(T)\).  Default \(\omega=0\) as a dynamical theory is already
excluded.

---

## 4. Extra terms on FLRW

Photon temperature after \(e^+e^-\) annihilation satisfies
\(\dot T=-H T\) (declared standard input).  For a homogeneous \(P(T)\)
the 00-equation of the prescribed-\(P\) theory is

\[
3P H^2+3H\dot P=8\pi G_0\,\rho,
\]

so the relative correction to Einstein-with-\(G_{\rm eff}\) is
background-independent:

\[
\varepsilon_F
=\frac{|\dot P|}{H P}
=\frac{T}{P}\Bigl|\frac{\mathrm{d}P}{\mathrm{d}T}\Bigr|.
\]

A preregistered numerical rule (frozen before evaluating the default
ansatz) says that \(G_{\rm eff}=G_0/P\) is an acceptable *infrared
approximation* — never the exact field equation — if
\(\varepsilon_F<0.01\) at both today and BBN.  Passing that rule does
not validate \(P\).

For the TCD ansatz with \(N=10^6\), \(c=0.33\):

| Clock | \(T\) | \(\varepsilon_F\) | IR substitution |
|---|---|---|---|
| today | \(2.35\times 10^{-13}\,\mathrm{GeV}\) | \(\sim 10^{-61}\) | acceptable approximation |
| BBN | \(1\,\mathrm{MeV}\) | \(\sim 10^{-41}\) | acceptable approximation |
| GUT | \(1.03\times 10^{16}\,\mathrm{GeV}\) | \(\sim 2\times 10^{-4}\) | still small |
| Planck | \(1.22\times 10^{19}\,\mathrm{GeV}\) | \(\mathcal{O}(1)\) | **not** acceptable |

Near the ansatz domain wall \(P\to 0^+\) the extra terms diverge and
the implementation fails closed.

---

## 5. What would actually derive \(P\)

All of the following are still missing:

1. a normalized graph ensemble with a continuum limit;
2. an independent area / bipartition entropy, not assigned by hand;
3. a scale map from graph temperature to a physical \(T\);
4. a proof that \(S/(\eta A)\to 1-c/\sqrt{N_{\rm eff}}\) rather than
   another function;
5. a frozen likelihood or a preregistered no-go on that function.

Jacobson 1995 supplies none of these.

---

## 6. How to run

```bash
PYTHONPATH=src python -c "from jacobson_clausius import gate3_jacobson_action; \
import json; print(json.dumps(gate3_jacobson_action()['decisions'], indent=2))"

PYTHONPATH=src python -m unittest -v tests.test_jacobson_clausius
python -m lab   # Jacobson bench
```

---

*v16.1 · August 2026 · fail-closed*
