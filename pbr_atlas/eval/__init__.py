"""B1 evaluation metrics and residual attribution wrappers."""

from .chart_purity import (
    chart_part_entropy,
    chart_part_purity,
    normalized_mutual_information,
    summarize_chart_part_overlap,
    weighted_chart_part_purity,
)
from .chart_curvature import summarize_atlas_file, summarize_chart_curvature_alignment
from .metrics import image_metrics, lpips_distance, normal_angular_error, per_channel_mae, psnr, ssim
from .residual_attribution import residual_localization_hit_rate

__all__ = [
    "chart_part_entropy",
    "chart_part_purity",
    "image_metrics",
    "lpips_distance",
    "normal_angular_error",
    "normalized_mutual_information",
    "per_channel_mae",
    "psnr",
    "residual_localization_hit_rate",
    "summarize_atlas_file",
    "summarize_chart_part_overlap",
    "summarize_chart_curvature_alignment",
    "ssim",
    "weighted_chart_part_purity",
]
