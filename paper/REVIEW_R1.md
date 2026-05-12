# PG 2026 Paper Review — Round 1（fresh codex gpt-5.5 xhigh）

**Date**: 2026-04-29
**Reviewer**: senior PG/CGF reviewer, blind to prior history

## Overall Score: 5.8 / 10
（6 = weak accept, 7 = accept, 8.5+ = strong accept）

## Verdict: Ready for submission? Almost

## Summary（≤3 句）

The paper proposes a selective, rollback-gated UV atlas repair method driven by held-out PBR relighting residuals. The narrative is unusually honest about narrow trigger rate and proxy-metric trade-offs, and the accepted PartUV cases show large PSNR gains. However, the current draft is not yet PG/CGF-ready because the evidence accounting is internally inconsistent, the "generated assets" claim is only weakly supported, and key method/ablation details are not reproducible enough from the manuscript.

## Strengths（按重要性 ranked，3-5 条）

1. The core framing is useful: atlas quality is judged by downstream PBR relighting residuals rather than only chart count, padding, utilization, or distortion proxies.
2. The C5 rollback gate is a practical deployment stance and prevents the paper from overclaiming a universal UV optimizer.
3. The accepted spot/PartUV and bunny/PartUV cases are strong within their narrow scope, with large reported PSNR gains (+14.67 dB and +10.23 dB).
4. The matched-control section is candid: the gains survive atlas-size, padding, and chart-count locks but disappear under distortion/utilization locks.
5. The draft openly discloses weak components, failed baseline reproductions, and the non-monotonic noise anomaly instead of hiding them.

## Weaknesses（CRITICAL > MAJOR > MINOR，每条带 specific fix）

### CRITICAL 1: The denominator and rollback accounting are internally inconsistent.

- **What**: The abstract and Sec. 1 claim "Across 18 tested asset/baseline combinations" and a 3/18 trigger rate, while Table 2 has 12 rows and Table 4 has 8 rows, i.e. 20 rows. Sec. 5.2 also says "12 main B3 cases and eight B7 transfer cases" with "3 repairs and 17 candidates", which is 3/20, not 3/18. Table 4 further contradicts the rollback semantics: several rollback rows report negative "Ours PSNR" values (e.g., `proc_noisy_capsule` 38.37 -> 37.68) even though the caption and text say rollback means no final change.
- **Why critical**: This directly affects the central safety claim: "all other cases are rolled back to the baseline atlas" and "no deployed row degrades." A reviewer cannot tell whether Table 4 reports candidate performance, deployed performance, or a mixture.
- **Specific fix**: Choose one accounting convention and apply it everywhere.
  - If all displayed rows count, change all "18" / "3/18" claims to "20" / "3/20", and say "17 rollback rows".
  - If some rows are excluded, explicitly mark them as excluded in Table 2 or Table 4 and make the denominator match the displayed table.
  - Split Table 4 columns into candidate and deployed metrics:

```latex
\begin{tabular}{@{}lrrrrl@{}}
\toprule
Generated mesh & Baseline PSNR & Candidate PSNR & Final PSNR & $\Delta$Final & C5 \\
\midrule
proc\_crumpled\_box & 37.37 & 37.34 & 37.37 & +0.00 & rollback \\
proc\_dented\_torus & 42.41 & 42.40 & 42.41 & +0.00 & rollback \\
proc\_lumpy\_ico & 37.44 & 37.44 & 37.44 & +0.00 & rollback \\
proc\_noisy\_capsule & 38.37 & 37.68 & 38.37 & +0.00 & rollback \\
...
proc\_warped\_cylinder & 30.38 & 41.12 & 41.12 & +10.74 & accept \\
\bottomrule
\end{tabular}
```

### CRITICAL 2: The title and abstract overclaim "Generated Assets" relative to the actual evidence.

