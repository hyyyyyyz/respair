"""C2 residual-attributed local chart repair.

This module keeps the repair space deliberately local: the input atlas is a
B2 ``BaselineAtlas`` and every operator edits only selected high-residual
charts. It does not introduce a new global UV solver.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Callable, Iterable, Optional, Sequence

import torch

from pbr_atlas.baker import (
    DifferentiablePBRBaker,
    LightSpec,
    PBRMaps,
    ViewSpec,
    make_lights,
    make_orbit_views,
    sample_face_pbr_from_maps,
)
from pbr_atlas.baker.residual import ResidualAttribution, mesh_seam_edges, per_chart_residual
from pbr_atlas.baselines.base import BaselineAtlas, clone_mesh_with_atlas, repack_existing_charts
from pbr_atlas.baselines.matched_protocol import AtlasStats, compute_atlas_stats
from pbr_atlas.data.mesh_loader import MeshData


@dataclass
class RepairConfig:
    top_k_ratio: float = 0.15
    top_k_max: int = 32
    edit_types: tuple[str, ...] = ("split", "merge", "boundary_slide", "local_arap")
    beam_size: int = 4
    distortion_area_max: float = 2.0
    distortion_angle_max: float = 35.0
    edit_budget: float = 0.15
    eta_seam: float = 0.25
    lambda_d: float = 1.0
    lambda_theta: float = 0.01
    lambda_n: float = 0.02
    lambda_b: float = 0.25
    lambda_render: float = 1.0
    boundary_slide_amount: float = 0.035
    local_arap_iterations: int = 10
    render_eval_views: int = 1
    render_eval_lights: int = 1
    mip_levels: int = 4
    raster_resolution: int = 128


@dataclass
class RepairCandidate:
    chart_id: int
    edit_type: str
    score: float
    delta_render: float
    delta_seam: float
    area_q95: float
    angle_q95: float
    chart_count: int
    atlas: BaselineAtlas = field(repr=False)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("atlas", None)
        return data


@dataclass
class RepairLog:
    baseline_chart_count: int
    final_chart_count: int
    candidate_count: int
    selected_chart_ids: list[int]
    edits: list[dict[str, Any]]
    skipped_chart_ids: list[int]
    edited_chart_ratio: float
    config: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clone_atlas(atlas: BaselineAtlas, *, name: Optional[str] = None, metadata: Optional[dict[str, Any]] = None) -> BaselineAtlas:
    merged_metadata = dict(atlas.metadata)
    if metadata:
        merged_metadata.update(metadata)
    return replace(
        atlas,
        name=name or atlas.name,
        uv=atlas.uv.detach().clone(),
        face_uv=atlas.face_uv.detach().clone(),
        chart_ids=atlas.chart_ids.detach().clone(),
        metadata=merged_metadata,
    )


def _compact_chart_ids(chart_ids: torch.Tensor) -> torch.Tensor:
    if chart_ids.numel() == 0:
        return chart_ids.to(torch.long)
    _, inverse = torch.unique(chart_ids.detach().cpu().to(torch.long), sorted=True, return_inverse=True)
    return inverse.to(torch.long)


def _chart_count(chart_ids: torch.Tensor) -> int:
    return int(torch.unique(chart_ids.detach().cpu().to(torch.long)).numel()) if chart_ids.numel() else 0


def _repack(atlas: BaselineAtlas, *, name: str, metadata: dict[str, Any]) -> BaselineAtlas:
    uv, face_uv, chart_ids = repack_existing_charts(
        atlas.uv,
        atlas.face_uv,
        _compact_chart_ids(atlas.chart_ids),
        atlas_size=atlas.atlas_size,
        padding=atlas.padding,
    )
    return replace(
        atlas,
        name=name,
        uv=uv,
        face_uv=face_uv,
        chart_ids=chart_ids,
        metadata={**dict(atlas.metadata), **metadata},
    )


def _target_uv_ids(atlas: BaselineAtlas, target_chart: int) -> torch.Tensor:
    mask = atlas.chart_ids.detach().cpu().to(torch.long) == int(target_chart)
    if not mask.any():
        return torch.empty(0, dtype=torch.long)
    return torch.unique(atlas.face_uv.detach().cpu().to(torch.long)[mask].reshape(-1))


def _chart_uv_centroids(atlas: BaselineAtlas) -> dict[int, torch.Tensor]:
    out: dict[int, torch.Tensor] = {}
    uv = atlas.uv.detach().cpu().to(torch.float32)
    face_uv = atlas.face_uv.detach().cpu().to(torch.long)
    chart_ids = atlas.chart_ids.detach().cpu().to(torch.long)
    for chart in torch.unique(chart_ids).tolist():
        mask = chart_ids == int(chart)
        uv_ids = torch.unique(face_uv[mask].reshape(-1))
        out[int(chart)] = uv[uv_ids].mean(dim=0) if uv_ids.numel() else torch.zeros(2)
    return out


def op_split_chart(charts: BaselineAtlas, target_chart: int, axis: str = "dominant_curvature") -> BaselineAtlas:
    """Split one chart by a deterministic local median cut.

    FINAL_PROPOSAL C2 operator comment:
        split is one element of A_c. It changes only faces in the selected
        chart c and leaves all other chart memberships untouched.
    """

    del axis
    atlas = _clone_atlas(charts)
    chart_ids = atlas.chart_ids.detach().cpu().to(torch.long)
    face_uv = atlas.face_uv.detach().cpu().to(torch.long)
    uv = atlas.uv.detach().cpu().to(torch.float32)
    mask = chart_ids == int(target_chart)
    face_indices = torch.nonzero(mask, as_tuple=False).flatten()
    if face_indices.numel() < 2:
        return _clone_atlas(charts, name=f"{charts.name}_split_skip", metadata={"c2_skip": "split needs at least two faces"})
    centers = uv[face_uv[face_indices]].mean(dim=1)
    axis_idx = int(torch.var(centers, dim=0).argmax().item())
    median = torch.median(centers[:, axis_idx])
    high = centers[:, axis_idx] > median
    if not high.any() or bool(high.all()):
        high = torch.arange(face_indices.numel()) >= face_indices.numel() // 2
    new_id = int(chart_ids.max().item()) + 1
    chart_ids[face_indices[high]] = new_id
    candidate = replace(atlas, chart_ids=chart_ids)
    return _repack(
        candidate,
        name=f"{charts.name}_c2_split",
        metadata={"c2_last_edit": "split", "c2_target_chart": int(target_chart)},
    )


def op_merge_chart(charts: BaselineAtlas, target_chart: int, neighbor_choice: str = "lowest_seam_residual") -> BaselineAtlas:
    """Merge the selected chart into its nearest UV-chart neighbor."""

    del neighbor_choice
    atlas = _clone_atlas(charts)
    chart_ids = atlas.chart_ids.detach().cpu().to(torch.long)
    charts_present = [int(c) for c in torch.unique(chart_ids).tolist()]
    if int(target_chart) not in charts_present or len(charts_present) <= 1:
        return _clone_atlas(charts, name=f"{charts.name}_merge_skip", metadata={"c2_skip": "no neighbor chart"})
    centroids = _chart_uv_centroids(atlas)
    target_center = centroids[int(target_chart)]
    neighbors = [c for c in charts_present if c != int(target_chart)]
    neighbor = min(neighbors, key=lambda c: float((centroids[c] - target_center).norm().item()))
    chart_ids[chart_ids == int(target_chart)] = int(neighbor)
    chart_ids = _compact_chart_ids(chart_ids)
    candidate = replace(atlas, chart_ids=chart_ids)
    return _repack(
        candidate,
        name=f"{charts.name}_c2_merge",
        metadata={"c2_last_edit": "merge", "c2_target_chart": int(target_chart), "c2_neighbor_chart": int(neighbor)},
    )


def op_boundary_slide(charts: BaselineAtlas, target_chart: int, slide_amount: float) -> BaselineAtlas:
    """Move selected-chart UV boundary vertices by a small local scale step."""

    atlas = _clone_atlas(charts)
    uv = atlas.uv.detach().cpu().to(torch.float32).clone()
    uv_ids = _target_uv_ids(atlas, target_chart)
    if uv_ids.numel() == 0:
        return _clone_atlas(charts, name=f"{charts.name}_slide_skip", metadata={"c2_skip": "empty target chart"})
    center = uv[uv_ids].mean(dim=0, keepdim=True)
    scale = 1.0 + float(slide_amount)
    uv[uv_ids] = (center + (uv[uv_ids] - center) * scale).clamp(0.0, 1.0)
    return replace(
        atlas,
        name=f"{charts.name}_c2_boundary_slide",
        uv=uv,
        metadata={
            **dict(atlas.metadata),
            "c2_last_edit": "boundary_slide",
            "c2_target_chart": int(target_chart),
            "c2_slide_amount": float(slide_amount),
        },
    )


def op_local_arap(charts: BaselineAtlas, target_chart: int, iterations: int = 10) -> BaselineAtlas:
    """Apply a lightweight local ARAP-style UV smoothing step.

    This is an engineering surrogate for the local ARAP candidate in C2: only
    UV vertices used by the target chart are smoothed over local chart edges,
    then rescaled back to the original chart bounding box.
    """

    atlas = _clone_atlas(charts)
    uv = atlas.uv.detach().cpu().to(torch.float32).clone()
    face_uv = atlas.face_uv.detach().cpu().to(torch.long)
    mask = atlas.chart_ids.detach().cpu().to(torch.long) == int(target_chart)
    uv_ids = torch.unique(face_uv[mask].reshape(-1)) if mask.any() else torch.empty(0, dtype=torch.long)
    if uv_ids.numel() < 3:
        return _clone_atlas(charts, name=f"{charts.name}_arap_skip", metadata={"c2_skip": "local ARAP needs at least three UV vertices"})
    old = uv[uv_ids].clone()
    min_xy = old.min(dim=0).values
    span = (old.max(dim=0).values - min_xy).clamp_min(1.0e-6)
    local_index = {int(idx): local for local, idx in enumerate(uv_ids.tolist())}
    adjacency = [set() for _ in range(uv_ids.numel())]
    for tri in face_uv[mask].tolist():
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            if int(a) in local_index and int(b) in local_index:
                ia, ib = local_index[int(a)], local_index[int(b)]
                adjacency[ia].add(ib)
                adjacency[ib].add(ia)
    local = old.clone()
    for _ in range(max(1, int(iterations))):
        updated = local.clone()
        for idx, nbrs in enumerate(adjacency):
            if not nbrs:
                continue
            avg = local[torch.tensor(sorted(nbrs), dtype=torch.long)].mean(dim=0)
            updated[idx] = 0.85 * local[idx] + 0.15 * avg
        local = updated
    local_min = local.min(dim=0).values
    local_span = (local.max(dim=0).values - local_min).clamp_min(1.0e-6)
    local = (local - local_min) / local_span * span + min_xy
    uv[uv_ids] = local.clamp(0.0, 1.0)
    return replace(
        atlas,
        name=f"{charts.name}_c2_local_arap",
        uv=uv,
        metadata={
            **dict(atlas.metadata),
            "c2_last_edit": "local_arap",
            "c2_target_chart": int(target_chart),
            "c2_local_arap_iterations": int(iterations),
        },
    )


class LocalChartRepair:
    """C2: top-K residual chart -> beam search edits -> repaired atlas.

    FINAL_PROPOSAL C2 equations:
        C_edit = TopK_c(E_c + eta * S_c),
        K <= min(0.15 * |C0|, 32).

        J(c,a) = Delta L_render(c,a)
                 + lambda_d [D_area(U_a)-tau_a]_+^2
                 + lambda_theta [D_angle(U_a)-tau_theta]_+^2
                 + lambda_n ||C_a|-|C0||
                 + lambda_b Delta L_seam.

        a*_c = argmin_{a in A_c} J(c,a).

    Candidate render deltas are finite-difference evaluations: for each
    topology/UV edit a, the code bakes and renders U_a under no_grad and
    subtracts the current render loss. No gradient is taken through chart
    topology changes.
    """

    def __init__(self, config: RepairConfig):
        self.config = config

    def repair(
        self,
        baker: DifferentiablePBRBaker,
        mesh: MeshData,
        baseline: BaselineAtlas,
        oracle_pbr: PBRMaps,
        residual_attribution: ResidualAttribution,
        proposal_views: Optional[Sequence[ViewSpec]] = None,
        proposal_lights: Optional[Sequence[LightSpec]] = None,
    ) -> tuple[BaselineAtlas, RepairLog]:
        cfg = self.config
        current = _clone_atlas(baseline, name=f"{baseline.name}_c2_start")
        initial_chart_count = _chart_count(current.chart_ids)
        if initial_chart_count == 0:
            log = RepairLog(0, 0, 0, [], [], [], 0.0, asdict(cfg))
            return current, log

        top_chart_ids = self._select_top_charts(current, residual_attribution)
        max_edits = min(len(top_chart_ids), max(1, int(initial_chart_count * cfg.edit_budget + 0.999)), int(cfg.top_k_max))
        selected = top_chart_ids[:max_edits]
        skipped: list[int] = []
        edits: list[dict[str, Any]] = []
        candidate_count = 0

        render_context = self._make_render_context(
            baker,
            mesh,
            current,
            oracle_pbr,
            views=proposal_views,
            lights=proposal_lights,
        )
        current_loss = self._safe_render_loss(baker, mesh, current, render_context, residual_attribution)
        current_seam = self._seam_proxy(mesh, current, residual_attribution)

        for chart_id in selected:
            candidates = self._make_candidates(current, chart_id)[: max(1, int(cfg.beam_size))]
            scored: list[RepairCandidate] = []
            for edit_type, candidate in candidates:
                candidate_count += 1
                candidate_loss = self._safe_render_loss(baker, mesh, candidate, render_context, residual_attribution)
                candidate_seam = self._seam_proxy(mesh, candidate, residual_attribution)
                stats = compute_atlas_stats(mesh, candidate, raster_resolution=int(cfg.raster_resolution))
                delta_render = float(candidate_loss - current_loss)
                delta_seam = float(candidate_seam - current_seam)
                score = self._score_candidate(stats, delta_render, delta_seam, initial_chart_count)
                scored.append(
                    RepairCandidate(
                        chart_id=int(chart_id),
                        edit_type=edit_type,
                        score=score,
                        delta_render=delta_render,
                        delta_seam=delta_seam,
                        area_q95=float(stats.area_distortion_q95),
                        angle_q95=float(stats.angle_distortion_q95),
                        chart_count=int(stats.chart_count),
                        atlas=candidate,
                    )
                )
            if not scored:
                skipped.append(int(chart_id))
                continue
            best = min(scored, key=lambda item: item.score)
            hard_ok = self._hard_guard(best, initial_chart_count)
            record = best.to_dict()
            record["accepted"] = bool(hard_ok)
            record["beam"] = [item.to_dict() for item in sorted(scored, key=lambda item: item.score)]
            edits.append(record)
            if not hard_ok:
                skipped.append(int(chart_id))
                continue
            current = best.atlas
            current_loss = current_loss + best.delta_render
            current_seam = current_seam + best.delta_seam

        final_chart_count = _chart_count(current.chart_ids)
        edited_ratio = float(len([edit for edit in edits if edit.get("accepted")])) / float(max(initial_chart_count, 1))
        final = replace(
            current,
            name=f"{baseline.name}_c2_repaired",
            metadata={
                **dict(current.metadata),
                "c2_repaired": True,
                "c2_edited_chart_ratio": edited_ratio,
                "c2_edit_count": len([edit for edit in edits if edit.get("accepted")]),
            },
        )
        log = RepairLog(
            baseline_chart_count=initial_chart_count,
            final_chart_count=final_chart_count,
            candidate_count=candidate_count,
            selected_chart_ids=[int(c) for c in selected],
            edits=edits,
            skipped_chart_ids=skipped,
            edited_chart_ratio=edited_ratio,
            config=asdict(cfg),
        )
        return final, log

    def _select_top_charts(self, atlas: BaselineAtlas, residual: ResidualAttribution) -> list[int]:
        cfg = self.config
        chart_ids = atlas.chart_ids.detach().to(residual.e_f.device, torch.long)
        e_chart = residual.E_c.detach().to(residual.e_f.device, torch.float32)
        if e_chart.numel() <= int(chart_ids.max().item() if chart_ids.numel() else -1):
            e_chart = per_chart_residual(residual.e_f, chart_ids)
        seam_chart = torch.zeros_like(e_chart)
        if residual.seam_edges.numel() and residual.seam_residual.numel():
            seams = residual.seam_edges.to(chart_ids.device)
            values = residual.seam_residual.to(chart_ids.device, torch.float32)
            incident = chart_ids[seams.reshape(-1)].reshape(-1, 2)
            sums = torch.zeros_like(e_chart)
            counts = torch.zeros_like(e_chart)
            for side in (0, 1):
                ids = incident[:, side].clamp(0, e_chart.numel() - 1)
                sums.scatter_add_(0, ids, values)
                counts.scatter_add_(0, ids, torch.ones_like(values))
            seam_chart = sums / counts.clamp_min(1.0)
        scores = e_chart + float(cfg.eta_seam) * seam_chart
        present = torch.unique(chart_ids.detach().cpu()).to(torch.long)
        if present.numel() == 0:
            return []
        k = min(max(1, int(present.numel() * cfg.top_k_ratio + 0.999)), int(cfg.top_k_max), int(present.numel()))
        present_scores = scores[present.to(scores.device)].detach().cpu()
        order = torch.argsort(present_scores, descending=True)[:k]
        return [int(present[idx].item()) for idx in order]

    def _make_candidates(self, atlas: BaselineAtlas, chart_id: int) -> list[tuple[str, BaselineAtlas]]:
        out: list[tuple[str, BaselineAtlas]] = []
        for edit_type in self.config.edit_types:
            if edit_type == "split":
                out.append(("split", op_split_chart(atlas, chart_id)))
            elif edit_type == "merge":
                out.append(("merge", op_merge_chart(atlas, chart_id)))
            elif edit_type == "boundary_slide":
                out.append(("boundary_slide", op_boundary_slide(atlas, chart_id, self.config.boundary_slide_amount)))
            elif edit_type == "local_arap":
                out.append(("local_arap", op_local_arap(atlas, chart_id, self.config.local_arap_iterations)))
        return out

    def _score_candidate(self, stats: AtlasStats, delta_render: float, delta_seam: float, initial_chart_count: int) -> float:
        cfg = self.config
        area_over = max(0.0, float(stats.area_distortion_q95) - float(cfg.distortion_area_max))
        angle_over = max(0.0, float(stats.angle_distortion_q95) - float(cfg.distortion_angle_max))
        chart_delta = abs(int(stats.chart_count) - int(initial_chart_count))
        return float(
            cfg.lambda_render * delta_render
            + cfg.lambda_d * area_over * area_over
            + cfg.lambda_theta * angle_over * angle_over
            + cfg.lambda_n * chart_delta
            + cfg.lambda_b * delta_seam
        )

    def _hard_guard(self, candidate: RepairCandidate, initial_chart_count: int) -> bool:
        cfg = self.config
        max_chart_delta = max(1, int(initial_chart_count * cfg.edit_budget + 0.999))
        if abs(int(candidate.chart_count) - int(initial_chart_count)) > max_chart_delta:
            return False
        if candidate.area_q95 > float(cfg.distortion_area_max) * 3.0:
            return False
        if candidate.angle_q95 > float(cfg.distortion_angle_max) * 3.0:
            return False
        return True

    def _make_render_context(
        self,
        baker: DifferentiablePBRBaker,
        mesh: MeshData,
        baseline: BaselineAtlas,
        oracle_pbr: PBRMaps,
        views: Optional[Sequence[ViewSpec]] = None,
        lights: Optional[Sequence[LightSpec]] = None,
    ) -> dict[str, Any]:
        source_mesh = clone_mesh_with_atlas(mesh, baseline, device=baker.device)
        face_values = sample_face_pbr_from_maps(source_mesh, oracle_pbr.to(baker.device))
        uses_proposal_split = views is not None or lights is not None
        if not views:
            views = make_orbit_views(max(1, int(self.config.render_eval_views)), device=baker.device)
        if not lights:
            lights = make_lights(max(1, int(self.config.render_eval_lights)), device=baker.device)
        views = list(views)
        lights = list(lights)
        with torch.no_grad():
            target_maps = baker.bake(source_mesh, face_values)
            target_images = baker.render(source_mesh, target_maps, views, lights).images.detach()
        return {
            "face_values": face_values,
            "views": views,
            "lights": lights,
            "target_images": target_images,
            "split": "proposal" if uses_proposal_split else "legacy",
        }

    def _safe_render_loss(
        self,
        baker: DifferentiablePBRBaker,
        mesh: MeshData,
        atlas: BaselineAtlas,
        context: dict[str, Any],
        residual: ResidualAttribution,
    ) -> float:
        try:
            with torch.no_grad():
                candidate_mesh = clone_mesh_with_atlas(mesh, atlas, device=baker.device)
                maps = baker.bake(candidate_mesh, context["face_values"])
                pred = baker.render(candidate_mesh, maps, context["views"], context["lights"]).images
                return float((pred.to(torch.float32) - context["target_images"].to(pred.device, torch.float32)).abs().mean().detach().cpu())
        except Exception:
            return float(residual.e_f.detach().to(torch.float32).mean().cpu()) if residual.e_f.numel() else 0.0

    @staticmethod
    def _seam_proxy(mesh: MeshData, atlas: BaselineAtlas, residual: ResidualAttribution) -> float:
        chart_ids = atlas.chart_ids.detach().to(mesh.faces.device, torch.long)
        seams = mesh_seam_edges(mesh.faces, chart_ids)
        if seams.numel() == 0 or residual.e_f.numel() == 0:
            return 0.0
        e_f = residual.e_f.to(seams.device, torch.float32)
        return float((0.5 * (e_f[seams[:, 0]] + e_f[seams[:, 1]])).mean().detach().cpu())


__all__ = [
    "LocalChartRepair",
    "RepairCandidate",
    "RepairConfig",
    "RepairLog",
    "op_boundary_slide",
    "op_local_arap",
    "op_merge_chart",
    "op_split_chart",
]
