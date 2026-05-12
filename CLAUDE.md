# CLAUDE.md — PG 2026 PBR-Atlas 项目

## 1. 项目一句话

为 **Pacific Graphics 2026 (CCF-B, CGF special issue, 截稿 2026-06-09)** 做 **Differentiable PBR Baking-Error Atlas for Generated Assets** (`I-A3-001-p`)：

- 不重新发明 UV unwrap；在 PartUV/FlexPara/classical atlas 初始化上，由"实际烘焙后的 PBR 重光照残差"驱动**局部** chart repair + mip-aware texel reallocation
- Novelty 来自把 atlas 评价标准从"几何 distortion"换成"下游 PBR bake/relight 残差"
- 5 个 named components（C1 differentiable PBR baker / C2 residual-attributed local chart repair / C3 mip-aware texel reallocation / C4 cross-channel seam coupling / C5 synthetic oracle benchmark）

**Contribution 顺序锁死**：principled atlas evaluation → local repair operators → matched-control validation。任何改写保持这个顺序。

**备投**：PRCV 2026 (CCF-C, LNCS, 2026-05-30，已延期)。降级路径写在 `refine-logs/FINAL_PROPOSAL.md` 末尾。

---

## 2. 当前阶段

**已完成**（idea-discovery 工作流）：
- Phase 1-5 全跑通：research-lit (377 papers) → idea-creator (15 ideas) → novelty-check ×2 (round-2 救援) → research-review → research-refine + experiment-plan
- Codex GPT-5.5 xhigh 最终评分：**Novelty 8.2 / Review 8.1**（双 ≥8 acceptance gate 全过）
- 候选漏斗：15 → 11 survivors → 5 ranked → 4 KEEP (round-2) → 1 ACCEPT (主投)
- 全部 codex trace 在 `.aris/traces/` 归档

**当前**（Phase 0 实施前的同步与环境）：
- 远程服务器 `server2` 已就绪（4090 + 共享 /data + clash 代理）
- 待办：在 `/data/dip_1_ws/` 建立工作区、验证 conda env、跑 W1 sanity pilot (B1)、wikification 完整对齐

---

## 3. 关键文档索引（不重复正文，只列位置）

| 文件 | 内容 |
|---|---|
| `idea-stage/FINAL_IDEA_REPORT.md` | idea-discovery 全程总报告（213 行） |
| `refine-logs/FINAL_PROPOSAL.md` | 方法 spec 到 equation 级（251 行，含 PRCV 降级路径） |
| `refine-logs/EXPERIMENT_PLAN.md` | 6 周 roadmap + 7 blocks (B1-B7) + claims-to-results matrix |
| `refine-logs/EXPERIMENT_TRACKER.md` | 执行追踪表（更新这个，不是 PLAN） |
| `idea-stage/pivoted/I-A3-001-p.md` | 主投 pivoted method skeleton |
| `idea-stage/review/I-A3-001-p.md` | review verdict 8.1/ACCEPT/TIER-1 |
| `idea-stage/NOVELTY_SUMMARY_R2.md` | round-2 novelty 总览（8.2 winner） |
| `idea-stage/REVIEW_SUMMARY.md` | review 总览 + MVI |
| `idea-stage/LIT_LANDSCAPE.md` | 5 PG 子方向 + 红海化警告 |
| `research-wiki/` | 24 papers / 28 ideas / 76 edges 知识图谱 |
| `egPublStyle-PG2026/` | PG 2026 LaTeX 模板（Eurographics / CGF） |
| `LaTeX2e_Proceedings_Templates/` | PRCV 2026 备投模板（Springer LNCS） |

---

## 4. 远程云容器（主力计算节点）

### 4.1 SSH 别名

配在本地 `~/.ssh/config` 里，**已就绪**：

```bash
ssh server2                         # 交互式登录
ssh server2 "<cmd>"                 # 一次性命令
scp <local> server2:<remote>        # 文件上传
rsync -avz <local>/ server2:<rem>/  # 目录同步
```

### 4.2 硬件与系统现状（2026-04-27 侦察）

