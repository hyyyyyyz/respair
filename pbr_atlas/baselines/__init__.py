"""B2 baseline registry."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Type

from .base import BaselineAtlas, BaselineBackend, BackendBase, clone_mesh_with_atlas
from .blender_uv import BlenderUVBackend
from .flatten_anything import FlattenAnythingBackend
from .flexpara import FlexParaBackend
from .matched_oracle import MatchedOracleBackend
from .otuvgs import OTUVGSBackend
from .parapoint import ParaPointBackend
from .partuv import PartUVBackend
from .visibility_param import VisibilityParamBackend
from .xatlas_classical import XAtlasClassicalBackend

BACKEND_REGISTRY: Dict[str, Type[BackendBase]] = {
    "xatlas_classical": XAtlasClassicalBackend,
    "blender_uv": BlenderUVBackend,
    "partuv": PartUVBackend,
    "flexpara": FlexParaBackend,
    "otuvgs": OTUVGSBackend,
    "flatten_anything": FlattenAnythingBackend,
    "parapoint": ParaPointBackend,
    "visibility_param": VisibilityParamBackend,
    "matched_oracle": MatchedOracleBackend,
}


def create_backend(name: str, config: Mapping[str, Any] | None = None) -> BackendBase:
    try:
        cls = BACKEND_REGISTRY[name]
    except KeyError as exc:
        raise KeyError(f"Unknown B2 baseline backend: {name}") from exc
    return cls(config)


__all__ = [
    "BACKEND_REGISTRY",
    "BaselineAtlas",
    "BaselineBackend",
    "BackendBase",
    "BlenderUVBackend",
    "FlattenAnythingBackend",
    "FlexParaBackend",
    "MatchedOracleBackend",
    "OTUVGSBackend",
    "ParaPointBackend",
    "PartUVBackend",
    "VisibilityParamBackend",
    "XAtlasClassicalBackend",
    "clone_mesh_with_atlas",
    "create_backend",
]
