# PG 2026 Paper Review — Round 2（fresh codex gpt-5.5 xhigh）

**Date**: 2026-04-29
**Reviewer**: senior PG/CGF reviewer, blind to all prior review history

## Overall Score: 6.8 / 10
（6 = weak accept, 7 = accept, 8.5+ = strong accept）

## Verdict: Ready for submission? No

## Summary（≤3 句）

The paper presents a carefully bounded residual-driven UV atlas repair method that uses held-out PBR relighting error, local chart edits, fixed-budget texel reallocation, and a rollback gate. The strongest current result is selective but real: three accepted cases out of 20 tested rows gain roughly 10--15 dB while rollback prevents deployed degradation. The draft is honest and much clearer than a typical overclaiming systems paper, but it is not yet submission-ready because the evidence base, citation foundation, and auditability of the deployment gate are still below PG/CGF standards.

## Strengths（按重要性，3-5 条）

1. **Honest selective framing.** The paper does not claim universal UV dominance; it explicitly says the method triggers only 3/20 times, rolls back otherwise, and loses gain under strict distortion/utilization locks.
2. **Clear deployment semantics.** C5 makes the deployed output unambiguous: either accept a residual-backed local repair or return the upstream atlas. This is a useful engineering stance for asset pipelines.
3. **Strong accepted-case gains.** Spot/PartUV, bunny/PartUV, and warped cylinder show large relit PSNR improvements (+14.67, +10.23, +10.74 dB) under the reported setup.
4. **Matched-control analysis improves credibility.** Showing that gains survive atlas-size, padding, and chart-count locks but vanish under distortion/utilization locks is exactly the right kind of confound disclosure.
5. **Writing is unusually candid.** The limitations, failed baseline reproduction table, zero-signal C4 disclosure, and noise anomaly are visible rather than hidden.

## Weaknesses（CRITICAL > MAJOR > MINOR，每条 specific fix）

### CRITICAL

1. **The generated/noisy-asset motivation is under-supported by real generated assets.** The introduction motivates procedural, generated, and noisy assets, but the actual transfer evidence is eight procedural meshes and no Trellis-3D, GET3D, SDS, or comparable generated outputs.
   **Specific fix:** Add a small real-generated evaluation, even if only 6--10 assets, with the same C5 reporting; or tighten the abstract/introduction/title language so the evidence claim is explicitly "controlled and procedural noisy meshes" rather than generated-asset deployment.

2. **The practical value relative to xatlas is not fully established.** On spot and bunny, repaired PartUV still remains below the xatlas baseline in PSNR, and the reason not to use xatlas is semantic/part structure preservation, which is asserted but not measured.
   **Specific fix:** Add a quantitative or visual semantic-preservation/editability comparison: chart-part purity, part boundary preservation, accessory/rig-aware edit example, or a table showing what xatlas loses that PartUV+repair preserves. Without this, reviewers can read the method as improving a weak baseline while not beating a standard production atlas.

3. **The bibliography is far below PG/CGF expectations.** `references.bib` has only nine entries, almost all recent arXiv papers. The paper uses UV parameterization, ARAP, PBR/GGX, differentiable rendering, SSIM/LPIPS, nvdiffrast/Mitsuba, xatlas/Blender, and classical distortion metrics without adequate foundational citation support.
   **Specific fix:** Add a real related-work backbone before submission: classical UV parameterization/unwrapping, stretch/distortion metrics, ARAP/local parameterization, atlas packing/texture atlases, differentiable rendering/rasterization, PBR microfacet rendering, SSIM/LPIPS, and the actual software baselines used.

### MAJOR

1. **C5 is not auditable from the main tables.** The accept rule depends on PSNR, seam error, and distortion tail, but the main/transfer tables mostly expose PSNR and verdict. The reader cannot verify why a candidate accepted or rolled back.
   **Specific fix:** For every accepted row and representative rollback rows, report candidate PSNR, final PSNR, seam error change, distortion Q95 change, utilization change, chart-count change, SSIM, and LPIPS. A compact "C5 audit table" would fix this.

2. **Ablations contain incomplete and ambiguous rows.** Table 3 includes A10/A11 incomplete rows, zero-signal A1/A5/A9, and A6 where removing the gate improves bunny by +1.56 despite being marked as matching the expected negative direction. This weakens component attribution.
   **Specific fix:** Either complete/remove the incomplete rows, split "diagnostic stress tests" from true ablations, and explain A6/A13 direction mismatches in the caption/text; or move them to appendix and keep the main ablation table to verified component claims.

