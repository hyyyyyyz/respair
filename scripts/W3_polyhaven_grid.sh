#!/usr/bin/env bash
# W3 Polyhaven CC0 PBR grid: 12 models × {baseline_only, ours} = 24 runs.
# Uses authored albedo/normal/metallicRoughness as oracle face PBR.

set -o pipefail

REPO=${REPO:-/home/ubuntu/dip_1_ws}
OUTPUT_ROOT=${OUTPUT_ROOT:-/data/dip_1_ws/runs/W3_polyhaven}
CONFIG=${CONFIG:-configs/B7_transfer.yaml}
GPU=${GPU:-1}
PER_RUN_TIMEOUT=${PER_RUN_TIMEOUT:-3600}

SLUGS=${SLUGS:-"ArmChair_01 Barrel_01 Camera_01 Chandelier_01 ClassicConsole_01 CoffeeTable_01 Drill_01 GreenChair_01 Lantern_01 Sofa_01 Television_01 Ukulele_01"}
METHODS=${METHODS:-"baseline_only ours"}
SEEDS=${SEEDS:-"42"}

mkdir -p "$OUTPUT_ROOT"
LOG_FILE="$OUTPUT_ROOT/grid.log"
echo "=== W3 Polyhaven grid start $(date) GPU=$GPU ===" | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$REPO"

count=0
total=0
for s in $SLUGS; do for m in $METHODS; do for sd in $SEEDS; do total=$((total+1)); done; done; done
echo "total: $total" | tee -a "$LOG_FILE"

for slug in $SLUGS; do
  for method in $METHODS; do
    for seed in $SEEDS; do
      count=$((count+1))
      run_id="${slug}_partuv_${method}_seed${seed}"
      run_dir="$OUTPUT_ROOT/$run_id"
      if [[ -f "$run_dir/metrics.json" ]]; then
        echo "[${count}/${total}] SKIP $run_id" | tee -a "$LOG_FILE"; continue
      fi
      rm -rf "$run_dir"
      ts=$(date +%s)
      echo "[${count}/${total}] START $run_id $(date)" | tee -a "$LOG_FILE"
      CUDA_VISIBLE_DEVICES=$GPU timeout "$PER_RUN_TIMEOUT" python -u scripts/W3_polyhaven_track.py \
        --slug "$slug" --baseline partuv --method "$method" \
        --config "$CONFIG" --output-root "$OUTPUT_ROOT" \
        --run-id "$run_id" --seed "$seed" --split-seed "$seed" --no-lpips >>"$LOG_FILE" 2>&1
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
echo "=== W3 Polyhaven grid done $(date) ===" | tee -a "$LOG_FILE"
