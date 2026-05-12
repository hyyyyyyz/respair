# Restructure Draft (Held until W1 data lands)

Don't apply these to main.tex yet — keep current 7.5 PDF intact.
Apply after DiLiGenT-MV W1 results materialize and exhibit positive signal.

## New Title (R1)
Old: "PBR Baking-Error Atlases for Selective UV Atlas Repair"
New: "Captured-Target Residuals for Selective UV Atlas Repair"

## Contributions (R3)
- Drop from claim list: C4 cross-channel seam coupling; explicit mip term
- Keep as diagnostic regularizers in implementation
- Reduce to 4 contributions:
  C1 channel-aware baker / C2 local repair / C3 residual allocation / C5 holdout gate

## Section 3.X "Target signal regime" (R8)
Three regimes the method handles:
1. **Synthetic oracle** (controlled): voronoi+smooth+region oracle PBR maps; isolates UV from material noise
2. **Self-described oracle** (generated mesh): mesh comes with implicit material params; treat as oracle
3. **Captured imagery** (DiLiGenT-MV): real photometric stereo capture (16-bit linear PNG, 96 calibrated lights/view, 20 views, mask eroded 2px, light-intensity normalized, saturated excluded)

The method is identical across regimes; only the supervisory target_render swaps.

## Headline table swap (R2 + R7)
- table1_main = DiLiGenT-MV captured 5 objects × baselines
- Synthetic oracle 12-case → moves to confound/ablation section
- table9_real_mesh stays as transfer
- Visual figure uses DiLiGenT captured rows when positive

## Baseline (R4)
- Drop FlexPara/FA/ParaPoint reproduction effort
- Add Semantic-Visibility-UV with 3-day kill switch
- matched_oracle moves to synthetic confound only

## Stats (R6)
- DiLiGenT core: n=5 split seeds
- SemVis/transfer: n=3
- Top-2 accept + top-2 rollback: n=10 if borderline

