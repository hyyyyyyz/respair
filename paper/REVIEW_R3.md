# Fresh PG2026 / CGF Review R3

Overall Score: 5.4/10

Verdict: Almost

## Summary

The paper proposes a selective, rollback-gated UV atlas repair method driven by held-out PBR relighting residuals rather than classical UV proxy metrics. The core idea is useful and the manuscript is unusually honest about selectivity, but the present evidence package has serious internal consistency, evaluation-design, and target-domain gaps. I would not accept this version as-is for PG/CGF, but I can see a weak-accept path if the critical issues below are fixed cleanly.

## Strengths

1. **Clear practical problem framing.** The fixed-atlas, DCC-ready setting is believable, and the distinction between "replace the atlas" and "locally repair a chosen upstream atlas" is well motivated.
2. **Conservative deployment semantics.** Separating candidate and deployed results is a good design choice; the rollback gate prevents the paper from overstating unconditional optimizer behavior.
3. **Strong improvements in accepted cases.** The reported spot/PartUV and bunny/PartUV gains are large (+14.67 dB and +10.23 dB), and the warped-cylinder transfer case suggests the mechanism is not purely single-asset.
4. **Matched-control analysis is valuable.** Showing that gains vanish under distortion/utilization locks is exactly the kind of trade-off disclosure CGF reviewers appreciate.
5. **Honest negative evidence.** The manuscript explicitly demotes C4 and the explicit mip term after weak ablations, which improves trust relative to a more promotional version.

## Weaknesses

### CRITICAL

1. **The result accounting is internally inconsistent.**
   The abstract, introduction, and Sec. 5.2 claim 3/20 accepted rows: spot/PartUV, bunny/PartUV, and proc_warped_cylinder. But the extended transfer table reports 2/10 accepts, including proc_crumpled_box and proc_warped_cylinder, with different baseline/candidate values from the earlier transfer table. The limitations also say robustness is only shown for spot, while Table 7 includes bunny robustness. This creates a trust problem, not just a wording issue.
   **Fix:** Define one canonical evaluation set and one supplemental set. If Table 5 is supplemental, remove it from headline counts and explain overlap. If it extends the count, update abstract/introduction/conclusion and reconcile duplicated procedural rows. Fix the outdated limitations sentence about bunny robustness.

2. **The evaluation appears to use the same held-out validation signal for residual attribution, candidate search, and C5 acceptance.**
   C1 computes held-out residuals, C2 scores local actions using the same held-out render loss, and C5 accepts on held-out relighting. This is not an independent test; it can overfit to the selected validation views/lights, especially with large PSNR jumps and local edit search.
   **Fix:** Split views/lights/material perturbations into train-for-residual, validation-for-C5, and final blind test sets. Report candidate and deployed PSNR on the blind test only, with confidence intervals over multiple random splits.

3. **The paper is framed around generated/noisy assets but does not evaluate real generated assets.**
   The manuscript repeatedly invokes Trellis-3D, GET3D, and SDS/DreamFusion-style outputs, but the actual transfer evaluation is procedural noisy meshes. The paper admits this, but the title/abstract/introduction still lean on the generated-asset motivation.
   **Fix:** Either add real generated-mesh cases with realistic UV/material defects, or narrow the claim to controlled/procedural/noisy meshes throughout. For PG/CGF, at least a small real generated-asset benchmark would materially change the score.

4. **The accepted cases are all failures of PartUV, while stronger baselines often remain better.**
   xatlas has higher final PSNR than the repaired PartUV outputs on spot and bunny, and the paper justifies not switching by chart-part purity. However, the purity proxy is defined relative to the PartUV hierarchy, so it partly bakes in the desired conclusion.
   **Fix:** Add an editability/semantic-preservation evaluation independent of PartUV itself: human-labeled parts, downstream editing tasks, rig/accessory transfer, or a metric not defined using the PartUV leaf partition.

5. **The availability of the deployment target signal is underspecified.**
   The method depends on held-out relighting residuals against target images or known PBR channels. In real production, the ground truth for "correct" relit appearance may not exist, especially when material prediction is noisy.
   **Fix:** State exactly where \(I^*\) comes from in oracle, procedural, and practical deployment settings. Add an experiment where material error and atlas error are disentangled, or explicitly scope the method to cases with a trusted procedural/oracle PBR source.

### MAJOR

1. **C5 definition and narrative disagree about utilization.**
   The text says candidates can fail seam, distortion, utilization, or chart-count guards, and the audit tables include \(\Delta\)Util. But Eq. (16) accepts only PSNR, seam, and distortion-tail conditions, and accepted PartUV rows reduce utilization substantially.
   **Fix:** Put every hard gate in the equation, or call utilization an audit-only diagnostic. Then recompute accept/rollback labels consistently.

