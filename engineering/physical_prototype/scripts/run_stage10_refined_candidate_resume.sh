#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-/tmp/rft-qpu-clean/bin/python}"
RESULTS="engineering/physical_prototype/results"
PREFIX="stage10_bias_refined_candidate"
SCRIPT="engineering/physical_prototype/scripts/run_stage9_bias_convergence.py"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "STOP: Python interpreter not found: $PYTHON_BIN" >&2
  exit 1
fi

if [[ -s "$RESULTS/$PREFIX.json" ]]; then
  echo "Stage 10 convergence is already complete: $RESULTS/$PREFIX.json"
  exit 0
fi

if [[ ! -s "$RESULTS/$PREFIX.checkpoint.json" || ! -s "$RESULTS/$PREFIX.checkpoint_matrices.npz" ]]; then
  echo "STOP: Stage 10 120-grid checkpoint is missing." >&2
  exit 1
fi

export PYTHONPATH="$ROOT/engineering/physical_prototype/src${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" "$SCRIPT" \
  --bias-offset-Phi0 -0.0075 \
  --pump-offset-from-static-kHz -64 \
  --amplitude-Phi0 0.020 \
  --duration-us 1.081 \
  --ramp-periods 8 \
  --steps-per-period 120 240 480 \
  --output-dir "$RESULTS" \
  --prefix "$PREFIX" \
  --resume \
  --max-new-grids 1

echo
if [[ -s "$RESULTS/$PREFIX.json" ]]; then
  echo "PASS: Stage 10 convergence is complete."
else
  echo "One grid chunk completed. Run this script again to calculate the next grid."
fi
