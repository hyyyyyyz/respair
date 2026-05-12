"""B5 strict matched-control constraints.

The B5 controls are runtime patches around the B3 runner.  They do not edit
the C1-C4 method implementation; instead they make C5 reject any candidate
atlas that violates the requested matched-control condition.
"""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping

import torch


@dataclass(frozen=True)
class B5Condition:
    id: str
    name: str
    constraints: tuple[str, ...]
    expected: str


B5_CONDITIONS: dict[str, B5Condition] = {
    "B5.1": B5Condition(
        id="B5.1",
        name="Atlas-size and padding locked",
        constraints=("atlas_size", "padding"),
        expected="Final PSNR should stay close to B3 ACCEPT when atlas size and padding are fixed.",
    ),
    "B5.2": B5Condition(
        id="B5.2",
        name="Chart count locked within +/-5%",
        constraints=("chart_count",),
        expected="Delta PSNR over the PartUV initial atlas should remain at least +0.3 dB.",
    ),
    "B5.3": B5Condition(
        id="B5.3",
        name="Distortion Q95 locked",
        constraints=("distortion_q95",),
        expected="Final max Q95 distortion must be no more than baseline Q95 + 0.5.",
    ),
    "B5.4": B5Condition(
        id="B5.4",
        name="Texture utilization locked",
        constraints=("utilization",),
        expected="Final texture utilization must be at least 95% of baseline utilization.",
    ),
    "B5.5": B5Condition(
        id="B5.5",
        name="All strict matched controls",
        constraints=("atlas_size", "padding", "chart_count", "distortion_q95", "utilization"),
        expected="With all four controls enforced, Delta PSNR should remain at least +0.3 dB if the gain is not confounded.",
    ),
}


def normalize_condition_id(condition: str) -> str:
    """Normalize CLI/config spellings such as ``B5_1`` or ``1`` to ``B5.1``."""

    raw = str(condition).strip().upper().replace("_", ".")
    if raw.startswith("B5.") and raw in B5_CONDITIONS:
        return raw
    if raw.startswith("B5") and raw[2:].lstrip(".").isdigit():
        key = f"B5.{int(raw[2:].lstrip('.'))}"
        if key in B5_CONDITIONS:
            return key
    if raw.isdigit():
        key = f"B5.{int(raw)}"
        if key in B5_CONDITIONS:
            return key
    raise KeyError(f"Unknown B5 condition: {condition!r}")


def patch_config(cfg: Mapping[str, Any], condition: str) -> dict[str, Any]:
    """Return a B3-compatible config with B5 metadata and strict thresholds."""

    condition_id = normalize_condition_id(condition)
    spec = B5_CONDITIONS[condition_id]
    out = deepcopy(dict(cfg or {}))
    atlas_resolution = int(out.get("atlas_resolution", 1024))
    matched = out.setdefault("matched_protocol", {})
    matched["atlas_size"] = atlas_resolution
    matched.setdefault("padding", 8)
    matched["chart_count_window"] = 0.05 if "chart_count" in spec.constraints else float(matched.get("chart_count_window", 0.08))

    c5 = out.setdefault("c5_guard", {})
    if "distortion_q95" in spec.constraints:
        c5["distortion_tail_epsilon"] = 0.5
    else:
        c5.setdefault("distortion_tail_epsilon", 3.0)

    repair = out.setdefault("repair", {})
    if "chart_count" in spec.constraints:
        repair["edit_types"] = ["boundary_slide", "local_arap"]
        repair["edit_budget"] = min(float(repair.get("edit_budget", 0.15)), 0.15)

    b5 = out.setdefault("b5_strict", {})
    b5.update(
        {
            "id": spec.id,
            "name": spec.name,
            "constraints": list(spec.constraints),
            "expected": spec.expected,
            "chart_count_window": 0.05,
            "distortion_q95_epsilon": 0.5,
            "utilization_ratio_min": 0.95,
            "freeze_repack_layout": any(key in spec.constraints for key in ("distortion_q95", "utilization")),
        }
    )
    out["block"] = "B5_matched"
    return out


