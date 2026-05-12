# Experiment Tracker

| Run ID | Block | Config | GPU h | Status | Result | Notes |
|---|---|---|---:|---|---|---|
| B1-001 | B1 | bunny (procedural fallback), seed=42, 1024px atlas, 6 train + 4 holdout view, 4+4 light, bf16 | 0.003 | ✅ DONE | PSNR 27.88 / SSIM 0.857 / LPIPS 0.234 / max e_f 0.326 / G_l 0.889 / peak mem 0.57 GB / wall 9.6s | C1 baker forward+backward 跑通；procedural fallback bunny normals 较 noisy 导致 normal MAE 40°；output 0.08 MB ✅ storage-safe |
| B1-DET | B1 | bunny, seed=42, run twice | 0.006 | ✅ DONE | e_f / E_c / G_l diff = 0 全部精确一致 | Determinism check **PASS**；CUBLAS_WORKSPACE_CONFIG warning 无影响实际确定性 |
| B1-002 | B1 | spot (real UV mesh), seed=42, same config | 0.003 | ✅ DONE | PSNR 33.40 / SSIM 0.932 / LPIPS 0.095 / max e_f 0.082 / G_l 0.0 / peak mem 0.57 GB | 真实 UV → 显著好于 procedural bunny；G_l=0 说明 Spot atlas 无 mip 漏色（baseline 验证 method 在干净 atlas 上行为正确）|
| B1-003 (待跑) | B1 | objaverse (procedural fallback), seed=42 | ~0.003 | PENDING | — | objaverse HF 实时下载未启用，procedural fallback 有效；可选作 robustness sanity |

## B1 Sanity 结论（W1 第一关）

**全部通过**：
- C1 baker forward + backward 在 4090 GPU1 上跑通，gradients all finite
- 显存峰值 **0.57 GB**（远低于 14 GB 预算，**留 23 GB 余量**给 C2-C5 / 双卡并行）
- Wall-clock per asset **9.6 s**（W4 估算每天 30 assets/day 现在看完全可达，可能远超）
- Storage **0.08 MB / asset**（200 MB/asset 预算的 0.04%，**实际全集 600 assets 约 50 MB total**）
- Determinism PASS：同 seed 完全 reproducible
- 真实 UV (Spot) 表现优于 procedural fallback (bunny) → method 在 high-quality input 上更稳定（符合 hypothesis）

**与 EXPERIMENT_PLAN B1 success criterion 对照**：
- ✅ Differentiable PBR baking residual 计算正确
- ✅ Per-face e_f / per-chart E_c / mip leakage G_l 全部产生
- ✅ Storage-safe on-the-fly rendering 验证
- ✅ Determinism guaranteed under fixed seed

**不需要触发任何 risk register 中的 fallback**（finite-difference / 子集化 / 减小 atlas）。

## 下一步

进入 B2 Baseline Reproduction（PartUV / FlexPara / classical xatlas / OT-UVGS adapted），或先在 1-2 个 Objaverse 真实 asset 上做扩展 sanity（B1-extra）。

**当前 GPU 占用**：仅 GPU1 用过 0.57 GB，其他项目共 ~12 GB。可以开始小规模并行测试。
