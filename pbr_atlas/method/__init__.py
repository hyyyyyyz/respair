"""B3 C2-C4 method components."""

from .chart_repair import LocalChartRepair, RepairConfig, RepairLog
from .seam_coupling import CrossChannelSeamLoss, channel_seam_metrics
from .signals import estimate_face_pbr_frequency, estimate_face_visibility
from .texel_alloc import MipAwareAllocator, allocation_to_chart_scales

__all__ = [
    "CrossChannelSeamLoss",
    "LocalChartRepair",
    "MipAwareAllocator",
    "RepairConfig",
    "RepairLog",
    "allocation_to_chart_scales",
    "channel_seam_metrics",
    "estimate_face_pbr_frequency",
    "estimate_face_visibility",
]
