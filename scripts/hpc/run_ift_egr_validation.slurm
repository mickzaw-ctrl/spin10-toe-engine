#!/usr/bin/env bash
#SBATCH --job-name=ift-egr-validation
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=logs/ift-egr-%j.out
#SBATCH --error=logs/ift-egr-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
cd "$REPO_ROOT"
mkdir -p logs results

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_ROOT="${SLURM_TMPDIR:-/tmp}/ift-egr-${SLURM_JOB_ID:-local}"
"$PYTHON_BIN" -m venv "$VENV_ROOT"
"$VENV_ROOT/bin/python" -m pip install --quiet --upgrade pip
"$VENV_ROOT/bin/python" -m pip install --quiet -r requirements-ift-egr.txt

export PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export JAX_ENABLE_X64=True
export XLA_FLAGS="${XLA_FLAGS:---xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=${SLURM_CPUS_PER_TASK:-8}}"

# Execute exactly the same contract suite used by GitHub Actions.
"$VENV_ROOT/bin/python" -m unittest -v tests.test_ift_egr
"$VENV_ROOT/bin/python" scripts/run_ift_egr_validation.py \
  --steps 600 \
  --nodes 32 \
  --edge-modes 6 \
  --output "results/ift_egr_validation_${SLURM_JOB_ID:-local}.json"
