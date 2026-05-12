"""C1 oracle-controlled differentiable PBR baker.

This module implements only the B1 sanity/oracle baker path. It does not
contain C2-C5 atlas repair, allocation, seam coupling, or validation logic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Mapping, List, Optional, Sequence, Tuple

import torch
import torch.nn.functional as nnF

from .ggx import EPS, ggx_brdf, normalize


@dataclass
class PBRMaps:
    """Per-texel PBR atlas maps in ``[H, W, C]`` layout."""

    albedo: torch.Tensor
    normal: torch.Tensor
    roughness: torch.Tensor
    metallic: torch.Tensor
    face_ids: Optional[torch.Tensor] = None

    def to(self, device: Optional[torch.device] = None, dtype: Optional[torch.dtype] = None) -> "PBRMaps":
        def cast(x: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
            if x is None:
                return None
            kwargs = {}
            if device is not None:
                kwargs["device"] = device
            if dtype is not None and x.is_floating_point():
                kwargs["dtype"] = dtype
            return x.to(**kwargs)

        return replace(
            self,
            albedo=cast(self.albedo),
            normal=cast(self.normal),
            roughness=cast(self.roughness),
            metallic=cast(self.metallic),
            face_ids=cast(self.face_ids),
        )


@dataclass
class FacePBRValues:
    """Per-face oracle PBR samples used by the C1 texel coverage bake."""

    albedo: torch.Tensor
    normal: torch.Tensor
    roughness: torch.Tensor
    metallic: torch.Tensor


@dataclass
class ViewSpec:
    eye: torch.Tensor
    target: torch.Tensor
    up: torch.Tensor
    fov_degrees: float = 45.0


@dataclass
class LightSpec:
    direction: torch.Tensor
    color: torch.Tensor
    intensity: float = 1.0


@dataclass
class ViewLightSplit:
    views: List[ViewSpec]
    lights: List[LightSpec]
    view_indices: list[int]
    light_indices: list[int]


@dataclass
class ViewLightSplits:
    proposal: ViewLightSplit
    gate: ViewLightSplit
    test: ViewLightSplit
    split_seed: int

    def to_metadata(self) -> dict[str, object]:
        return {
            "split_seed": int(self.split_seed),
            "proposal": {
                "views": len(self.proposal.views),
                "lights": len(self.proposal.lights),
                "view_indices": list(self.proposal.view_indices),
                "light_indices": list(self.proposal.light_indices),
            },
            "gate": {
                "views": len(self.gate.views),
                "lights": len(self.gate.lights),
                "view_indices": list(self.gate.view_indices),
                "light_indices": list(self.gate.light_indices),
            },
            "test": {
                "views": len(self.test.views),
                "lights": len(self.test.lights),
                "view_indices": list(self.test.view_indices),
                "light_indices": list(self.test.light_indices),
            },
        }


@dataclass
class RenderOutput:
    images: torch.Tensor
    face_ids: torch.Tensor
    alpha: torch.Tensor


def precision_to_dtype(precision: str) -> torch.dtype:
    table = {
        "fp32": torch.float32,
        "float32": torch.float32,
        "fp16": torch.float16,
        "float16": torch.float16,
        "bf16": torch.bfloat16,
        "bfloat16": torch.bfloat16,
    }
    try:
        return table[precision.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported precision: {precision}") from exc


def make_orbit_views(
    count: int,
    radius: float = 2.7,
    elevation_degrees: float = 22.5,
    azimuth_offset_degrees: float = 0.0,
    device: Optional[torch.device] = None,
) -> List[ViewSpec]:
    device = device or torch.device("cpu")
    views: List[ViewSpec] = []
    elevation = math.radians(elevation_degrees)
    offset = math.radians(float(azimuth_offset_degrees))
    for idx in range(count):
        azimuth = offset + 2.0 * math.pi * idx / max(count, 1)
        eye = torch.tensor(
            [
                radius * math.cos(elevation) * math.cos(azimuth),
                radius * math.sin(elevation),
                radius * math.cos(elevation) * math.sin(azimuth),
            ],
            dtype=torch.float32,
            device=device,
        )
        views.append(
            ViewSpec(
                eye=eye,
                target=torch.zeros(3, dtype=torch.float32, device=device),
                up=torch.tensor([0.0, 1.0, 0.0], dtype=torch.float32, device=device),
            )
        )
    return views


def make_lights(count: int, device: Optional[torch.device] = None) -> List[LightSpec]:
    device = device or torch.device("cpu")
    lights: List[LightSpec] = []
    for idx in range(count):
        azimuth = 2.0 * math.pi * (idx + 0.37) / max(count, 1)
        elevation = math.radians(35.0 if idx % 2 == 0 else 12.0)
        direction = torch.tensor(
            [
                math.cos(elevation) * math.cos(azimuth),
                math.sin(elevation),
                math.cos(elevation) * math.sin(azimuth),
            ],
            dtype=torch.float32,
            device=device,
        )
        color = torch.tensor(
            [1.0, 0.92 + 0.08 * (idx % 2), 0.86 + 0.06 * ((idx + 1) % 2)],
            dtype=torch.float32,
            device=device,
        )
        lights.append(LightSpec(direction=normalize(direction), color=color, intensity=1.0))
    return lights


def make_view_light_splits(
    view_counts: Mapping[str, int],
    light_counts: Mapping[str, int],
    *,
    split_seed: int = 0,
    device: Optional[torch.device] = None,
) -> ViewLightSplits:
    """Create disjoint proposal/gate/test view and light splits.

    A1 validation-leakage fix:
        proposal split is used for residual attribution and C2 candidate
        scoring, gate split is used only by C5 deployment decisions, and test
        split is used only for reported headline metrics.
    """

    device = device or torch.device("cpu")
    names = ("proposal", "gate", "test")
    v_counts = {name: max(0, int(view_counts.get(name, 0))) for name in names}
    l_counts = {name: max(0, int(light_counts.get(name, 0))) for name in names}
    if sum(v_counts.values()) <= 0:
        v_counts["proposal"] = 1
    if sum(l_counts.values()) <= 0:
        l_counts["proposal"] = 1

    total_views = sum(v_counts.values())
    total_lights = sum(l_counts.values())
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(split_seed))

    view_offset = float(torch.rand((), generator=generator).item() * 360.0)
    light_phase = int(torch.randint(0, max(total_lights, 1), (), generator=generator).item())
    all_views = make_orbit_views(total_views, azimuth_offset_degrees=view_offset, device=device)
    all_lights = make_lights(total_lights, device=device)
    if total_lights:
        all_lights = all_lights[light_phase:] + all_lights[:light_phase]

    view_order = torch.randperm(total_views, generator=generator).tolist() if total_views else []
    light_order = torch.randperm(total_lights, generator=generator).tolist() if total_lights else []

    def take(counts: dict[str, int], order: list[int], source: list) -> dict[str, tuple[list, list[int]]]:
        out: dict[str, tuple[list, list[int]]] = {}
        cursor = 0
        for name in names:
            count = int(counts[name])
            indices = [int(idx) for idx in order[cursor : cursor + count]]
            out[name] = ([source[idx] for idx in indices], indices)
            cursor += count
        return out

    view_parts = take(v_counts, view_order, all_views)
    light_parts = take(l_counts, light_order, all_lights)

    def split(name: str) -> ViewLightSplit:
        views, view_indices = view_parts[name]
        lights, light_indices = light_parts[name]
        return ViewLightSplit(views=list(views), lights=list(lights), view_indices=view_indices, light_indices=light_indices)

    return ViewLightSplits(
        proposal=split("proposal"),
        gate=split("gate"),
        test=split("test"),
        split_seed=int(split_seed),
    )


def _look_at(view: ViewSpec) -> torch.Tensor:
    eye = view.eye.to(torch.float32)
    target = view.target.to(torch.float32)
    up = view.up.to(torch.float32)
    z_axis = normalize(eye - target)
    x_axis = normalize(torch.cross(up, z_axis, dim=0))
    y_axis = torch.cross(z_axis, x_axis, dim=0)
    mat = torch.eye(4, dtype=torch.float32, device=eye.device)
    mat[0, :3] = x_axis
    mat[1, :3] = y_axis
    mat[2, :3] = z_axis
    mat[:3, 3] = -torch.stack([torch.dot(x_axis, eye), torch.dot(y_axis, eye), torch.dot(z_axis, eye)])
    return mat


def _perspective(fov_degrees: float, aspect: float, near: float, far: float, device: torch.device) -> torch.Tensor:
    f = 1.0 / math.tan(math.radians(fov_degrees) * 0.5)
    mat = torch.zeros(4, 4, dtype=torch.float32, device=device)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2.0 * far * near) / (near - far)
    mat[3, 2] = -1.0
    return mat


def _transform_points(vertices: torch.Tensor, mvp: torch.Tensor) -> torch.Tensor:
    ones = torch.ones(vertices.shape[:-1] + (1,), dtype=vertices.dtype, device=vertices.device)
    homo = torch.cat([vertices, ones], dim=-1)
    return homo @ mvp.T


def _nhwc_to_nchw(x: torch.Tensor) -> torch.Tensor:
    return x.permute(2, 0, 1).unsqueeze(0)


def _resize_nhwc(x: torch.Tensor, size: int, mode: str = "bilinear") -> torch.Tensor:
    kwargs = {"align_corners": False} if mode in {"bilinear", "bicubic"} else {}
    y = nnF.interpolate(_nhwc_to_nchw(x), size=(size, size), mode=mode, **kwargs)
    return y.squeeze(0).permute(1, 2, 0)


class DifferentiablePBRBaker:
    """B1 C1 baker with nvdiffrast first and a deterministic torch fallback."""

    def __init__(
        self,
        atlas_resolution: int = 1024,
        render_resolution: int = 256,
        precision: str = "bf16",
        gradient_checkpointing: bool = True,
        device: Optional[torch.device] = None,
    ) -> None:
        self.atlas_resolution = int(atlas_resolution)
        self.render_resolution = int(render_resolution)
        self.precision = precision
        self.precision_dtype = precision_to_dtype(precision)
        self.gradient_checkpointing = bool(gradient_checkpointing)
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._dr = None
        self._ctx = None

    def _nvdiffrast(self):
        if self._dr is False:
            return None
        if self._dr is not None:
            return self._dr
        if self.device.type != "cuda":
            self._dr = False
            return None
        try:
            import nvdiffrast.torch as dr  # type: ignore

            self._ctx = dr.RasterizeCudaContext()
            self._dr = dr
            return self._dr
        except Exception:
            self._dr = False
            return None

    def bake(self, mesh, face_values: FacePBRValues) -> PBRMaps:
        """Bake per-face PBR values into atlas maps.

        FINAL_PROPOSAL C1 equation comment:
            For channel k in {A,N,R,M_t},
            T_k(t) = sum_f w_{t,f} P_k(f) / (sum_f w_{t,f} + eps).
        In this B1 implementation, nvdiffrast rasterizes UV-space triangles and
        provides the texel-to-face coverage w_{t,f}. The fallback path uses the
        same barycentric coverage deterministically on torch tensors.
        """

        mesh = mesh.to(self.device)
        face_values = FacePBRValues(
            albedo=face_values.albedo.to(self.device, torch.float32),
            normal=face_values.normal.to(self.device, torch.float32),
            roughness=face_values.roughness.to(self.device, torch.float32),
            metallic=face_values.metallic.to(self.device, torch.float32),
        )
        dr = self._nvdiffrast()
        if dr is not None:
            return self._bake_with_nvdiffrast(mesh, face_values, dr)
        return self._bake_with_torch(mesh, face_values)

    def _bake_with_nvdiffrast(self, mesh, face_values: FacePBRValues, dr) -> PBRMaps:
        face_count = mesh.faces.shape[0]
        uv_tri = mesh.uv[mesh.face_uv].reshape(face_count * 3, 2).to(torch.float32)
        clip_xy = uv_tri * 2.0 - 1.0
        clip = torch.cat(
            [
                clip_xy,
                torch.zeros(face_count * 3, 1, dtype=torch.float32, device=self.device),
                torch.ones(face_count * 3, 1, dtype=torch.float32, device=self.device),
            ],
            dim=-1,
        ).unsqueeze(0)
        tri = torch.arange(face_count * 3, dtype=torch.int32, device=self.device).reshape(face_count, 3)
        rast, _ = dr.rasterize(self._ctx, clip, tri, resolution=[self.atlas_resolution, self.atlas_resolution])

        def interp(attr: torch.Tensor) -> torch.Tensor:
            per_vertex = attr[:, None, :].expand(face_count, 3, attr.shape[-1]).reshape(face_count * 3, attr.shape[-1])
            out, _ = dr.interpolate(per_vertex.unsqueeze(0).contiguous(), rast, tri)
            return out[0]

        albedo = interp(face_values.albedo).clamp(0.0, 1.0)
        normal = normalize(interp(face_values.normal))
        roughness = interp(face_values.roughness).clamp(0.02, 1.0)
        metallic = interp(face_values.metallic).clamp(0.0, 1.0)
        mask = rast[0, ..., 3:4] > 0
        face_ids = rast[0, ..., 3].to(torch.long) - 1
        face_ids = torch.where(mask[..., 0], face_ids, torch.full_like(face_ids, -1))
        albedo = torch.where(mask, albedo, torch.full_like(albedo, 0.5))
        normal = torch.where(mask, normal, torch.tensor([0.0, 0.0, 1.0], device=self.device).view(1, 1, 3))
        roughness = torch.where(mask, roughness, torch.full_like(roughness, 0.4))
        metallic = torch.where(mask, metallic, torch.zeros_like(metallic))
        return PBRMaps(albedo, normal, roughness, metallic, face_ids)

    def _bake_with_torch(self, mesh, face_values: FacePBRValues) -> PBRMaps:
        size = self.atlas_resolution
        albedo = torch.full((size, size, 3), 0.5, dtype=torch.float32, device=self.device)
        normal = torch.zeros((size, size, 3), dtype=torch.float32, device=self.device)
        normal[..., 2] = 1.0
        roughness = torch.full((size, size, 1), 0.4, dtype=torch.float32, device=self.device)
        metallic = torch.zeros((size, size, 1), dtype=torch.float32, device=self.device)
        face_ids = torch.full((size, size), -1, dtype=torch.long, device=self.device)
        uv_pixels = mesh.uv[mesh.face_uv].to(torch.float32) * float(size - 1)

        for face_idx in range(mesh.faces.shape[0]):
            tri = uv_pixels[face_idx]
            min_xy = torch.floor(tri.min(dim=0).values).clamp(0, size - 1).to(torch.long)
            max_xy = torch.ceil(tri.max(dim=0).values).clamp(0, size - 1).to(torch.long)
            if (max_xy < min_xy).any():
                continue
            ys = torch.arange(min_xy[1], max_xy[1] + 1, device=self.device)
            xs = torch.arange(min_xy[0], max_xy[0] + 1, device=self.device)
            if ys.numel() == 0 or xs.numel() == 0:
                continue
            grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
            p = torch.stack([grid_x.to(torch.float32), grid_y.to(torch.float32)], dim=-1)
            bary = _barycentric_2d(p, tri)
            inside = (bary >= -1.0e-5).all(dim=-1)
            if not inside.any():
                continue
            y_idx = grid_y[inside]
            x_idx = grid_x[inside]
            albedo[y_idx, x_idx] = face_values.albedo[face_idx]
            normal[y_idx, x_idx] = face_values.normal[face_idx]
            roughness[y_idx, x_idx] = face_values.roughness[face_idx]
            metallic[y_idx, x_idx] = face_values.metallic[face_idx]
            face_ids[y_idx, x_idx] = face_idx
        return PBRMaps(albedo, normalize(normal), roughness.clamp(0.02, 1.0), metallic.clamp(0.0, 1.0), face_ids)

    def render(
        self,
        mesh,
        maps: PBRMaps,
        views: Sequence[ViewSpec],
        lights: Sequence[LightSpec],
    ) -> RenderOutput:
        """Render all held-out view/light pairs with the C1 GGX renderer.

        FINAL_PROPOSAL C1 equation comment:
            I_hat_{v,l} = R_pbr(M,U,T_A,T_N,T_R,T_M; v,l),
            and B1 uses the Cartesian product V_ho x L_ho for residuals.
        """

        mesh = mesh.to(self.device)
        maps = maps.to(self.device)
        dr = self._nvdiffrast()
        images = []
        face_ids = []
        alpha = []
        for view in views:
            view = ViewSpec(view.eye.to(self.device), view.target.to(self.device), view.up.to(self.device), view.fov_degrees)
            for light in lights:
                light = LightSpec(light.direction.to(self.device), light.color.to(self.device), light.intensity)
                if dr is not None:
                    image, ids, mask = self._render_one_nvdiffrast(mesh, maps, view, light, dr)
                else:
                    image, ids, mask = self._render_one_fallback(maps, view, light)
                images.append(image.to(torch.float32))
                face_ids.append(ids)
                alpha.append(mask.to(torch.float32))
        return RenderOutput(torch.stack(images, dim=0), torch.stack(face_ids, dim=0), torch.stack(alpha, dim=0))

    def _render_one_nvdiffrast(self, mesh, maps: PBRMaps, view: ViewSpec, light: LightSpec, dr):
        face_count = mesh.faces.shape[0]
        tri_pos = mesh.vertices[mesh.faces].reshape(face_count * 3, 3).to(torch.float32)
        tri_norm = mesh.normals_per_vertex[mesh.faces].reshape(face_count * 3, 3).to(torch.float32)
        tri_uv = mesh.uv[mesh.face_uv].reshape(face_count * 3, 2).to(torch.float32)
        tri = torch.arange(face_count * 3, dtype=torch.int32, device=self.device).reshape(face_count, 3)
        view_mat = _look_at(view)
        proj_mat = _perspective(view.fov_degrees, 1.0, 0.05, 20.0, self.device)
        mvp = proj_mat @ view_mat
        clip = _transform_points(tri_pos, mvp).unsqueeze(0).contiguous()
        rast, _ = dr.rasterize(self._ctx, clip, tri, resolution=[self.render_resolution, self.render_resolution])
        pos, _ = dr.interpolate(tri_pos.unsqueeze(0).contiguous(), rast, tri)
        geom_normal, _ = dr.interpolate(tri_norm.unsqueeze(0).contiguous(), rast, tri)
        uv, _ = dr.interpolate(tri_uv.unsqueeze(0).contiguous(), rast, tri)

        def tex(x: torch.Tensor) -> torch.Tensor:
            # B1 memory comment:
            # Texture lookup is the main differentiable map access. We keep
            # numerically sensitive interpolation in fp32 for bf16 runs because
            # nvdiffrast texture kernels may not accept bf16, then cast sampled
            # values before GGX if a lower precision path is requested.
            tex_dtype = torch.float16 if self.precision_dtype == torch.float16 else torch.float32
            texel = x.to(tex_dtype).unsqueeze(0).contiguous()
            uv_in = uv.contiguous()

            def lookup(texel_arg: torch.Tensor, uv_arg: torch.Tensor) -> torch.Tensor:
                return dr.texture(texel_arg, uv_arg, filter_mode="linear")

            if self.gradient_checkpointing and (texel.requires_grad or uv_in.requires_grad):
                from torch.utils.checkpoint import checkpoint

                out = checkpoint(lookup, texel, uv_in, use_reentrant=False)
            else:
                out = lookup(texel, uv_in)
            if self.precision_dtype in (torch.float16, torch.bfloat16):
                out = out.to(self.precision_dtype)
            return out[0].to(torch.float32)

        albedo = tex(maps.albedo)
        tex_normal = tex(maps.normal)
        roughness = tex(maps.roughness)
        metallic = tex(maps.metallic)
        normal = normalize(0.65 * normalize(geom_normal[0]) + 0.35 * normalize(tex_normal))
        view_dir = normalize(view.eye.view(1, 1, 3) - pos[0])
        light_dir = light.direction.view(1, 1, 3).expand_as(view_dir)
        light_color = (light.color * light.intensity).view(1, 1, 3)
        shaded = ggx_brdf(normal, view_dir, light_dir, albedo, roughness, metallic, light_color)
        mask = rast[0, ..., 3] > 0
        image = torch.where(mask[..., None], shaded.to(torch.float32), torch.zeros_like(shaded, dtype=torch.float32))
        ids = rast[0, ..., 3].to(torch.long) - 1
        ids = torch.where(mask, ids, torch.full_like(ids, -1))
        return image, ids, mask

    def _render_one_fallback(self, maps: PBRMaps, view: ViewSpec, light: LightSpec):
        size = self.render_resolution
        albedo = _resize_nhwc(maps.albedo, size)
        normal = normalize(_resize_nhwc(maps.normal, size))
        roughness = _resize_nhwc(maps.roughness, size)
        metallic = _resize_nhwc(maps.metallic, size)
        v = normalize(view.eye).view(1, 1, 3).expand(size, size, 3)
        l = light.direction.view(1, 1, 3).expand(size, size, 3)
        color = (light.color * light.intensity).view(1, 1, 3)
        image = ggx_brdf(normal, v, l, albedo, roughness, metallic, color).to(torch.float32)
        if maps.face_ids is None:
            ids = torch.full((size, size), -1, dtype=torch.long, device=self.device)
        else:
            ids_float = nnF.interpolate(
                maps.face_ids.to(torch.float32).view(1, 1, *maps.face_ids.shape),
                size=(size, size),
                mode="nearest",
            )
            ids = ids_float[0, 0].to(torch.long)
        mask = ids >= 0
        return torch.where(mask[..., None], image, torch.zeros_like(image)), ids, mask


def _barycentric_2d(points: torch.Tensor, tri: torch.Tensor) -> torch.Tensor:
    a, b, c = tri[0], tri[1], tri[2]
    v0 = b - a
    v1 = c - a
    v2 = points - a
    denom = v0[0] * v1[1] - v1[0] * v0[1]
    if torch.abs(denom) < 1.0e-12:
        return torch.full(points.shape[:-1] + (3,), -1.0, dtype=points.dtype, device=points.device)
    inv = 1.0 / denom
    v = (v2[..., 0] * v1[1] - v1[0] * v2[..., 1]) * inv
    w = (v0[0] * v2[..., 1] - v2[..., 0] * v0[1]) * inv
    u = 1.0 - v - w
    return torch.stack([u, v, w], dim=-1)


def create_synthetic_oracle_maps(
    resolution: int,
    seed: int,
    device: Optional[torch.device] = None,
    region_count: int = 12,
) -> PBRMaps:
    """Create procedural oracle PBR maps for B1 when no real PBR exists.

    The oracle map is deterministic under ``utils.seed.set_global_seed`` and
    this local generator seed. It gives C1 a known ``T_k^*`` for
    ``lambda_pbr * sum_k omega_k ||T_k - T_k^*||_1`` sanity metrics.
    """

    device = device or torch.device("cpu")
    gen = torch.Generator(device="cpu")
    gen.manual_seed(int(seed))
    coords_1d = torch.linspace(0.0, 1.0, resolution, dtype=torch.float32)
    v, u = torch.meshgrid(coords_1d, coords_1d, indexing="ij")
    uv = torch.stack([u, v], dim=-1)
    centers = torch.rand(region_count, 2, generator=gen)
    palette = torch.rand(region_count, 3, generator=gen) * 0.65 + 0.25
    rough_table = torch.rand(region_count, 1, generator=gen) * 0.55 + 0.22
    metal_table = (torch.rand(region_count, 1, generator=gen) > 0.82).to(torch.float32) * 0.55
    flat_uv = uv.reshape(-1, 2)
    labels = torch.cdist(flat_uv, centers).argmin(dim=1).reshape(resolution, resolution)
    stripes = 0.08 * torch.sin(2.0 * math.pi * (9.0 * u + 5.0 * v))[..., None]
    albedo = (palette[labels] + stripes).clamp(0.0, 1.0)
    height = 0.035 * torch.sin(2.0 * math.pi * (13.0 * u + 3.0 * v)) + 0.025 * torch.cos(
        2.0 * math.pi * (4.0 * u - 11.0 * v)
    )
    dh_dv, dh_du = torch.gradient(height, spacing=(coords_1d, coords_1d))
    normal = normalize(torch.stack([-dh_du, -dh_dv, torch.ones_like(height)], dim=-1))
    roughness = (rough_table[labels] + 0.05 * torch.sin(2.0 * math.pi * 17.0 * u)[..., None]).clamp(0.04, 1.0)
    metallic = metal_table[labels].clamp(0.0, 1.0)
    return PBRMaps(
        albedo=albedo.to(device),
        normal=normal.to(device),
        roughness=roughness.to(device),
        metallic=metallic.to(device),
    )


def _sample_nhwc(map_tensor: torch.Tensor, uv: torch.Tensor) -> torch.Tensor:
    tex = map_tensor.permute(2, 0, 1).unsqueeze(0)
    grid = uv.clamp(0.0, 1.0).view(1, -1, 1, 2) * 2.0 - 1.0
    sampled = nnF.grid_sample(tex, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return sampled.squeeze(0).squeeze(-1).T


def sample_face_pbr_from_maps(mesh, oracle_maps: PBRMaps) -> FacePBRValues:
    """Sample face-center oracle values used as ``P_k(f)`` in C1 bake."""

    uv_centers = mesh.uv[mesh.face_uv].mean(dim=1).to(oracle_maps.albedo.device)
    albedo = _sample_nhwc(oracle_maps.albedo, uv_centers).clamp(0.0, 1.0)
    normal = normalize(_sample_nhwc(oracle_maps.normal, uv_centers))
    roughness = _sample_nhwc(oracle_maps.roughness, uv_centers).mean(dim=-1, keepdim=True).clamp(0.04, 1.0)
    metallic = _sample_nhwc(oracle_maps.metallic, uv_centers).mean(dim=-1, keepdim=True).clamp(0.0, 1.0)
    return FacePBRValues(albedo=albedo, normal=normal, roughness=roughness, metallic=metallic)
