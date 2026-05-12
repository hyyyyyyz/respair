# FINAL PROPOSAL: Differentiable PBR Baking-Error Atlas for Generated Assets

## Problem Anchor（≤4 句，整篇论文范围内不变）

AI-generated 或 noisy mesh 即使已有可用 UV atlas，也经常在固定 DCC texture budget 下出现 PBR baking residual、mip leakage、seam ringing 与 relighting artifact。本文不重新发明全局 UV unwrapping，而是在 PartUV/FlexPara/classical unwrap 的初始化上，只对 high-residual charts 做局部 repair、texel reallocation 与 cross-channel seam control。核心问题是：在相同 atlas size、padding、chart-count/distortion guard 下，如何让标准单套 UV atlas 更好地服务 albedo/normal/roughness/metallic 的 bake 与 relight。成功标准是 synthetic oracle PBR 与 generated predicted-PBR 两条线都显示 relit error、channel residual 和 seam map 稳定下降，而几何 distortion 与 DCC 可用性不退化。

## Thesis（≤2 句）

我们提出 Differentiable PBR Baking-Error Atlas：把 generated assets 的 atlas quality 从几何 distortion 主导改为 held-out PBR bake/relight residual 主导，并用可微 residual 只驱动局部 chart repair 与 mip-aware texel reallocation。核心 claim 是，在固定单套 UV atlas 与同等 texture budget 下，PBR baking-error feedback 比 distortion-only 或 capacity-only objective 更能减少下游材质与重光照 artifact。

## Why Now / Why This Bar（≤4 句）

到 2026-04，PartUV (arXiv:2511.16659v2) 已经覆盖 AI-generated mesh 的 part-aware unwrapping，FlexPara (arXiv:2504.19210v3) 已经覆盖 flexible neural parameterization，OT-UVGS (arXiv:2604.19127v1) 也把 Gaussian UV 写成 fixed-budget capacity allocation。新的 bar 不应是“再做一个 unwrap”，而应证明 UV atlas 是否真正改善 generated asset 在 PBR baking、mip、seam 和 relighting 下的可用性。PG/CGF 评审会要求同等 atlas size、padding、chart-count 和 distortion guard，因此本文把贡献压到 residual attribution、local edit、mip allocation、cross-channel seam coupling 和 matched-control validation。这个 framing 比 PartUV/FlexPara 高一档，因为它评价并优化 downstream appearance physics，而不是只优化 chart geometry。

## Core Method（4-6 named components）

### C1: Oracle-Controlled Differentiable PBR Baker

- **Name**: C1 Oracle-Controlled Differentiable PBR Baker
- **Input → Output**: mesh \(M=(V,F)\)、初始 UV \(U_0\)、atlas size \(S\)、PBR channels \(P=\{A,N,R,M_t\}\)、训练视角/光照 \(\mathcal{V}_{tr},\mathcal{L}_{tr}\)、held-out 视角/光照 \(\mathcal{V}_{ho},\mathcal{L}_{ho}\) → per-texel maps \(T_k\)、per-face residual \(e_f\)、per-chart residual \(E_c\)、seam residual map \(S_e\)、mip leakage map \(G_\ell\)。
- **Math / Algorithm**: 对 channel \(k\in\{A,N,R,M_t\}\)，用 differentiable rasterizer 得到 texel-to-surface coverage \(w_{t,f}\)，bake map
  \[
  T_k(t)=\frac{\sum_{f\in F} w_{t,f}\,P_k(f)}{\sum_{f\in F}w_{t,f}+\epsilon}.
  \]
  对 held-out pair \((v,l)\)，用 GGX microfacet renderer
  \[
  \hat I_{v,l}=R_{\mathrm{pbr}}(M,U,T_A,T_N,T_R,T_{M_t};v,l)
  \]
  计算 residual
  \[
  \mathcal{L}_{render}=\sum_{(v,l)\in\mathcal{V}_{ho}\times\mathcal{L}_{ho}}
  \rho_1(\hat I_{v,l}-I^{*}_{v,l})+\beta\frac{1-\mathrm{SSIM}(\hat I_{v,l},I^{*}_{v,l})}{2}
  +\gamma\,\mathrm{LPIPS}(\hat I_{v,l},I^{*}_{v,l}).
  \]
  face residual 用 raster contribution 反投影：
  \[
  e_f=\frac{\sum_{v,l,x}\alpha_{x,f}^{v,l}\,\|\hat I_{v,l}(x)-I^{*}_{v,l}(x)\|_1}
  {\sum_{v,l,x}\alpha_{x,f}^{v,l}+\epsilon},\quad
  E_c=\frac{1}{|F_c|}\sum_{f\in F_c}e_f.
  \]
