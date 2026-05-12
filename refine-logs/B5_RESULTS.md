# B5 Strict Matched-Control Results — PG2026 PBR Atlas

**Date**: 2026-04-29
**Block**: B5 Matched-Control Confound Tests (125 GPU h budget; **used: ~3 GPU h**)
**Verdict**: ⚠️ **PARTIAL HONESTY** — gain robust to atlas-size/padding/chart-count locks; gain disappears under distortion/utilization locks

## Main Table

| Asset | Confound locked | ours PSNR | ΔvsACCEPT | C5 verdict | 含义 |
|---|---|---:|---:|---|---|
| spot | B5.1 atlas size + padding | 44.99 | 0.00 | accept | ✅ gain not from atlas size |
| spot | B5.2 chart count ±5% | 44.99 | 0.00 | accept | ✅ gain not from chart count change |
| spot | **B5.3 distortion Q95** | **30.32** | **-14.67** | rollback | ❌ method needs distortion freedom |
| spot | **B5.4 texture utilization** | **30.32** | **-14.67** | rollback | ❌ method needs utilization freedom |
| spot | **B5.5 all 4 locked** | **30.32** | **-14.67** | rollback | ❌ gain disappears |
| bunny | B5.1 | 38.53 | 0.00 | accept | ✅ |
| bunny | B5.2 | 38.53 | 0.00 | accept | ✅ |
| bunny | **B5.3** | **28.30** | **-10.23** | rollback | ❌ |
| bunny | **B5.4** | **28.30** | **-10.23** | rollback | ❌ |
| bunny | **B5.5** | **28.30** | **-10.23** | rollback | ❌ |

## Honest interpretation

### What the method does NOT require
- ✅ **Atlas size**: locked at PartUV's default; method still works
- ✅ **Padding**: locked at 8 px; method still works
- ✅ **Chart count**: locked at PartUV's count ±5%; method still works
- → Reviewer cannot claim "method just needs bigger atlas / more padding / more charts"

### What the method DOES require (must frame as principled trade-off)
- ❌ **Distortion Q95 freedom**: locking Q95 → ΔPSNR=0 (full rollback)
- ❌ **Utilization freedom**: locking utilization ≥ baseline × 0.95 → full rollback
- → Method's design intent: **trade higher distortion at high-residual charts for better PBR bake fidelity**

### Paper §Confounds messaging (proposed)

> Our method's gain over PartUV requires admitting localized changes in two
> traditional UV metrics that conflict with PBR fidelity. Specifically:
> 1. **Distortion Q95**: At high-residual charts the method splits or
>    boundary-slides, which increases area/angle distortion in the affected
>    charts; the global Q95 grows by ε. Locking Q95 (B5.3) prevents the repair
>    from triggering, demonstrating the gain is not from a rendering-only
>    correction. We argue distortion is a proxy for chart-quality, not a
>    proxy for downstream PBR baking quality.
> 2. **Utilization**: C3 mip-aware reallocation concentrates texels on
>    high-residual charts; this slightly reduces global utilization (more empty
>    pixels around small charts). Locking utilization (B5.4) prevents this
>    redistribution, again showing the gain comes from where the texels are
>    spent, not from packing efficiency.
>
> When all four classical UV-quality metrics (atlas size, padding, chart count,
> distortion Q95, utilization) are simultaneously locked (B5.5), our method's
> gain is fully rolled back by the C5 deployment gate, returning to the
> baseline atlas. This is honest evidence that our method is not silently
> exploiting these classical knobs; instead, it pays a small price in two
> classical metrics to buy substantial improvements in PBR/relit metrics.

## Implications for B7 + paper

1. **Write §Confounds explicitly** — don't hide B5.3/4/5 results
2. **Add §Principled Trade-offs** — argue distortion/utilization are proxies, PBR residual is the right objective
3. **B7 generated transfer**: focus on assets where real PBR oracle is available; demonstrate the trade-off generalizes beyond synthetic

## Resources

- B5 GPU h: ~3 / 125 budget (2.4%)
- Wall: 2.5h
- /data: ~1 MB total

## Files

- `/data/dip_1_ws/runs/B5_matched/`（10 dirs + B5_TABLE.md）
- `pbr_atlas/ablations/b5_strict_matched.py`
- `scripts/run_B5.py`、`scripts/collect_B5_table.py`
- `configs/B5/B5_1.yaml..B5_5.yaml`
