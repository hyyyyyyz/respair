# B1 Sanity / Oracle Baker Pilot

This is the minimal W1 B1 code path only. It implements C1
Oracle-Controlled Differentiable PBR Baker from `refine-logs/FINAL_PROPOSAL.md`
and does not implement B2-B9, model training, chart repair, or atlas
optimization.

## Quickstart on server2

```bash
ssh server2
source ~/miniconda3/bin/activate /data/conda_envs/dip1_pbr
cd ~/dip_1_ws
pip install -e .
python scripts/setup_data_b1.py
CUDA_VISIBLE_DEVICES=1 python scripts/run_B1.py --asset bunny
CUDA_VISIBLE_DEVICES=1 python scripts/determinism_check.py --asset bunny
```

Expected output:

```text
/data/dip_1_ws/runs/B1_sanity/<run_id>/
  metrics.json
  residual_atlas.npz
  residual_atlas.png
  summary.md
```

## C1 Equation Alignment

- `pbr_atlas/baker/baker.py` implements
  `T_k(t)=sum_f w_{t,f}P_k(f)/(sum_f w_{t,f}+eps)` and
  `I_hat=R_pbr(M,U,T_A,T_N,T_R,T_M;v,l)`.
- `pbr_atlas/baker/ggx.py` implements GGX `D`, Schlick `F`, Smith `G2`,
  diffuse/specular radiance, and epsilon guards.
- `pbr_atlas/baker/residual.py` implements
  `e_f`, `E_c`, seam residual `S_e`, and mip leakage `G_l`.

All RNG should go through `pbr_atlas.utils.seed.set_global_seed`.

