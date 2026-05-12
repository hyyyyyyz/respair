# Experiment Plan: I-A3-001-p Dual-Card Revision

**Problem**: AI-generated / noisy mesh atlases often look geometrically acceptable but fail under PBR baking, mip filtering, seam inspection, and held-out relighting.
**Method Thesis**: Differentiable PBR baking residual should drive only local chart repair, mip-aware texel reallocation, and cross-channel seam coupling under a fixed single-UV DCC atlas budget.
**Date**: 2026-04-27
**Hardware Contract**: Core method remains runnable on one RTX 4090 24GB. The second RTX 4090 is used only for data-parallel multi-asset throughput, not DDP, model parallelism, or a larger method.

## Claim Map

| Claim | Why It Matters | Minimum Convincing Evidence | Linked Blocks |
|---|---|---|---|
| C1: PBR baking residual identifies atlas failures missed by distortion-only metrics. | PG/CGF reviewers will not accept a UV paper that only changes geometry metrics while downstream PBR artifacts remain. | Held-out relit PSNR +0.5 dB on oracle assets, LPIPS -0.015, residual top-20% charts cover >=60% visible seam/mip failures. | B1, B3, B4 |
| C2: High-residual local chart repair improves bake quality without becoming a new global UV parameterization method. | This keeps novelty away from PartUV/FlexPara and makes the contribution a constrained atlas repair loop. | Edited chart ratio <=15%, chart-count delta <=8%, distortion Q95 <= baseline +3%, seam residual -12% or better. | B3, B4, B5 |
| C3: Mip-aware texel allocation improves relighting and leakage under the same atlas size. | It rules out the trivial explanation that gains come from more texture capacity. | Mip leakage G_c -15%, relit PSNR +0.3 dB after matched-utilization and matched-padding controls. | B3, B4, B5 |
| C4: Cross-channel seam coupling is necessary for DCC-ready single-UV PBR assets. | Independent per-channel UVs may optimize metrics but violate practical asset workflows. | Normal seam angular error -10%, roughness seam MAE -8%, albedo seam MAE -6%, single-UV readiness preserved. | B4, B6, B8 |
| C5: Gains are not explained by predictor bias, bigger atlas area, chart count, padding, or looser distortion. | This is the main rebuttal shield for PG/CGF. | Oracle-PBR keeps >=70% of predicted-PBR gain; matched-utilization, matched-distortion, matched-padding, and matched-chart-count controls remain positive. | B2, B5, B7 |

## Paper Storyline

- **Main paper must prove**: C1 residual attribution, C2 local repair, C3 fixed-budget mip allocation, C5 matched controls, and a visually interpretable residual atlas -> chart edit -> relight/seam improvement chain.
- **Main paper should include**: B1 sanity, B2 baseline protocol, B3 main result, B4 core ablation summary, B5 matched controls, and B6 qualitative channel stress figures.
- **Appendix can support**: full 18-ablation matrix, B7 generated transfer details, B8 expert preference protocol/results, B9 dynamic temporal stability pilot, failed baseline reproduction notes.
- **Experiments intentionally cut**: any new global UV learner, any method that needs multi-GPU inference, any full new PBR predictor training, any large-scale human subject study beyond expert quality preference.

## Baselines and Controls

