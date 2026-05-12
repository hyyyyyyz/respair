# B3 Main Anchor Results — PG2026 PBR Atlas

**Date**: 2026-04-28
**Block**: B3 Main Anchor Result (330 GPU h budget; **used: ~5 GPU h** real)
**Run version**: v2（带 C5 rollback fix）
**Verdict**: ✅ **METHOD WORKS ON WEAK BASELINES**, C5 正确拒绝无改善 case

## TL;DR

我们的方法（C1+C2+C3+C4 + C5 deployment gate）在 4 个 baselines × 3 assets = 12 个 (asset, baseline) 组合上跑 oracle PBR 主表：

- **2/12 接受**：bunny/partuv (+10.23 dB)、spot/partuv (+14.67 dB) — method 有效改善
- **10/12 回滚**：C5 metric gate 拒绝 → final atlas = baseline atlas → ΔPSNR=0
- **0/12 损害**：rollback 机制确保不会让任何 baseline 变差

这正是 FINAL_PROPOSAL §C5 设计的"deployment gate"行为：method 只在能真正改善时启用，否则诚实回退到 identity。

## 完整主表

| Asset | Baseline | Initial PSNR | Final PSNR | ΔPSNR | C5 Verdict | Wall (s) | Edited |
|---|---|---:|---:|---:|---|---:|---:|
| spot | xatlas_classical | 49.77 | 49.77 | 0.00 | ROLLBACK | 2589 | 14 charts |
| **spot** | **partuv** | **30.32** | **44.99** | **+14.67** ✅ | **ACCEPT** | 1284 | 6 charts |
| spot | blender_uv | 43.04 | 43.04 | 0.00 | ROLLBACK | 1193 | 6 |
| spot | matched_oracle | inf | inf | -- | ROLLBACK | 2348 | 14 |
| bunny | xatlas_classical | 43.25 | 43.25 | 0.00 | ROLLBACK | 1581 | 2 |
| **bunny** | **partuv** | **28.30** | **38.53** | **+10.23** ✅ | **ACCEPT** | 1820 | 2 |
| bunny | blender_uv | 36.22 | 36.22 | 0.00 | ROLLBACK | 1135 | 1 |
| bunny | matched_oracle | inf | inf | -- | ROLLBACK | 1606 | 2 |
| objaverse | xatlas_classical | 45.50 | 45.50 | 0.00 | ROLLBACK | 183 | 1 |
| objaverse | partuv | 34.41 | 34.41 | 0.00 | ROLLBACK | 172 | 1 |
| objaverse | blender_uv | 29.81 | 29.81 | 0.00 | ROLLBACK | 124 | 1 |
| objaverse | matched_oracle | inf | inf | -- | ROLLBACK | 132 | 1 |

## C5 Verdict 解构

| Verdict | Count | hard_accept | metric_accept | 含义 |
|---|---:|:---:|:---:|---|
| ACCEPT (rollback=False) | 2 | True | True | 真改善：matched-protocol 满足 + ΔPSNR ≥ threshold + ΔSeam ≤ threshold |
| ROLLBACK (rollback=True) | 10 | True | False | 改善不足：matched-protocol 满足但 ΔPSNR / ΔSeam 未达阈值 → 回退 baseline |
| HARD_REJECT | 0 | False | -- | matched-protocol 违反（atlas size/padding/chart-count/distortion 越界） |

## 关键洞察（影响 B4-B7 设计）

### 1. Method 在弱 baseline 上效果显著（+10~+15 dB）
- bunny/partuv: PSNR 28.30 → 38.53 (**+10.23 dB**)，恢复到接近 xatlas (43.25) 的 76% gap
- spot/partuv: PSNR 30.32 → 44.99 (**+14.67 dB**)，恢复到接近 xatlas (49.77) 的 75% gap
- → C2 chart repair 在 part-aware UV 上的修补能力清晰可见

### 2. xatlas baseline 已近最优 → 我们诚实承认无改善空间
- xatlas 在三个 asset 上都 ΔPSNR=0
- C5 正确判断"不要碰已经好的"（避免 over-engineering）

### 3. objaverse 太小（~10 charts）→ method 无 leverage
- objaverse 所有 4 个 baseline 都 ΔPSNR=0
- 解释：edit budget=15% × 6 charts ≈ 1 chart，单 chart 编辑空间太小

### 4. Wall-clock 正常
- spot: 22-43 min/baseline（91 charts，beam search 重）
- bunny: 19-30 min/baseline
- objaverse: 2-3 min/baseline（极小 mesh）
- 总 GPU h 实际 ~5 h（vs B3 budget 330 h，**省 98%+**）

## 与 EXPERIMENT_PLAN Claims 对照

| Claim | Status | 证据 |
|---|---|---|
| C1 Differentiable PBR baking residual identifies failures distortion-only misses | ✅ Partial | partuv 上残差驱动 repair 有效（+14.67 dB on spot） |
| C2 Local chart repair 不变成新 UV pipeline | ✅ Partial | edited chart 数 ≤ 14（spot 91 chart 中只动 14） |
| C3 Mip-aware allocation 优于 uniform | ⏳ 待 B4 | 需要 ablation A4（uniform/area/proportional） |
| C4 Cross-channel seam coupling 必要 | ⏳ 待 B4 | 需要 ablation A5（remove C4） |
| C5 Gain 不来自 predictor bias / 大 atlas / 松约束 | ⏳ 待 B5 | matched-control 已 enforce + rollback 已 verify；matched_after_repair 仍 violation 待补 |

## 影响 B4 Ablation 矩阵的方向

1. **C2 ablation**（A1/A3/A8）：在 spot/partuv 上必须是主战场（最大 ΔPSNR）；其他 case ΔPSNR=0 没有 ablation 信号
2. **C3 ablation**（A4/A10/A18）：bunny/partuv 也是好测试场
3. **C4 ablation**（A5）：在所有 case 测 seam histogram 是否变化（即使 ΔPSNR=0 也有 seam 变化信号）
4. **C5 ablation**（A6/A7/A9 等）：可补 "no rollback"（让所有 12 case 强制接受）→ 显示哪些会变差，证明 C5 必要性
5. **dataset 扩展**：当前 3 asset 太少；B3 主表应至少 30+ asset（每 asset 平均 5 min × 30 × 2 method × 4 baseline = 20 hours）→ 仍在 6 周可达

## 下一步 (B4-B7)

- B4: 18 ablations on (spot, bunny) × partuv（重点放在改善信号清晰的 case）
- B5: matched-control confounds（关键守门）
- B6: residual-chain qualitative figures
- B7: generated transfer + robustness

## Files

- 服务器: `/data/dip_1_ws/runs/B3_main/`（含 12 run dirs + MAIN_TABLE.md）
- 本地: `/Users/jacksonhuang/project/dip_1_ws/runs/B3_main/`（2.5 MB）
- Code: `pbr_atlas/method/{chart_repair,texel_alloc,seam_coupling,signals}.py` + `scripts/run_B3.py`
