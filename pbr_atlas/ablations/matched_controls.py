"""A10-A13 hard matched-control enforcement for B4."""

from __future__ import annotations

from typing import Any, Callable

from pbr_atlas.ablations.common import mark_ablation


def _tolerance(cfg: dict[str, Any], key: str, default: float) -> float:
    return float(cfg.get("ablation", {}).get("matched_tolerances", {}).get(key, default))


def enforce_matched_control(control_id: str, cfg: dict[str, Any], guard: dict[str, Any], *, baseline_atlas, candidate_atlas) -> dict[str, Any]:
    base = guard.get("baseline_stats", {})
    cand = guard.get("candidate_stats", {})
    violations: list[str] = []
    if control_id == "A10":
        tol = _tolerance(cfg, "utilization_abs", 0.015)
        delta = abs(float(cand.get("texture_utilization", 0.0)) - float(base.get("texture_utilization", 0.0)))
        if delta > tol:
            violations.append(f"utilization_delta={delta:.6f} > {tol:.6f}")
    elif control_id == "A11":
        tol = _tolerance(cfg, "distortion_q95_abs", 0.03)
        delta = abs(float(cand.get("max_distortion_q95", 0.0)) - float(base.get("max_distortion_q95", 0.0)))
        if delta > tol:
            violations.append(f"distortion_q95_delta={delta:.6f} > {tol:.6f}")
    elif control_id == "A12":
        if int(candidate_atlas.padding) != int(baseline_atlas.padding):
            violations.append(f"padding={candidate_atlas.padding} != {baseline_atlas.padding}")
    elif control_id == "A13":
        window = _tolerance(cfg, "chart_count_window", 0.05)
        base_count = int(base.get("chart_count", 0))
        cand_count = int(cand.get("chart_count", 0))
        limit = max(1, int(base_count * window + 0.999))
        if abs(cand_count - base_count) > limit:
            violations.append(f"chart_count_delta={cand_count - base_count} exceeds +/-{limit}")
    if violations:
        raise RuntimeError(f"{control_id} matched-control violation: {'; '.join(violations)}")
    guard["matched_control"] = {"id": control_id, "hard_constraint_ok": True}
    return guard


def patch_c5_guard(component: Callable[..., dict[str, Any]], control_id: str, cfg: dict[str, Any]):
    def wrapped_guard(**kwargs):
        guard = component(**kwargs)
        return enforce_matched_control(
            control_id,
            cfg,
            guard,
            baseline_atlas=kwargs["baseline_atlas"],
            candidate_atlas=kwargs["candidate_atlas"],
        )

    return wrapped_guard


def patch_A10(component):
    cfg = mark_ablation(component, "A10", name="Matched-utilization control", mechanism="lock_texture_utilization")
    cfg.setdefault("ablation", {})["matched_control"] = "utilization"
    cfg["ablation"].setdefault("matched_tolerances", {})["utilization_abs"] = 0.015
    return cfg


def patch_A11(component):
    cfg = mark_ablation(component, "A11", name="Matched-distortion control", mechanism="lock_q95_distortion")
    cfg.setdefault("ablation", {})["matched_control"] = "distortion"
    cfg["ablation"].setdefault("matched_tolerances", {})["distortion_q95_abs"] = 0.03
    return cfg


def patch_A12(component):
    cfg = mark_ablation(component, "A12", name="Matched-padding control", mechanism="lock_padding")
    cfg.setdefault("ablation", {})["matched_control"] = "padding"
    return cfg


def patch_A13(component):
    cfg = mark_ablation(component, "A13", name="Matched-chart-count control", mechanism="lock_chart_count_pm5")
    cfg.setdefault("ablation", {})["matched_control"] = "chart_count"
    cfg["ablation"].setdefault("matched_tolerances", {})["chart_count_window"] = 0.05
    cfg.setdefault("matched_protocol", {})["chart_count_window"] = 0.05
    cfg.setdefault("repair", {})["edit_budget"] = min(float(cfg["repair"].get("edit_budget", 0.15)), 0.10)
    return cfg


def patch(component):
    ablation_id = str(component.get("ablation", {}).get("id", "")).upper()
    if ablation_id == "A10":
        return patch_A10(component)
    if ablation_id == "A11":
        return patch_A11(component)
    if ablation_id == "A12":
        return patch_A12(component)
    if ablation_id == "A13":
        return patch_A13(component)
    raise KeyError(f"matched_controls.patch requires A10-A13 config, got {ablation_id!r}")


__all__ = [
    "enforce_matched_control",
    "patch",
    "patch_A10",
    "patch_A11",
    "patch_A12",
    "patch_A13",
    "patch_c5_guard",
]