- **What**: The main evaluation uses spot, bunny, and one Objaverse asset; transfer uses eight procedural generated/noisy meshes. Sec. 4.4 and Sec. 6 admit that real Trellis-3D, GET3D, SDS-style, or comparable generated assets are not evaluated.
- **Why critical**: The paper title, abstract, and introduction frame the contribution around generated assets, but the current evidence mostly supports "selective PartUV repair on a few controlled assets." PG/CGF reviewers will likely treat the generated-asset claim as unsupported.
- **Specific fix**: Either add a real generated-asset suite or narrow the claim.
  - Experimental fix: add at least 10-20 real generated meshes from 2-3 generation sources, report topology/material failures, and include both PartUV and production baselines under the same C5 protocol.
  - Wording fix if experiments cannot be added before submission: retitle to something like `PBR Baking-Error Atlases for Selective UV Repair`, and change the abstract first sentence to "Generated, procedural, and noisy meshes..." only if the tables explicitly separate real generated from procedural cases.

### CRITICAL 3: The practical value is unclear because xatlas is stronger than repaired PartUV in the main table.

- **What**: Table 2 reports spot/xatlas at 49.77 dB and bunny/xatlas at 43.25 dB, both higher than repaired PartUV at 44.99 dB and 38.53 dB. The paper says it is not trying to beat xatlas, but it does not clearly explain why a pipeline should repair PartUV instead of choosing xatlas.
- **Why critical**: Without a production constraint that makes the initial atlas fixed or preferable, the method looks like a repair for a weaker baseline rather than a generally useful asset-pipeline method.
- **Specific fix**: Add an explicit "fixed upstream atlas" motivation and measure what xatlas gives up. For example, add a small table with chart semantic alignment, part consistency, editability, or DCC constraint metrics showing why PartUV is worth preserving even when xatlas has higher PSNR. If that evidence is unavailable, rewrite the claim as "given a fixed upstream atlas, we can safely repair some PartUV failures" rather than suggesting an atlas-selection advantage.

### MAJOR 1: Method details are too underspecified for reproduction.

- **What**: Sec. 3 defines C1-C5 at a high level, but does not specify key parameters or implementation choices: texture size `S`, padding `p`, view/light counts, train/held-out split, BRDF details, renderer, thresholds `delta_p`, `delta_s`, `eps_D`, `Delta_C`, `K`, all lambdas, beam-search stopping, ARAP iterations, repacking method, and how `I^*` is obtained for procedural/generated transfer.
- **Why critical**: The method's novelty depends on the gate and local action space; without these details, reviewers cannot distinguish a reproducible algorithm from a tuned experimental harness.
- **Specific fix**: Add a compact "Implementation details" subsection at the end of Sec. 3:

```latex
\subsection{Implementation details}
\label{sec:implementation}
We use atlas resolution $S=\ldots$, padding $p=\ldots$, held-out
views/lights $\ldots$, and thresholds
$(\delta_p,\delta_s,\epsilon_D,\Delta_C)=(\ldots)$.
C2 uses at most $K=\ldots$ charts, a beam width of 4, split/merge
actions defined by ..., ARAP with ... iterations, and repacking via ....
All experiments use the same parameters unless explicitly stated.
```

### MAJOR 2: The ablation table does not identify the ablated components.

- **What**: Table 3 lists A1-A18 with "Variant set" mostly equal to `base`, but the paper text refers to RGB-only baker, no C2 repair, uniform allocation, global re-unwrap, A5/A9, A18, etc. The mapping is not in the table or nearby text.
- **Why critical**: The strongest mechanistic claim ("C1 is the strongest validated component; C2 and C3 matter; C4 is weak") relies on a table that is not interpretable without external knowledge.
- **Specific fix**: Replace `ID`/`Variant set` with named variants. Example rows:

