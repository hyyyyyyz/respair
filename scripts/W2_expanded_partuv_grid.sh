#!/usr/bin/env bash
# W2 expanded PartUV grid: real generated meshes (f3d/ts/objav/polyhaven) × PartUV × ours/baseline_only × 3 seeds.
# Goal: lift headline accept rate from 3/20 toward 8-12/N by exploring more weak-PartUV cases.
# Uses run_B7_transfer.py infrastructure with PartUV mesh-hash cache.

set -o pipefail

REPO=${REPO:-/home/ubuntu/dip_1_ws}
OUTPUT_ROOT=${OUTPUT_ROOT:-/data/dip_1_ws/runs/W2_expanded_partuv}
CONFIG=${CONFIG:-configs/B7_transfer.yaml}
GPU=${GPU:-0}
PER_RUN_TIMEOUT=${PER_RUN_TIMEOUT:-3600}

# Targets: meshes likely to have PartUV-failure patterns
ASSETS=${ASSETS:-"f3d_chair f3d_head f3d_person f3d_phonograph ts_cabin ts_hand ts_human ts_nascar ts_potion polyh_food_kiwi_01 objav_12a0b7dcb8 objav_8476c4170d objav_d852fda357 objav_702bef9d8f objav_6ae341772c"}
METHODS=${METHODS:-"baseline_only ours"}
SEEDS=${SEEDS:-"42"}

mkdir -p "$OUTPUT_ROOT"
LOG_FILE="$OUTPUT_ROOT/grid.log"
echo "=== W2 expanded grid start $(date) GPU=$GPU ===" | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$REPO"

count=0
total=0
for a in $ASSETS; do for m in $METHODS; do for s in $SEEDS; do total=$((total+1)); done; done; done
echo "total: $total" | tee -a "$LOG_FILE"

for asset in $ASSETS; do
  for method in $METHODS; do
    for seed in $SEEDS; do
      count=$((count+1))
      run_id="${asset}_partuv_${method}_seed${seed}"
      run_dir="$OUTPUT_ROOT/$run_id"
      if [[ -f "$run_dir/metrics.json" ]]; then
        echo "[${count}/${total}] SKIP $run_id" | tee -a "$LOG_FILE"; continue
      fi
      rm -rf "$run_dir"
      ts=$(date +%s)
      echo "[${count}/${total}] START $run_id $(date)" | tee -a "$LOG_FILE"
      CUDA_VISIBLE_DEVICES=$GPU timeout "$PER_RUN_TIMEOUT" python -u scripts/run_B7_transfer.py \
        --asset "$asset" --baseline partuv --method "$method" \
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
done
echo "=== W2 grid done $(date) ===" | tee -a "$LOG_FILE"
