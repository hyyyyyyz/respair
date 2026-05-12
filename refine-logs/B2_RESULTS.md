# B2 Baseline Reproduction Results — PG2026 PBR Atlas

**Date**: 2026-04-27 / 2026-04-28
**Block**: B2 Baseline Reproduction and Matched Protocol (170 GPU h budget; **used: ~0.05 GPU h**)
**Server**: server2 / RTX 4090 GPU1
**Verdict**: ⚠️ **PARTIAL** — scaffold + matched-protocol enforcement in place; 2/9 baselines fully verified, 4/9 proxy (real repos cloned but not integrated), 3/9 failed

## Honesty Status (per Review Guardrail #4: failure table mandatory)

| 类别 | 数量 | Baseline 列表 | 真实状态 |
|---|---|---|---|
| ✅ Real & matched-OK | 1 | xatlas_classical | 完整 xatlas Python API；matched-protocol 全部满足 |
| ✅ Real & matched-violator | 1 | blender_uv | Blender 3.0.1 Smart UV；不同范式（chart 数 ≪ xatlas），matched-protocol 违规属预期 |
| ⚠️ Real reference (理论上界) | 1 | matched_oracle | 自实现 ground-truth UV reference（PSNR=∞） |
| ⚠️ Proxy（repo 已 clone 但未真实接入） | 4 | partuv, flexpara, otuvgs, visibility_param | repo 在 `/data/dip_1_ws/baseline_repos/`，proxy 实现走的是 dominant-axis / PCA-grid / visibility-weighted 启发式；**论文不可作为正式 reproduction claim** |
| ❌ Failed (no repo wiring) | 2 | flatten_anything, parapoint | 登记到 B2_FAILURE_TABLE.md |

## Real Verified Baselines（可写进 paper）

| Asset | Baseline | PSNR | SSIM | LPIPS | E_c mean | G_l | Charts | Util | Dist Q95 | Matched OK |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| bunny | xatlas_classical | 36.88 | 0.989 | 0.016 | 0.0006 | 0.734 | 8 | 0.579 | 8.0 | ✅ |
| bunny | blender_uv | 30.16 | 0.954 | 0.092 | 0.0019 | 0.279 | 2 | 0.778 | 60.9 | ❌ paradigm |
| bunny | matched_oracle | inf | 1.000 | 0.000 | 0.0000 | 0.727 | 8 | 0.371 | 20.0 | ❌ util |
| spot | xatlas_classical | 45.95 | 0.997 | 0.005 | 0.0015 | 0.670 | 91 | 0.661 | 5.3 | ✅ |
| spot | blender_uv | 41.33 | 0.988 | 0.028 | 0.0037 | 0.413 | 37 | 0.467 | 73.0 | ❌ |
| spot | matched_oracle | inf | 1.000 | 0.000 | 0.0000 | 0.666 | 91 | 0.374 | 28.0 | ❌ util |
| objaverse | xatlas_classical | 39.85 | 0.990 | 0.009 | 0.0011 | 0.895 | 6 | 0.732 | 0.6 | ✅ |
| objaverse | blender_uv | 26.49 | 0.843 | 0.198 | 0.0108 | 0.793 | 2 | 0.998 | 62.5 | ❌ paradigm |
| objaverse | matched_oracle | inf | 1.000 | 0.000 | 0.0000 | 0.883 | 6 | 0.713 | 1.3 | ✅ |

## Proxy Baselines（HONEST but NOT publishable as reproduction）

PartUV / FlexPara / OT-UVGS / VisibilityParam (arXiv:2509.25094v3 attempt) 都使用启发式 proxy 替代真实 repo inference。结果数字仅供 sanity，**绝不能在 paper 中作为"我们 reproduce 了 X 方法"的 claim**。

详见 `B2_FAILURE_TABLE.md`。

## Acceptance vs Plan §B2

| Criterion | Target | Actual | Status |
|---|---|---|---|
| ≥6 baseline 实现（含 proxy 也算 attempt） | 6 | 7 (5 proxy + 2 real + 1 oracle) | ✅ |
| matched_protocol enforce + violator detection | yes | 完整实现 + 13/27 pass + 6/27 violator + 8/27 N/A | ✅ |
| Failure table 登记 | mandatory | B2_FAILURE_TABLE.md 完整 | ✅ |
| 显式 attempt arXiv:2509.25094v3 (Guardrail #1) | mandatory | visibility_param.py + 失败表登记 | ✅ |
| 公平对比：同 mesh/同 view/同 light | yes | 全部 baseline 共享 mesh + holdout views/lights | ✅ |
| 单 baseline-asset ≤30s | ≤30s | wall-clock 25-165s（多数 <60s） | 部分超 |

## Implications for B3 Main

**可作为 B3 主结果对照的"真"baseline 只有 2 个**：xatlas_classical（强对照）+ matched_oracle（理论上界）。

**必须在 B3 之前补完**（Guardrail：reviewer 攻击点）：
1. 至少把 PartUV (arXiv:2511.16659v2) 真正接入 — repo 已 clone 在 `/data/dip_1_ws/baseline_repos/PartUV/`
2. 至少把 FlexPara (arXiv:2504.19210v3) 真正接入 — repo 已 clone 在 `/data/dip_1_ws/baseline_repos/FlexPara/`
3. 不接入也行，但 paper §Baselines 必须**显式说明** PartUV/FlexPara 在我们环境无法复现，failure table 在 appendix 列出，且去除"我们和 PartUV 比"的措辞，改为"我们参考 PartUV gap analysis"

## 资源使用

| 项 | 预算 | 实际 | 余量 |
|---|---:|---:|---:|
| GPU memory peak | 14 GB | 0.42 GB | 23.6 GB safety |
| GPU h (B2 budget) | 170 | ~0.05 | 99.97% 余量 |
| Storage | 50 GB cap | 1.3 MB | 99.99% 余量 |
| Wall-clock | — | 25-165s/baseline-asset | ~10 min total grid |

## Files

- 服务器: `/data/dip_1_ws/runs/B2_baseline/` (含 27 个 run + MATCHED_TABLE.md + B2_FAILURE_TABLE.md + B2_RESULTS.md)
- 本地: `/Users/jacksonhuang/project/dip_1_ws/runs/B2_baseline/`
- 代码: `pbr_atlas/baselines/{base,xatlas_classical,blender_uv,partuv,flexpara,otuvgs,flatten_anything,parapoint,visibility_param,matched_oracle,matched_protocol,baseline_failure_table}.py`