2. **Ablations support fewer components than the architecture suggests.**
   The paper presents C1-C5, but C4 has zero isolated signal, A1 contradicts expectation, A18 is nearly neutral, and C2/C3 effects are modest on bunny. The validated contribution is closer to "channel-aware residual + small local repair/allocation + rollback gate" than the full named architecture.
   **Fix:** Collapse or demote weak components in the main method diagram and contribution list. Keep C4/mip terms in diagnostics or appendix unless new stress tests prove them.

3. **Robustness evidence is thin and anomalies are not diagnosed.**
   The noise anomaly is honestly retained, but not resolved. Bunny \(\sigma=0.01\) reports higher PSNR than reference while still rolling back, without the seam/distortion audit needed to interpret the rejection.
   **Fix:** Add audit columns for all robustness rollbacks and run several random seeds/noise realizations, not single points.

4. **Metrics are too PSNR-centric for a visual PBR paper.**
   SSIM/LPIPS are mentioned but not systematically tabled. Visual artifacts are described as hot spots, mip leakage, and seams, yet figures rarely show rendered before/after relighting crops.
   **Fix:** Add relit image crops under held-out lights, seam/mip close-ups, and SSIM/LPIPS/seam-error tables for accepted and rejected cases.

5. **Baseline scope remains weak for a PG/CGF special issue.**
   FlexPara, Flatten Anything, ParaPoint, OT-UVGS, and visibility-param controls are not reproduced. The failure table is honest, but it also means the paper's competitive evidence is narrow.
   **Fix:** Add at least one more modern neural/data-driven UV baseline or a stronger texture-aware parameterization control, even if limited to spot/bunny.

6. **Some equations read like design intent rather than implemented evidence.**
   The total objective includes \(\lambda_{seam}\mathcal{L}_{C4}\) although C4 is diagnostic-only, and C2 local operators are only specified at pseudocode level.
   **Fix:** Separate implemented optimization terms from reported diagnostics, and provide enough local-operator detail to reproduce split/merge/slide/ARAP decisions.

### MINOR

1. **Wrong citation in extended transfer text.** The real generated-asset sentence cites PartUV for Trellis-3D in the PDF.  
   **Fix:** cite the Trellis entry, not PartUV.

2. **The "oracle = infinity PSNR" rows are visually distracting and analytically weak.**  
   **Fix:** report finite numerical precision or omit oracle from PSNR ranking and keep it as a sanity check.

3. **Table/figure numbering and density hurt readability.** The 12-page PDF is within budget, but pages 6-9 are very crowded, with small plots and tightly packed tables.
   **Fix:** move secondary transfer/robustness tables to appendix or reduce repeated table panels.

4. **The title may overpromise generality.**  
   **Fix:** consider "Selective PBR Baking-Error Atlases for Local UV Repair" or similar.

## Visual Review

The visual package is functional but not yet publication-strong. Fig. 2 is clean and communicates the pipeline, but it is too schematic to establish technical novelty. Fig. 3 and Fig. 6 are readable and support the selective-gate story. Fig. 4 is overloaded: many rows are tiny, several labels are hard to parse, and the message is clearer in the table than the plot. The residual-chain figures are visually striking but not sufficiently diagnostic: they mostly show atlas-domain overlays and seam-line clutter, not the actual before/after rendered PBR artifacts a graphics reviewer wants to inspect. The rollback gallery is too small on the page and the final residual/seam panels look like dense line noise. Add rendered crops, material-channel crops, and zoomed seam/mip examples.

## Component Score Breakdown

- Logical flow: 7.0/10
- Claim-evidence alignment: 4.8/10
- Method clarity: 5.6/10
- Experimental rigor: 4.4/10
- Honest disclosure: 8.0/10
- Writing: 7.2/10
- Visual quality: 5.1/10
- Page budget/use: 6.0/10

## Missing Citations

- Purnomo, Cohen, and Kumar, "Seamless Texture Atlases" - important for seam-aware atlas discussion.
- Williams, "Pyramidal Parametrics" / classic mipmapping reference, and possibly Heckbert texture filtering survey - needed for mip leakage and atlas bleeding context.
- Burley and Lacewell, "Ptex: Per-Face Texture Mapping for Production Rendering" - relevant because the paper commits to single UV atlases and excludes no-UV/per-face alternatives.
- Mikkelsen / MikkTSpace tangent-space normal mapping reference - relevant to cross-channel seams and tangent-space normal baking.
- PyTorch3D or another modern differentiable rendering framework reference, if used as a comparison point for nvdiffrast-style pipelines.
- TexRecon or related multi-view texture reconstruction / texture baking references, to better ground the baking-error residual setup.
- A correct Trellis-3D citation in the extended transfer paragraph; the current PDF appears to cite PartUV for Trellis-like outputs.
