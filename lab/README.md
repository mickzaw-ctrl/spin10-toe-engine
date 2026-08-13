# Spin(10) Research Lab

Interactive, fail-closed workbench over the audited modules in this repository.

This is **not** a completed Theory of Everything. v16.1 closes the *internal*
specification — axioms, Spin(10) embedding, independent Gate-1 / Gate-2
computations, the prescribed-P Jacobson action (Gate 3), and a prediction
registry. Empirically the programme stays open.  \(P(N,T)\) is still not
derived.

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
| Jacobson / prescribed P | `src/jacobson_clausius.py` | action closed; P underived; G_eff NO-GO |
| Assumption ledger | `docs/TCD_ASSUMPTION_LEDGER.json` | machine-readable audit |

Validated TCD predictions: **0**.
