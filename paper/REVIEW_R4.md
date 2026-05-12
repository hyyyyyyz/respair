# Overall Score 5.6/10

# Verdict

Almost

# Summary

The paper presents a practical, well-scoped idea: use held-out PBR relighting residuals to decide whether a fixed upstream UV atlas should receive local repair, and roll back when the evidence is insufficient. The writing is unusually honest about selectivity and confounds, but the current empirical support is too narrow for a strong PG/CGF special-issue acceptance. The main technical risk is that the same held-out relighting signal appears to drive both repair selection and final gate validation, so the reported "no deployed degradation" evidence needs an independent test split.

# Strengths

1. The problem is real and well motivated: UV proxy metrics can miss downstream PBR baking and relighting artifacts.
2. The deployment framing is mature: the method does not claim to beat xatlas globally and explicitly rolls back weak candidates.
3. The paper separates candidate and deployed results, which makes the selective behavior more transparent than a standard average-gain table.
4. The matched-control section is valuable because it admits that the gain depends on distortion/utilization freedom.
5. The baseline reproduction appendix is honest about failed or partial baselines instead of silently omitting them.

# Weaknesses

## CRITICAL

1. Validation leakage: the repair loop and C5 gate appear to use the same held-out view/light set.

Specific issue: Appendix A says the C2 render term uses the same held-out view/light set as C5. That means the candidate search is tuned on the data later used to accept the deployed atlas. The paper's central safety claim, "no deployed row degrades," is therefore not fully supported as an independent deployment statement.

Specific fix: split the data into proposal/training, gate/validation, and final test views/lights. Use proposal data for residual attribution and local search, validation data only for C5 thresholding, and report all headline PSNR/SSIM/LPIPS/seam metrics on a final untouched test split. Add confidence intervals over several random view/light splits.

2. Evidence is too narrow for the generated/noisy-asset claim.

Specific issue: the main accepted cases are spot/PartUV and bunny/PartUV; the headline transfer adds one procedural warped-cylinder case; the extended procedural sweep adds one new acceptance; the real-mesh evidence is a single `ts_animal` case. Meanwhile real Trellis-3D, GET3D, and SDS-style generated outputs are explicitly deferred. For PG/CGF, the paper needs more than a few controlled/procedural positive cases to support a deployment method for generated/noisy meshes.

Specific fix: add a real-mesh/generated-mesh benchmark with at least 20-30 assets across Trellis-like, SDS/threestudio, Objaverse, and production-style scans. Report trigger rate, accepted gain, rollback causes, runtime, failure categories, and representative visual crops for accepted and rejected cases.

3. The paper does not yet prove why one should use the repaired PartUV atlas instead of a stronger atlas.

Specific issue: xatlas has higher relit PSNR than repaired PartUV on spot and bunny. The paper argues that PartUV semantics matter, but the chart-part purity metric uses the PartUV leaf-chart partition as the reference, making PartUV and the repaired output perfect by construction. This is not enough to establish a real production trade-off.

Specific fix: add a non-tautological semantic/editability evaluation: human-labeled part boundaries, downstream part editing/accessory transfer, rig-aware editing, or artist-facing chart operations. Compare against xatlas, PartUV reruns/parameter sweeps, and any part-preserving repair baseline under the same semantic metric.

## MAJOR

1. C5 thresholds are central but underjustified.

Specific fix: add a threshold sensitivity study for `delta_p`, `delta_s`, `epsilon_D`, and utilization tolerance. Show how trigger rate, final test PSNR, seam error, and rollback false positives/false negatives change.

2. Component evidence is uneven.

Specific issue: C1 channel awareness is strongly supported, but C2 and C3 effects are small on bunny, C4 has zero isolated signal, and the explicit mip term is weak. A1 also reports no loss when residual localization is disabled, which cuts against the residual-atlas contribution.

Specific fix: reduce the claimed component list to the components that are empirically validated, or add targeted stress tests for residual localization, C4 seam coupling, and mip leakage. Figure/table captions should not present diagnostic components as validated contributions.

3. Ablation reporting has confusing signs and mismatches.

Specific issue: A6 says removing C5 is expected negative but improves bunny by +1.56 dB; Figure 4 includes A10/A11/A13/n/a labels not present in Table 3; several rows are marked as matches even when the interpretation is not obvious.

Specific fix: rebuild the ablation table/figure from one source of truth. Add a short "how to read delta" note and mark mixed-direction cases explicitly.

4. The matched-control conclusion is important but incomplete.

Specific issue: the gains vanish when distortion or utilization is locked. That may be an acceptable trade-off, but the paper does not quantify whether the resulting distortion/utilization changes are visually or operationally tolerable beyond C5 thresholds.

Specific fix: report absolute distortion tails, area/angle histograms, packing utilization, overlap/inversion checks, and texture-density maps before/after for accepted cases.

5. The target signal assumption is too strong for production use.

Specific issue: the method needs either ground-truth oracle PBR channels, procedural oracle channels, validation renders under known lighting, or a high-trust PBR estimator. This is exactly the difficult part in real generated-asset pipelines.

