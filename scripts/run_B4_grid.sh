#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
OUTPUT_ROOT="${B4_OUTPUT_ROOT:-${ROOT_DIR}/runs/B4_ablation}"
B3_ROOT_LOCAL="${B3_ROOT_LOCAL:-${ROOT_DIR}/runs/B3_main}"
B3_ROOT_REMOTE_STYLE="${B3_ROOT_REMOTE_STYLE:-/data/dip_1_ws/runs/B3_main}"
SESSION="${B4_TMUX_SESSION:-B4_ablation}"
GPU_ARG=()
if [[ -n "${B4_GPU:-}" ]]; then
  GPU_ARG=(--gpu "${B4_GPU}")
fi

mkdir -p "${OUTPUT_ROOT}"
COMMAND_FILE="${OUTPUT_ROOT}/B4_grid_commands.txt"
: > "${COMMAND_FILE}"

baseline_run() {
  local asset="$1"
  local baseline="$2"
  local seed="${3:-42}"
  local local_path="${B3_ROOT_LOCAL}/${asset}_${baseline}_ours_seed${seed}"
  if [[ -d "${local_path}" ]]; then
    printf '%s' "${local_path}"
  else
    printf '%s' "${B3_ROOT_REMOTE_STYLE}/${asset}_${baseline}_ours_seed${seed}"
  fi
}

append_cmd() {
  local ablation="$1"
  local asset="$2"
  local baseline="$3"
  local variant="${4:-}"
  local baseline_path
  baseline_path="$(baseline_run "${asset}" "${baseline}" 42)"
  local cmd=(
    "${PYTHON_BIN}" "${ROOT_DIR}/scripts/run_B4_ablation.py"
    --ablation "${ablation}"
    --asset "${asset}"
    --baseline "${baseline}"
    --config "${ROOT_DIR}/configs/B4_ablations/${ablation}.yaml"
    --baseline-run "${baseline_path}"
    --output-root "${OUTPUT_ROOT}"
  )
  if [[ -n "${B4_GPU:-}" ]]; then
    cmd+=("${GPU_ARG[@]}")
  fi
  if [[ -n "${variant}" ]]; then
    cmd+=(--variant "${variant}")
  fi
  printf '%q ' "${cmd[@]}" >> "${COMMAND_FILE}"
  printf '\n' >> "${COMMAND_FILE}"
}

# A1-A9 plus A17/A18 on the two main positive-signal cases: 11 * 2 = 22.
for ablation in A1 A2 A3 A4 A5 A6 A7 A8 A9 A17 A18; do
  append_cmd "${ablation}" spot partuv
  append_cmd "${ablation}" bunny partuv
done

# A10-A13 matched controls on the same two main cases: 4 * 2 = 8.
for ablation in A10 A11 A12 A13; do
  append_cmd "${ablation}" spot partuv
  append_cmd "${ablation}" bunny partuv
done

# A14 resolution sweep on spot/partuv: 3.
for variant in 1k 2k 4k; do
  append_cmd A14 spot partuv "${variant}"
done

# A15 BRDF sweep on spot/partuv: 4.
for variant in ggx ct lambert disney; do
  append_cmd A15 spot partuv "${variant}"
done

# A16 light-type sweep on spot/partuv: 4.
for variant in point area hdr grazing; do
  append_cmd A16 spot partuv "${variant}"
done

COUNT="$(wc -l < "${COMMAND_FILE}" | tr -d ' ')"
if [[ "${COUNT}" != "41" ]]; then
  echo "expected 41 B4 commands, got ${COUNT}" >&2
  exit 1
fi
if [[ "${B4_DRY_RUN:-0}" == "1" ]]; then
  echo "commands: ${COMMAND_FILE}"
  echo "count: ${COUNT}"
  exit 0
fi

RUNNER_SCRIPT="${OUTPUT_ROOT}/run_B4_grid_inner.sh"
{
  printf '#!/usr/bin/env bash\n'
  printf 'set -euo pipefail\n'
  printf 'while IFS= read -r cmd; do\n'
  printf '  echo "[B4] ${cmd}"\n'
  printf '  eval "${cmd}"\n'
  printf 'done < %q\n' "${COMMAND_FILE}"
  printf '%q %q --input-root %q --b3-root %q\n' "${PYTHON_BIN}" "${ROOT_DIR}/scripts/collect_B4_table.py" "${OUTPUT_ROOT}" "${B3_ROOT_LOCAL}"
} > "${RUNNER_SCRIPT}"
chmod +x "${RUNNER_SCRIPT}"

if [[ "${B4_NO_TMUX:-0}" == "1" ]]; then
  bash "${RUNNER_SCRIPT}"
else
  tmux new-session -d -s "${SESSION}" "bash ${RUNNER_SCRIPT}"
  echo "tmux session: ${SESSION}"
  echo "commands: ${COMMAND_FILE}"
fi