3. **C4 is still over-present in the method relative to evidence.** The paper says C4 is diagnostic, but the architecture and contribution framing still include it as a named component while A5/A9 show zero isolated signal.
   **Specific fix:** Downgrade C4 visually and textually: call it "reported seam diagnostic" rather than a validated repair component, remove any implication that it drives gains, and put seam-specific stress tests in future work unless new evidence is added.

4. **Robustness evidence is too narrow.** Robustness sweeps are only on spot/PartUV, while bunny and warped cylinder are also accepted cases. The non-monotonic sigma=0.01 rollback anomaly is reported honestly but remains unexplained.
   **Specific fix:** Add at least a minimal robustness table for bunny/PartUV and warped cylinder, or explicitly state that robustness is demonstrated only for spot. Add candidate metrics for sigma=0.01 to diagnose whether the failure is PartUV chart instability, C2 edit selection, or C5 seam/distortion rejection.

5. **Method implementation details are still not reproducible enough.** The equations are clear, but the exact C2 action parameterization, local ARAP constraints, beam scoring granularity, residual-to-chart attribution implementation, and renderer/material assumptions are not fully specified.
   **Specific fix:** Add an implementation appendix with pseudocode-level details for split/merge/boundary-slide actions, candidate enumeration counts, rejection criteria, and exact metrics used by C5.

### MINOR

1. **Visuals are dense and often too small.** Fig. 1 and Fig. 8 are visually important but dark and hard to inspect; Fig. 7 is too small for a rollback gallery; Fig. 4 and Table 3 have high information density.
   **Specific fix:** Enlarge the residual-chain crops, simplify Fig. 4, move some ablation rows to appendix, and make Fig. 7 either a two-row focused figure or appendix-only.

2. **Some source-facing labels leak into presentation.** "B3", "B4", "B5", "B6", "B7", and `B4_TABLE` read like internal experiment bookkeeping.
   **Specific fix:** Rename these to reader-facing labels in captions and text, or define them once if they must remain.

3. **A few grammar/copy issues remain.** Example: "Table 3 and Fig. 4 isolates" should be "isolate"; some captions are long enough to compete with the main text.
   **Specific fix:** Do one final copy pass after figure/table reshuffling.

## Visual Review（PDF）

The 9-page PDF compiles and is generally readable, but the visual presentation is only borderline for a graphics venue. Page 2's hero residual-chain figure communicates the story, but the atlas/residual panels are too dark and the small text overlays are barely legible. Page 6 is especially crowded: the full-width ablation table, ablation plot, and robustness plot compete for attention, and the robustness figure appears before the robustness subsection text. Page 7 stacks transfer, robustness, matched controls, and the matched-control figure before the Section 5 discussion, which makes the narrative order feel float-driven rather than reviewer-friendly. Page 8's rollback gallery is too small to verify the visual claim. Page 9's appendix table is readable but cramped; the bunny residual-chain qualitative is useful and should be made larger if it remains part of the visual evidence.

## Missing Citations（如有）

The missing-citation issue is substantial. Add citations for:

- Classical surface parameterization and UV unwrapping: LSCM, ABF/ABF++, ARAP parameterization, stretch/distortion metrics, charting/segmentation, and packing.
- Production/software baselines actually used: xatlas, Blender Smart UV, and any oracle/matched-atlas construction precedent.
- Texture atlas and signal-aware parameterization literature, including work that allocates texel density according to texture or view-dependent signal.
- PBR rendering and BRDF foundations: GGX/Trowbridge-Reitz microfacet model, normal/roughness/metallic workflow references if claimed as standard.
- Differentiable rendering/rasterization and renderers used: nvdiffrast, Mitsuba 3, and any differentiable baking/raster contribution method.
- Metrics: SSIM and LPIPS.
- Generated-asset context if the motivation remains: Trellis-3D, GET3D, SDS-style text-to-3D or reconstruction pipelines, with citations to the actual systems whose outputs are discussed.

## Component Score Breakdown

- Logical flow: 7.8/10
- Claim-evidence alignment: 6.6/10
- Method clarity: 7.2/10
- Experimental rigor: 6.4/10
- Honest disclosure quality: 8.8/10
- Writing clarity: 7.8/10
- Visual presentation: 6.5/10
- Page-budget feasibility: 6.9/10