- **Why principled**: 误差来自标准 PBR bake 和 held-out relighting，而不是人为给 UV distortion 加权；synthetic oracle PBR 直接隔离 upstream PBR predictor bias。
- **Loss / Objective**:
  \[
  \mathcal{L}_{C1}=\mathcal{L}_{render}
  +\lambda_{pbr}\sum_{k}\omega_k\|T_k-T_k^*\|_1
  +\lambda_{vis}\sum_f \mathrm{stopgrad}(q_f)e_f,
  \]
  其中 oracle assets 使用 \(T_k^*\)，generated assets 使用 predicted-PBR/control split，只把 \(\mathcal{L}_{render}\) 作为主信号。
- **训练时 vs 推理时行为**: 训练/开发阶段用 oracle synthetic assets 校准 \(\lambda\)、light set 与 residual attribution；推理阶段对单个 asset 运行 differentiable bake + held-out residual，不训练大模型。

### C2: Residual-Attributed Local Chart Repair

- **Name**: C2 Residual-Attributed Local Chart Repair
- **Input → Output**: 初始 charts \(\mathcal{C}_0\)、residual \(E_c\)、seam residual \(S_e\)、distortion guard \(D_{max}\)、edit budget \(K\) → repaired charts \(\mathcal{C}'\)、UV map \(U'\)、edit log。
- **Math / Algorithm**: 只选择 top-\(K\) residual charts
  \[
  \mathcal{C}_{edit}=\operatorname{TopK}_{c\in\mathcal{C}_0}(E_c+\eta S_c),
  \quad K\le \min(0.15|\mathcal{C}_0|,32).
  \]
  每个 chart 只允许 split、merge-with-neighbor、boundary slide、local ARAP reparameterization 四类 edit。对候选 edit \(a\in\mathcal{A}_c\)，定义
  \[
  J(c,a)=\Delta \mathcal{L}_{render}(c,a)
  +\lambda_d\,[D_{area}(U_a)-\tau_a]_+^2
  +\lambda_\theta\,[D_{angle}(U_a)-\tau_\theta]_+^2
  +\lambda_n\left||\mathcal{C}_a|-|\mathcal{C}_0|\right|
  +\lambda_b\Delta L_{seam}.
  \]
  用 beam search 保留 \(B=4\) 个局部候选，最终选
  \[
  a_c^*=\arg\min_{a\in\mathcal{A}_c}J(c,a).
  \]
- **Why principled**: 这是 constrained local optimization，不是新 UV pipeline；edit 空间被 residual、distortion tail、chart-count delta 与 seam length 共同约束。
- **Loss / Objective**:
  \[
  \mathcal{L}_{C2}=\mathcal{L}_{C1}
  +\lambda_{guard}\sum_c([D_{area}^c-\tau_a]_+^2+[D_{angle}^c-\tau_\theta]_+^2)
  +\lambda_{cc}\left||\mathcal{C}'|-|\mathcal{C}_0|\right|.
  \]
- **训练时 vs 推理时行为**: 训练阶段只学习 edit weights 和 thresholds；推理阶段固定 PartUV/FlexPara/classical output 为 \(U_0\)，执行 deterministic top-\(K\) local repair，并输出 edit budget 报告。

### C3: Mip-Aware Texel Budget Reallocator

