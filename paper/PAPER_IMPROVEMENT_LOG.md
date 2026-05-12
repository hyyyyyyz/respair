# Paper Improvement Log

## Round 1 fixes

Date: 2026-04-29

### Implemented patches

- Retitled the paper to "PBR Baking-Error Atlases for Selective UV Atlas Repair."
- Narrowed the abstract and introduction from a broad generated-asset claim to procedural/noisy meshes and selective upstream-atlas repair.
- Unified the deployment denominator to 20 displayed cases: 12 B3 main rows plus 8 B7 transfer rows, with 3 accepts (3/20, 15%) and 17 rollback rows.
- Added fixed-upstream-atlas motivation explaining why PartUV may be preserved even when xatlas reports stronger PSNR.
- Added a Sec. 3 implementation-details subsection with atlas resolution, padding, view/light splits, renderer/precision choices, C2/C3 settings, C5 thresholds, and hardware/software stack.
- Added an experiment-setup paragraph stating that upstream atlases are frozen and xatlas is treated as a strong global re-charting baseline, not as a semantic replacement for PartUV.
- Reworked Table 2 to identify the disabled component or matched-control stress for each ablation row.
- Reworked Table 4 to separate candidate PSNR from deployed final PSNR, so rollback rows deploy the baseline and have +0.00 final delta.
- Clarified limitations and conclusion language: real Trellis-3D/GET3D/SDS evaluation is deferred to future work.
- Fixed related-work paragraph headings to avoid numbered paragraph labels, and split the C5 hard-guard equation to reduce overfull layout pressure.

### Verification

- Recompiled with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
- Output PDF: `paper/main_round1.pdf`.
- `pdfinfo`: 9 pages, 607624 bytes.
- `main.log`: no undefined references or undefined citations.
- PDF text check confirms the new title, `Across 20 tested asset/baseline combinations`, `3/20`, and Table 4 `Candidate PSNR` / `Final PSNR` columns.
- Source check finds no remaining `3/18`, `18 tested`, `Ours PSNR`, or old generated-assets title strings.
- Citation-key check: all cited keys are present in `references.bib`, and all bibliography entries are cited.

### Remaining known issues

- Some pre-existing equation overfull hboxes remain in Sec. 3, but they do not block compilation.
- Broader reviewer requests for additional metrics, visual crop evidence, and expanded real generated-asset experiments remain future work because they require new artifacts beyond the R1 brief.

## Round 2 cheap fixes

Date: 2026-04-29

### Implemented patches

- Expanded the bibliography from 9 entries to 41 entries, covering classical UV parameterization, stretch/distortion metrics, atlas packing/compression, differentiable rendering, PBR microfacet shading, image/perceptual metrics, production UV tools, and generated-asset context.
- Added C5 audit panels to the Main Anchor Evaluation and Transfer and Robustness Study transfer tables: candidate PSNR, final PSNR, seam change, distortion Q95 change, utilization change, chart-count change, and C5 verdict are now visible.
- Demoted C4 to a reported cross-channel seam diagnostic rather than a validated repair component; updated the method title/caption, regenerated the architecture figure with a dashed diagnostic-only C4 box, and marked A5/A9 as diagnostic in the ablation table.
- Removed incomplete A10/A11 and redundant/mismatched A13 rows from the main ablation table.
- Added implementation details for C2 actions, beam scoring, residual attribution through the nvdiffrast face-id buffer, renderer assumptions, and logged C5 thresholds.
- Replaced reader-visible B3/B4/B5/B6/B7/B4_TABLE labels with reader-facing names, and moved qualitative residual-chain figure references to `figures/qualitative_residual_chain/`.
- Added explicit future-work statements for real Trellis-3D/GET3D/SDS generated meshes, chart-part purity/semantic preservation, and bunny/warped-cylinder robustness sweeps.

### Verification

- Recompiled with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
- Output PDF: `paper/main_round2.pdf`.
- `pdfinfo`: 11 pages, 638117 bytes.
- `main.log`: no undefined references or undefined citations.
- Source check finds no remaining reader-visible `B3`, `B4`, `B5`, `B6`, `B7`, or `B4_TABLE` labels in `paper/main.tex`, `paper/sections/`, or `paper/tables/`.
- Source check finds no `[VERIFY]`, `??`, or `[?]` markers in paper sources.

## Rounds 3-9 review-driven fixes

Date: 2026-04-30 to 2026-05-03

### Trajectory

- R3: 5.4/10 → R4: 5.6/10 → R5: 7.2/10 → R6: 7.0/10 → R7: 7.2/10 → R8: 7.3/10 → R9: 7.5/10.

### Critical fixes (R3/R4 critical → resolved by R5)

- **Validation leakage (R3 critical 1, R4 critical 1)**: introduced explicit proposal/gate/test 3-split protocol. Headline PSNR is reported on the test split only; candidate search uses proposal; C5 uses gate. Implemented in `scripts/run_B3.py --split-seed`. Multi-seed across 3 random split seeds for 4 cases reported in `tab:a1_split` and §5.2.
- **Real-mesh evidence (R4 critical 2)**: extended from 1 to 5 real SDS-init meshes (Fantasia3D `f3d_animal`, threestudio `ts_animal`/`ts_blub`/`ts_env_sphere`/`ts_teddy`); 2 accept, 3 rollback. Reported in `tab:real_mesh`.
- **Non-tautological editability metric (R4 critical 3)**: chart-boundary curvature alignment in `tab:curvature_alignment`. Honestly disclosed: xatlas's distortion-driven seams beat PartUV-style semantic seams under this geometry-only metric (e.g. spot 0.43 vs 0.09).

### Major fixes (R4-R9)

- Abstract acceptance counting reconciled (R4 minor 1) — "one additional non-overlapping acceptance" instead of "fourth acceptance".
- Mitsuba 3 citation added (R4 minor 4) — `\cite{jakob2022mitsuba3}` while keeping `nimier_david2019_mitsuba2` for retargetable reference.
- Fig 4 ablation IDs aligned with `tab:ablation` (R4 major 3) — drop A10/A11/A13 placeholder rows from the figure.
- Table 3 panel (b) absolute Q95/utilization/chart/seam stats for accepted cases (R4 major 4).
- Appendix A C2 leakage text fixed (R5 major 1) — explicitly states C2 uses proposal split only.
- Oracle ∞ rows replaced with "n/a" (R5 minor 1).
- Visual evidence Fig 7: 5 accepted-case before/after with shared inferno colorbar 0–0.4, gamma+gain brightening, xatlas baseline column added (R6/R7 visual evidence majors).
- Runtime + peak GPU table 12 in appendix (R6 minor 3).
- C5 hard guard equation now explicitly includes utilization guard (R9 minor 5).
- Fig 7 zoom insets: yellow-boxed highest-error region with top-right zoomed inset on each panel (R8/R9 visual density concern).

### W1+ structural restructure in flight

- Path A "BEAST 8.0 plan" launched 2026-05-03. Captured-target evaluation on DiLiGenT-MV is the planned headline replacement for synthetic oracle main results. Code, captured-target adapter, runner, grid driver, bootstrap collector, n=10 statistical runner, target-signal confound test, Polyhaven CC0 fallback, and Semantic-Visibility-UV install kill switch are all prepared. Restructured abstract and Section 3 "Target signal regime" subsection drafts saved to `refine-logs/`.

### Verification

- Final PDF (pre-restructure): `main_round18_zoom_caption.pdf`, 14 pages.
- All 18 round snapshots preserved in `paper/main_round*.pdf` for review history.
- `main.log`: no undefined references, no missing citations, modulo pre-existing overfull hbox warnings in dense equations.

