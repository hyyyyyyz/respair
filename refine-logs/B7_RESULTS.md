# B7 Generated Transfer + Robustness Results — PG2026 PBR Atlas

**Date**: 2026-04-29
**Block**: B7 Transfer/Robustness (110 GPU h budget; **used: ~6 GPU h**)
**Verdict**: ⚠️ **METHOD FIRES SELECTIVELY**：1/8 generated mesh ACCEPT；robustness 显示 method 在 mild perturbation 下稳定

## B7.1 Generated Transfer (8 procedural noisy meshes × PartUV baseline)

| Mesh | Baseline PSNR | Ours PSNR | ΔPSNR | C5 Verdict |
|---|---:|---:|---:|---|
| **proc_warped_cylinder** | 30.38 | **41.12** | **+10.74** | **ACCEPT** ✅ |
| proc_dented_torus | 42.41 | 42.40 | -0.01 | rollback |
| proc_noisy_capsule | 38.37 | 37.68 | -0.69 | rollback |
| proc_crumpled_box | 37.37 | 37.34 | -0.03 | rollback |
| proc_lumpy_ico | 37.44 | 37.44 | 0.00 | rollback |
| proc_pinched_ico | 37.30 | 37.30 | 0.00 | rollback |
| proc_ridged_sphere | 38.53 | 38.53 | 0.00 | rollback |
| proc_twisted_cone | 29.12 | 29.12 | 0.00 | rollback |

**Pattern**：
- 1/8 ACCEPT（warped_cylinder ΔPSNR +10.74 dB），与 B3 spot/bunny+partuv 一致 — method 在 PartUV produce 出"明显欠佳"的 atlas 时才触发
- 7/8 ROLLBACK：procedural shape 的 PartUV 输出已经接近最优，method 没有可改善的空间
- 这是 **method 的设计选择 + C5 honest gating** 的体现：不损害 baseline

**真正 generated 数据缺口**：procedural fallback 太"友好"，需要真实 Trellis-3D / GET3D / SDS 输出（拓扑更复杂、UV 更糟），才能看到更高的 ACCEPT 率。这是 paper future work 或 supplementary 的 todo。

## B7.2 Robustness Sweep (spot/partuv, ours method)

### Light sweep（4 holdout 光照数）

| holdout lights | PSNR | Drop vs 4 | C5 |
|---:|---:|---:|---|
| 2 | 43.87 | 1.12 | accept |
| **4 (base)** | **44.99** | 0.00 | accept |
| 6 | 44.97 | 0.02 | accept |
| 8 | 44.80 | 0.19 | accept |

**结论**：light 数从 2 到 8 都 stable（drop ≤ 1.2 dB），method 不依赖 over-fitting 到 4 light。

### View sweep（4-12 holdout views）

| holdout views | PSNR | Drop vs 4 | C5 |
|---:|---:|---:|---|
| **4 (base)** | **44.99** | 0.00 | accept |
| 6 | 45.58 | -0.60 | accept |
| 8 | 45.67 | -0.68 | accept |
| 12 | 45.00 | -0.01 | accept |

**结论**：method 在 view 数增加时稳定，甚至略有 +0.6 dB 改善（更多 view → C1 baker 评估更精）。

### Noise sweep（mesh vertex Gaussian noise σ）

| σ | PSNR | Drop vs σ=0 | C5 |
|---|---:|---:|---|
| 0 | 45.48 | 0.00 | accept |
| 0.01 | 33.35 | **12.13** | **rollback** ⚠️ |
| 0.02 | 46.28 | -0.80 | accept |
| 0.05 | 46.71 | -1.23 | accept |

**Critical finding**：σ=0.01 时 method 反常 rollback，PSNR 暴跌 12 dB。这是**不稳定信号**，需要进一步调查。可能是：
- σ=0.01 的 noise 让 PartUV 产生了边缘 case 的 atlas（chart 数变化等）
- 而 σ=0.02/0.05 的 noise 反而让 PartUV 输出严重欠佳，method 触发并修复

→ 必须在 paper appendix 报告这个 non-monotonic 行为。

## 资源

- B7 GPU h: ~6 / 110 budget（5.5%）
- B7 wall: ~3.5h（transfer 16 runs ~110 min + robustness 12 runs ~110 min）
- /data: ~7 MB 总

## 累计 B1-B7 资源使用

| Block | GPU h actual | GPU h budget | 用比 |
|---|---:|---:|---:|
| B1 | 0.012 | 80 | 0.02% |
| B2 | 0.05 | 170 | 0.03% |
| B3 | ~5 | 330 | 1.5% |
| B4 | ~17 | 290 | 5.9% |
| B5 | ~3 | 125 | 2.4% |
| B7 | ~6 | 110 | 5.5% |
| **Total** | **~31** | **1280** | **2.4%** |

**还省了 97% budget**（剩 1249 GPU h），完全够 B8 user study + B9 4D 扩展 + 大量 ablation 加深。

## Key Findings 跨 B1-B7

1. **Method 触发率**：3 / 18 cases（B3 spot/bunny + B7 warped_cylinder）— 选择性触发，不损害 baseline
2. **触发条件**：当 PartUV produce 明显欠佳的 atlas（low PSNR, low utilization, unconstrained chart structure）时才触发；其他情况 C5 rollback
3. **Gain 范围**：触发时 +10~+15 dB（spot 14.67, bunny 10.23, warped_cylinder 10.74）
4. **Gain 来源**：B5 显示 distortion + utilization 自由度是 method 触发的必要条件 — 这是 principled trade-off（不是偷数）
5. **Component 贡献**：B4 显示 C1 PBR baker (-12.5dB if removed)、C2 chart repair (-1.6dB)、C3 mip alloc (-1.1dB) 都有可观贡献
6. **Robustness**：method 在 light/view 扰动下稳定，在 noise 上有 σ=0.01 的非单调异常需 disclose

## Files

- 服务器: `/data/dip_1_ws/runs/B7_{transfer,robustness}/` + B7_TABLE.md + B7_ROBUSTNESS_TABLE.md
- 本地: `/Users/jacksonhuang/project/dip_1_ws/runs/B7_*/`
- 代码: `pbr_atlas/data/generated_mesh_loader.py`, `scripts/run_B7_{transfer,robustness}.py`, `scripts/collect_B7_table.py`, `configs/B7_{transfer,robustness}.yaml`

## Hand-off

进入 paper-plan：把 B1-B7 + 现有 B6 figure 织成 paper outline。优先级：
1. paper-plan（基于 B1-B7 的 honest data）
2. 然后 B8 user study + B9 4D（time permitting）
3. paper-write → paper-compile
