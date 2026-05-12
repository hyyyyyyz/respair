#!/usr/bin/env bash
# DiLiGenT-MV PartUV captured-target grid: 5 obj × 1 baseline (partuv) × 2 methods × 3 seeds = 30 runs.
# PartUV is the weak baseline where residual repair has leverage (per spot/PartUV +14.67dB precedent).

set -o pipefail

REPO=${REPO:-/home/ubuntu/dip_1_ws}
OUTPUT_ROOT=${OUTPUT_ROOT:-/data/dip_1_ws/runs/W1_diligent_mv}
CONFIG=${CONFIG:-configs/DILIGENT_MV.yaml}
ROOT_DATA=${ROOT_DATA:-/data/dip_1_ws/datasets/diligent_mv/extracted/DiLiGenT-MV/mvpmsData}
GPU=${GPU:-0}
PER_RUN_TIMEOUT=${PER_RUN_TIMEOUT:-7200}

PROP_VIEWS=${PROP_VIEWS:-6}
GATE_VIEWS=${GATE_VIEWS:-4}
TEST_VIEWS=${TEST_VIEWS:-4}
PROP_LIGHTS=${PROP_LIGHTS:-8}
GATE_LIGHTS=${GATE_LIGHTS:-4}
TEST_LIGHTS=${TEST_LIGHTS:-4}

ASSETS=${ASSETS:-"bear cow pot2 buddha reading"}
BASELINES=${BASELINES:-"partuv"}
METHODS=${METHODS:-"baseline_only ours"}
SEEDS=${SEEDS:-"0 1 2"}

mkdir -p "$OUTPUT_ROOT"
LOG_FILE="$OUTPUT_ROOT/partuv_grid.log"
echo "=== PartUV grid start $(date) GPU=$GPU ===" | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dip1_pbr
cd "$REPO"

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
          echo "[${count}/${total}] SKIP $run_id" | tee -a "$LOG_FILE"; continue
        fi
        rm -rf "$run_dir"
        run_start=$(date +%s)
        echo "[${count}/${total}] START $run_id $(date)" | tee -a "$LOG_FILE"
        CUDA_VISIBLE_DEVICES=$GPU timeout "$PER_RUN_TIMEOUT" python -u scripts/run_diligent_mv.py \
          --asset "$asset" --baseline "$baseline" --method "$method" \
          --config "$CONFIG" --root "$ROOT_DATA" \
          --output-root "$OUTPUT_ROOT" --run-id "$run_id" \
          --seed "$seed" --split-seed "$seed" \
          --proposal-views "$PROP_VIEWS" --gate-views "$GATE_VIEWS" --test-views "$TEST_VIEWS" \
          --proposal-lights "$PROP_LIGHTS" --gate-lights "$GATE_LIGHTS" --test-lights "$TEST_LIGHTS" \
          --no-lpips ${USE_PMS_FLAG:-} >>"$LOG_FILE" 2>&1
        rc=$?
        run_dt=$(( $(date +%s) - run_start ))
        if [[ -f "$run_dir/metrics.json" ]]; then
          echo "[${count}/${total}] DONE $run_id ${run_dt}s rc=$rc" | tee -a "$LOG_FILE"
        else
          echo "[${count}/${total}] FAIL $run_id rc=$rc dt=${run_dt}s" | tee -a "$LOG_FILE"
        fi
      done
    done
  done
done
echo "=== PartUV grid done $(date) ===" | tee -a "$LOG_FILE"
