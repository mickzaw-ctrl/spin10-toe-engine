# Spin(10) Research Lab

Interactive, fail-closed workbench over the audited modules in this repository.

This is **not** a completed Theory of Everything. It runs the solvers that actually
exist, labels every output as established / hypothesis / rejected / calibration,
and refuses to treat a reference input as a confirmed prediction.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lab.txt
python -m lab
```

Then open `http://127.0.0.1:8000`.

## What it computes

| Bench | Source | Status |
|---|---|---|
| SM / MSSM RGE unification | `src/numerical_rge_solver.py` | established baseline |
| Spectral dimension on reference graphs | lab walker + `src/spectral_dimension_random_walk.py` | estimator, not TCD flow |
| TCD temperature diagnostics | `src/termo_chromo_dynamics.py` | hypothesis + NO-GO gates |
| LQC bounce / isolated horizon / GFT | `src/ift_egr_closure.py` | imported LQC identities |
| α-attractor n_s, r | standard slow-roll formulae | α = 3.75 is a project choice |
| Assumption ledger | `docs/TCD_ASSUMPTION_LEDGER.json` | machine-readable audit |

Validated TCD predictions: **0**.
