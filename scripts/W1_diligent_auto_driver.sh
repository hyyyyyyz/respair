#!/usr/bin/env bash
# W1 driver: when DiLiGenT-MV.zip rsync completes, automatically extract,
# audit, smoke-test, and (optionally) launch the full grid.
#
# Idempotent: each phase checks for completion markers before running.

set -o pipefail
# NOTE: deliberately omit -u; conda activate scripts reference unbound vars (e.g. NVCC_PREPEND_FLAGS).

REPO=${REPO:-/home/ubuntu/dip_1_ws}
DATA_ROOT=${DATA_ROOT:-/data/dip_1_ws/datasets/diligent_mv}
RAW_ZIP=${RAW_ZIP:-$DATA_ROOT/raw/DiLiGenT-MV.zip}
EXTRACT_ROOT=${EXTRACT_ROOT:-$DATA_ROOT/extracted}
PROCESSED_ROOT=${PROCESSED_ROOT:-$DATA_ROOT/processed}
RUN_ROOT=${RUN_ROOT:-/data/dip_1_ws/runs/W1_diligent_mv}
GPU=${GPU:-1}
DRIVER_LOG=${DRIVER_LOG:-$RUN_ROOT/W1_driver.log}

mkdir -p "$RUN_ROOT" "$PROCESSED_ROOT"
exec >> "$DRIVER_LOG" 2>&1
echo "=== W1 driver start $(date) GPU=$GPU ==="

# Phase 1: wait for zip to exist as final filename (rsync renames partial -> final)
while [[ ! -f "$RAW_ZIP" ]]; do
  echo "[$(date)] waiting for $RAW_ZIP ..."
  sleep 300
done
SIZE=$(stat -c %s "$RAW_ZIP" 2>/dev/null || stat -f %z "$RAW_ZIP")
echo "[$(date)] zip ready: $SIZE bytes"

# Phase 2: extract (idempotent)
if [[ ! -d "$EXTRACT_ROOT/DiLiGenT-MV/mvpmsData/bearPNG" ]]; then
  echo "[$(date)] extracting..."
  mkdir -p "$EXTRACT_ROOT"
  cd "$EXTRACT_ROOT" && unzip -q "$RAW_ZIP" || { echo "FAIL: unzip rc=$?"; exit 2; }
  echo "[$(date)] extracted"
else
  echo "[$(date)] already extracted"
fi

# Phase 3: setup audit
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$REPO"
echo "[$(date)] audit..."
CUDA_VISIBLE_DEVICES=$GPU python scripts/setup_diligent_mv.py \
  --root "$EXTRACT_ROOT/DiLiGenT-MV/mvpmsData" \
  --out-json "$PROCESSED_ROOT/setup_audit.json" \
  --max-lights 4

if ! grep -q '"status": "ok"' "$PROCESSED_ROOT/setup_audit.json"; then
  echo "FAIL: audit reported no ok objects; aborting before smoke"
  exit 3
fi

# Phase 4: smoke (Bear, xatlas, baseline_only and ours, seed 0, low-res)
SMOKE_FLAG=$RUN_ROOT/.smoke_done
if [[ ! -f "$SMOKE_FLAG" ]]; then
  for METHOD in baseline_only ours; do
    RUN_ID="bear_xatlas_classical_${METHOD}_split0_seed0"
    echo "[$(date)] SMOKE $RUN_ID"
    CUDA_VISIBLE_DEVICES=$GPU timeout 3600 python scripts/run_diligent_mv.py \
      --asset bear --baseline xatlas_classical --method $METHOD \
      --config configs/DILIGENT_MV.yaml --output-root "$RUN_ROOT" --run-id "$RUN_ID" \
      --seed 0 --split-seed 0 \
      --proposal-views 6 --gate-views 4 --test-views 4 \
      --proposal-lights 24 --gate-lights 12 --test-lights 12 \
      --no-lpips || { echo "FAIL: smoke run $METHOD rc=$?"; exit 4; }
  done
  touch "$SMOKE_FLAG"
  echo "[$(date)] smoke complete"
else
  echo "[$(date)] smoke already done"
fi

# Phase 5: full grid (5 objects × 2 baselines × 2 methods × 5 seeds)
GRID_FLAG=$RUN_ROOT/.grid_done
if [[ ! -f "$GRID_FLAG" ]]; then
  echo "[$(date)] starting grid..."
  ASSETS="bear cow pot2 buddha reading" \
    BASELINES="xatlas_classical blender_uv" \
    METHODS="baseline_only ours" \
    SEEDS="0 1 2 3 4" \
    GPU=$GPU \
    bash scripts/run_diligent_mv_grid.sh
  touch "$GRID_FLAG"
  echo "[$(date)] grid complete"
fi

# Phase 6: collect table + bootstrap CIs
echo "[$(date)] collecting..."
python scripts/collect_diligent_mv_table.py \
  --root "$RUN_ROOT" \
  --out-tex paper/tables/table13_diligent_mv.tex \
  --out-md "$RUN_ROOT/DILIGENT_MV_SUMMARY.md" \
  --out-json "$RUN_ROOT/diligent_mv_metrics.json"

echo "=== W1 driver done $(date) ==="
