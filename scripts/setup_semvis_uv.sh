#!/usr/bin/env bash
# Semantic-Visibility-UV install attempt with 3-day kill switch.
# Per BEAST plan R4: try → if fails by EOD W1 D7 (5/9), drop and document.
#
# Repo: https://github.com/AHHHZ975/Semantic-Visibility-UV-Param
# Note: paper is 2026 ICLR. cu128 path is closer to our stack than FlexPara.

set -euo pipefail

REPO_DIR="${REPO_DIR:-/data/dip_1_ws/baseline_repos/SemVis_UV}"
CONDA_ENV="${CONDA_ENV:-semvis_uv}"
LOG_FILE="${LOG_FILE:-/data/dip_1_ws/runs/W1_diligent_mv/semvis_install.log}"

mkdir -p "$(dirname "$LOG_FILE")"

echo "=== SemVis-UV install attempt $(date) ===" | tee -a "$LOG_FILE"

if [[ ! -d "$REPO_DIR" ]]; then
  echo "Cloning SemVis-UV..." | tee -a "$LOG_FILE"
  if ! git clone --depth 1 https://github.com/AHHHZ975/Semantic-Visibility-UV-Param "$REPO_DIR" 2>&1 | tee -a "$LOG_FILE"; then
    echo "FAIL: clone failed" | tee -a "$LOG_FILE"
    exit 1
  fi
fi

cd "$REPO_DIR"
ls -la | tee -a "$LOG_FILE"

source "$HOME/miniconda3/etc/profile.d/conda.sh"

if ! conda env list | grep -q "$CONDA_ENV"; then
  echo "Creating conda env $CONDA_ENV..." | tee -a "$LOG_FILE"
  conda create -n "$CONDA_ENV" python=3.10 -y 2>&1 | tee -a "$LOG_FILE"
fi

conda activate "$CONDA_ENV"
echo "Active env: $(which python)" | tee -a "$LOG_FILE"

if [[ -f requirements.txt ]]; then
  pip install --quiet --no-cache-dir -r requirements.txt 2>&1 | tee -a "$LOG_FILE" || {
    echo "FAIL: pip install -r requirements.txt failed" | tee -a "$LOG_FILE"
    exit 2
  }
fi

if [[ -f environment.yml ]]; then
  echo "Found environment.yml — applying with conda env update" | tee -a "$LOG_FILE"
  conda env update -f environment.yml -n "$CONDA_ENV" 2>&1 | tee -a "$LOG_FILE" || {
    echo "WARN: conda env update reported errors" | tee -a "$LOG_FILE"
  }
fi

# Smoke test: any importable entry-point?
python -c "import sys; sys.path.insert(0,'.'); import os; print('repo files:', os.listdir('.'))" 2>&1 | tee -a "$LOG_FILE"

echo "=== SemVis-UV install attempt finished $(date) ===" | tee -a "$LOG_FILE"
