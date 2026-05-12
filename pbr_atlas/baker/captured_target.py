"""Captured-image target adapter for the C1-C5 pipeline.

The standard pipeline expects ``target_render`` to be a ``RenderOutput`` whose
``.images`` are the supervision signal. For captured datasets such as
DiLiGenT-MV, those images come from real cameras rather than synthetic
oracle bakes. This module reshapes captured imagery into a RenderOutput
that the rest of the pipeline can consume unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import torch
import torch.nn.functional as F

from pbr_atlas.baker.baker import RenderOutput


@dataclass
class CapturedSplit:
    """A captured target subset for one (view-set, light-set) split."""

    view_indices: list[int]
    light_indices: list[int]
    images: torch.Tensor  # [N_pairs, H, W, 3] linear, intensity-normalized
    masks: torch.Tensor   # [N_pairs, H, W] bool (validity)


def _resize_image(image_hw3: torch.Tensor, target_size: int) -> torch.Tensor:
    if image_hw3.shape[0] == target_size and image_hw3.shape[1] == target_size:
        return image_hw3
    chw = image_hw3.permute(2, 0, 1).unsqueeze(0)
    out = F.interpolate(chw, size=(target_size, target_size), mode="bilinear", align_corners=False, antialias=True)
    return out.squeeze(0).permute(1, 2, 0).contiguous()


def _resize_mask(mask_hw: torch.Tensor, target_size: int) -> torch.Tensor:
    chw = mask_hw.float().unsqueeze(0).unsqueeze(0)
    out = F.interpolate(chw, size=(target_size, target_size), mode="nearest")
    return out.squeeze(0).squeeze(0) > 0.5


def build_captured_split(
    asset,
    view_indices: Sequence[int],
    light_indices: Sequence[int],
    *,
    render_resolution: int,
) -> CapturedSplit:
    """Pack captured imagery for the (V, L) Cartesian product into a CapturedSplit.

    Pairs are ordered ``(v0,l0), (v0,l1), ..., (v0,lN-1), (v1,l0), ...`` to
    match the layout produced by the baker's render() over Cartesian
    products of views and lights.
    """
    pairs_images: list[torch.Tensor] = []
    pairs_masks: list[torch.Tensor] = []
    for vi in view_indices:
        view = asset.views[vi]
        view_imgs = view.images.detach().to(torch.float32)
        mask = view.mask.detach().to(torch.bool)
        for li in light_indices:
            img = view_imgs[li]
            img_r = _resize_image(img, render_resolution)
            mask_r = _resize_mask(mask, render_resolution)
            pairs_images.append(img_r)
            pairs_masks.append(mask_r)
    images = torch.stack(pairs_images, dim=0).clamp(0.0, 16.0)
    masks = torch.stack(pairs_masks, dim=0)
    return CapturedSplit(
        view_indices=list(view_indices),
        light_indices=list(light_indices),
        images=images,
        masks=masks,
    )


def captured_split_to_render_output(split: CapturedSplit, *, device: torch.device) -> RenderOutput:
    """Convert a CapturedSplit into a RenderOutput-shaped object.

    ``face_ids`` is a placeholder tensor of zeros: the pipeline only consumes
    target ``.images`` for loss/residual computation; ``.face_ids`` from the
    captured side are not used for residual attribution (which reads them from
    the *predicted* render path instead).
    """
    images = split.images.to(device).to(torch.float32)
    masks = split.masks.to(device)
    face_ids = torch.zeros(images.shape[:3], dtype=torch.long, device=device)
    alpha = masks.to(torch.float32)
    return RenderOutput(images=images, face_ids=face_ids, alpha=alpha)


def make_captured_view_light_splits(
    asset,
    *,
    proposal_views: Sequence[int],
    proposal_lights: Sequence[int],
    gate_views: Sequence[int],
    gate_lights: Sequence[int],
    test_views: Sequence[int],
    test_lights: Sequence[int],
    render_resolution: int,
    device: torch.device,
) -> dict[str, RenderOutput]:
    """Bundle proposal/gate/test captured RenderOutput-shaped targets."""
    splits = {
        "proposal": build_captured_split(asset, proposal_views, proposal_lights, render_resolution=render_resolution),
        "gate": build_captured_split(asset, gate_views, gate_lights, render_resolution=render_resolution),
        "test": build_captured_split(asset, test_views, test_lights, render_resolution=render_resolution),
    }
    return {k: captured_split_to_render_output(v, device=device) for k, v in splits.items()}


__all__ = [
    "CapturedSplit",
    "build_captured_split",
    "captured_split_to_render_output",
    "make_captured_view_light_splits",
]