- **Name**: C3 Mip-Aware Texel Budget Reallocator
- **Input → Output**: charts \(\mathcal{C}'\)、visibility \(V_c\)、PBR frequency \(F_c\)、mip leakage \(G_c\)、residual \(E_c\)、fixed atlas area \(A=S^2\) → per-chart texel area \(a_c\)、packed atlas。
- **Math / Algorithm**: 估计 chart demand
  \[
  q_c=(E_c+\epsilon)^{\alpha}(V_c+\epsilon)^\beta(F_c+\epsilon)^\gamma(G_c+\epsilon)^\delta,
  \]
  并在 fixed budget 下解 water-filling style allocation：
  \[
  a_c=A_{\min,c}+(A-\sum_jA_{\min,j})\frac{\exp(\tau\log q_c)}{\sum_j\exp(\tau\log q_j)}.
  \]
  \(F_c\) 来自 PBR channel 的 band-pass energy：
  \[
  F_c=\sum_{k,\ell}\omega_{k,\ell}\|\nabla D_\ell(T_k)|_c\|_1,
  \]
  \(G_c\) 来自 mip consistency：
  \[
  G_c=\sum_{\ell=1}^{L}\sum_{(t^+,t^-)\in\partial c}
  \|D_\ell(T)(t^+)-D_\ell(T)(t^-)\|_1.
  \]
- **Why principled**: fixed atlas budget 下，texels 被分给对 held-out relighting 和 mip aliasing 最敏感的 charts；这比 uniform density 或 distortion-only density 更接近下游 error minimization。
- **Loss / Objective**:
  \[
  \mathcal{L}_{C3}=\mathcal{L}_{C1}
  +\lambda_{mip}\sum_{\ell}\|R(D_\ell(T))-D_\ell(R(T))\|_1
  +\lambda_{pack}[u_{target}-u_{pack}]_+^2.
  \]
- **训练时 vs 推理时行为**: 训练阶段在 oracle set 上拟合 \(\alpha,\beta,\gamma,\delta,\tau\) 的小网格或 tiny MLP scorer；推理阶段使用固定 scorer 重新缩放 charts，并保持 atlas size、padding、chart count matched controls。

### C4: Cross-Channel Shared-Boundary Seam Coupler

- **Name**: C4 Cross-Channel Shared-Boundary Seam Coupler
- **Input → Output**: repaired atlas \(U'\)、PBR maps \(T_k\)、seam pairs \(\mathcal{E}_{seam}\)、channel tolerances \(\sigma_k\) → seam-aware loss、seam visibility map、channel-local residual histograms。
- **Math / Algorithm**: 对每条 seam pair \((p^+,p^-)\)，在 shared chart boundary 上计算 channel-normalized discontinuity：
  \[
  \mathcal{L}_{seam}=\sum_{(p^+,p^-)\in\mathcal{E}_{seam}}
  \sum_{k}\lambda_k\frac{\|T_k(p^+)-T_k(p^-)\|_1}{\sigma_k}
  +\lambda_n(1-\langle N(p^+),N(p^-)\rangle).
  \]
  对 normal、roughness、albedo 使用不同 tolerance，但约束单套 UV：
  \[
  U_A=U_N=U_R=U_{M_t}=U'.
  \]
- **Why principled**: DCC pipeline 通常要求 single UV set；多 channel 的 seam artifact 来自不同物理 channel 的尺度与感知容忍度，而不是需要多套 UV。
- **Loss / Objective**:
  \[
  \mathcal{L}_{C4}=\mathcal{L}_{seam}
  +\lambda_{hist}\sum_{k}\mathrm{W}_1(h_k^{seam},h_k^{interior}),
  \]
  其中 \(\mathrm{W}_1\) 度量 seam-local residual distribution 是否被拉回 interior residual level。
- **训练时 vs 推理时行为**: 训练阶段在三类 stress subsets 上校准 \(\sigma_A,\sigma_N,\sigma_R,\sigma_M\)；推理阶段只使用一套 UV 进行 channel-aware seam correction，并输出 normal/roughness/albedo 分离 failure maps。

### C5: Matched-Control Validation Loop

- **Name**: C5 Matched-Control Validation Loop
- **Input → Output**: baseline atlas \(U_0\)、candidate atlas \(U'\)、matched settings \((S,padding,|\mathcal{C}|,D_{tail})\)、held-out views/lights → accept/reject decision、residual atlas → chart edit → relit/seam improvement 主图。
- **Math / Algorithm**: 每次 repair 后必须满足 hard guard：
  \[
  S'=S,\quad padding'=padding,\quad ||\mathcal{C}'|-|\mathcal{C}_0||\le \Delta_C,\quad
  Q_{95}(D'_{area/angle})\le Q_{95}(D^0_{area/angle})+\epsilon_D.
  \]
  接受准则：
  \[
  \mathrm{Accept}(U')=
  [\Delta\mathrm{RelitPSNR}\ge\delta_p]\land
  [\Delta\mathrm{SeamErr}\le-\delta_s]\land
  [\Delta D_{tail}\le\epsilon_D].
  \]
- **Why principled**: 它把所有可能的混淆项锁死，直接回答 reviewer 的问题：gain 是否来自 baking-error feedback，而不是 atlas size、padding、chart count 或 distortion 改变。
- **Loss / Objective**:
  \[
  \mathcal{L}_{total}=\mathcal{L}_{C1}
  +\lambda_{repair}\mathcal{L}_{C2}
  +\lambda_{mip}\mathcal{L}_{C3}
  +\lambda_{seam}\mathcal{L}_{C4}.
  \]
- **训练时 vs 推理时行为**: 训练阶段所有 ablation 都通过 C5 统一配置；推理阶段 C5 是 deployment gate，若 guard 不满足则回退到 \(U_0\) 或只启用 C3/C4。

## Datasets & Assets

- **主数据集**:
  - ShapeNetCore subset: 12 个常见刚体类别，每类 20-30 个 clean meshes；用于 clean-to-noisy stress、oracle PBR bake、geometry distortion guard。
  - Objaverse subset: 300-500 个公开 object assets，过滤非流形、极端面数、缺失纹理；用于 real generated/noisy asset transfer。
  - Thingi10K subset: 300-500 个 printable/noisy meshes；用于拓扑和 chart fragmentation stress。
- **AI-generated mesh 来源**:
  - TRELLIS-3D public/open-source generated mesh samples 或本地可运行 checkpoint 输出，优先使用 released examples 以控制时间。
  - GET3D-style public generated meshes / open-source checkpoints；作为 category-consistent textured mesh source。
  - SDS-pretrained text-to-3D outputs，例如 DreamFusion/Magic3D-style public samples 或复现实验中的 small prompt set。
  - Objaverse 中标注为生成/重建来源的 noisy assets，作为无需额外生成成本的 transfer set。
- **PBR oracle synthetic data 构建管线**:
  1. 从 ShapeNet/Objaverse/Thingi10K 选 mesh，统一 scale、normal、manifold repair，保留原始 noisy 版本与 simplified 版本。
  2. 用 Blender/Cycles 或 Mitsuba3 给每个 face/material region 分配 procedural SVBRDF，channels 为 albedo、normal、roughness、metallic，粗糙度和法线频率受控。
  3. 生成三类 stress subsets：normal 高频但 albedo 平滑、roughness 高频但 normal 平滑、mixed-frequency。
  4. 用固定 1K/2K atlas、相同 padding、相同 baker，对 PartUV/FlexPara/classical UV 和本方法 bake PBR maps。
  5. 渲染 8 个训练 view、4 个 held-out view、4 个 held-out light conditions，保存 oracle maps、rendered images、per-face visibility 与 residual attribution。

## Baselines（≥4 strong）

| Baseline | arXiv id | 为什么是 fair comparison | 重新训练或 inference-only |
|---|---|---|---|
| PartUV: Part-Based UV Unwrapping of 3D Meshes | 2511.16659v2 | 最直接的 AI/noisy mesh UV baseline，覆盖 part-aware charting、少 chart count、低 seam length；本方法固定其输出再做 local repair | inference-only；作为 initialization 与 baseline |
| FlexPara: Flexible Neural Surface Parameterization | 2504.19210v3 | neural global/multi-chart parameterization baseline，覆盖 flexible chart assignment；用于证明不是 another neural parameterization | 若代码/checkpoint 可用则 inference-only，否则复现实验小子集 |
| Flatten Anything: Unsupervised Neural Surface Parameterization | 2405.14633v2 | ordinary/low-quality 3D data parameterization baseline，适合 ShapeNet/Objaverse/Thingi10K | 需要按公开设置训练或使用作者 checkpoint |
| ParaPoint: Learning Global Free-Boundary Surface Parameterization of 3D Point Clouds | 2403.10349v1 | 点云/非标准输入 parameterization baseline，可检验 noisy generated geometry 下的鲁棒性 | 需要复现或 inference-only，取决于公开实现 |
| OT-UVGS: Revisiting UV Mapping for Gaussian Splatting as a Capacity Allocation Problem | 2604.19127v1 | 只作为 capacity-allocation-inspired control，不称为 direct mesh UV SOTA；将其 rank/visibility allocation 适配到 mesh chart texel budget | 我们实现 mesh-adapted inference-only control |
| TexSpot: 3D Texture Enhancement with Spatially-uniform Point Latent Representation | 2602.12157v2 | texture-quality adjacent baseline，检验绕开 UV 的 texture enhancement 是否比 DCC-ready UV repair 更合适 | inference-only 或 released sample comparison |
| Chord: Chain of Rendering Decomposition for PBR Material Estimation from Generated Texture Images | 2509.09952v1 | PBR predictor confound control；验证本方法不是过拟合某个 material estimator | inference-only predictor/source，非 UV baseline |
| DiffTex: Differentiable Texturing for Architectural Proxy Models | 2509.23336v2 | differentiable texturing adjacent baseline；用于说明本文目标是 generated mesh PBR atlas repair，而非 proxy-model texturing | inference-only/qualitative adjacent comparison |

## Evaluation Metrics（必须包含 PG/CGF 主观+客观 mix）

- **Texture/PBR 重建**:
  - Rendered RGB PSNR / SSIM / LPIPS on held-out views。
  - Albedo MSE / MAE、roughness MSE / MAE、metallic MAE、normal angular error。
  - Relighting error under 4 lighting conditions: studio HDRI、side key light、grazing light、colored environment。
  - PBR channel residual split: oracle-PBR 与 predicted-PBR 两列主表分开报告。
- **几何稳定性**:
  - Normal error、curvature error、area distortion \(Q_{50}/Q_{95}\)、angle distortion \(Q_{50}/Q_{95}\)。
  - UV distortion tail、packing utilization、chart count delta、seam length delta、topology failure rate。
  - Edit budget: edited chart ratio、split/merge/boundary-slide/local-ARAP 次数。
- **主观可视化**:
  - 至少 3 套定性对比：oracle ShapeNet/Objaverse、generated Objaverse/TRELLIS/GET3D、Thingi10K noisy stress。
  - 每套包含 input mesh、baseline atlas、residual atlas、chart edit overlay、relit image、seam visibility map。
  - 至少 1 套 user study optional：pairwise preference on seam visibility / relit artifact，20-30 participants，随机化 30 pairs。
- **Sanity**:
  - Residual atlas heatmap: \(E_c\) 是否集中在被 edit 的 charts。
  - Seam visibility map: normal/roughness/albedo 分离显示。
  - Matched-control table: atlas size、padding、chart count、distortion tail 全部锁定。

## Ablations（≥7，含 ≥2 反向证明 design choice 必要性）

1. **No C1 differentiable baker**: 用 distortion-only objective 替代 PBR residual，预期 relit PSNR 和 seam error 明显退化。
2. **RGB-only baker**: 只优化 RGB texture，不使用 normal/roughness/metallic channel，预期 roughness ringing 和 normal seam map 退化。
3. **No C2 chart repair**: 保留 C3/C4，只重分配 texels，不改变局部 charts，检验 local edit 是否必要。
4. **No C3 mip-aware allocator**: uniform texel density 或 area-proportional density，检验 mip leakage 是否回升。
5. **No C4 cross-channel coupler**: 使用普通 shared seam L1 或 RGB seam loss，检验 channel-specific failure maps 是否恶化。
6. **Reverse proof A, overbuilt global re-unwrap**: 允许全局重新 parameterization；若 distortion/chart count 改善但 matched relit gain 不稳定，证明本文 local repair 更克制且可解释。
7. **Reverse proof B, independent UV per channel**: 给 albedo/normal/roughness 各自 UV；若指标略升但 DCC usability 失败，证明 shared-boundary coupler 的工程必要性。
8. **Matched-utilization control**: 强制 baseline 和 ours packing utilization 相同，排除 texture area 混淆。
9. **Matched-distortion control**: 让 ours 与 baseline 的 distortion \(Q_{95}\) 相同，排除几何 distortion 混淆。
10. **Synthetic-only vs generated-mixed calibration**: 只用 oracle synthetic 校准 vs synthetic+generated predictor split，检验 PBR predictor bias。
11. **No held-out relighting gate**: 只看 training views/lights 的 bake residual，检验 overfit 到 fixed lighting 的风险。

## 6-Week Timeline (2x RTX 4090 data-parallel, method single-card runnable)

| Week | GPU0 | GPU1 | Main Deliverable |
|---|---|---|---|
| W1 | B1 oracle PBR baker、held-out view/light split、metric determinism、on-the-fly rendering cache policy | B2 xatlas/Blender/UVAtlas + PartUV install，40-asset baseline pilot | residual attribution sanity table；确认 `/data` 不缓存 multi-light renders |
| W2 | C1-C4 integration pilot on 60 assets；锁定 top-\(K\)、distortion guard、seam tolerances | FlexPara / Flatten Anything / ParaPoint / mesh-adapted OT-UVGS reproduction 与 failure log | 8 baseline/control protocol table；B1 success/fail gate |
| W3 | B3 main run: ShapeNet oracle + Objaverse oracle/predicted | B4 core ablations A1-A9: C1/C2/C3/C4、held-out gate、reverse proof、per-channel UV | main-result draft table；若 oracle 不 positive，提前 pivot |
| W4 | B3 finish: Thingi10K stress、generated subset、selected 2K reruns；B6 residual-chain figure seed | B5 matched controls + B4 A10-A13: utilization、distortion、padding、chart-count | **first PR-able results**: main table + matched-control table + residual atlas -> chart edit -> relight/seam figure |
| W5 | B6 channel stress maps + B7 generated transfer and robustness | B4 A14-A18: texture size、BRDF、light-type、edit budget、allocator terms；B9 temporal pilot starts | full 18-ablation appendix table；qualitative failure maps |
| W6 | B8 expert-study comparison-board rendering；main figures/tables cleanup；paper writing | B9 cleanup、robustness reruns、appendix packaging、metric consistency checks | submission-ready PG experiment package；若 B8 n<8，改 quantitative-only |

## Risk Register

| Risk | Level | Trigger | Mitigation / Downgrade |
|---|---|---|---|
| PBR predictor error 被误当 atlas error | HIGH | predicted-PBR 上有 gain，但 oracle-PBR 上 relit PSNR < +0.3 dB 或 channel MAE 无改善 | 主表以 oracle-PBR 为核心；predicted-PBR 只作 transfer；增加 Chord-style predictor/source split |
| PartUV/FlexPara baseline 跑不通 | MEDIUM | W2 结束仍不能稳定生成 atlas 或 license/代码阻塞 | 用 xatlas/Blender/UVAtlas + PartUV sample + FlexPara verified subset；失败率进 appendix，不静默丢弃 |
| C2 edit 自由度过大，像新 UV pipeline | MEDIUM | edited chart ratio >20% 或 chart count delta >10% | 收紧 top-\(K\) 到 <=15%；只保留 boundary slide + local ARAP；split/merge 放 ablation |
| C3 gain 来自 packing utilization | MEDIUM | matched-utilization control 后 relit PSNR gain < +0.3 dB | 降低 C3 claim，转为 mip leakage diagnostic；主 claim 改由 C1+C2+C4 支撑 |
| C4 被认为只是 loss-weight trick | MEDIUM | stress subsets 中 channel residual histogram 无明显分离 | 删除 C4 强 claim，只保留 seam diagnostic；channel-aware allocation 放 appendix |
| 4090 时间超预算 | LOW | W4 双卡主实验吞吐 <30 assets/day 或共享 GPU 长时间被占用 | 先排查 GPU 占用；缩小 2K/sweep subset，保留 B1-B6 主证据；B8/B9 可切 appendix |
| Differentiable renderer 数值不稳定 | MEDIUM | normal/roughness gradients 出现 NaN/inf 或 seam artifacts 与梯度无关 | 用 bf16 替代 fp16；normal/roughness gradient clip 与 stop-grad guard；GGX epsilon-pad；必要时 GPU1 做 fp32 sensitive-op cross-check |
| Qualitative 不够好看 | MEDIUM | residual metrics positive 但主图 artifact 不直观 | 固定 stress scenes 生成 residual atlas -> chart edit -> relit/seam chain；附完整 gallery，避免 cherry-pick |
| User study 招募不足 | LOW | W6 前 expert participants <8 | 不强制 user study；B8 改 quantitative-only + full gallery；若 n>=8 但 <10，只放 appendix exploratory |
| Multi-GPU data-parallel synchronization 出 bug | LOW | GPU0/GPU1 同时写 metric/cache 导致重复、覆盖或 inconsistent rows | 不用 DDP；每卡独立 asset shard 与 job queue；metric 写入采用 file lock + atomic rename；共享 cache 只读或按 GPU 分目录 |

## PRCV 备投降级路径

若 PG 6 周内主实验或 PartUV/FlexPara matched controls 不完整，降级为 PRCV2026 framing：题目改为 **Benchmarking and Local Repair of PBR Baking Artifacts in Generated Mesh Atlases**。贡献从 PG 的 principled atlas optimization 降为 CV/PR 友好的 generated asset post-processing benchmark + lightweight local repair；主表只保留 ShapeNet/Objaverse/Thingi10K 三个 subset、PartUV/classical/mesh-adapted capacity 三类 baseline、C1/C2/C4 三个核心 ablation。删除 user study 和部分 2K 结果，把重点放在 oracle vs predicted-PBR confound、residual heatmap 可解释性、以及 generated mesh cleanup pipeline 可复现性。
