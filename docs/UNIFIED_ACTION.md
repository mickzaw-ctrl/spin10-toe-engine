# Gate 4 — one dynamics

**Status:** classical candidate specified; T2 **UNMET**.  
**Validated observational predictions:** 0.  
**This is not a Theory of Everything.**

T2 requires gravity and the Standard Model in **one** action or measure.
A stack of imported LQC + α-attractors + SM/MSSM RGE is not that action.

Implementation: [`src/unified_action.py`](../src/unified_action.py).

---

## The continuum candidate

\[
S[g,A,\psi,\Phi]
=
S_{\mathrm{grav}}[g;P]
+
S_{\mathrm{YM}}[A,g]
+
S_{16}[\psi,A,g]
+
S_{\mathrm{H}}[\Phi,A,g,\psi].
\]

| Term | Formula | Status |
|---|---|---|
| \(S_{\mathrm{grav}}\) | \((1/16\pi G_0)\int\sqrt{-g}\,P\,R\) | Einstein–Hilbert if \(P=1\); Gate 3 if \(P(x)\) prescribed. \(P(N,T)\) not derived. |
| \(S_{\mathrm{YM}}\) | \(-\frac{1}{2g_{10}^2}\int\sqrt{-g}\,\mathrm{Tr}(F^2)\), \(A\in\Omega^1(\mathfrak{spin}(10))\) | Established. 45 bosons; 12 massless after breaking. |
| \(S_{16}\) | \(\sum_{a=1}^{N_{\mathrm{gen}}}\int\sqrt{-g}\,\bar\psi_a i\not D\psi_a\), \(\psi\in\mathbf{16}\) | One 16 is A1. \(N_{\mathrm{gen}}=3\) is an input. |
| \(S_{\mathrm{H}}\) | kinetic terms for \(\mathbf{10},\mathbf{126},\mathbf{210}\) \(-\,V(\Phi)+Y(\psi,\Phi)\) | Standard GUT Higgs. \(V\) and \(Y\) are free. |

This is textbook **GR + Spin(10) GUT**. Writing it is the *syntax* of T2.

---

## Not in \(S\)

| Module | Why it is not a term of \(S\) |
|---|---|
| LQC \(H^2\propto\rho(1-\rho/\rho_c)\) | Holonomy correction, not a variation of \(S\). |
| α-attractor with \(\alpha=45/12\) | \(\alpha\) is not a coupling of \(S\). \(n_s=1-2/N\) is not a consequence. |
| RGE from \(M_Z\) | Beta functions can be the IR of \(S\), but \(M_Z\) couplings are inputs. |
| TCD \(P=1-0.33/\sqrt{N_{\mathrm{eff}}}\) | Not a solution of \(S\). |

---

## What follows, and what does not

**Follows from \(S\)** (group theory / standard GUT): \(\sin^2\theta_W=3/8\) at a Spin(10) point; \(\nu_R\) in each 16; dim-6 \(B\) violation *after* breaking, with \(M_X\) from \(\langle\Phi\rangle\); seesaw *structure*.

**Does not follow:** C1 \(n_s\) (α-attractors); LQC bounce; \(\alpha_{\mathrm{em}}=1/137\); \(N_{\mathrm{gen}}=3\); implemented \(\tau_p\) that uses RGE \(M_{\mathrm{GUT}}\).

---

## Preregistered T2 rule

T2 is MET only if

1. one action or measure is specified,
2. every claimed fundamental prediction is a consequence of it,
3. LQC, α-attractors and \(M_Z\)-input RGE are derived as limits or withdrawn.

Clause (1) is now true for the classical candidate.  
Clauses (2) and (3) are false. **T2 stays UNMET.**

A quantum measure for the same fields is T3 and is still missing.
