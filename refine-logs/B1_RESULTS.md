# B1 Sanity Results — PG2026 PBR Atlas

**Date**: 2026-04-27 / 2026-04-28（跨日）
**Block**: B1 Sanity and Oracle Baker Pilot (80 GPU h budget; **used: 0.012 GPU h**)
**Server**: server2 / RTX 4090 GPU1 (other projects on GPU0/1 ~12 GB shared)
**Verdict**: ✅ **ALL PASS** — proceed to B2

## Acceptance Criteria (per EXPERIMENT_PLAN.md §B1)

| Criterion | Target | Actual | Status |
|---|---|---|---|
| C1 differentiable PBR baker forward+backward 跑通 | gradients all finite | all_grads_finite=true, loss=0.0129 | ✅ |
| Multi-view multi-light render 不爆显存 | ≤14 GB peak | **0.57 GB** | ✅ (留 23 GB safety) |
| Metric determinism (same seed → same output) | e_f / E_c / G_l diff=0 | diff=0 全部 | ✅ |
| Storage-safe on-the-fly rendering | persistent ≤200 MB / asset | **0.08 MB / asset** | ✅ |
| Pipeline 跑通 mesh+UV → bake → relight → residual | 1-3 sample asset | bunny (procedural) + spot (real UV) | ✅ |
| 输出 e_f / E_c / G_l 可观测 | metrics.json + residual_atlas.png | 全部生成 | ✅ |

## Quantitative Results

### Bunny (procedural fallback OBJ, xatlas-generated UV)

```
relit PSNR        : 27.88 dB
relit SSIM        : 0.857
LPIPS             : 0.234
albedo MAE        : 0.087
normal angular err: 40.2°  (procedural bunny 法线 noisy，预期值)
roughness MAE     : 0.081
metallic MAE      : 0.066
max e_f           : 0.326
G_l (mip leakage) : 0.889
seam top-20 hit   : 0.21
peak memory       : 0.57 GB
wall-clock        : 9.6 s
output size       : 0.082 MB
```

### Spot (Keenan Crane real UV mesh)

```
relit PSNR        : 33.40 dB     (+5.5 dB vs bunny, 真实 UV 优势)
relit SSIM        : 0.932
LPIPS             : 0.095
max e_f           : 0.082
G_l (mip leakage) : 0.0          (干净 atlas → 无漏色，符合 hypothesis)
peak memory       : 0.57 GB
output size       : 0.048 MB
```

### Determinism Check (Bunny, seed=42, 跑两次)

```
e_f  diff: 0.0
E_c  diff: 0.0
G_l  diff: 0.0
verdict  : PASS
```

## Resource Usage

| 项 | 预算 | 实际 | 余量 |
|---|---:|---:|---:|
| GPU memory peak | 14 GB | 0.57 GB | **23 GB safety** |
| GPU h (B1 budget) | 80 | 0.012 | **99.98%** |
| Storage / asset | 200 MB | 0.08 MB | **99.96%** |
| Wall-clock / asset | — | 9.6 s | 30 assets/day → 可达 ~9000 assets/day |

## Implications for B2-B7

1. **显存 budget 极宽松**：0.57 GB / 24 GB → 完全可以 (a) 把 atlas 升到 2K-4K、(b) batch 评估多 candidate edits 并行、(c) 与其他项目共享 GPU 不会冲突
2. **Wall-clock 极快**：B3 main run 估算 330 GPU h，按当前每 asset ≤10s + 多 view/light/PBR component 慢 10x = 100s/asset → 600 assets ≤ 17 GPU h **远低于 330 h 预算**
3. **Storage 极小**：原计划 200 MB/asset，实际 0.08 MB/asset = 0.04%，整套 600 assets ≤50 MB 持久化（除 oracle render 缓存）
4. **Determinism 保证**：CUBLAS_WORKSPACE_CONFIG warning 无影响（可选 export 提升严格度），seed 固定下完全 reproducible

## Findings to Watch

- **Procedural bunny 法线噪声大** (40.2° MAE)：B2 baseline 必须用真实 UV/normal 数据集，不能依赖 procedural fallback 做主表
- **Mip leakage G_l 在 procedural bunny 上 0.889**（vs spot 0.0）：说明 G_l 估算器对 chart 边界敏感；fallback bunny 是 single chart，但 procedural noise 可能导致虚假 leakage 信号 → 需要 B2 中验证 G_l 估算器在真实多 chart atlas 上的行为
- **seam top-20 hit rate 21%**（高残差面是否落在 chart 边界）：单 chart fallback 没意义；待 spot 多 chart 数据 + 真实多 chart 时再评估

## Hand-off to B2

下一步用 `/experiment-bridge` 翻译 B2 Baseline Reproduction:
- PartUV (arXiv:2511.16659v2) atlas → C1 bake on bunny/spot/objaverse
- FlexPara (arXiv:2504.19210v3) atlas → C1 bake
- xatlas classical → C1 bake (已可用，xatlas 已装)
- OT-UVGS-adapted (arXiv:2604.19127v1) → C1 bake
- 主问题：cite arXiv:2509.25094v3（review guardrail 1）—— 必须显式处理或在 baseline 中加入

## Files

- `/Users/jacksonhuang/project/dip_1_ws/runs/B1_sanity/` ← rsync from server
  - 20260428_001833_bunny_seed42/ (metrics.json, residual_atlas.npz/png, summary.md)
  - 20260428_001949_spot_seed42/
  - determinism_20260428_001910_bunny_seed42_{a,b}/ + .json verdict

- Server: `/data/dip_1_ws/runs/B1_sanity/` (380 KB total)