def strict_report(
    guard: Mapping[str, Any],
    *,
    baseline_atlas,
    candidate_atlas,
    condition: str,
    cfg: Mapping[str, Any],
) -> dict[str, Any]:
    """Compute strict matched-control pass/fail details for a C5 guard call."""

    condition_id = normalize_condition_id(condition)
    spec = B5_CONDITIONS[condition_id]
    b5_cfg = dict(dict(cfg).get("b5_strict", {}))
    base = dict(guard.get("baseline_stats") or {})
    cand = dict(guard.get("candidate_stats") or {})
    violations: list[str] = []
    limits: dict[str, Any] = {}

    if "atlas_size" in spec.constraints:
        expected = int(getattr(baseline_atlas, "atlas_size"))
        actual = int(getattr(candidate_atlas, "atlas_size"))
        limits["atlas_size"] = expected
        if actual != expected:
            violations.append(f"atlas_size={actual} != {expected}")

    if "padding" in spec.constraints:
        expected = int(getattr(baseline_atlas, "padding"))
        actual = int(getattr(candidate_atlas, "padding"))
        limits["padding"] = expected
        if actual != expected:
            violations.append(f"padding={actual} != {expected}")

    if "chart_count" in spec.constraints:
        window = float(b5_cfg.get("chart_count_window", 0.05))
        base_count = int(base.get("chart_count", 0))
        cand_count = int(cand.get("chart_count", 0))
        lower = int(math.ceil(base_count * (1.0 - window)))
        upper = int(math.floor(base_count * (1.0 + window)))
        if lower > upper:
            lower = upper = base_count
        limits["chart_count_bounds"] = [lower, upper]
        if cand_count < lower or cand_count > upper:
            violations.append(f"chart_count={cand_count} outside [{lower}, {upper}]")

    if "distortion_q95" in spec.constraints:
        eps = float(b5_cfg.get("distortion_q95_epsilon", 0.5))
        base_q95 = float(base.get("max_distortion_q95", 0.0))
        cand_q95 = float(cand.get("max_distortion_q95", 0.0))
        limit = base_q95 + eps
        limits["max_distortion_q95"] = limit
        if cand_q95 > limit:
            violations.append(f"max_distortion_q95={cand_q95:.4f} > {limit:.4f}")

    if "utilization" in spec.constraints:
        ratio = float(b5_cfg.get("utilization_ratio_min", 0.95))
        base_util = float(base.get("texture_utilization", 0.0))
        cand_util = float(cand.get("texture_utilization", 0.0))
        limit = base_util * ratio
        limits["texture_utilization_min"] = limit
        if cand_util < limit:
            violations.append(f"texture_utilization={cand_util:.4f} < {limit:.4f}")

    return {
        "id": condition_id,
        "name": spec.name,
        "constraints": list(spec.constraints),
        "matched_ok": not violations,
        "violations": violations,
        "limits": limits,
        "baseline_stats": base,
        "candidate_stats": cand,
    }


def patch_c5_guard(component: Callable[..., dict[str, Any]], condition: str, cfg: Mapping[str, Any]):
    """Wrap ``scripts.run_B3._c5_guard`` with B5 strict-control rejection."""

    condition_id = normalize_condition_id(condition)

    def wrapped_guard(**kwargs):
        guard = component(**kwargs)
        report = strict_report(
            guard,
            baseline_atlas=kwargs["baseline_atlas"],
            candidate_atlas=kwargs["candidate_atlas"],
            condition=condition_id,
            cfg=cfg,
        )
        if report["violations"]:
            guard.setdefault("violations", [])
            guard["violations"] = list(guard["violations"]) + [f"B5 {item}" for item in report["violations"]]
            guard["hard_accept"] = False
            guard["accept"] = False
        else:
            guard["hard_accept"] = bool(guard.get("hard_accept", False))
            guard["accept"] = bool(guard["hard_accept"] and guard.get("metric_accept", False))
        guard["b5_strict"] = report
        return guard

    return wrapped_guard


def make_layout_preserving_repack(original):
    """Return a repack wrapper that preserves the incoming UV layout.

    B5.3/B5.4/B5.5 need to separate method gains from distortion/utilization
    changes introduced by C3 repacking.  The wrapper keeps the C3 allocation
    log intact but prevents the allocation step from changing atlas geometry.
    """

    def wrapped_repack(uv, face_uv, chart_ids, *, atlas_size: int, padding: int, chart_scales=None):
        del atlas_size, padding, chart_scales
        return (
            uv.detach().clone() if isinstance(uv, torch.Tensor) else torch.as_tensor(uv).clone(),
            face_uv.detach().clone() if isinstance(face_uv, torch.Tensor) else torch.as_tensor(face_uv).clone(),
            chart_ids.detach().clone() if isinstance(chart_ids, torch.Tensor) else torch.as_tensor(chart_ids).clone(),
        )

    wrapped_repack.__name__ = getattr(original, "__name__", "repack_existing_charts")
    wrapped_repack.__doc__ = "B5 layout-preserving wrapper around repack_existing_charts."
    return wrapped_repack


def annotate_metrics(metrics: Mapping[str, Any], condition: str, cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Add B5 table-facing metadata to a completed metrics payload."""

    condition_id = normalize_condition_id(condition)
    spec = B5_CONDITIONS[condition_id]
    out = deepcopy(dict(metrics or {}))
    out["block"] = "B5_matched"
    out["condition"] = condition_id
    out["condition_name"] = spec.name
    out["condition_expected"] = spec.expected
    out["resolved_b5_config"] = deepcopy(dict(cfg).get("b5_strict", {}))
    c5 = out.setdefault("c5", {})
    if "b5_strict" not in c5:
        c5["b5_strict"] = {
            "id": condition_id,
            "name": spec.name,
            "constraints": list(spec.constraints),
            "matched_ok": c5.get("hard_accept") is True,
            "violations": list(c5.get("violations") or []),
        }
    return out


__all__ = [
    "B5_CONDITIONS",
    "B5Condition",
    "annotate_metrics",
    "make_layout_preserving_repack",
    "normalize_condition_id",
    "patch_c5_guard",
    "patch_config",
    "strict_report",
]
