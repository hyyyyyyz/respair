"""B1 metric implementations: PSNR, SSIM, LPIPS, channel MAE."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import torch


def _to_numpy_image(x: torch.Tensor | np.ndarray) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        x = x.detach().to(torch.float32).cpu().numpy()
    return np.asarray(x, dtype=np.float32).clip(0.0, 1.0)


def psnr(pred: torch.Tensor | np.ndarray, target: torch.Tensor | np.ndarray, eps: float = 1.0e-10) -> float:
    """Peak signal-to-noise ratio for held-out relit RGB."""

    pred_np = _to_numpy_image(pred)
    target_np = _to_numpy_image(target)
    mse = float(np.mean((pred_np - target_np) ** 2))
    if mse <= eps:
        return float("inf")
    return float(-10.0 * np.log10(max(mse, eps)))


def ssim(pred: torch.Tensor | np.ndarray, target: torch.Tensor | np.ndarray) -> float:
    """SSIM averaged over a batch of ``[N,H,W,3]`` images."""

    pred_np = _to_numpy_image(pred)
    target_np = _to_numpy_image(target)
    try:
        from skimage.metrics import structural_similarity
    except Exception:
        return float(1.0 - np.mean(np.abs(pred_np - target_np)))

    if pred_np.ndim == 3:
        pred_np = pred_np[None]
        target_np = target_np[None]
    values = []
    for p_img, t_img in zip(pred_np, target_np):
        win = min(7, p_img.shape[0], p_img.shape[1])
        if win % 2 == 0:
            win -= 1
        if win < 3:
            values.append(float(1.0 - np.mean(np.abs(p_img - t_img))))
        else:
            values.append(
                float(
                    structural_similarity(
                        t_img,
                        p_img,
                        channel_axis=-1,
                        data_range=1.0,
                        win_size=win,
                    )
                )
            )
    return float(np.mean(values))


_LPIPS_MODEL = None


def lpips_distance(pred: torch.Tensor, target: torch.Tensor, device: Optional[torch.device] = None) -> Optional[float]:
    """LPIPS(alex) distance, returning ``None`` when the optional package is absent."""

    global _LPIPS_MODEL
    try:
        import lpips  # type: ignore
    except Exception:
        return None

    device = device or pred.device
    if _LPIPS_MODEL is None:
        _LPIPS_MODEL = lpips.LPIPS(net="alex").to(device).eval()
    pred_t = pred.to(device, torch.float32).permute(0, 3, 1, 2).clamp(0.0, 1.0) * 2.0 - 1.0
    target_t = target.to(device, torch.float32).permute(0, 3, 1, 2).clamp(0.0, 1.0) * 2.0 - 1.0
    with torch.no_grad():
        return float(_LPIPS_MODEL(pred_t, target_t).mean().detach().cpu())


def per_channel_mae(pred_maps: Dict[str, torch.Tensor], target_maps: Dict[str, torch.Tensor]) -> Dict[str, float]:
    """MAE for oracle PBR channels A/N/R/M_t.

    FINAL_PROPOSAL C1 loss comment:
        lambda_pbr * sum_k omega_k ||T_k - T_k^*||_1 is reported here per
        channel for the B1 oracle sanity table.
    """

    out: Dict[str, float] = {}
    for key, pred in pred_maps.items():
        if key not in target_maps:
            continue
        target = target_maps[key].to(pred.device, torch.float32)
        out[f"{key}_mae"] = float((pred.to(torch.float32) - target).abs().mean().detach().cpu())
    return out


def normal_angular_error(pred_normal: torch.Tensor, target_normal: torch.Tensor, eps: float = 1.0e-6) -> float:
    pred = pred_normal.to(torch.float32)
    target = target_normal.to(pred.device, torch.float32)
    pred = pred / pred.norm(dim=-1, keepdim=True).clamp_min(eps)
    target = target / target.norm(dim=-1, keepdim=True).clamp_min(eps)
    cos = (pred * target).sum(dim=-1).clamp(-1.0, 1.0)
    return float(torch.rad2deg(torch.acos(cos)).mean().detach().cpu())


def image_metrics(pred: torch.Tensor, target: torch.Tensor, compute_lpips: bool = True) -> Dict[str, Optional[float]]:
    metrics: Dict[str, Optional[float]] = {
        "psnr": psnr(pred, target),
        "ssim": ssim(pred, target),
    }
    metrics["lpips"] = lpips_distance(pred, target) if compute_lpips else None
    return metrics

