#!/usr/bin/env bash
# n=10 split-seed extension runner (BEAST proposal #8: statistical power upgrade).
# Runs 7 additional split seeds for accepted PartUV cases + rollback controls,
# bringing n from 3 to 10 across the most reported cells.
#
# Existing seeds in runs/A1_split: 42, 1234, 9999
# New seeds: 7, 17, 23, 31, 53, 71, 91 (avoid clashing patterns)

set -uo pipefail

REPO=${REPO:-/home/ubuntu/dip_1_ws}
OUTPUT_ROOT=${OUTPUT_ROOT:-/data/dip_1_ws/runs/A1_split}
CONFIG=${CONFIG:-configs/B3_main.yaml}
GPU=${GPU:-0}
TIMEOUT_S=${TIMEOUT_S:-7200}

NEW_SEEDS=${NEW_SEEDS:-"7 17 23 31 53 71 91"}
CASES=${CASES:-"spot:partuv bunny:partuv spot:xatlas_classical objaverse:xatlas_classical"}

mkdir -p "$OUTPUT_ROOT"
LOG_FILE="$OUTPUT_ROOT/n10.log"
echo "=== n=10 grid start $(date) GPU=$GPU ===" | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$REPO"

count=0
total=0
for c in $CASES; do for s in $NEW_SEEDS; do total=$((total+1)); done; done
echo "total runs: $total" | tee -a "$LOG_FILE"

for case in $CASES; do
  asset="${case%%:*}"
  baseline="${case##*:}"
  for seed in $NEW_SEEDS; do
    count=$((count+1))
    run_id="${asset}_${baseline}_ours_split${seed}"
    run_dir="$OUTPUT_ROOT/$run_id"
    if [[ -f "$run_dir/metrics.json" ]]; then
      echo "[${count}/${total}] SKIP $run_id (already done)" | tee -a "$LOG_FILE"
      continue
    fi
    echo "[${count}/${total}] START $run_id $(date)" | tee -a "$LOG_FILE"
    CUDA_VISIBLE_DEVICES=$GPU timeout "$TIMEOUT_S" python scripts/run_B3.py \
      --asset "$asset" --baseline "$baseline" --method ours \
      --config "$CONFIG" --output-root "$OUTPUT_ROOT" \
      --run-id "$run_id" --split-seed "$seed" 2>&1 | tee -a "$LOG_FILE" | tail -3 || \
      echo "  WARN rc=$? for $run_id" | tee -a "$LOG_FILE"
  done
done

echo "=== n=10 grid done $(date) ===" | tee -a "$LOG_FILE"
