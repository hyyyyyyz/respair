#!/usr/bin/env bash
# W3 statistical-power extension: 4 new W2 accepts × 3 new seeds = 12 runs.
# Strengthens the 6/18 real-mesh acceptance claim with multi-seed confidence.

set -o pipefail

REPO=${REPO:-/home/ubuntu/dip_1_ws}
OUTPUT_ROOT=${OUTPUT_ROOT:-/data/dip_1_ws/runs/W3_seeds_ext}
CONFIG=${CONFIG:-configs/B7_transfer.yaml}
GPU=${GPU:-0}
PER_RUN_TIMEOUT=${PER_RUN_TIMEOUT:-3600}

ASSETS=${ASSETS:-"f3d_head ts_cabin ts_nascar ts_potion"}
SEEDS=${SEEDS:-"0 1 2"}

mkdir -p "$OUTPUT_ROOT"
LOG_FILE="$OUTPUT_ROOT/grid.log"
echo "=== W3 seeds extension start $(date) GPU=$GPU ===" | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$REPO"

count=0
total=0
for a in $ASSETS; do for s in $SEEDS; do total=$((total+1)); done; done
echo "total: $total" | tee -a "$LOG_FILE"

for asset in $ASSETS; do
  for seed in $SEEDS; do
    count=$((count+1))
    run_id="${asset}_partuv_ours_seed${seed}"
    run_dir="$OUTPUT_ROOT/$run_id"
    if [[ -f "$run_dir/metrics.json" ]]; then
      echo "[${count}/${total}] SKIP $run_id" | tee -a "$LOG_FILE"; continue
    fi
    rm -rf "$run_dir"
    ts=$(date +%s)
    echo "[${count}/${total}] START $run_id $(date)" | tee -a "$LOG_FILE"
    CUDA_VISIBLE_DEVICES=$GPU timeout "$PER_RUN_TIMEOUT" python -u scripts/run_B7_transfer.py \
      --asset "$asset" --baseline partuv --method ours \
      --config "$CONFIG" --output-root "$OUTPUT_ROOT" \
      --data-root /data/dip_1_ws/datasets/pg_real_meshes \
      --manifest /data/dip_1_ws/datasets/pg_real_meshes/PG_REAL_MESHES_MANIFEST_v2.json \
      --seed "$seed" --no-lpips >>"$LOG_FILE" 2>&1
    rc=$?
    dt=$(( $(date +%s) - ts ))
    if [[ -f "$run_dir/metrics.json" ]]; then
      echo "[${count}/${total}] DONE $run_id ${dt}s rc=$rc" | tee -a "$LOG_FILE"
    else
      echo "[${count}/${total}] FAIL $run_id rc=$rc dt=${dt}s" | tee -a "$LOG_FILE"
    fi
  done
done
echo "=== W3 seeds extension done $(date) ===" | tee -a "$LOG_FILE"
