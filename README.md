# respair

**Residual-driven selective UV atlas repair for PBR-baked assets.**

Companion code for our PG 2026 / CGF special issue submission *PBR Baking-Error Atlases for Selective UV Atlas Repair*. `respair` treats held-out PBR relighting residuals as the deployment signal for UV atlas repair: it bakes albedo / normal / roughness / metallic through a differentiable PBR renderer, attributes residuals back to faces and charts, repairs only high-residual local charts, reallocates a fixed texel budget by residual-aware demand, and deploys the candidate atlas **only if** a matched-control C5 gate accepts it on a held-out gate split.

The method is intentionally narrow. It does not replace a production UV unwrap. Given a mesh, an existing single UV atlas (e.g. PartUV, xatlas, Blender Smart UV), and a fixed texture budget, it answers a deployment question: *should this atlas be locally repaired, or left untouched?*

## What's in this repo

| Path | What |
|---|---|
| `pbr_atlas/` | Core library: differentiable baker, baselines, residual attribution, chart repair, allocator, C5 gate |
| `scripts/` | Entry points for the experiment grids (`run_B3.py`, `run_diligent_mv.py`, `W1_lean_grid.sh`, `W2_expanded_partuv_grid.sh`, ...) |
| `configs/` | Hyperparameter configs for each block (B1-B7 and W1-W2) |
| `paper/` | LaTeX source for the submission |
| `refine-logs/` | Method spec (`FINAL_PROPOSAL.md`), experiment plan, structural review log |
| `figures/scripts/` | Plot generators that read run metrics into paper-ready figures |

## Quickstart

```bash
conda create -n respair python=3.10 -y
conda activate respair
pip install -r requirements.txt
# main controlled evaluation
python scripts/run_B3.py --asset spot --baseline partuv --method ours --config configs/B3_main.yaml
# real-mesh transfer
python scripts/run_B7_transfer.py --asset f3d_head --baseline partuv --method ours --config configs/B7_transfer.yaml
# DiLiGenT-MV captured rollback audit
python scripts/run_diligent_mv.py --asset bear --baseline partuv --method ours --use-pms
```

Run metrics land in `runs/<block>/<run_id>/metrics.json`. Paper-ready tables are produced by `scripts/collect_*` and dropped into `paper/tables/`.

## Reproducing the headline numbers

The full main + transfer + real-mesh + DiLiGenT-MV evaluation is orchestrated by the shell drivers in `scripts/`. Each driver is idempotent and skips runs that already have `metrics.json` to make resumption safe across SSH disconnects. We use:

- `scripts/W1_lean_grid.sh` for the DiLiGenT-MV captured rollback audit (5 objects × {xatlas, PartUV} × {baseline_only, ours} × 3 seeds)
- `scripts/W2_expanded_partuv_grid.sh` for the 18-mesh real-mesh sweep (Fantasia3D, threestudio, Trellis-style, Objaverse init shapes)
- `scripts/run_n10_seeds.sh` for the multi-seed statistical-power upgrade on the key accepted cases

Headline accepts (held-out test split, multi-seed where applicable):

| Asset | Baseline | Init dB | Final dB | $\Delta$ |
|---|---|---:|---:|---:|
| spot | PartUV | 31.20$\pm$0.40 | 43.78$\pm$1.23 | **+12.58$\pm$0.83** |
| bunny | PartUV | 28.21$\pm$0.08 | 40.05$\pm$0.81 | **+11.84$\pm$0.89** |
| warped_cylinder | PartUV | 30.38 | 41.12 | **+10.74** |
| ts_potion | threestudio | 31.11 | 39.10 | **+7.99** |
| f3d_animal | Fantasia3D | 31.32 | 37.71 | **+6.39** |
| ts_animal | threestudio | 36.02 | 41.79 | **+5.77** |
| ts_nascar | threestudio | 34.05 | 37.90 | **+3.85** |
| f3d_head | Fantasia3D | 30.76 | 34.37 | **+3.61** |
| ts_cabin | threestudio | 33.31 | 34.50 | **+1.19** |

All other tested cells roll back to the baseline atlas without deployed degradation.

## Citation

```bibtex
@inproceedings{respair2026,
  title  = {PBR Baking-Error Atlases for Selective UV Atlas Repair},
  author = {Anonymous},
  year   = {2026},
  booktitle = {Pacific Graphics / Computer Graphics Forum special issue (submitted)}
}
```

## License

MIT (see `LICENSE`). Paper text and figures are CC BY 4.0.