| Baseline / Control | arXiv id | Repo / Source | Role in This Paper | Execution Plan |
|---|---|---|---|---|
| PartUV: Part-Based UV Unwrapping of 3D Meshes | 2511.16659v2 | github.com/EricWang12/PartUV | Strong generated/noisy mesh UV baseline and primary initialization. | Inference-only on all main assets when valid. |
| FlexPara: Flexible Neural Surface Parameterization | 2504.19210v3 | github.com/AidenZhao/FlexPara | Neural global/multi-chart parameterization baseline. | Inference-only or verified subset if runtime blocks full sweep. |
| xatlas / Blender Smart UV / UVAtlas classical stack | no arXiv; classical engineering baseline | github.com/jpcy/xatlas; Blender/UVAtlas docs | Robust classical UV baseline and stress fallback. | Full run on all assets. |
| OT-UVGS: Revisiting UV Mapping for Gaussian Splatting as a Capacity Allocation Problem | 2604.19127v1 | repo 未核实 | Capacity-allocation-inspired control, adapted to mesh chart texel allocation. | Our mesh-adapted inference-only control; not claimed as direct mesh UV SOTA. |
| Flatten Anything: Unsupervised Neural Surface Parameterization | 2405.14633v2 | github.com/keeganhk/FlattenAnything | Neural free-boundary parameterization baseline for ordinary/noisy 3D data. | Full or 90-asset verified subset depending on runtime. |
| ParaPoint: Learning Global Free-Boundary Surface Parameterization of 3D Point Clouds | 2403.10349v1 | repo 未核实 / code announced | Point-cloud parameterization control for noisy/generated geometry. | Mesh-to-point sampling control on subset. |
| TexSpot: 3D Texture Enhancement with Spatially-uniform Point Latent Representation | 2602.12157v2 | github.com/texlet-arch/TexSpot | Texture-enhancement adjacent baseline: can texture repair bypass UV repair? | Inference/sample comparison on generated transfer set. |
| Chord: Chain of Rendering Decomposition for PBR Material Estimation from Generated Texture Images | 2509.09952v1 | repo 未核实 | PBR predictor confound control, not a UV baseline. | Predictor/source split for oracle-vs-predicted analysis. |

## Dataset and Protocol

- **Candidate pool**: ShapeNetCore oracle 300, Objaverse oracle/predicted 120, Thingi10K stress 60, generated stress 120 from TRELLIS/GET3D/SDS-style public samples, plus 2-3 animated meshes for B9.
- **Main execution subset**: B3 uses 240 assets: ShapeNet oracle 80, Objaverse oracle/predicted 100, Thingi10K stress 40, generated stress 20. B2/B4/B5 use matched representative subsets to keep the 18 ablations within budget.
- **Atlas settings**: 1K for all full-set comparisons; 2K for representative main assets; 4K only for A14 texture-size sweep. Padding defaults to 8 px unless matched-padding control changes it.
- **Views/lights**: 8 train views, 4 held-out views, and 4 held-out lights: point, area, HDR environment, and grazing/colored stress. BRDF defaults to GGX and is varied only in A15.
- **Storage policy**: `/data` has only 84GB free. Do on-the-fly oracle rendering, persist only source meshes, final UVs, residual atlases, seam maps, metric tables, and selected figures; delete multi-light render buffers after metric extraction.

## Experiment Blocks

### B1: Sanity and Oracle Baker Pilot

- **Claim tested**: C1.
- **Why this block exists**: Before optimizing atlases, verify that differentiable baking, held-out relighting, metric scripts, and residual attribution are numerically trustworthy.
- **Dataset / split / task**: 40 assets: ShapeNetCore 25, Objaverse 10, Thingi10K 5; 1K atlas; oracle PBR maps; 4 train views/lights and 2 held-out views/lights for quick pilot.
- **Compared systems**: xatlas, PartUV if install succeeds, ours evaluator-only without repair.
- **Metrics**: train/held-out PSNR, SSIM, LPIPS, albedo/roughness MAE, normal angular error, residual localization hit rate, rerun metric determinism.
- **Setup details**: PyTorch3D/nvdiffrast or Mitsuba/Blender oracle; GGX default; Adam for texel maps, 300 iterations per asset; seeds=3 on 10 stochastic assets.
- **Success criterion**: oracle train reconstruction PSNR >=28 dB; residual top-20% faces cover >=60% visually obvious seam/mip artifacts; metric rerun difference <=1e-4.
- **Failure interpretation**: If residual attribution is unstable, freeze C2/C3 and treat C1 as a diagnostic evaluator until attribution is fixed.
- **Table / figure target**: Appendix sanity table and one residual attribution figure.
- **GPU h**: 80.
- **Priority**: MUST-RUN.

