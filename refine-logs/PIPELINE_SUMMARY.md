# Pipeline Summary: Dual-Card Upgrade

**Date**: 2026-04-27
**Scope**: Upgrade the I-A3-001-p experiment pipeline from single-card 640 GPU h to dual-card 1280 GPU h while keeping the method itself single-card runnable.

## Upgrade Snapshot

| Item | Before | After |
|---|---|---|
| GPU budget | 640 GPU h on one RTX 4090 | 1280 GPU h effective on 2x RTX 4090 |
| Method requirement | single-card runnable | unchanged; second card only for multi-asset throughput |
| Ablations | 11 | 18, including matched utilization/distortion/padding/chart-count and texture/BRDF/light sweeps |
| Baselines / controls | 4-5 | 8: PartUV, FlexPara, xatlas/classical, OT-UVGS-adapted, Flatten Anything, ParaPoint, TexSpot, Chord |
| Datasets | ShapeNet / Objaverse / Thingi10K main sets | same core pool plus generated stress subset and 2-3 animated assets |
| User study | optional inside transfer block | B8 expert preference, n=10-15, quantitative-only pivot if n<8 |
| Temporal pilot | none | B9 4D/dynamic stability pilot on Mixamo / DeformingThings4D |
| Storage stance | 1.8-2.5TB estimate | on-the-fly rendering; persist residuals/tables/figures under `/data` constraint |

## 6-Week Milestones

| Week | Milestone |
|---|---|
| W1 | B1 baker sanity, metric determinism, storage-safe on-the-fly rendering; xatlas/PartUV pilot. |
| W2 | C1-C4 integration and 8-baseline/control protocol freeze. |
| W3 | B3 main oracle/predicted runs on GPU0; B4 A1-A9 core ablations on GPU1. |
| W4 | B3 finish on GPU0 while B5 matched controls and A10-A13 run on GPU1; B6 residual-chain seed starts. |
| W5 | B6 channel stress and B7 generated transfer on GPU0; A14-A18 sweeps and B9 temporal pilot on GPU1. |
| W6 | B8 comparison-board rendering, B9 cleanup, final tables/figures, PG writing package. |

## W4 First PR-able Results

By the end of W4, the project should have a reviewable core package:

- Main quantitative table: ours vs strongest valid baselines on oracle/predicted/stress assets.
- Matched-control table: utilization, distortion, padding, and chart-count locked.
- Main qualitative chain: residual atlas -> chart edit overlay -> relit/seam improvement.
- Early ablation evidence: C1-C4 removal plus matched-control deltas.

If W4 does not show oracle-PBR positive evidence, the plan pivots before spending the remaining budget on user study, temporal pilot, or large appendix sweeps.
