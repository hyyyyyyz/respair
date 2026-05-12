#!/usr/bin/env bash
# DiLiGenT-MV captured-target grid runner: assets × baselines × methods × seeds.
# Logs per-run output, skips already-completed runs. Sequential per-asset.

set -uo pipefail

ROOT="${ROOT:-/home/ubuntu/dip_1_ws}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/data/dip_1_ws/runs/W1_diligent_mv}"
CONFIG="${CONFIG:-configs/DILIGENT_MV.yaml}"
GPU="${GPU:-1}"
TIMEOUT_S="${TIMEOUT_S:-7200}"

ASSETS=${ASSETS:-"bear cow pot2 buddha reading"}
BASELINES=${BASELINES:-"xatlas_classical blender_uv"}
METHODS=${METHODS:-"baseline_only ours"}
SEEDS=${SEEDS:-"0 1 2 3 4"}

mkdir -p "$OUTPUT_ROOT"
LOG_FILE="$OUTPUT_ROOT/grid.log"
echo "=== DiLiGenT grid start $(date) GPU=$GPU ===" | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$ROOT"

count=0
total=0
for a in $ASSETS; do for b in $BASELINES; do for m in $METHODS; do for s in $SEEDS; do total=$((total+1)); done; done; done; done
echo "total runs: $total" | tee -a "$LOG_FILE"

for asset in $ASSETS; do
  for baseline in $BASELINES; do
    for method in $METHODS; do
      for seed in $SEEDS; do
        count=$((count+1))
        run_id="${asset}_${baseline}_${method}_split${seed}_seed${seed}"
        run_dir="$OUTPUT_ROOT/$run_id"
        if [[ -f "$run_dir/metrics.json" ]]; then
          echo "[${count}/${total}] SKIP $run_id (already complete)" | tee -a "$LOG_FILE"
          continue
        fi
        echo "[${count}/${total}] START $run_id $(date)" | tee -a "$LOG_FILE"
        CUDA_VISIBLE_DEVICES=$GPU timeout "$TIMEOUT_S" python scripts/run_diligent_mv.py \
          --asset "$asset" --baseline "$baseline" --method "$method" --config "$CONFIG" \
          --output-root "$OUTPUT_ROOT" --run-id "$run_id" \
          --seed "$seed" --split-seed "$seed" 2>&1 | tee -a "$LOG_FILE" | tail -3 || \
          echo "  WARN: rc=$? for $run_id" | tee -a "$LOG_FILE"
      done
    done
  done
done

echo "=== DiLiGenT grid done $(date) ===" | tee -a "$LOG_FILE"