Specific fix: add an experiment where the target signal comes from a realistic imperfect estimator or captured validation images, then measure whether the residual atlas still identifies UV/bake artifacts rather than material-estimation error.

6. Visual evidence is weaker than the numerical story.

Specific fix: for every accepted headline case, show ground truth/reference render, initial render, repaired render, residual heatmap, and zoomed seam/mip artifacts under the same held-out lighting. For rollback cases, show a candidate that improves PSNR but fails the audit, explaining visually why C5 rejects it.

7. Baseline scope is transparent but still thin.

Specific issue: FlexPara, Flatten Anything, ParaPoint, OT-UVGS, and visibility-parameterization controls are not real main baselines. That is honestly disclosed, but it weakens claims relative to recent UV/learned parameterization work.

Specific fix: either reproduce at least one stronger learned/data-driven baseline or soften the related-work positioning so the paper is clearly a deployment-gated PartUV/xatlas repair study, not a broad comparison against modern learned UV methods.

## MINOR

1. The abstract says the supplemental sweep "adds a fourth acceptance," while Table 5 contains two acceptances and overlaps warped cylinder. This is explainable but easy to misread.

Specific fix: state "one additional non-overlapping acceptance" in the abstract.

2. The real-mesh result is placed in the main experiments but is only a single case.

Specific fix: keep it as a clearly labeled pilot/existence result, or move it to appendix unless the real sweep is expanded.

3. The notation around `D_tail`, `Q95`, utilization guards, and seam thresholds should be unified.

Specific fix: define all C5 audit quantities once and use the same symbols in equations, tables, and captions.

4. The implementation cites Mitsuba 3.5 but the bibliography entry is Mitsuba 2.

Specific fix: cite the correct Mitsuba version or state that Mitsuba 2 is the conceptual renderer reference while the implementation used Mitsuba 3.5.

5. Some table placement is dense in the 12-page PDF.

Specific fix: move extended procedural transfer, extended robustness, and baseline reproduction details to supplementary material if PG page limits allow a cleaner main story.

# Visual Review

The overall PDF is readable and fits the 12-page format, but it is dense. Figure 2 is clean as a pipeline schematic, and Figures 3, 5, and 6 communicate the main numerical story efficiently. Figure 4 is visually useful but currently inconsistent with Table 3 because it shows extra ablation IDs/n/a entries not in the table.

The main qualitative figures are not yet persuasive enough for a graphics venue. Figure 1 and Figure 8 are atlas-centric and text-heavy; they show PSNR, edited charts, and texel allocation, but not enough rendered before/after evidence for the actual PBR artifacts. The rollback gallery is also too small and metadata-heavy to function as visual proof. For PG/CGF, the paper needs larger relit render crops, residual heatmaps, and seam/mip zoom-ins that make the artifact improvement obvious without relying on PSNR.

# Component Score Breakdown

| Component | Score | Rationale |
|---|---:|---|
| Problem relevance | 8.0/10 | PBR bake quality under fixed UV constraints is a meaningful graphics pipeline problem. |
| Novelty | 6.5/10 | Residual-gated local repair is a useful framing, but many ingredients are recombinations of differentiable rendering, texture allocation, and UV repair. |
| Technical soundness | 5.0/10 | The formulation is plausible, but validation leakage and weak component isolation limit confidence. |
| Experimental strength | 4.5/10 | Positive gains are large but occur in very few cases; real generated-asset evidence is insufficient. |
| Baselines | 4.5/10 | xatlas/Blender/PartUV are useful, but several recent learned baselines are missing or only discussed as failed reproductions. |
| Visual evidence | 5.0/10 | Figures are organized, but the actual rendering artifacts and improvements are not shown strongly enough. |
| Writing and honesty | 7.5/10 | The paper is clear and unusually transparent about selectivity and limitations. |
| Reproducibility | 5.5/10 | Hyperparameters are listed, but implementation details, splits, thresholds, and failed baseline setup need stronger reproducible protocol. |

# Missing Citations

1. Seam placement and distortion-aware parameterization: add modern seam/layout and locally injective parameterization work, e.g. ABF++ and Seamster-style seam optimization, plus SLIM/bounded-distortion parameterization if distortion guards are central.
2. Differentiable material/PBR reconstruction: add nvdiffrec-style differentiable mesh/material optimization and related inverse-rendering material papers, since the method depends on differentiable PBR baking and relighting.
3. Graphics perceptual error metrics: consider FLIP or other graphics-oriented image-difference metrics in addition to PSNR/SSIM/LPIPS.
4. Neural texture / atlas-aware appearance: cite neural texture mapping and atlas-domain appearance optimization work if claiming novelty around texture-space residuals.
5. Recent generated 3D asset systems: DreamGaussian, Magic3D, Fantasia3D, InstantMesh/LRM-style systems, TripoSR, MeshAnything, CraftsMan/MeshLRM-type methods are relevant context if the paper continues to motivate generated/noisy assets.
6. Production texture baking and DCC workflows: cite texture baking and mip/seam handling references from production rendering or game-asset pipelines, not only UV parameterization papers.
7. Mitsuba versioning: cite Mitsuba 3 if that is the implementation dependency, or clarify why Mitsuba 2 is the bibliography reference.

