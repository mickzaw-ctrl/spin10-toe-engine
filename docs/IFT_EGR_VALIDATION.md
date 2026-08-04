# IFT-EGR v0.2: Information-Frequency Time Research Module

## Status

IFT-EGR is an isolated research hypothesis implemented as a numerically stable JAX/Equinox module. It is not part of the validated Spin(10) observable set and does not constitute a derivation or experimental validation of general relativity.

## Classification

- **Established physics:** symmetric logarithmic derivative, quantum Fisher information, Bures metric normalization, unitary density-matrix evolution, and the lapse relation `H_coord = Omega * H_proper`.
- **Project hypothesis:** proper time is proportional to Bures path length; temporally weighted entropy defines `G_eff`; modular variance defines `Xi`.
- **Unverified assumption:** graph information frequency has a covariant continuum limit sourced by physical matter.

## Stabilized implementation

The original self-modular flow used `K = -log(rho)` and `d rho / dt = -i [K, rho]`. Since every matrix function of `rho` commutes with `rho`, that flow is identically zero. Version 0.2 uses a deterministic graph-coupled Hamiltonian and a positivity-preserving unitary update.

The module also:

- defines Bures speed as `0.5 * sqrt(F_Q)`;
- projects numerical density matrices to Hermitian, positive-semidefinite, unit-trace states;
- counts undirected edges once and enforces `rho_ij = rho_ji`;
- treats homogeneous `Omega` as a lapse rather than an additional Friedmann source;
- fails closed when the Friedmann bracket is negative;
- records a machine-readable assumption ledger in every validation artifact.

## Local validation

```bash
python -m pip install -r requirements-ift-egr.txt
PYTHONPATH=src python -m unittest -v tests.test_ift_egr
PYTHONPATH=src python scripts/run_ift_egr_validation.py \
  --steps 600 --nodes 32 --edge-modes 6 \
  --output results/ift_egr_validation.json
```

## Continuous integration

`docs/ci/ift-egr-ci.yml.example` contains a reviewed workflow template for the exact contract tests and the 600-step validation on Python 3.11. It is intentionally inactive because the current GitHub OAuth grant does not include the `workflow` scope. To activate it manually, copy it to `.github/workflows/ift-egr-ci.yml`. The JSON validation report is then uploaded as a workflow artifact.

## HPC/Slurm validation

Submit from the repository root:

```bash
sbatch scripts/hpc/run_ift_egr_validation.slurm
```

The Slurm job creates an isolated environment in node-local temporary storage, executes the same `tests.test_ift_egr` suite used by CI, runs the same 600-step configuration, and writes:

```text
results/ift_egr_validation_<job-id>.json
logs/ift-egr-<job-id>.out
logs/ift-egr-<job-id>.err
```

A successful process exit and `numerical_status: PASS` establish numerical stability only.

## Remaining scientific blockers

1. No covariant action or constraint algebra derives `Omega`, `G_eff`, or `Xi`.
2. No graph Poisson equation connects local information frequency to mass density.
3. No perturbation or likelihood module predicts CMB, BAO, supernova, atomic-clock, lensing, or black-hole observables.
4. The continuum and graph-refinement limits are untested.

## External references

- S. L. Braunstein and C. M. Caves, “Statistical distance and the geometry of quantum states,” DOI: `10.1103/PhysRevLett.72.3439`.
- J. Anandan and Y. Aharonov, “Geometry of quantum evolution,” DOI: `10.1103/PhysRevLett.65.1697`.
- D. N. Page and W. K. Wootters, “Evolution without evolution,” DOI: `10.1103/PhysRevD.27.2885`.