| 项 | 值 |
|---|---|
| Hostname | `jittor-ubuntu22-04-desktop-v3-3-54gb-100m` |
| OS | Ubuntu 22.04，kernel 5.15.0-128 |
| GPU | **RTX 4090 × 2**, 24564 MiB × 2 (48GB 合计)。**默认 data-parallel 双卡运行**（GPU0 + GPU1 各跑不同 asset），用户已确认；method 本身仍单卡可跑，第二卡纯作"实验吞吐倍增器" |
| 磁盘 `/` | 39 GB 总，4.9 GB 剩余（系统盘，禁放大文件） |
| 磁盘 `/data` | **1003 GB（`/dev/vdb`，ext4，LABEL=data），剩 840 GB 可用**（用户已升级，2026-04-27） ← 共享盘 |
| Python | `~/miniconda3/`（已装），多个 env 在 `/data/conda_envs/` |
| 代理 | mihomo systemd active，`proxy_on / proxy_off` alias 已配 |
| HF | `HF_ENDPOINT=https://hf-mirror.com`，`HF_HUB_ENABLE_HF_TRANSFER=1` |
| HF 缓存 | `HF_HOME=/data/hf_cache`，`TORCH_HOME=/data/torch_hub` |

### 4.3 共享服务器约束（重要）

- **本服务器是共享的**。`/data` 上已有：`LIBERO/`、`openvla-oft/`（aris_1 项目）、`dassd*/`（dassd 项目）、`dip_3_ws/`（dip_3 项目）。**dip_1 必须放在 `/data/dip_1_ws/` 命名空间下**，不要污染同盘其他项目目录。
- **/data 840 GB free**（升级后），`EXPERIMENT_PLAN.md` 名义 1.8-2.5 TB 仍超量但已可控：B1 仍验证 on-the-fly oracle rendering，B3+ 主集允许部分缓存 frequently-accessed PBR oracle 通道（≤200 GB），residual atlas 和 seam map 长期保留。详见 §4.6。
- **GPU 共享（当前阶段）**：用户已配 2× 4090，但其他项目正占用约 12-32 GB（动态变化）；W1-W3 阶段我只用空闲容量（GPU1 当前 21 GB free 优先）。**其他项目结束后可独占 48GB** —— 届时再启动 B3 主实验完整双卡运行。跑前必须 `nvidia-smi` 确认。
- **2× 4090 默认开**：双卡 data-parallel 跑 multi-asset，吞吐 ×2，6 周 effective 1400 GPU h。GPU0 跑 main / GPU1 跑 ablation / baseline reproduction。**论文 narrative 严格写**：core method runs on a single 24GB GPU; second 4090 used only for parallel data evaluation。即不让 reviewer 误以为方法依赖多卡。
- **不需要 DDP / model parallel**：仅做 per-GPU per-asset 数据并行；工程复杂度增量近零。

### 4.4 网络代理（已就绪，无需重配）

| 通道 | 状态 | 用途 |
|---|---|---|
| **mihomo (Clash.Meta)** systemd | ✅ active (port 7897/5335/9097) | Google / GitHub / HF / OpenAI 代理 |
| `~/.profile` 中 `proxy_on` / `HF_ENDPOINT` | ✅ login shell 自动加载 | 无须手动 export |
| `proxy_off` alias | ✅ 临时关代理（本地 PyPI 镜像直连时用） |
| **hf-mirror.com** (HF 镜像) | ✅ HF_ENDPOINT 默认走，比代理快 |
| **mirrors.aliyun.com** (PyPI) | ✅ 国内直连，pip install 时建议先 `proxy_off` |

切换/重启 mihomo / 换订阅的具体步骤照搬自 `aris_1_ws/CLAUDE.md` §4.5.x（同一服务器同一套配置）。

### 4.5 项目目录约定（dip_1 namespace）

```
/home/ubuntu/                       # 系统盘 /，4.9GB 剩
└── dip_1_ws/                       # 项目代码（rsync from local，<200MB）
    ├── .gitignore                  # 排除 runs/ ckpts/ datasets/
    ├── pbr_atlas/                  # 主代码（C1-C5 module）
    ├── eval/                       # 评测 harness
    └── configs/

/data/dip_1_ws/                     # 数据盘命名空间
├── ckpts/                          # 任何 ≥100MB checkpoint
├── datasets/                       # ShapeNet/Objaverse/Thingi10K 子集
│   ├── shapenet_oracle_300/        # 300 assets oracle PBR
│   ├── objaverse_oracle_120/
│   ├── thingi10k_stress_60/
│   └── generated_stress_120/       # PartUV/FlexPara 跑出来的
├── atlases/                        # 原始 PartUV/FlexPara/classical UV
├── runs/                           # 实验输出
│   ├── B1_sanity/
│   ├── B2_baseline/
│   ├── B3_main/
│   ├── B4_ablation/
│   ├── B5_matched_control/
│   ├── B6_qualitative/
│   └── B7_transfer/
├── residual_atlases/               # 主要可视化产物（small）
└── tmp/                            # on-the-fly oracle render（用完删）
```

