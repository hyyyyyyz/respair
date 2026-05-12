#!/usr/bin/env bash
set -euo pipefail

SEEDS="${SEEDS:-42 43 44}"
GPU="${GPU:-0}"
B3_ROOT="${B3_ROOT:-/data/dip_1_ws/runs/B3_main_A1}"
REAL_ROOT="${REAL_ROOT:-/data/dip_1_ws/runs/PG_enh1_real_v2_A1}"
CURV_ROOT="${CURV_ROOT:-/data/dip_1_ws/runs/PG_enh2_v2_curvature_A1}"
DATA_ROOT="${DATA_ROOT:-/data/dip_1_ws/datasets/sample}"
REAL_DATA_ROOT="${REAL_DATA_ROOT:-/data/dip_1_ws/datasets/PG_enh1_real_generated}"

main_cases=(
  "spot partuv"
  "bunny partuv"
  "spot xatlas_classical"
  "objaverse xatlas_classical"
)

for seed in ${SEEDS}; do
  for item in "${main_cases[@]}"; do
    read -r asset baseline <<<"${item}"
    python scripts/run_B3.py \
      --asset "${asset}" \
      --baseline "${baseline}" \
      --method ours \
      --config configs/B3_main.yaml \
      --output-root "${B3_ROOT}" \
      --data-root "${DATA_ROOT}" \
      --seed "${seed}" \
      --split-seed "${seed}" \
      --gpu "${GPU}"
  done

  python scripts/run_PG_enh1_real_generated.py \
    --count 1 \
    --source-manifest configs/pg_real_meshes_A.json \
    --output-root "${REAL_ROOT}" \
    --data-root "${REAL_DATA_ROOT}" \
    --config configs/B7_transfer.yaml \
    --baseline partuv \
    --method ours \
    --seed "${seed}" \
    --gpu "${GPU}"
done

python scripts/collect_B3_table.py --input-root "${B3_ROOT}"
python scripts/run_PG_enh2_v2_curvature.py \
  --b3-root "${B3_ROOT}" \
  --real-root "${REAL_ROOT}" \
  --output-root "${CURV_ROOT}" \
  --paper-table paper/tables/table10_curvature.tex \
  --data-root "${DATA_ROOT}"