```latex
A2 & RGB-only baker (remove PBR-channel awareness) & -12.55 & -12.51 & negative & yes \\
A3 & no local chart repair (disable C2 actions) & -1.62 & -0.22 & negative & yes \\
A4 & uniform texel allocation (disable residual demand) & -1.11 & -0.30 & negative & yes \\
A5 & no cross-channel seam diagnostic & +0.00 & +0.00 & negative & no \\
```

Move incomplete A10/A11 rows to an appendix or mark exactly why they are incomplete.

### MAJOR 3: The paper lists many metrics but reports almost only PSNR.

- **What**: Sec. 4.1 says metrics include SSIM, LPIPS, PBR channel residuals, seam error, mip leakage, distortion tail, utilization, chart count, edited chart count, and C5 verdict. The main tables mostly report PSNR and C5; some figure overlays include SSIM/seam text only for accepted cases.
- **Why critical**: The paper's premise is multi-signal PBR fidelity and seam/mip diagnostics. A single PSNR table cannot support claims about cross-channel seams, mip leakage, or proxy-metric trade-offs.
- **Specific fix**: Add a compact appendix table for accepted and representative rollback cases with columns: `PSNR`, `SSIM`, `LPIPS`, `SeamErr`, `MipLeak`, `Dtail`, `Util`, `Chart #`, `Edited #`. In the main text, explicitly state which claims are supported only by PSNR and which are supported by the additional metrics.

### MAJOR 4: The C5 gate can mask failure modes unless candidate results are reported.

- **What**: Table 2 reports deployed performance for rollbacks, while Table 4 appears to report candidate performance for rollbacks. In both cases, the reader needs candidate metrics to judge whether the search is useful, unstable, or frequently harmful.
- **Why critical**: "No deployed row degrades" is nearly tautological if rollback always returns the baseline. The scientific question is whether residual attribution proposes useful candidates and whether C5 reliably separates good from bad candidates.
- **Specific fix**: Add columns for `Candidate PSNR`, `Candidate SeamErr`, `Final PSNR`, and `Gate reason`. Report how many candidates improved PSNR but failed seam/distortion, how many degraded PSNR, and whether any accepted candidate worsened a non-PSNR metric.

### MAJOR 5: Visual evidence is too small to support the qualitative claims.

- **What**: Fig. 1, Fig. 7, and Fig. 8 use tiny atlas/residual panels. Fig. 7's per-panel labels are effectively unreadable in the compiled PDF. Fig. 4 is dense and relies on small labels/hatching. The paper claims visible PBR baking artifacts, but the figures mainly show UV charts and line overlays rather than relit image crops where artifacts are visible.
- **Why critical**: For PG/CGF, the qualitative visual story matters. The paper needs to show the actual visible failure and the repaired relit result, not only atlas diagrams and bar charts.
- **Specific fix**: Replace one table/plot footprint with a figure containing rendered image crops: baseline relit, repaired relit, absolute residual heatmap, and seam close-up for spot and bunny. Move the rollback gallery to appendix or enlarge it to a full-width figure with fewer panels.

### MAJOR 6: Related work and references are too thin for a PG/CGF paper.

- **What**: The bibliography has only 9 entries, mostly recent arXiv entries. The paper discusses classical UV unwrapping, xatlas, Blender Smart UV, PBR/GGX rendering, texture atlas packing, seams, mip leakage, differentiable rendering, SSIM, and LPIPS without citing the foundational sources or software references.
- **Why critical**: Even if the method is narrow, PG/CGF reviewers expect the work to be positioned against standard geometry processing, texture mapping, rendering, and evaluation literature.
- **Specific fix**: Add citations for classical UV parameterization/unwrapping, texture atlas packing, xatlas/software baselines, Blender Smart UV or Blender documentation, GGX/Disney/PBR reflectance, differentiable rendering/rasterization, seam/mip texture filtering artifacts, and PSNR/SSIM/LPIPS metric definitions.

### MINOR 1: Related-work headings render as `2.0.0.1`, `2.0.0.2`, etc.

