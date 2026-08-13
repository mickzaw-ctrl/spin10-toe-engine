# Validation contract NS-AT-INSTANT-01

**Hypothesis:** α-attractor inflation with a declared `α` and instantaneous reheating.  
**Not claimed:** a Theory of Everything.

## The four fields

| Field | Implementation |
|---|---|
| Independent derivation | `n_s = 1 − 2/N`, `r = 12α/N²`. `N` comes from `a_*=k_*/H_*` and `T_reh=T_end`. |
| Inputs excluding the target | `A_s=2.1×10⁻⁹`, `k_*=0.05 Mpc⁻¹`, `α`, SM `g_*`. **`n_s` is not an input.** |
| Likelihood | Frozen Gaussian on the OBS-2026-08 `n_s` card. Not Planck Plik/CamSpec. |
| Preregistered no-go | Reject if `|pull| > 2`. Constant `NOGO_ABS_PULL` in `src/inflation_contract.py`. |

## Control

Row **C1b** still uses a hand-chosen `N` and is labelled **circular**, so the old “pick N=60” move cannot be mistaken for the contract.

## Result

Evaluated after the rule was frozen. See the Data bench, row C1.

TOE-validated observational predictions remain **0**.