### B2: Baseline Reproduction and Matched Protocol

- **Claim tested**: C5.
- **Why this block exists**: Establish fair comparison before claiming downstream gains.
- **Dataset / split / task**: 160 assets from the main pool; all baselines at 1K, padding 8 px, same PBR baker and renderer.
- **Compared systems**: PartUV, FlexPara, xatlas/Blender/UVAtlas, mesh-adapted OT-UVGS, Flatten Anything, ParaPoint subset, TexSpot adjacent, Chord predictor control.
- **Metrics**: atlas success rate, chart count, seam length, packing utilization, area/angle distortion Q50/Q95, relit PSNR/SSIM/LPIPS, channel MAE.
- **Setup details**: Run classical baselines on all assets; run neural baselines on full set when feasible or verified 90-asset subset; log failures explicitly.
- **Success criterion**: >=5 baselines/controls produce valid comparable outputs on >=85% of intended assets; all tables include atlas size, padding, chart count, utilization, distortion Q95.
- **Failure interpretation**: If a neural baseline blocks, move it to verified subset and keep PartUV + xatlas + FlexPara subset + OT-UVGS control complete.
- **Table / figure target**: Main Table 1 protocol/baseline table and appendix failure table.
- **GPU h**: 170.
- **Priority**: MUST-RUN.

### B3: Main Anchor Result

- **Claim tested**: C1, C2, C3, C4.
- **Why this block exists**: This is the primary evidence that PBR baking-error feedback improves DCC-ready atlas quality under fixed budget.
- **Dataset / split / task**: 240 assets: ShapeNet oracle 80, Objaverse oracle/predicted 100, Thingi10K stress 40, generated stress 20; 1K full set, 2K on 80 representative assets.
- **Compared systems**: strongest valid baseline per asset, PartUV init + ours, FlexPara init + ours, xatlas init + ours, OT-UVGS-adapted allocation control.
- **Metrics**: held-out relit PSNR/SSIM/LPIPS, albedo/roughness/metallic MAE, normal seam angular error, mip leakage G_c, seam residual, edited chart ratio, chart count delta, distortion Q95.
- **Setup details**: final method C1+C2+C3+C4+C5; top-K <=15% charts; distortion guard Q95 <= baseline +3%; chart-count delta <=8%; seeds=3 on 60 stochastic assets.
- **Success criterion**: vs strongest valid UV baseline, oracle relit PSNR +0.5 dB, predicted/generated +0.3 dB, LPIPS -0.015, seam residual -12%, roughness MAE -7%, normal seam angular error -10%.
- **Failure interpretation**: If oracle positive but predicted negative, main claim becomes oracle-controlled atlas repair with predictor-bias limitation. If both fail, pivot to diagnostic benchmark.
- **Table / figure target**: Main Table 2, Main Figure 1, Main Figure 2.
- **GPU h**: 330.
- **Priority**: MUST-RUN.

### B4: Full Design-Choice Ablation Matrix

- **Claim tested**: C1, C2, C3, C4, and anti-claims in C5.
- **Why this block exists**: The paper needs reverse proof that each design choice prevents a specific failure mode.
- **Dataset / split / task**: 100 representative assets from B3: 35 ShapeNet oracle, 35 Objaverse oracle/predicted, 20 Thingi10K stress, 10 generated stress; 1K atlas.
- **Compared systems**: final method against A1-A18 below.
- **Metrics**: same as B3, plus per-ablation expected deltas and failure maps.
- **Setup details**: GPU1 runs most B4 variants while GPU0 runs B3; seeds=3 for A1-A9, seeds=1 for mechanical sweeps A10-A18 unless variance is high.
- **Success criterion**: At least 14/18 ablations produce the predicted metric direction; all four core components C1-C4 have a visible and quantitative failure mode when removed.
- **Failure interpretation**: Any component whose ablation is flat moves from main claim to appendix implementation detail.
- **Table / figure target**: Main Table 3 compressed ablation table; full appendix table for all 18.
- **GPU h**: 290.
- **Priority**: MUST-RUN.

