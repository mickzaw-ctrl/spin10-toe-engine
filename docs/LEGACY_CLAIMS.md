# Legacy marketing table — audited

**Status:** every row classified.  
**TOE-validated observational predictions:** 0.  
**This is not a Theory of Everything.**

The v8–v14 README table (and the paste that listed MEG-II, Planck PR4,
BICEP/Keck, Hyper-K, CASPEr, LISA, …) is software history.  The labels
“⏳ w zasięgu” / “porównanie starszych wersji” are not measurements.

Implementation: [`src/observational_confrontation.py`](../src/observational_confrontation.py)
rows **C4–C23**.  Frozen numbers: [`OBSERVATIONAL_CARD.json`](OBSERVATIONAL_CARD.json).

Confrontation verdicts: `compatible` · `not_excluded` · `excluded` ·
`circular` · `incomplete` · `rejected_formula`.

| ID | Observable | Legacy claim | Published number used here | Verdict |
|---|---|---|---|---|
| C1 | \(n_s\), \(N\) from reheating | not the marketing band | \(0.9682\pm0.0032\) Planck PR4 proxy | **compatible** for α-attractor + instant reheating (\(N\approx57.47\Rightarrow n_s\approx0.9652\)). Not TOE. |
| C1b | \(n_s\) at hand \(N=60\) | \(0.9667\) | same Planck proxy | **circular** |
| C23 | legacy band \(0.9629\)–\(0.9667\) | invert \(N=2/(1-n_s)\in[53.91,60.06]\) | same Planck proxy | **circular by construction** |
| C2 | \(r\) | 0.0125 at \(N=60\) | \(r<0.036\) BK18 | **not excluded**; an upper limit cannot confirm |
| C4 | BR(\(\mu\to e\gamma\)) | \(8\times10^{-14}\) | \(<3.1\times10^{-13}\) MEG-II+MEG | **not excluded** · **incomplete** (no loop) |
| C5 | \(\eta_B\) | \(6.11\times10^{-10}\) | \(6.12\times10^{-10}\) Planck+BBN card | **incomplete** (no Boltzmann solver) |
| C7 | \(\alpha_s(M_Z)\) | “running −0.0006” / 0.118 | PDG 0.1180 | **circular** / C22 **incomplete** |
| C9 | \(1/\alpha_{\mathrm{em}}\) | 1/137.036 | CODATA | **circular** (hidden −6.5504) |
| C11 | \(M_{\mathrm{GUT}}\) | \(1.03\times10^{16}\,\mathrm{GeV}\) | — | **circular** diagnostic |
| C12 | \(\sin^2\theta_W\) | 0.3779 | group theory \(3/8=0.375\) | **circular** as a datum; \(3/8\) is algebra, not Planck |
| C13 | Immirzi \(\gamma\) | 0.2739 | matched to \(S=A/4\) | **circular** / calibration |
| C14 | \(f_{NL}^{\mathrm{eq}}\) | 14.5 | Planck 2018 \(-26\pm47\) | **incomplete** (no bispectrum). A small pull would not count. |
| C15 | \(m_{\tilde g}\) | 10.6 TeV | LHC floor \(\sim2.2\,\mathrm{TeV}\) | **incomplete**; not excluded ≠ derived |
| C16 | \(m_a\) | 28.5 neV | — | **incomplete**; CASPEr is a future search |
| C17 | BR(\(\mu\to eee\)) | \(\sim10^{-16}\) | — | **incomplete**; Mu3e Phase-II is future |
| C18 | \(\Omega_{\mathrm{GW}}(1\,\mathrm{mHz})\) | \(10^{-7}\) | — | **incomplete**; LISA is not data |
| C3 | \(\tau(p\to e^+\pi^0)\) implemented | — | Super-K \(>2.4\times10^{34}\) yr | **excluded** at default \(\alpha_H=0.015\) (\(\sim1.9\times10^{34}\) yr) |
| C19 | same, marketing band | \(2.9\)–\(4.9\times10^{35{-}36}\) yr | Super-K \(2.4\times10^{34}\) | **rejected formula** (not the implemented estimate; 1.7e34 is stale) |
| C20 | \(d_S\) 2→4 | interpolation | Gate 1 independent ensemble | **rejected formula** (NO-GO on that ensemble) |
| C21 | AS \(g_*\) | 0.83 | — | **incomplete** |
| C10 | \(\Omega_\Lambda\) | 0.685 from \(T_c^4/M_{\mathrm{Pl}}^2\) | — | **rejected formula** |

Typos in the pasted table, corrected above: BICEP/Keck (not “BICEPS/Brzuch”);
CASPEr; Super-K limit \(2.4\times10^{34}\) yr (not Hyper-K \(1.7\times10^{34}\)).

No row is an observational validation of a Theory of Everything.