### 4.6 存储紧约束策略（84 GB 撑住 1.8 TB 名义需求）

由于盘紧，**B1 阶段就必须验证以下三条**：

1. **不缓存 multi-light renderings**：每个 asset on-the-fly 渲染 4-8 个 held-out 光照、即用即丢；只持久化 per-face residual `e_f` 和 per-chart residual `E_c`（每 asset KB 量级）
2. **oracle PBR 也按需渲染**：用 Mitsuba 3 / nvdiffrast 在线 bake，不预算 700 GB cached PBR 通道
3. **assets 子集化**：主集 ShapeNet 300 + Objaverse 120 + Thingi10K 60 + generated stress 120 ≈ 600 assets；按 100GB cap 估算每 asset ≤ 170MB（含原 mesh + 一套 PartUV atlas + residual maps），符合预算
4. **运行中 nvidia-smi 监控 + df -h 监控**：每 block 跑完立刻 `du -sh /data/dip_1_ws/runs/<B>` 检查；超 15GB 单 block 就触发清理
5. **应急扩盘**：若 W2 验证不可行，需向用户申请扩 `/data` 至 ≥500GB 或外挂对象存储

### 4.7 首次环境初始化（按顺序）

**Step A — 创建项目目录骨架**（远程一次性）：
```bash
ssh server2 << 'EOF'
mkdir -p /data/dip_1_ws/{ckpts,datasets/{shapenet_oracle_300,objaverse_oracle_120,thingi10k_stress_60,generated_stress_120},atlases,runs/{B1_sanity,B2_baseline,B3_main,B4_ablation,B5_matched_control,B6_qualitative,B7_transfer},residual_atlases,tmp}
mkdir -p ~/dip_1_ws
df -hT /data
EOF
```

**Step B — Conda env**（基于 server2 已有 miniconda3）：
```bash
ssh server2 << 'EOF'
source $HOME/miniconda3/bin/activate
conda config --add envs_dirs /data/conda_envs
conda create -n dip1_pbr python=3.10 -y
conda activate dip1_pbr
EOF
```

**Step C — 系统依赖**（图形学栈）：
```bash
ssh server2 "sudo apt update && sudo apt install -y libgl1 libosmesa6-dev libglew-dev libegl1 libgbm1 xvfb tmux htop blender meshlab"
```

**Step D — Python 栈**（PyTorch 2.7 + nvdiffrast/Mitsuba/trimesh）：
```bash
ssh server2 << 'EOF'
source $HOME/miniconda3/bin/activate
conda activate dip1_pbr
proxy_off  # 走 aliyun 镜像更快
pip install torch==2.7.1 torchvision==0.22.1 --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
proxy_on
pip install nvdiffrast trimesh pyglet meshio xatlas open3d
pip install mitsuba==3.5.0 drjit
pip install transformers accelerate diffusers safetensors
pip install matplotlib scikit-image lpips imageio[ffmpeg]
python -c "import torch, nvdiffrast.torch as dr; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_count(), torch.cuda.get_device_name(0))"
# 期望：2.7.1+cu128 True 1 NVIDIA GeForce RTX 4090（双卡时 device_count=2）
EOF
```

**Step E — 数据准备（流式下载，不一次性）**：
- ShapeNet 通过 HF mirror 下载子集（每类 ≤30 个）
- Objaverse 通过官方 sample script，限 120 个
- Thingi10K 公开下载脚本拉 stress 60 个

---

## 5. 常用命令速查

### 5.1 启动远程会话

```bash
ssh server2
source $HOME/miniconda3/bin/activate
conda activate dip1_pbr
cd ~/dip_1_ws
```

### 5.2 长任务（tmux 防断连）

```bash
ssh server2
tmux new -s b3_main           # 主实验
# Ctrl+b d 脱离
tmux attach -t b3_main         # 重连
```

### 5.3 同步代码到远程