#### B4 Ablation List: 18 Named Tests

| ID | Ablation / Control | Design Choice Tested | Expected Metric Delta vs Final Method |
|---|---|---|---|
| A1 | No C1 differentiable PBR baker, distortion-only objective | PBR residual is the right signal. | relit PSNR -0.5 to -0.8 dB; LPIPS +0.012; residual localization hit rate -20 pp. |
| A2 | RGB-only baker, no normal/roughness/metallic residual | PBR channels cannot be collapsed into RGB. | roughness seam MAE +8%; normal seam angular error +10%; relit PSNR -0.2 dB. |
| A3 | No C2 chart repair, C3/C4 only | Local edits are needed, not just texel realloc. | seam residual +10% to +14%; edited chart ratio 0 but visible seam failures remain. |
| A4 | No C3 mip-aware allocator, uniform or area-proportional texels | Mip-aware allocation is necessary. | mip leakage G_c +15%; relit PSNR -0.3 dB; grazing-light LPIPS +0.008. |
| A5 | No C4 cross-channel seam coupler, ordinary RGB seam loss | Channel-specific seam constraints matter. | normal seam angular error +9%; roughness seam MAE +8%; user-study seam score worse. |
| A6 | No held-out relighting gate, train views/lights only | Avoiding lighting overfit matters. | held-out relit PSNR -0.35 dB; train/held-out gap +0.5 dB. |
| A7 | Synthetic-only calibration vs synthetic+generated-mixed calibration | Predictor/domain bias handling. | generated transfer seam residual +6%; oracle remains within -0.1 dB. |
| A8 | Reverse proof: overbuilt global re-unwrap | Local repair is more controlled than full reparameterization. | possible PSNR +0.0 to +0.1 dB, but chart-count delta >15% or distortion guard failure. |
| A9 | Per-channel UV vs single-UV shared atlas | DCC-ready single UV is an explicit constraint. | relit PSNR may improve <=+0.1 dB, but single-UV readiness fails; seam consistency not publishable as main method. |
| A10 | Matched-utilization control | C3 gain is not just packing utilization. | after utilization match, relit PSNR still >=+0.3 dB and G_c still <=-10%. |
| A11 | Matched-distortion control | C2 gain is not from looser distortion. | at equal Q95 distortion, seam residual still <=-8% and LPIPS <=-0.010. |
| A12 | Matched-padding control | Seam gain is not from larger padding. | at equal padding, seam residual still <=-8%; mip leakage still <=-8%. |
| A13 | Matched-chart-count control, chart count locked within +/-5% | Repair gain is not chart proliferation. | at chart count +/-5%, seam residual still <=-8%; edited chart ratio <=15%. |
| A14 | Texture size sweep: 1K / 2K / 4K | Gain is not only higher texture resolution. | positive ordering preserved; 1K >=+0.3 dB, 2K >=+0.4 dB, 4K gain narrows but seam residual remains <=-6%. |
| A15 | BRDF model sweep: GGX / Cook-Torrance / Lambert / Disney | C1 is not overfit to one renderer. | GGX/Cook-Torrance/Disney keep >=70% gain; Lambert reduces roughness-specific gain as expected. |
| A16 | Light-type sweep: point / area / HDR / grazing colored | Held-out improvements survive lighting diversity. | every light type positive; grazing light seam residual <=-10%; HDR PSNR >=+0.25 dB. |
| A17 | Edit budget sweep: top-K 5% / 10% / 15% / 25% | The chosen local repair budget is necessary and bounded. | 5% under-repairs (-0.2 dB); 10-15% best; 25% gives <=+0.05 dB extra but violates edit simplicity. |
| A18 | Allocator demand-term ablation: remove visibility, PBR frequency, or mip term | C3 demand model terms are meaningful. | removing mip term G_c +12%; removing PBR frequency roughness MAE +5%; removing visibility relit PSNR -0.2 dB. |

