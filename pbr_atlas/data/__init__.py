"""B1/B7 sample asset loading and registry."""

from .asset_registry import DEFAULT_DATA_ROOT, prepare_asset, resolve_asset
from .generated_mesh_loader import (
    DEFAULT_B7_DATA_ROOT,
    DEFAULT_B7_ROBUSTNESS_ROOT,
    GeneratedMeshRecord,
    default_asset_ids,
    prepare_generated_mesh,
    prepare_generated_mesh_set,
    prepare_robustness_mesh,
    resolve_generated_mesh,
)
from .mesh_loader import MeshData, load_mesh
from .oracle_pbr import generate_synthetic_oracle_pbr

__all__ = [
    "DEFAULT_B7_DATA_ROOT",
    "DEFAULT_B7_ROBUSTNESS_ROOT",
    "DEFAULT_DATA_ROOT",
    "GeneratedMeshRecord",
    "MeshData",
    "default_asset_ids",
    "generate_synthetic_oracle_pbr",
    "load_mesh",
    "prepare_asset",
    "prepare_generated_mesh",
    "prepare_generated_mesh_set",
    "prepare_robustness_mesh",
    "resolve_asset",
    "resolve_generated_mesh",
]