```bash
cd /Users/jacksonhuang/project/dip_1_ws
rsync -avz --delete \
  --exclude=.git --exclude=__pycache__ \
  --exclude=runs --exclude=ckpts --exclude=datasets \
  --exclude=.aris --exclude=research-wiki --exclude=refine-logs \
  --exclude=idea-stage --exclude=idea-stage-prcv-archived-2026-04-27 \
  --exclude=egPublStyle-PG2026 --exclude=LaTeX2e_Proceedings_Templates \
  --exclude='*.pt' --exclude='*.safetensors' \
  --exclude='*.pdf' --exclude='*.ipynb_checkpoints' \
  ./ server2:~/dip_1_ws/
```

### 5.4 拉取远程实验结果

```bash
# 只拉小型 artifact（residual atlas / metric tables / final figures）
rsync -avz --include='*.json' --include='*.png' --include='*.csv' --include='*/' --exclude='*' \
  server2:/data/dip_1_ws/runs/ ./runs/
```

### 5.5 磁盘 / GPU 监控

```bash
ssh server2 "df -hT /data; du -sh /data/dip_1_ws/* 2>/dev/null | sort -h; echo '---'; nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv"
```

---

## 6. Git 工作流（待建仓）

**当前状态**：项目根目录 `/Users/jacksonhuang/project/dip_1_ws/` **尚未** init git 仓库。下面是建仓后的标准流程（建议在 W1 sanity 跑通后再建仓）：

- **建议远程仓库**：`github.com/<your-org>/dip-1-pbr-atlas`（私有；包含 `pbr_atlas/`、`eval/`、`configs/`，不含 datasets/runs/ckpts）
- **本地工作树**：`/Users/jacksonhuang/project/dip_1_ws/`
- **远端工作树**：`/home/ubuntu/dip_1_ws/`（pull-only；commit 走本地）
- **工作分支**：`main` 即可（单人项目，<6 周）
- **`.gitignore` 必排**：`runs/`、`ckpts/`、`datasets/`、`.aris/`、`research-wiki/`、`refine-logs/`、`idea-stage*`、`*.pt`、`*.safetensors`、`*.pdf`、`__pycache__`

### Commit message 格式