### B5: Matched-Control Confound Tests

- **Claim tested**: C3 and C5.
- **Why this block exists**: This directly answers reviewer concerns about atlas size, utilization, distortion, padding, and chart count.
- **Dataset / split / task**: 80 assets from B3 with balanced oracle/predicted/stress coverage; 1K atlas, 2K on 30 assets.
- **Compared systems**: final method vs strongest baseline under matched utilization, matched distortion Q95, matched padding, matched chart count +/-5%, same atlas size.
- **Metrics**: relit PSNR, seam residual, G_c mip leakage, LPIPS, chart count, utilization, padding, distortion Q95.
- **Setup details**: C5 accept/reject guard is enforced before metrics are counted; unmatched outputs are reported as guard failures.
- **Success criterion**: matched-utilization PSNR gain >=+0.3 dB; matched-distortion seam residual <=-8%; matched-padding seam residual <=-8%; matched-chart-count chart delta <=5% with positive relit/seam gains.
- **Failure interpretation**: If matched controls erase all gains, pivot to diagnostic benchmark. If only C3 disappears, keep C1+C2+C4 as main claim and move C3 to appendix.
- **Table / figure target**: Main Table 4.
- **GPU h**: 125.
- **Priority**: MUST-RUN.

### B6: Channel Stress and Qualitative Failure Maps

- **Claim tested**: C4.
- **Why this block exists**: PG reviewers need to see channel-specific failure separation, not just scalar PSNR.
- **Dataset / split / task**: 60 oracle stress assets: normal-HF 20, roughness-HF 20, mixed-frequency 20; 4 held-out light types.
- **Compared systems**: final method, no C4, RGB-only baker, xatlas, PartUV, FlexPara subset.
- **Metrics**: normal seam angular error, roughness/albedo seam MAE, seam-local vs interior histogram W1 distance, qualitative failure map alignment.
- **Setup details**: Output residual atlas, chart edit overlay, seam visibility map, channel histograms, and 4 qualitative chains.
- **Success criterion**: >=75% of stress assets show correct channel-specific residual localization; seam-local histogram mean improves >=10%.
- **Failure interpretation**: If channel separation is weak, downgrade C4 to seam diagnostic and keep figures as failure analysis.
- **Table / figure target**: Main Figure 3, Main Figure 4, appendix gallery.
- **GPU h**: 85.
- **Priority**: MUST-RUN.

### B7: Generated Transfer and Robustness

- **Claim tested**: C5 external validity.
- **Why this block exists**: The method should not look good only on controlled oracle assets.
- **Dataset / split / task**: 100 generated/noisy assets from TRELLIS/GET3D/SDS-style public samples and generated-like Objaverse subset; 1K atlas.
- **Compared systems**: final method, strongest valid UV baseline, TexSpot adjacent texture enhancement, Chord-based predictor control where available.
- **Metrics**: relit PSNR/SSIM/LPIPS, seam residual, predictor-source split, topology failure rate, storage/runtime per asset.
- **Setup details**: No new large model training; use released samples/checkpoints or public generated assets; log preprocessing and filtering rules.
- **Success criterion**: generated transfer set relit PSNR +0.3 dB or seam residual -10%; failure categories explain topology, PBR predictor, and renderer issues.
- **Failure interpretation**: If transfer is unstable, keep oracle main claim and write generated results as limitation.
- **Table / figure target**: Appendix transfer table and one main qualitative row if clean.
- **GPU h**: 110.
- **Priority**: MUST-RUN for robustness, not required to carry the main claim.

### B8: User Study (Expert Preference)

