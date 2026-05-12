#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="${PBR_ATLAS_BASELINE_REPOS_ROOT:-/data/dip_1_ws/baseline_repos}"
ATLAS_ROOT="${PBR_ATLAS_BASELINE_ATLAS_ROOT:-/data/dip_1_ws/atlases/B2}"

mkdir -p "${REPO_ROOT}" "${ATLAS_ROOT}"
mkdir -p "${ATLAS_ROOT}"/{partuv,flexpara,flatten_anything,parapoint,visibility_param}

clone_if_missing() {
  local name="$1"
  local url="$2"
  if [[ -z "${url}" ]]; then
    echo "[skip] ${name}: repo URL unverified or intentionally omitted."
    return 0
  fi
  if [[ -d "${REPO_ROOT}/${name}/.git" ]]; then
    echo "[ok] ${name}: existing repo at ${REPO_ROOT}/${name}"
    return 0
  fi
  echo "[clone] ${name} <- ${url}"
  git clone "${url}" "${REPO_ROOT}/${name}" || {
    echo "[warn] clone failed for ${name}; keep this as a documented B2 failure or provide a manual checkout."
    return 0
  }
}

clone_if_missing "PartUV" "https://github.com/EricWang12/PartUV"
clone_if_missing "FlexPara" "https://github.com/AidenZhao/FlexPara"
clone_if_missing "FlattenAnything" "https://github.com/keeganhk/FlattenAnything"
clone_if_missing "OT-UVGS" ""
clone_if_missing "ParaPoint" ""
clone_if_missing "VisibilityParam" ""

cat > "${REPO_ROOT}/README_B2_BASELINES.md" <<'EOF'
# B2 Baseline Reproduction Notes

- `PartUV`, `FlexPara`, and `FlattenAnything` use repo URLs cited in the local experiment docs.
- `OT-UVGS`, `ParaPoint`, and the arXiv:2509.25094v3 visibility-parameterization neighbor remain unverified here.
- For any external baseline you wire up manually, export `uv`, `face_uv`, and optional `chart_ids` into:
  `/data/dip_1_ws/atlases/B2/<baseline>/<asset>.npz`
- `scripts/run_B2.py` can also consume per-baseline `command` / `external_atlas` entries from `configs/B2_matched.yaml`.
EOF

python - <<'PY'
import importlib.util
import shutil

print("[env] xatlas:", "yes" if importlib.util.find_spec("xatlas") else "no")
print("[env] blender:", shutil.which("blender") or "missing")
PY

echo "[done] baseline repo root: ${REPO_ROOT}"
echo "[done] external atlas root: ${ATLAS_ROOT}"
