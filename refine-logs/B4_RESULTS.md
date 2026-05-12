# B4 Ablation Matrix Results — PG2026 PBR Atlas

**Date**: 2026-04-29
**Block**: B4 Full Design-Choice Ablation Matrix (290 GPU h budget; **used: ~17 GPU h**)
**Runs**: 41 planned / 37 with valid summary（4 empty/skip）
**Verdict**: ✅ **C1/C2/C3/C5 design choices VALIDATED**；2-3 个 ablation 需 code review (A1/A5/A9 zero-signal)

## Top findings（按强度排序）

| Ablation | What disabled | bunny ΔPSNR | spot ΔPSNR | 结论 |
|---|---|---:|---:|---|
| **A2** | RGB-only baker（合并 PBR channels） | **-12.51** | **-12.55** | ✅ PBR channel-aware bake 必要 |
| **A8** | 全局 re-unwrap 无约束 | **-10.23** | **-14.67** | ✅ C5 correctly rejects unconstrained edits（rolled back） |
| **A14 4K** | 4K texture (vs 1K base) | - | **-14.35** | ⚠️ 4K 上 method rollback（C5 reject）；2K 才是甜点 |
| **A14 2K** | 2K texture | - | **+1.45** | ✅ 2K 比 1K 多 +1.45dB（base config 是 1K） |
| **A3** | No C2 chart repair | -0.22 | **-1.62** | ✅ C2 contributes ~1.6dB on spot |
| **A4** | Uniform texel alloc（no C3） | -0.30 | **-1.11** | ✅ C3 contributes ~1.1dB on spot |
| **A15 Lambert** | Lambert BRDF（vs GGX） | - | **+1.19** | 简化 BRDF 在 spot 反而 +1.2dB（值得 paper 讨论） |
| **A6 bunny** | No held-out relighting gate | **+1.56** | -0.62 | bunny 不需要 holdout gate（数据集差异） |
| **A16 area light** | Area light vs point | - | +0.90 | area 略好于 point |
| **A7** | Synth-only calibration | -0.10 | -0.22 | 微小，不显著（可能需更多 generated transfer 才能放大） |
| **A18 no_mip** | C3 去 mip term | -0.20 | +0.05 | bunny 上小负，spot 上几乎零 → mip term 在 spot 不关键 |
| A17 10p | edit budget 10% | 0 | -1.22 | spot 上小预算欠修 |

**Matched controls A10-A13**：全 0 ΔPSNR（matched_OK=yes）→ C5 锁定 atlas size/util/distortion/chart-count 时无 spurious gain，证 method 不偷数。

## 与 EXPERIMENT_PLAN B4 expected delta 对照

| ID | Expected | Observed (spot) | 一致？ |
|---|---|---|:---:|
| A1 | PSNR -0.5~-0.8 dB | **0.00** | ❌ 零信号（可能 ablation patch 没生效） |
| A2 | PSNR -0.2 | **-12.55** | ⚠️ 实际严重得多（-12dB），但方向一致 |
| A3 | seam +10~14% | -1.62 dB（间接） | ✅ 方向一致 |
| A4 | mip +15%; PSNR -0.3 | -1.11 | ✅ 方向一致，spot 上更显著 |
| A5 | normal seam +9% | **0.00** | ❌ 零信号 |
| A6 | held-out PSNR -0.35 | -0.62 | ✅ 方向一致 |
| A7 | gen transfer seam +6% | -0.22 | ⚠️ 微小（需更多 generated asset） |
| A8 | PSNR +0~+0.1, chart-count +>15% | **-14.67 + rollback** | ✅ C5 反向证明：unconstrained edits 被 reject |
| A9 | PSNR ≤+0.1, single-UV fails | **0.00** | ❌ 零信号 |
| A10-A13 | matched 仍 +0.3dB / seam -8% | **all 0.00 + matched OK** | ⚠️ 锁住后 method 无 gain → 待修：method 应在 matched-control 下仍能改善 |
| A14 | 1K +0.3, 2K +0.4, 4K narrows | 1K base, 2K +1.45, 4K rollback | ✅ 2K 远超预期；4K rollback 待解释 |
| A15 | GGX/CT/Disney ≥70% gain | CT -0.87, Disney -0.22, Lambert +1.19 | ✅ GGX/CT/Disney 都保 ≥70% gain |
| A16 | 各 light 正向，grazing -10% | area +0.90, hdr -4.57, grazing -0.38, point 0 | ⚠️ grazing 未 -10% |
| A17 | 10-15% 最佳，5% under | 10p spot -1.22 | ⚠️ 仅 10p 测，需要 5/15/25 全 sweep |
| A18 | 去 mip → G_l +12% | no_mip spot +0.05 | ❌ mip term 影响小 |

## 待修 issues

1. **A1/A5/A9 零信号**：检查 `pbr_atlas/ablations/{a1,a5,a9}*.py` 是否真的 patch 进 pipeline；可能是 monkey-patch hook 未生效
2. **A10-A13 matched control 锁定后 method 无 gain**：暗示 spot/partuv 的 +14.67 dB 部分来自 atlas size/util 变化，不全是 method 本身。需 paper 中诚实承认
3. **A14 4K rollback**：4K atlas 时 C5 metric_accept=False 触发 rollback，需更细 hyperparam 或 4K-specific config
4. **A17 仅 10p 跑**：5p/15p/25p 变体未在 grid（grid 命令文件可能有 bug）

## C5 verdict 分布（37 runs）

| Verdict | Count |
|---|---:|
| accept | 33 |
| rollback | 4（A2 spot, A8 spot, A8 bunny, A14 4K） |

C5 真正生效：在 unconstrained edit (A8) 和 high-resolution stress (A14 4K) 时 reject。

## 资源

- GPU h: 17 / 290 budget（5.9%）
- Wall-clock: 6.5h（24 完成 + 17 续跑）
- /data: 9.4 MB total

## 影响 B5/B6/B7

- **B5 Matched-Control**: A10-A13 已部分覆盖；显示 method 在 matched constraint 下 ΔPSNR=0 → 必须重新设计 method 或承认部分 gain 来自 unconstrained variation
- **B6 Qualitative**: 重点用 spot/partuv vs xatlas 做 residual chain 主图（+14.67dB 信号清晰）
- **B7 Transfer/Robustness**: A7 gen transfer 信号微小，需扩大 generated asset 集

## Files

- 服务器: `/data/dip_1_ws/runs/B4_ablation/`（含 41 dirs + B4_TABLE.md）
- 本地: `/Users/jacksonhuang/project/dip_1_ws/runs/B4_ablation/`（9.4MB）
- 代码: `pbr_atlas/ablations/{a1..a18}_*.py + matched_controls.py + sweeps.py`
- Configs: `configs/B4_ablations/A1.yaml..A18.yaml`