- **Claim tested**: C2, C4, and appearance-readiness perception.
- **Why this block exists**: Expert preference catches seam visibility and material consistency failures that scalar metrics may underweight.
- **Dataset / split / task**: 30 stress assets selected before viewing outcomes; compare PBR bake/relight images from ours vs each baseline in randomized blind pairs.
- **Participants**: 10-15 experts: graphics researchers, DCC artists, technical artists, or lab colleagues with mesh/texture experience. Remote asynchronous evaluation is acceptable.
- **Compared systems**: ours vs strongest baseline per asset, ours vs xatlas/classical, and ours vs PartUV/FlexPara where available.
- **Evaluation dimensions**: seam visibility, material consistency, and overall asset readiness. Use 2AFC preference plus optional confidence 1-5.
- **Setup details**: Render standardized comparison boards only; no personal sensitive data; collect consent, role category, and opt-out acknowledgement. Treat as IRB-free/non-human-subject graphics quality preference under common lab practice; if local policy requires, file an exempt determination before publication.
- **Success criterion**: >=60% prefer ours over the strongest baseline; >=75% prefer ours over classical xatlas; binomial confidence reported with participant-level bootstrap.
- **Failure interpretation**: If recruitment <8 experts, drop the user study from main/appendix and use quantitative-only reporting plus full gallery.
- **Table / figure target**: Appendix user study table; one sentence in main if positive.
- **GPU h**: 30 for rendering comparison boards; evaluation is offline human time.
- **Priority**: NICE-TO-HAVE but planned.

### B9: 4D / Dynamic Temporal Stability Pilot

- **Claim tested**: Supplementary temporal stability only; not a main contribution.
- **Why this block exists**: Dynamic scenes are PG-relevant, and this pilot shows the atlas repair loop does not obviously drift or flicker across deformations.
- **Dataset / split / task**: 2-3 animated meshes from Mixamo and/or DeformingThings4D public data; 20-40 frames each; fixed identity/material, per-frame deformed geometry.
- **Compared systems**: final method with frame-wise repair, temporal-warm-start repair, xatlas/PartUV baseline where applicable.
- **Metrics**: adjacent-frame atlas IoU, chart correspondence stability, temporal residual variance, relit flicker metric, per-frame guard failure rate.
- **Setup details**: Use same atlas budget and padding; initialize frame t from t-1 when topology allows; render only diagnostic held-out views.
- **Success criterion**: adjacent-frame atlas IoU >=0.95, temporal residual variance <=2x static baseline, no systematic chart drift on the 2-3 pilot assets.
- **Failure interpretation**: If it fails, report as limitation and do not imply 4D contribution.
- **Table / figure target**: Supplementary pilot figure/table.
- **GPU h**: 60.
- **Priority**: NICE-TO-HAVE PG bonus.

## Run Order and Dual-Card Milestones

| Week | GPU0 | GPU1 | Decision Gate | Target Output |
|---|---|---|---|---|
| W1 | B1 oracle baker, metric determinism, on-the-fly rendering cache policy | B2 xatlas/PartUV install and 40-asset baseline pilot | B1 PSNR >=28 dB and residual maps sensible | Sanity table, storage-safe pipeline |
| W2 | Implement/freeze C1-C4 integration on 60 assets | B2 FlexPara/Flatten/ParaPoint/OT-UVGS reproduction and failure logging | >=5 baselines/controls have comparable protocol or verified subset | Baseline protocol table |
| W3 | B3 main run on ShapeNet/Objaverse oracle/predicted | B4 A1-A9 core ablations | B3 early effect positive on oracle or pivot before full burn | Main-result draft table |
| W4 | Finish B3 main tables, start B6 channel stress / residual-chain figures | B5 matched controls plus B4 A10-A13 | First PR-able result: main table + matched controls + residual chain | PR-able package for review |
| W5 | Finish B6 channel stress maps and run B7 generated transfer | B4 A14-A18 sweeps and B9 temporal pilot | C4 and C5 either supported or downgraded | Ablation appendix and qualitative figures |
| W6 | B8 comparison-board rendering, final figures, paper tables | B9 cleanup, robustness reruns, appendix packaging | User study n>=8 or quantitative-only pivot | Submission-ready experiment package |

