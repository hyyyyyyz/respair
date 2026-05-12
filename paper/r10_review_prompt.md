# R10 Fresh PG2026/CGF Review (post-W1 captured-target restructure)

You are a senior reviewer for **Pacific Graphics 2026 / Computer Graphics Forum special issue**. Read the paper at `paper/main.pdf` (LaTeX source under `paper/sections/*.tex`, tables under `paper/tables/*.tex`, figures under `figures/`) and provide an INDEPENDENT review.

## R9 → R10 changes since the last review

R9 reviewer scored 7.5/10 ("Almost") with one CRITICAL: no captured-PBR validation. Since R9 the paper has been **restructured** around the captured-target signal:

1. **New title and positioning**: "Captured-Target Residuals for Selective UV Atlas Repair." The deployment-readiness claim is no longer asserted in absentia of captured evidence; the captured regime is now part of the headline.
2. **New headline table**: `tab:diligent_mv` (Section 4 main results) reports captured-target evaluation on the DiLiGenT-MV dataset (5 objects, 20 calibrated views, 96 calibrated lights/view) under disjoint proposal/gate/test view+light splits, multi-seed reruns. This replaces the synthetic-oracle 12-case table as the headline. The synthetic oracle results are kept as a controlled diagnostic.
3. **New Section 3 subsection "Target signal regime"**: explicitly enumerates synthetic oracle, self-described oracle, and captured imagery as three regimes the same C1--C5 mechanism handles, and ties each to its evaluation table.
4. **Reduced contributions**: 4 contributions instead of 5 — channel-aware baker (C1), local repair (C2), residual allocation (C3), holdout gate (C5). Cross-channel seam (C4) and explicit mip term moved from claimed contributions to instrumentation diagnostics with their isolation-evidence weakness explicitly disclosed.
5. **C5 hard guard equation** now explicitly includes utilization guard.
6. **Visual evidence Fig 7** has yellow-boxed seam/mip zoom insets on each panel for paper-scale readability.
7. **Citations added**: OptCuts, Boundary First Flattening, SLIM-style scalable locally injective mappings, MikkTSpace tangent convention, FLIP perceptual metric.

R9 MAJOR items still open and explicitly deferred to future work:
- FlexPara reproduction (cu111/Python 3.9 stack mismatch persists);
- Component isolation for C4/mip (designed stress harnesses prepared but defer until a future revision);
- captured RGB-channel separation from material-prediction error (the synthetic confound test addresses this in part).

## Your task

Review the paper using this exact format. Do NOT anchor on prior scores; assess fresh.

```
# Overall Score X.X/10

# Verdict
[Reject | Almost | Weak Accept | Accept | Strong Accept]

# Summary
[2-4 sentences]

# Strengths
1. ...
2. ...

# Weaknesses

## CRITICAL
[Issues that block acceptance, if any]

## MAJOR
[Issues that significantly weaken the paper]

## MINOR
[Wording, citation, layout]

# Visual Review
[Honest assessment of figures]

# Component Score Breakdown
| Component | Score | Rationale |
|---|---:|---|
| Problem relevance | X.X/10 | ... |
| Novelty | X.X/10 | ... |
| Technical soundness | X.X/10 | ... |
| Experimental strength | X.X/10 | ... |
| Baselines | X.X/10 | ... |
| Visual evidence | X.X/10 | ... |
| Writing and honesty | X.X/10 | ... |
| Reproducibility | X.X/10 | ... |

# Missing Citations
[If any]
```

A score of 8.0+ requires that the paper would actually be accepted at PG/CGF special issue.
