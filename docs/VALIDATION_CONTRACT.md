# Validation contract NS-AT-INSTANT-01

**Hypothesis:** α-attractor inflation with a declared `α` and instantaneous reheating.  
**Not claimed:** a Theory of Everything.  
**Not claimed:** the legacy band \(n_s\in[0.9629,0.9667]\).

## Two different \(n_s\) stories

| Path | How \(N\) is obtained | \(n_s=1-2/N\) | Verdict |
|---|---|---|---|
| **C1** · NS-AT-INSTANT-01 | \(N\) from \(a_*=k_*/H_*\) and \(T_{\rm reh}=T_{\rm end}\) | \(\approx 0.9652\) at \(\alpha=3.75\) | **compatible** with the frozen Planck proxy (\(\lvert\mathrm{pull}\rvert<2\)). Phenomena only. Not TOE. |
| **C1b** | hand \(N=60\) | \(0.9667\) | **circular** |
| **C23** · v8–v14 band \(0.9629\)–\(0.9667\) | invert the quoted tilt: \(N=2/(1-n_s)\in[53.91,60.06]\) | the band itself | **circular by construction** |

The marketing band is not an independent prediction. It is the image of a
hand-chosen \(N\) interval under the leading α-attractor map. Contract C1
never inverts the observed tilt: \(n_s\) is not an input of
`derived_efolds`.

\(\alpha=3.75=\dim\mathrm{Spin}(10)/12\) remains a **project choice** on
both paths.

## The four fields (C1 only)

| Field | Implementation |
|---|---|
| Independent derivation | `n_s = 1 − 2/N`, `r = 12α/N²`. `N` comes from `a_*=k_*/H_*` and `T_reh=T_end`. |
| Inputs excluding the target | `A_s=2.1×10⁻⁹`, `k_*=0.05 Mpc⁻¹`, `α`, SM `g_*`. **`n_s` is not an input.** |
| Likelihood | Frozen Gaussian on the OBS-2026-08 `n_s` card. Not Planck Plik/CamSpec. |
| Preregistered no-go | Reject if `|pull| > 2`. Constant `NOGO_ABS_PULL` in `src/inflation_contract.py`. |

## Control

Rows **C1b** and **C23** stay labelled **circular**, so the old “pick \(N\)
until \(n_s\) looks like Planck” move cannot be mistaken for the contract.

## Result

Evaluated after the rule was frozen. See the Data bench, row C1.

TOE-validated observational predictions remain **0**.