```
<type>(<scope>): <subject>

Refs: PG2026 PBR-Atlas R<XX>.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
type ∈ {fix, feat, docs, refactor, test, chore}

---

## 7. ARIS skill 调用规则

| 阶段 | 已用 | 不再跑 | 接下来要跑 |
|---|---|---|---|
| 选题 | idea-discovery (W1 PG 全流程已完成) | idea-creator / novelty-check / research-review（已 commit I-A3-001-p） | — |
| 实施 | — | — | `/experiment-bridge`（把 EXPERIMENT_PLAN 翻译成代码骨架） |
| 跑实验 | — | — | `/run-experiment`、`/monitor-experiment`、`/training-check` |
| 分析 | — | — | `/analyze-results`、`/result-to-claim`、`/experiment-audit` |
| 投稿 | — | — | `/paper-plan` → `/paper-figure` → `/paper-write` → `/paper-compile` → `/auto-paper-improvement-loop` |
| 必过 audit | — | — | `/experiment-audit`、`/paper-claim-audit`、`/citation-audit`（投稿前必须 3 绿） |

**评审通道纪律**：所有外部模型评审都用 `codex exec --model gpt-5.5 -c model_reasoning_effort="xhigh"`，不用 `mcp__codex__codex`（用户已明确）。模型固定 **gpt-5.5**，不要回到 5.4。

---

## 8. Gate 检查点（来自 EXPERIMENT_PLAN）

实验路线 7 个 block：B1 Sanity/Oracle Baker → B2 Baseline Reproduction → B3 Main Anchor → B4 Novelty Isolation Ablations → B5 Matched-Control Confounds → B6 Channel Stress Qualitative → B7 Transfer / User Study。

**5 个核心 claims（必须用 B-block 证据兑现）**：
- C1 PBR baking residual 能捕捉 distortion-only 漏掉的 atlas 失败 → B1/B3
- C2 Local chart repair 不退化为新 UV pipeline → B3/B4，edited chart ratio ≤15%
- C3 Mip-aware 分配优于 uniform/distortion-only → B3/B4/B5，mip leakage -15%
- C4 Cross-channel seam coupling 必要 → B4/B6，seam histogram mean -10%
- C5 增益不来自 predictor 偏差 / 大 atlas / 松约束 → B2/B5/B7，oracle 保持 ≥70% predicted gain

**关键风险触发**（来自 FINAL_PROPOSAL Risk Register）：
- W2 PartUV/FlexPara baseline 跑不通 → 用 classical xatlas/Blender/UVAtlas + 已生成 PartUV sample
- W4 主实验吞吐 <30 assets/day（双卡基线）→ 先排查 GPU 共享冲突；若依然紧再缩小到 150 主集 + 60 stress（风险等级降为 LOW）
- C2 edited chart ratio >20% 或 chart count delta >10% → 收紧 top-K，把 split/merge 放 ablation
- C3 matched-utilization control 后 relit gain <+0.3 dB → 降级 C3 为 mip leakage diagnostic
- Differentiable renderer 数值不稳定（NaN/inf）→ 不降级为 finite-difference fallback（用户已确认显存无忧，不接受这种"垃圾替代方案"）；改用：(a) bf16 取代 fp16 提升数值稳定、(b) 对 normal/roughness gradient 加 clip 与 stop-grad guard、(c) GGX BRDF 边缘条件 ε-pad、(d) 必要时第二张 4090 跑 fp32 sensitive ops 双精度 cross-check

**总预算**：1280 GPU h（**双卡 4090 × 6 周** effective 利用率 70%），单卡 fallback 仍是 640 GPU h。利用双卡的实际计划：(a) ablation 矩阵从 11 扩到 18，(b) baseline 从 4-5 扩到 7-8，(c) +User study (n=10-15 expert)，(d) +4D/dynamic temporal stability pilot。存储采用 §4.6 紧约束策略。

---

## 9. 下一步（按顺序）

1. **建立服务器工作区**：跑 §4.7 Step A-E（mkdir + conda env + apt deps + PyTorch + nvdiffrast/Mitsuba/trimesh/xatlas）
2. **rsync 项目骨架到 `~/dip_1_ws/`**（暂为空，待 `/experiment-bridge` 生成代码）
3. **`/experiment-bridge "I-A3-001-p"`**：把 `refine-logs/EXPERIMENT_PLAN.md` 中 B1 翻译成可执行 sanity 代码（C1 differentiable PBR baker 最小复现）
4. **跑 B1 Sanity 验证**：on-the-fly oracle render 是否真的能撑住 84GB 盘约束（§4.6）；若不能，立刻申请扩盘
5. **G-W2 通过**后启动 B2 baseline reproduction（PartUV / FlexPara / classical xatlas）
6. **W3 锁数据集** + 建 `pbr_atlas/` 主代码 → **W4 跑 B3 main**
7. **2026-06-08** 主实验 + ablation + paper draft 完成 → **2026-06-09 PG 投稿**

若 W4 主实验滞后 → 按 FINAL_PROPOSAL §"PRCV 备投降级路径"重 framing 投 PRCV2026 (2026-05-30)。

---

## 10. 应急信息

- **Codex trace 索引**：`.aris/traces/<skill>/2026-04-27_run01_pg/`
  - research-lit: PG landscape 27 buckets / 377 papers
  - idea-creator: 15 ideas with self-≥8 gate
  - novelty-check round1 + round2（pivot 救援）
  - research-review: 4 candidates, 1 ACCEPT (8.1)
  - research-refine: FINAL_PROPOSAL.md 251 行
- **Wiki 工具**：
  - `python3 /Users/jacksonhuang/.claude/skills/research-wiki/tools/research_wiki.py stats research-wiki/`
  - `... rebuild_query_pack research-wiki/` （≥7 天后或大量变更后跑）
  - `... add_edge research-wiki/ --from idea:I-A3-001-p --to paper:<slug> --type tested_by --evidence "B3 main run"`（实验跑出来后用）
- **Meta-optimize 状态**：`.aris/meta/events.jsonl` 持续累积，≥5 个新 skill_invoke 后 SessionEnd 会提示 `/meta-optimize`
- **PRCV 旧产物**：`idea-stage-prcv-archived-2026-04-27/` + `refine-logs-prcv-archived/` 完整保留作历史；wiki 中 12 PRCV ideas + 12 PRCV papers 留作 backup pool（与当前 PG 项目正交，但可能在 PRCV 降级路径中复用某些方法骨架）
- **同服务器其他项目**：`/data/dip_3_ws/`（dip_3）、`/data/openvla-oft/`（aris_1）、`/data/dassd*/`（dassd）—— 如发现盘满，先和这些项目协调，不要直接删
