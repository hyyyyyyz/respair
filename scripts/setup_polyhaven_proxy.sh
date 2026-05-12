#!/usr/bin/env bash
# Poly Haven CC0 PBR proxy fallback (BEAST proposal #2).
# Downloads 12 small CC0 3D models with PBR textures.
# All assets are CC0; no auth needed.
# Used as a "production PBR asset proxy" if DiLiGenT-MV captured fails.

set -uo pipefail

OUT=${OUT:-/data/dip_1_ws/datasets/polyhaven_proxy}
mkdir -p "$OUT/raw"
LOG="$OUT/setup.log"
echo "=== Poly Haven proxy setup $(date) ===" | tee -a "$LOG"

# Hand-picked small (<= ~50 MB each) CC0 props.
# Slugs from https://polyhaven.com/models — using the 1k texture variant.
SLUGS=(
  "ceramic_vase_01"
  "wooden_bowl_01"
  "concrete_brick"
  "iron_chair_01"
  "marble_bust_01"
  "metal_lamp_01"
  "plastic_crate"
  "rocky_boulder_01"
  "rusted_barrel"
  "stone_buddha"
  "vintage_camera"
  "wooden_box_01"
)
RES=${RES:-1k}

for slug in "${SLUGS[@]}"; do
  asset_dir="$OUT/raw/$slug"
  if [[ -d "$asset_dir" && -f "$asset_dir/.done" ]]; then
    echo "[$(date)] SKIP $slug (already downloaded)" | tee -a "$LOG"
    continue
  fi
  mkdir -p "$asset_dir"
  echo "[$(date)] DL $slug" | tee -a "$LOG"
  files_url="https://api.polyhaven.com/files/$slug"
  if ! resp=$(curl --max-time 30 -sSL "$files_url" 2>>"$LOG"); then
    echo "[$(date)]   files API failed for $slug" | tee -a "$LOG"
    continue
  fi
  echo "$resp" > "$asset_dir/files.json"
  glb_url=$(python3 -c "import json,sys; data=json.loads(open('$asset_dir/files.json').read()); print(((data.get('blend',{}) or data.get('gltf',{}) or {}).get('${RES}',{}).get('blend',{}).get('url') or (data.get('gltf',{}).get('${RES}',{}).get('gltf',{}).get('url')) or '')" 2>/dev/null || echo "")
  if [[ -z "$glb_url" ]]; then
    glb_url=$(python3 -c "import json; d=json.load(open('$asset_dir/files.json')); g=d.get('gltf',{}).get('1k',{}); url=(g.get('gltf',{}) or g.get('glb',{}) or {}).get('url',''); print(url)" 2>/dev/null || echo "")
  fi
  if [[ -z "$glb_url" ]]; then
    echo "[$(date)]   no gltf/glb url for $slug" | tee -a "$LOG"
    continue
  fi
  ext="${glb_url##*.}"
  if curl --max-time 300 -sSL -o "$asset_dir/model.$ext" "$glb_url" 2>>"$LOG"; then
    touch "$asset_dir/.done"
    echo "[$(date)]   ok ($(du -sh "$asset_dir" | cut -f1))" | tee -a "$LOG"
  else
    echo "[$(date)]   download failed: $glb_url" | tee -a "$LOG"
  fi
done

echo "=== Poly Haven proxy setup done $(date) ===" | tee -a "$LOG"
ls -la "$OUT/raw" | tee -a "$LOG"
