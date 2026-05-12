"""GGX microfacet BRDF used by the B1 oracle-controlled baker.

The implementation follows FINAL_PROPOSAL C1's renderer
``I_hat = R_pbr(M, U, T_A, T_N, T_R, T_M; v, l)`` and keeps all sensitive
BRDF math in fp32 before casting the radiance back to the requested tensor
precision.
"""

from __future__ import annotations

import math
from typing import Optional

import torch

EPS = 1.0e-6


def normalize(x: torch.Tensor, eps: float = EPS) -> torch.Tensor:
    """Normalize vectors with an epsilon guard."""

    return x / x.norm(dim=-1, keepdim=True).clamp_min(eps)


def _dot(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return (a * b).sum(dim=-1, keepdim=True)


def _target_dtype(*values: torch.Tensor) -> torch.dtype:
    for value in values:
        if value.dtype in (torch.float16, torch.bfloat16):
            return value.dtype
    return torch.float32


def schlick_fresnel(v_dot_h: torch.Tensor, f0: torch.Tensor) -> torch.Tensor:
    """Schlick Fresnel.

    FINAL_PROPOSAL C1 GGX comment:
        F(v,h) = F0 + (1 - F0) * (1 - max(v dot h, 0))^5.
    """

    one_minus = (1.0 - v_dot_h.clamp(0.0, 1.0)).pow(5.0)
    return f0 + (1.0 - f0) * one_minus


def ggx_distribution(n_dot_h: torch.Tensor, roughness: torch.Tensor) -> torch.Tensor:
    """Trowbridge-Reitz / GGX normal distribution function.

    FINAL_PROPOSAL C1 GGX comment:
        alpha = max(roughness^2, 1e-4)
        D(h) = alpha^2 / (pi * ((n dot h)^2 * (alpha^2 - 1) + 1)^2).
    """

    alpha = roughness.pow(2.0).clamp_min(1.0e-4)
    alpha2 = alpha.pow(2.0)
    denom = n_dot_h.pow(2.0) * (alpha2 - 1.0) + 1.0
    return alpha2 / (math.pi * denom.pow(2.0).clamp_min(EPS))


def smith_joint_geometry(
    n_dot_v: torch.Tensor, n_dot_l: torch.Tensor, roughness: torch.Tensor
) -> torch.Tensor:
    """Height-correlated Smith joint masking-shadowing term.

    FINAL_PROPOSAL C1 GGX comment:
        G2(v,l,h) is Smith joint geometry with epsilon-guarded
        max(n dot v, eps) and max(n dot l, eps). This form is the common
        correlated GGX approximation:
        G2 = 2 Nv Nl / (Nv * sqrt(a^2 + (1-a^2) Nl^2)
                       + Nl * sqrt(a^2 + (1-a^2) Nv^2)).
    """

    alpha = roughness.pow(2.0).clamp_min(1.0e-4)
    alpha2 = alpha.pow(2.0)
    lambda_v = n_dot_l * torch.sqrt(alpha2 + (1.0 - alpha2) * n_dot_v.pow(2.0))
    lambda_l = n_dot_v * torch.sqrt(alpha2 + (1.0 - alpha2) * n_dot_l.pow(2.0))
    return (2.0 * n_dot_v * n_dot_l) / (lambda_v + lambda_l).clamp_min(EPS)


def ggx_brdf(
    n: torch.Tensor,
    v: torch.Tensor,
    l: torch.Tensor,
    albedo: torch.Tensor,
    roughness: torch.Tensor,
    metallic: torch.Tensor,
    light_color: Optional[torch.Tensor] = None,
    eps: float = EPS,
) -> torch.Tensor:
    """Evaluate batched GGX radiance for PBR atlas texels or pixels.

    Args:
        n: Surface normal, ``[..., 3]``.
        v: View direction from surface to camera, ``[..., 3]``.
        l: Light direction from surface to light, ``[..., 3]``.
        albedo: Base color ``A``, ``[..., 3]``.
        roughness: Roughness channel ``R``, ``[..., 1]`` or broadcastable.
        metallic: Metallic channel ``M_t``, ``[..., 1]`` or broadcastable.
        light_color: Optional radiance/intensity color, broadcastable to
            ``[..., 3]``.

    Returns:
        Per-pixel outgoing radiance ``[..., 3]``.
    """

    out_dtype = _target_dtype(n, v, l, albedo, roughness, metallic)
    n = normalize(n.to(torch.float32), eps)
    v = normalize(v.to(torch.float32), eps)
    l = normalize(l.to(torch.float32), eps)
    albedo = albedo.to(torch.float32).clamp(0.0, 1.0)
    roughness = roughness.to(torch.float32).clamp(0.0, 1.0)
    metallic = metallic.to(torch.float32).clamp(0.0, 1.0)
    if roughness.shape[-1] != 1:
        roughness = roughness.mean(dim=-1, keepdim=True)
    if metallic.shape[-1] != 1:
        metallic = metallic.mean(dim=-1, keepdim=True)

    h = normalize(v + l, eps)
    n_dot_v = _dot(n, v).clamp_min(eps)
    n_dot_l = _dot(n, l).clamp_min(eps)
    n_dot_h = _dot(n, h).clamp_min(eps)
    v_dot_h = _dot(v, h).clamp_min(eps)

    # FINAL_PROPOSAL C1 GGX comment:
    # F0 = 0.04 for dielectrics and A for conductors, blended by M_t.
    f0 = torch.full_like(albedo, 0.04) * (1.0 - metallic) + albedo * metallic
    f = schlick_fresnel(v_dot_h, f0)
    d = ggx_distribution(n_dot_h, roughness)
    g = smith_joint_geometry(n_dot_v, n_dot_l, roughness)

    # FINAL_PROPOSAL C1 GGX comment:
    # f_spec = D(h) F(v,h) G2(v,l,h) / (4 max(n dot v, eps) max(n dot l, eps)).
    specular = (d * f * g) / (4.0 * n_dot_v * n_dot_l).clamp_min(eps)

    # Energy-conserving diffuse lobe:
    # f_diff = (1 - F) (1 - M_t) A / pi.
    diffuse = (1.0 - f) * (1.0 - metallic) * albedo / math.pi
    radiance = (diffuse + specular) * n_dot_l

    if light_color is not None:
        radiance = radiance * light_color.to(torch.float32)
    return radiance.clamp_min(0.0).to(out_dtype)