- **What**: In the PDF, the `\paragraph` headings in Sec. 2 are numbered as `2.0.0.1`, which looks like a formatting bug.
- **Specific fix**: Use unnumbered paragraph heads:

```latex
\paragraph*{Classical and production UV unwrapping.}
\paragraph*{Neural and data-driven UV parameterization.}
\paragraph*{Capacity allocation and texture-aware UV ideas.}
\paragraph*{Relightable appearance and Gaussian/surfel representations.}
```

### MINOR 2: Several equations overflow the column.

- **What**: The LaTeX log reports overfull boxes around Eq. 3, Eq. 8, Eq. 13, Eq. 15, and Eq. 16; Eq. 15 is visibly crowded in the PDF.
- **Specific fix**: Break these equations with `aligned` or `split`. For Eq. 15:

```latex
\begin{equation}
\begin{aligned}
S' &= S,\qquad p'=p,\qquad ||\C'|-|\C_0||\le\Delta_C,\\
Q_{95}(D'_{area/angle}) &\le Q_{95}(D^0_{area/angle})+\eps_D .
\end{aligned}
\label{eq:hard_guard}
\end{equation}
```

### MINOR 3: One grammar issue is visible in the compiled PDF.

- **What**: Sec. 4.3 reads "Table 3 and Fig. 4 isolates the component evidence."
- **Specific fix**:

```latex
\Cref{tab:ablation,fig:ablation} isolate the component evidence.
```

### MINOR 4: Table 7 is too small and wastes a mostly blank appendix page.

- **What**: The baseline reproduction table is very wide with small text, while page 9 has substantial empty space below Fig. 8.
- **Specific fix**: Move Table 7 to a two-column-width appendix page with wrapped notes, or split it into `used baselines` and `attempted baselines`. If page budget matters, move long reproduction notes to supplementary material and keep only status plus one-sentence reason in the paper.

## Visual Review（PDF 视觉评估）

- Figure quality: Fig. 2 is clean. Fig. 3 and Fig. 6 are readable. Fig. 4 is marginal because the A1-A18 labels and hatching are dense. Fig. 1, Fig. 7, and Fig. 8 have panels whose text and fine lines are too small in the compiled PDF.
- Figure-caption alignment: Captions mostly match the figures, but Fig. 1/Fig. 8 claim a PBR residual chain without showing relit image crops, so the visible artifact claim is weaker than the caption suggests. Fig. 7's caption is accurate but the gallery panels are too small to inspect.
- Layout: No catastrophic orphaning, but Sec. 4.1 begins near the bottom of page 4 and the appendix leaves a large blank region on page 9. Several equations trigger overfull hboxes.
- Table formatting: Table 2 is readable. Table 3 is semantically unclear because ablation names are missing. Table 4's rollback rows conflict with the caption. Table 7 is too small for comfortable review.
- Visual consistency: Plots use a mostly consistent Matplotlib style, but the red overlays/purple residual lines in atlas figures will not distinguish well in grayscale. Add hatching, line styles, or explicit grayscale-safe encodings.

## Missing Citations（如有）

- Classical UV parameterization/unwrapping and distortion metrics.
- Texture atlas packing, seam handling, padding, and mip/filtering artifacts.
- xatlas and Blender Smart UV/software baseline references.
- GGX/Disney/PBR reflectance model references.
- Differentiable rendering/rasterization references for the C1 baker.
- PSNR, SSIM, and LPIPS metric references if they remain central evaluation metrics.
- Prior texture-aware or appearance-driven UV/atlas optimization work beyond the recent arXiv papers already cited.

## Component Score Breakdown

- Logical flow: 7.0/10
- Claim-evidence alignment: 5.0/10
- Method clarity: 5.0/10
- Experimental rigor: 5.2/10
- Honest disclosure quality: 8.0/10
- Writing clarity: 7.0/10
- Visual presentation: 5.0/10
- Page-budget feasibility: 6.0/10
