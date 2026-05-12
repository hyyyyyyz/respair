# B2 Real Baseline Integration Report — PG2026

**Date**: 2026-04-28
**Block**: B2 Baseline Reproduction (real-integration round)
**Verdict**: 2/8 真实接入；6/8 honest failure with reasons

## 真实接入状态

| Baseline | Repo Status | Wrapper Status | Verdict | 备注 |
|---|---|---|---|---|
| **xatlas_classical** | xatlas Python pkg ✅ | real | ✅ REAL | matched-protocol pass on all 3 assets |
| **blender_uv** | apt blender 3.0.1 ✅ | real（patched OBJ import API） | ✅ REAL | matched-protocol violator (Smart UV 不同范式，预期) |
| **partuv** | repo cloned + bpy 4.5.9 ✅ | real（subprocess + UV island detection） | ✅ REAL | spot 19 charts / bunny 2 / objaverse 2；matched-protocol violator |
| **matched_oracle** | self-implemented ✅ | real | ✅ REAL | 理论上界 PSNR=∞ |
| flexpara | repo cloned but PyTorch 1.10 + 无 ckpt + 自编 CUDA ops | proxy（PCA-grid） | ⚠️ PROXY | 见下文 reason |
| otuvgs | 公开 repo 不可定位（"未核实"） | proxy | ⚠️ PROXY | URL 在 BRIEF 中标 unverified |
| flatten_anything | repo cloned but Python 3.9 specific + pre-compiled kNN | failed → none | ❌ FAILED | code unavailable in our env |
| parapoint | URL 不可定位 | failed → none | ❌ FAILED | repo URL "未核实" |
| visibility_param (arXiv:2509.25094v3) | 无公开 repo | proxy | ⚠️ PROXY | review guardrail #1 显式 attempt + 失败表登记 |

## 真实接入的 PartUV 数字（关键）

| Asset | xatlas PSNR | partuv PSNR | xatlas charts | partuv charts | matched OK (xatlas) | matched OK (partuv) |
|---|---:|---:|---:|---:|:---:|:---:|
| bunny | 36.88 | 24.09 | 8 | **2** | ✅ | ❌ chart_count |
| spot | 45.95 | 29.46 | 91 | **19** | ✅ | ❌ chart/util/distortion |
| objaverse | 39.85 | 31.55 | 6 | **2** | ✅ | ❌ chart/util/distortion |

PartUV 的低 PSNR 反映了其**部件感知 UV** 的设计：用更少更大的 chart 换取 part 边界对齐，distortion 显著高于 xatlas 但 chart 数大幅下降。这是真实 PartUV 行为，可作 paper 主对比的"part-aware UV vs distortion-min UV"叙事。

## FlexPara 失败原因（详细）

阻挡因素：
1. **Python 3.9 only**：upstream 在 Python 3.9 编译，我们的环境是 3.10/3.11
2. **PyTorch 1.10.1 cu111**：与我们的 2.7.1 cu128 不兼容；cuda runtime 不同；custom CUDA ops 无法重编
3. **自编 CUDA ops** (cdbs/CD, cdbs/EMD)：必须与运行时 PyTorch 版本一致才能 link
4. **无 shipped checkpoint**：仓库不含 `flexpara_global.pth` / `flexpara_multi_8.pth`，需逐 mesh 训练 ~10K iters (~30 min/mesh)
5. **B2 budget 不允许**：完成 FlexPara 需创独立 conda env + 重编 + 逐 mesh 训练 600+ assets，估 30+ GPU hours，超 B2 budget

替代方案（已采用）：保留 PCA-grid proxy 为 partial 实现，附 explicit failure note；paper §Baselines 必须明确说明 FlexPara 未真复现。

## 软件栈（真实接入用）

```
/data/conda_envs/partuv/  Python 3.11 + PyTorch 2.7.1 cu128 + torch-scatter 2.1.2 + bpy 4.5.9 + partuv 0.x + cumesh2sdf
/data/conda_envs/dip1_pbr/  Python 3.10 + PyTorch 2.7.1 cu128 + nvdiffrast + Mitsuba 3.5.0 + xatlas + Blender 3.0.1（系统 apt）
```

PartUV wrapper 通过 subprocess 调用 partuv env 的 python，input mesh 经临时 OBJ 写入 → `demo/partuv_demo.py --pack_method blender` → 解析 `final_components.obj` + UV island detection → BaselineAtlas。

## 影响 B3 主实验

**可作主对比的真 baseline**：
1. **xatlas_classical**（matched-protocol 完全 pass，强基准）
2. **PartUV**（matched-protocol violator 但 honest，证明部件感知 UV 与 distortion-min UV 的差异化）
3. **matched_oracle**（理论上界）
4. **blender_uv**（Smart UV 不同范式，作"naive 通用 UV"对比）

**不可作主对比的 proxy**（必须放 appendix + 显式声明）：
- flexpara, otuvgs, visibility_param: 启发式 proxy
- flatten_anything, parapoint: 完全 failed

## Files

- `/data/dip_1_ws/baseline_repos/PartUV/`（clone + bpy + ckpt 全部就位）
- `/data/dip_1_ws/ckpts/partfield/model_objaverse.ckpt`（1.2 GB）
- `/data/conda_envs/partuv/`（独立 env，bpy 4.5.9）
- `/data/dip_1_ws/runs/B2_baseline/{spot,bunny,objaverse}_partuv_seed42/`（真实 PartUV 输出）
- `pbr_atlas/baselines/partuv.py`（真实 subprocess wrapper + UV island detection）
- `pbr_atlas/baselines/flexpara.py`（带详细失败原因的 proxy 版）

## 进入 B3 的就绪状态

- [x] 至少 2 个真实接入的 baseline（xatlas + partuv）覆盖三个 asset
- [x] matched-protocol enforcement 真实工作（chart_count/util/distortion 都正确捕获 violator）
- [x] failure table 完整登记每个未真接入的 baseline 与原因
- [x] review guardrail #1（arXiv:2509.25094v3 显式 attempt）已满足
- [x] B3 数据 pipeline 不受影响（C1 baker 接受任何 BaselineAtlas）

下一步进 B3 Main Anchor Result。