## Compute and Data Budget

| Block | Budget GPU h | Must / Nice | Notes |
|---|---:|---|---|
| B1 Sanity and Oracle Baker Pilot | 80 | MUST | Includes renderer/metric debug and rerun checks. |
| B2 Baseline Reproduction and Matched Protocol | 170 | MUST | Expanded from 4-5 to 8 baselines/controls. |
| B3 Main Anchor Result | 330 | MUST | Largest block, GPU0 priority. |
| B4 Full 18-Ablation Matrix | 290 | MUST | GPU1 parallel with B3/B5. |
| B5 Matched-Control Confound Tests | 125 | MUST | Utilization, distortion, padding, chart count. |
| B6 Channel Stress and Qualitative Failure Maps | 85 | MUST | Main qualitative chain and channel histograms. |
| B7 Generated Transfer and Robustness | 110 | MUST | External validity and predictor confound. |
| B8 Expert User Study Rendering | 30 | NICE | Rendering only; human evaluation offline. |
| B9 4D Temporal Stability Pilot | 60 | NICE | Supplementary dynamic-scene bonus. |
| **Total** | **1280** |  | Fits dual-card 6-week effective budget. |

- **Budget change**: original single-card plan was 640 GPU h. Dual-card plan spends the extra 640 GPU h on 18 ablations, 8 baselines/controls, B8 expert preference, and B9 temporal pilot.
- **Wall-clock model**: 2x RTX 4090 for multi-asset data parallel evaluation over 6 weeks; effective budget assumes shared-server interruptions and roughly 60-70% usable occupancy.
- **Single-card fallback**: Keep B1-B6 core, shrink B4 to A1-A13, move B8/B9 to appendix cut, and report B7 subset.
- **Persistent storage target**: <=80GB under `/data/dip_1_ws/`; no full multi-light render cache.
- **Biggest bottleneck**: baseline reproducibility and matched-control bookkeeping, not model training.

## Pivot Triggers

- **B1 fails residual attribution**: stop repair expansion and fix baker/metrics; do not publish optimizer claims.
- **B2 baseline reproduction incomplete by end of W2**: keep xatlas + PartUV + FlexPara subset + mesh-adapted OT-UVGS; move failed neural baselines to documented appendix subset.
- **B3 oracle and predicted both negative**: stop PG main path and pivot to PRCV-style diagnostic benchmark.
- **B3 oracle positive but predicted negative**: keep oracle-controlled PG framing and make predictor bias a limitation.
- **B4 ablation flat for a component**: move that component out of main claims.
- **B5 matched controls erase gains**: if all erased, downgrade to diagnostic benchmark; if only C3 erased, keep C1+C2+C4.
- **4090 time over budget**: risk level LOW under dual-card plan; if W4 throughput <30 assets/day, inspect GPU sharing and shrink 2K/sweep subsets before cutting main evidence.
- **User study recruitment <8 experts**: switch to quantitative-only reporting and full gallery; do not force B8.
- **B9 temporal pilot fails**: report as limitation; do not claim dynamic method.
- **Multi-GPU data-parallel synchronization or IO conflict**: switch to per-GPU job queues with disjoint asset shards, file locks for metric writes, and no shared mutable cache.

## Final Checklist

- [ ] Main paper tables covered by B2/B3/B5.
- [ ] Novelty isolated by B4 A1-A9.
- [ ] Confounds locked by B5 and B4 A10-A13.
- [ ] Texture size, BRDF, and light robustness checked by A14-A16.
- [ ] Simplicity defended by A8, A13, and A17.
- [ ] Single-UV DCC readiness defended by A9 and B8.
- [ ] User study has n>=8 or is dropped cleanly.
- [ ] 4D pilot is supplementary only.
- [ ] Method narrative remains single-card runnable.
