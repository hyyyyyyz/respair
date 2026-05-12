=== PER-ITEM DECISIONS ===
R1: <go|adjust to "X"|reject>
R2: ...
...
R9: ...

=== KEY ADDITIONS YOU RECOMMEND I ADD ===
- ...

=== W1 EXECUTION ORDER (specific, runnable) ===
Day 1 (today, 5/3): ...
Day 2: ...
...
Day 7: ...

=== EXACT FIRST 3 SHELL COMMANDS / SCRIPTS I SHOULD RUN NOW ===
1. ...
2. ...
3. ...

=== ABORT CRITERIA ===
If by EOD W1 day X we haven't achieved Y, switch to fallback Z.
```

Be terse and concrete. I need decisions, not analysis. The analysis was the previous round.
codex
I’ll verify the DiLiGenT-MV protocol and whether there is a stronger current UV baseline before committing the go/adjust calls.
web search: 
web search: DiLiGenT-MV dataset protocol 5 objects 20 views 96 lights masks calibrated lights color management
web search: 
web search: https://sites.google.com/site/photometricstereodata/mv
codex
I’m checking the repo layout so the first commands are actually runnable in this workspace, not placeholders.
exec
/bin/zsh -lc pwd in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
/Users/jacksonhuang/project/dip_1_ws

exec
/bin/zsh -lc "find . -maxdepth 2 -type d | sort | sed -n '1,120p'" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
.
./.aris
./.aris/meta
./.aris/traces
./.claude
./3rdparty
./3rdparty/Fantasia3D
./3rdparty/GET3D
./3rdparty/TRELLIS
./3rdparty/threestudio
./LaTeX2e_Proceedings_Templates
./configs
./configs/B4_ablations
./configs/B5
./datasets
./datasets/pg_real_meshes_local
./egPublStyle-PG2026
./figures
./figures/B6
./figures/main
./figures/qualitative_residual_chain
./figures/scripts
./figures/visual_evidence
./idea-stage
./idea-stage-prcv-archived-2026-04-27
./idea-stage-prcv-archived-2026-04-27/lit-raw
./idea-stage-prcv-archived-2026-04-27/novelty
./idea-stage-prcv-archived-2026-04-27/novelty-raw
./idea-stage-prcv-archived-2026-04-27/review
./idea-stage/backup-novelty
./idea-stage/lit-raw
./idea-stage/novelty
./idea-stage/novelty-raw
./idea-stage/pivoted
./idea-stage/review
./paper
./paper-backup-20260429_161024
./paper-backup-20260429_161024/figures
./paper-backup-20260429_161024/sections
./paper-backup-20260429_161024/tables
./paper-plan
./paper/egPublStyle-PG2026
./paper/figures
./paper/sections
./paper/tables
./pbr_atlas
./pbr_atlas/__pycache__
./pbr_atlas/ablations
./pbr_atlas/baker
./pbr_atlas/baselines
./pbr_atlas/data
./pbr_atlas/eval
./pbr_atlas/method
./pbr_atlas/utils
./refine-logs
./refine-logs-prcv-archived
./research-wiki
./research-wiki/claims
./research-wiki/experiments
./research-wiki/graph
./research-wiki/ideas
./research-wiki/papers
./runs
./runs/A1_split
./runs/B1_sanity
./runs/B2_baseline
./runs/B3_main
./runs/B4_ablation
./runs/B5_matched
./runs/B7_robustness
./runs/B7_transfer
./runs/PG_enh1_data_test
./runs/PG_enh1_real_generated
./runs/PG_enh1_real_v2
./runs/PG_enh2_purity
./runs/PG_enh3_robust
./scripts
./scripts/__pycache__

exec
/bin/zsh -lc "rg --files | sed -n '1,160p'" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
CLAUDE.md
runs/B2_baseline/bunny_visibility_param_seed42/residual_atlas.png
runs/B2_baseline/bunny_visibility_param_seed42/residual_atlas.npz
runs/B2_baseline/bunny_visibility_param_seed42/atlas.npz
runs/B2_baseline/bunny_visibility_param_seed42/summary.md
runs/B2_baseline/bunny_visibility_param_seed42/metrics.json
runs/B2_baseline/objaverse_otuvgs_seed42/residual_atlas.png
runs/B2_baseline/objaverse_otuvgs_seed42/residual_atlas.npz
runs/B2_baseline/objaverse_otuvgs_seed42/atlas.npz
runs/B2_baseline/objaverse_otuvgs_seed42/summary.md
runs/B2_baseline/objaverse_otuvgs_seed42/metrics.json
runs/B2_baseline/B2_FAILURE_TABLE.md
runs/B2_baseline/MATCHED_TABLE.md
runs/B2_baseline/B2_RESULTS.md
runs/B2_baseline/bunny_parapoint_seed42/atlas.npz
runs/B2_baseline/bunny_parapoint_seed42/summary.md
runs/B2_baseline/bunny_parapoint_seed42/metrics.json
runs/B2_baseline/spot_otuvgs_seed42/residual_atlas.png
runs/B2_baseline/spot_otuvgs_seed42/residual_atlas.npz
runs/B2_baseline/spot_otuvgs_seed42/atlas.npz
runs/B2_baseline/spot_otuvgs_seed42/summary.md
runs/B2_baseline/spot_otuvgs_seed42/metrics.json
runs/PG_enh2_purity/PURITY_TABLE.md
runs/PG_enh2_purity/purity_metrics.json
runs/B2_baseline/objaverse_flatten_anything_seed42/atlas.npz
runs/B2_baseline/objaverse_flatten_anything_seed42/summary.md
runs/B2_baseline/objaverse_flatten_anything_seed42/metrics.json
runs/B2_baseline/spot_blender_uv_seed42/residual_atlas.png
runs/B2_baseline/spot_blender_uv_seed42/residual_atlas.npz
runs/B2_baseline/spot_blender_uv_seed42/atlas.npz
runs/B2_baseline/spot_blender_uv_seed42/summary.md
runs/B2_baseline/objaverse_parapoint_seed42/atlas.npz
runs/B2_baseline/spot_blender_uv_seed42/metrics.json
runs/B2_baseline/objaverse_partuv_seed42/residual_atlas.png
runs/B2_baseline/objaverse_parapoint_seed42/summary.md
runs/B2_baseline/objaverse_partuv_seed42/residual_atlas.npz
runs/B2_baseline/objaverse_parapoint_seed42/metrics.json
runs/B2_baseline/objaverse_partuv_seed42/atlas.npz
runs/B2_baseline/objaverse_partuv_seed42/summary.md
runs/B2_baseline/objaverse_partuv_seed42/metrics.json
setup.py
texput.log
runs/B2_baseline/objaverse_visibility_param_seed42/residual_atlas.png
runs/B2_baseline/objaverse_visibility_param_seed42/residual_atlas.npz
runs/B2_baseline/objaverse_visibility_param_seed42/atlas.npz
runs/B2_baseline/objaverse_visibility_param_seed42/summary.md
runs/B2_baseline/objaverse_visibility_param_seed42/metrics.json
runs/B2_baseline/B2_MATCHED_TABLE.md
runs/B2_baseline/failure_records.json
runs/B2_baseline/objaverse_xatlas_classical_seed42/residual_atlas.png
runs/B2_baseline/objaverse_xatlas_classical_seed42/residual_atlas.npz
runs/B2_baseline/objaverse_xatlas_classical_seed42/atlas.npz
runs/B2_baseline/objaverse_xatlas_classical_seed42/summary.md
runs/B2_baseline/objaverse_xatlas_classical_seed42/metrics.json
figures/main/fig2_architecture.mmd
figures/main/fig6_robustness.png
figures/main/fig6_robustness.pdf
figures/main/fig4_ablation.pdf
figures/main/fig5_matched.pdf
figures/main/fig4_ablation.png
figures/main/fig5_matched.png
figures/main/latex_includes.tex
figures/main/fig2_architecture.png
figures/main/fig2_architecture.pdf
figures/main/fig3_comparison.pdf
figures/main/fig3_comparison.png
runs/B2_baseline/spot_partuv_seed42/residual_atlas.png
runs/B2_baseline/spot_partuv_seed42/residual_atlas.npz
runs/B2_baseline/spot_partuv_seed42/atlas.npz
runs/B2_baseline/spot_partuv_seed42/summary.md
runs/B2_baseline/spot_partuv_seed42/metrics.json
runs/B2_baseline/spot_parapoint_seed42/atlas.npz
runs/B2_baseline/spot_parapoint_seed42/summary.md
runs/B2_baseline/spot_parapoint_seed42/metrics.json
runs/B2_baseline/bunny_partuv_seed42/residual_atlas.png
runs/B2_baseline/bunny_partuv_seed42/residual_atlas.npz
runs/B2_baseline/bunny_partuv_seed42/atlas.npz
runs/B2_baseline/bunny_partuv_seed42/summary.md
runs/B2_baseline/bunny_partuv_seed42/metrics.json
runs/B2_baseline/spot_flatten_anything_seed42/atlas.npz
runs/B2_baseline/spot_flatten_anything_seed42/summary.md
runs/B2_baseline/spot_flatten_anything_seed42/metrics.json
paper-backup-20260429_161024/tables/table1_main.tex
paper-backup-20260429_161024/tables/table5_robustness.tex
paper-backup-20260429_161024/tables/table3_matched.tex
paper-backup-20260429_161024/tables/table2_ablation.tex
paper-backup-20260429_161024/tables/table4_transfer.tex
runs/B2_baseline/spot_xatlas_classical_seed42/residual_atlas.png
runs/B2_baseline/spot_xatlas_classical_seed42/residual_atlas.npz
runs/B2_baseline/spot_xatlas_classical_seed42/atlas.npz
runs/B2_baseline/spot_xatlas_classical_seed42/summary.md
runs/B2_baseline/spot_xatlas_classical_seed42/metrics.json
runs/B2_baseline/bunny_blender_uv_seed42/residual_atlas.png
runs/B2_baseline/bunny_blender_uv_seed42/residual_atlas.npz
runs/B2_baseline/bunny_blender_uv_seed42/atlas.npz
runs/B2_baseline/bunny_blender_uv_seed42/summary.md
runs/B2_baseline/bunny_blender_uv_seed42/metrics.json
research-wiki/query_pack.md
research-wiki/gap_map.md
research-wiki/ideas/I-D2-001.md
research-wiki/ideas/I-A2-002.md
research-wiki/ideas/I-D2-004.md
research-wiki/ideas/I-A2-003.md
research-wiki/ideas/I-A5-001.md
research-wiki/ideas/I-A4-002.md
research-wiki/ideas/I-D3-003.md
research-wiki/ideas/I-D1-002.md
research-wiki/ideas/I-A1-001.md
research-wiki/ideas/I-A3-001.md
research-wiki/ideas/I-A4-003.md
research-wiki/ideas/I-D3-002.md
research-wiki/ideas/I-D1-003.md
research-wiki/ideas/I-A3-002.md
research-wiki/ideas/I-A1-003.md
research-wiki/ideas/I-D1-004.md
research-wiki/ideas/I-D3-001.md
research-wiki/ideas/I-A4-001.md
research-wiki/ideas/I-D1-001.md
research-wiki/ideas/I-A3-003.md
research-wiki/ideas/I-A1-002.md
research-wiki/ideas/I-A3-001-p.md
research-wiki/ideas/I-D3-004.md
research-wiki/ideas/I-D2-003.md
research-wiki/ideas/I-A5-002.md
research-wiki/ideas/I-D2-002.md
research-wiki/ideas/I-A5-003.md
research-wiki/ideas/I-A2-001.md
research-wiki/index.md
research-wiki/log.md
research-wiki/graph/edges.jsonl
research-wiki/experiments/B4-a8-unconstrained.md
research-wiki/experiments/B4-a2-rgb-only.md
research-wiki/experiments/B3-bunny-xatlas.md
research-wiki/experiments/B3-bunny-partuv.md
research-wiki/experiments/B4-a3-no-c2-spot.md
research-wiki/experiments/B4-a10-13-matched-controls.md
research-wiki/experiments/B4-a4-uniform-spot.md
research-wiki/experiments/B3-spot-xatlas.md
research-wiki/experiments/B3-objaverse-all.md
research-wiki/experiments/B4-a14-resolution.md
research-wiki/experiments/B7-robustness.md
research-wiki/experiments/B7-transfer-grid.md
research-wiki/experiments/B3-spot-partuv-ours-seed42.md
research-wiki/experiments/B3-spot-partuv-v2.md
research-wiki/experiments/B5-matched-control-grid.md
research-wiki/papers/kim2026_ot_uvgs_revisiting_uv.md
research-wiki/papers/gomez2026_blobs_spokes_high_fidelity.md
research-wiki/papers/elangovan2026_quantifying_explanation_consistency_c.md
research-wiki/papers/zhao2025_flexpara_flexible_neural_surface.md
research-wiki/papers/dai2026_surfelsplat_learning_efficient_generalizable.md
research-wiki/papers/moretti2026_adaptive_slicing_assisted_hyper.md
research-wiki/papers/li2026_improving_layout_representation_learning.md
research-wiki/papers/hamdi2026_tableseq_unified_generation_structure.md
research-wiki/papers/kittler2026_protoclip_prototype_aligned_latent.md
research-wiki/papers/li2026_uhr_detr_efficient_end.md
research-wiki/papers/zheng2026_ssd_gs_scattering_shadow.md
research-wiki/papers/wang2025_partuv_part_based_uv.md
research-wiki/papers/bao2026_ramen_robust_test_time.md
research-wiki/papers/watanabe2026_neural_gabor_splatting_enhanced.md
research-wiki/papers/liu2026_parser_oriented_structural_refinement.md

codex
The repo already has experiment, table, and figure structure, so the W1 plan can anchor on existing scripts rather than inventing a new pipeline.
exec
/bin/zsh -lc "rg --files scripts pbr_atlas configs paper/tables paper/sections figures/scripts | sed -n '1,220p'" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
figures/scripts/gen_fig5_matched.py
figures/scripts/gen_latex_includes.py
figures/scripts/gen_tables.py
figures/scripts/gen_fig2_architecture.py
figures/scripts/paper_plot_style.py
figures/scripts/gen_fig6_robustness.py
scripts/render_B6_figures.py
scripts/run_PG_enh3_robust.py
scripts/setup_data_b1.py
scripts/run_B5.py
scripts/determinism_check.py
scripts/run_B1.py
scripts/collect_B5_table.py
scripts/collect_B4_table.py
scripts/run_B4_ablation.py
scripts/run_PG_enh1_real_generated.py
scripts/collect_B2_table.py
scripts/collect_B3_table.py
scripts/reproduce_baselines.sh
scripts/ingest_user_provided_mesh.py
scripts/collect_B7_table.py
scripts/run_A_structural_fix_cases.sh
figures/scripts/__pycache__/paper_plot_style.cpython-313.pyc
figures/scripts/gen_fig3_comparison.py
figures/scripts/gen_fig4_ablation.py
pbr_atlas/method/chart_repair.py
pbr_atlas/method/texel_alloc.py
configs/B2_matched.yaml
scripts/__pycache__/collect_B4_table.cpython-313.pyc
scripts/__pycache__/run_B7_robustness.cpython-313.pyc
scripts/__pycache__/determinism_check.cpython-313.pyc
scripts/__pycache__/run_B5.cpython-313.pyc
scripts/__pycache__/run_B2.cpython-313.pyc
scripts/__pycache__/run_PG_enh1_real_generated.cpython-313.pyc
scripts/__pycache__/run_PG_enh3_robust.cpython-313.pyc
scripts/__pycache__/setup_data_b7.cpython-313.pyc
scripts/__pycache__/run_B3.cpython-313.pyc
scripts/__pycache__/run_PG_enh2_v2_curvature.cpython-313.pyc
scripts/__pycache__/run_PG_enh2_purity.cpython-313.pyc
scripts/__pycache__/setup_data_b1.cpython-313.pyc
scripts/__pycache__/collect_B2_table.cpython-313.pyc
scripts/__pycache__/run_B1.cpython-313.pyc
scripts/__pycache__/run_B4_ablation.cpython-313.pyc
scripts/__pycache__/collect_B5_table.cpython-313.pyc
scripts/__pycache__/collect_B7_table.cpython-313.pyc
scripts/__pycache__/run_B7_transfer.cpython-313.pyc
scripts/__pycache__/collect_B3_table.cpython-313.pyc
scripts/__pycache__/render_B6_figures.cpython-313.pyc
scripts/fetch_real_meshes_C.py
scripts/run_B7_transfer.py
scripts/render_visual_figure.py
scripts/run_B4_grid.sh
scripts/run_PG_enh2_purity.py
scripts/run_PG_enh2_v2_curvature.py
scripts/run_B2.py
scripts/run_B7_robustness.py
scripts/setup_data_b7.py
scripts/run_B3.py
scripts/digest_a1_split.py
pbr_atlas/method/__pycache__/__init__.cpython-313.pyc
pbr_atlas/method/__pycache__/texel_alloc.cpython-313.pyc
pbr_atlas/method/__pycache__/seam_coupling.cpython-313.pyc
pbr_atlas/method/__pycache__/signals.cpython-313.pyc
pbr_atlas/method/__pycache__/chart_repair.cpython-313.pyc
pbr_atlas/method/__init__.py
pbr_atlas/method/seam_coupling.py
pbr_atlas/method/signals.py
pbr_atlas/utils/seed.py
pbr_atlas/utils/visualization.py
pbr_atlas/data/mesh_loader.py
pbr_atlas/data/asset_registry.py
pbr_atlas/data/oracle_pbr.py
pbr_atlas/utils/__pycache__/__init__.cpython-313.pyc
pbr_atlas/utils/__pycache__/figure.cpython-313.pyc
pbr_atlas/utils/__pycache__/seed.cpython-313.pyc
pbr_atlas/utils/__pycache__/visualization.cpython-313.pyc
pbr_atlas/utils/__pycache__/io.cpython-313.pyc
pbr_atlas/utils/__init__.py
pbr_atlas/utils/figure.py
pbr_atlas/utils/io.py
pbr_atlas/__init__.py
configs/B7_transfer.yaml
configs/B3_main.yaml
paper/tables/table4_transfer.tex
configs/pg_real_meshes_A.json
configs/B7_robustness.yaml
configs/B1_sanity.yaml
pbr_atlas/ablations/matched_controls.py
pbr_atlas/ablations/a18_allocator_term_ablation.py
pbr_atlas/ablations/a15_brdf_model_sweep.py
pbr_atlas/ablations/a4_uniform_alloc.py
pbr_atlas/ablations/a17_edit_budget_sweep.py
pbr_atlas/ablations/sweeps.py
pbr_atlas/ablations/a16_light_type_sweep.py
pbr_atlas/ablations/a12_matched_padding.py
pbr_atlas/ablations/common.py
pbr_atlas/ablations/a8_global_reunwrap.py
pbr_atlas/ablations/a7_oracle_only_calib.py
pbr_atlas/data/__pycache__/__init__.cpython-313.pyc
pbr_atlas/data/__pycache__/oracle_pbr.cpython-313.pyc
pbr_atlas/data/__pycache__/mesh_loader.cpython-313.pyc
pbr_atlas/data/__pycache__/generated_mesh_loader.cpython-313.pyc
pbr_atlas/data/__pycache__/asset_registry.cpython-313.pyc
pbr_atlas/data/__init__.py
pbr_atlas/data/generated_mesh_loader.py
pbr_atlas/ablations/a9_per_channel_uv.py
pbr_atlas/ablations/a5_rgb_seam_loss.py
pbr_atlas/ablations/a10_matched_utilization.py
pbr_atlas/ablations/a11_matched_distortion.py
pbr_atlas/ablations/a6_no_holdout_gate.py
pbr_atlas/ablations/a2_rgb_only_baker.py
paper/tables/table10_curvature.tex
paper/tables/table1_main.tex
paper/tables/table5_robustness.tex
paper/tables/table7_robust_extended.tex
paper/tables/table9_real_mesh.tex
paper/tables/table12_runtime.tex
paper/tables/table11_a1_split.tex
paper/tables/table7_purity.tex
paper/tables/table3_matched.tex
paper/tables/table2_ablation.tex
paper/tables/table8_extended_transfer.tex
configs/B5/B5_1.yaml
configs/B5/B5_3.yaml
configs/B5/B5_2.yaml
configs/B5/B5_5.yaml
configs/B5/B5_4.yaml
pbr_atlas/ablations/a3_no_c2_repair.py
pbr_atlas/ablations/__init__.py
pbr_atlas/ablations/a14_texture_size_sweep.py
pbr_atlas/ablations/a13_matched_chart_count.py
pbr_atlas/ablations/b5_strict_matched.py
pbr_atlas/ablations/a1_distortion_only.py
configs/B4_ablations/A12.yaml
configs/B4_ablations/A13.yaml
configs/B4_ablations/A8.yaml
configs/B4_ablations/A4.yaml
configs/B4_ablations/A14.yaml
configs/B4_ablations/A18.yaml
configs/B4_ablations/A10.yaml
configs/B4_ablations/A3.yaml
configs/B4_ablations/A11.yaml
configs/B4_ablations/A2.yaml
configs/B4_ablations/A6.yaml
configs/B4_ablations/A15.yaml
configs/B4_ablations/A5.yaml
configs/B4_ablations/A9.yaml
configs/B4_ablations/A17.yaml
configs/B4_ablations/A7.yaml
configs/B4_ablations/A1.yaml
pbr_atlas/ablations/__pycache__/matched_controls.cpython-313.pyc
configs/B4_ablations/A16.yaml
pbr_atlas/baselines/xatlas_classical.py
pbr_atlas/baselines/flatten_anything.py
pbr_atlas/baker/__init__.py
pbr_atlas/baker/baker.py
pbr_atlas/baker/ggx.py
pbr_atlas/ablations/__pycache__/a9_per_channel_uv.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a11_matched_distortion.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a1_distortion_only.cpython-313.pyc
pbr_atlas/baker/residual.py
pbr_atlas/baselines/otuvgs.py
pbr_atlas/baselines/visibility_param.py
pbr_atlas/baselines/flexpara.py
pbr_atlas/baselines/partuv.py
pbr_atlas/baselines/matched_protocol.py
pbr_atlas/baselines/base.py
pbr_atlas/ablations/__pycache__/a13_matched_chart_count.cpython-313.pyc
pbr_atlas/baselines/baseline_failure_table.py
pbr_atlas/baselines/blender_uv.py
pbr_atlas/baselines/matched_oracle.py
pbr_atlas/ablations/__pycache__/a5_rgb_seam_loss.cpython-313.pyc
pbr_atlas/baselines/parapoint.py
pbr_atlas/baselines/__init__.py
pbr_atlas/ablations/__pycache__/a4_uniform_alloc.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a15_brdf_model_sweep.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a10_matched_utilization.cpython-313.pyc
pbr_atlas/ablations/__pycache__/__init__.cpython-313.pyc
pbr_atlas/ablations/__pycache__/sweeps.cpython-313.pyc
pbr_atlas/ablations/__pycache__/b5_strict_matched.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a8_global_reunwrap.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a2_rgb_only_baker.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a14_texture_size_sweep.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a16_light_type_sweep.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a3_no_c2_repair.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a12_matched_padding.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a17_edit_budget_sweep.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a7_oracle_only_calib.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a18_allocator_term_ablation.cpython-313.pyc
pbr_atlas/ablations/__pycache__/common.cpython-313.pyc
pbr_atlas/ablations/__pycache__/a6_no_holdout_gate.cpython-313.pyc
pbr_atlas/eval/__init__.py
pbr_atlas/eval/metrics.py
pbr_atlas/eval/chart_curvature.py
pbr_atlas/eval/residual_attribution.py
pbr_atlas/eval/chart_purity.py
pbr_atlas/baker/__pycache__/__init__.cpython-313.pyc
pbr_atlas/baker/__pycache__/residual.cpython-313.pyc
pbr_atlas/baker/__pycache__/ggx.cpython-313.pyc
pbr_atlas/baker/__pycache__/baker.cpython-313.pyc
pbr_atlas/__pycache__/__init__.cpython-313.pyc
pbr_atlas/eval/__pycache__/residual_attribution.cpython-313.pyc
pbr_atlas/eval/__pycache__/__init__.cpython-313.pyc
pbr_atlas/eval/__pycache__/metrics.cpython-313.pyc
pbr_atlas/eval/__pycache__/chart_purity.cpython-313.pyc
pbr_atlas/eval/__pycache__/chart_curvature.cpython-313.pyc
pbr_atlas/baselines/__pycache__/matched_protocol.cpython-313.pyc
pbr_atlas/baselines/__pycache__/__init__.cpython-313.pyc
pbr_atlas/baselines/__pycache__/matched_oracle.cpython-313.pyc
pbr_atlas/baselines/__pycache__/otuvgs.cpython-313.pyc
pbr_atlas/baselines/__pycache__/visibility_param.cpython-313.pyc
pbr_atlas/baselines/__pycache__/flexpara.cpython-313.pyc
pbr_atlas/baselines/__pycache__/baseline_failure_table.cpython-313.pyc
pbr_atlas/baselines/__pycache__/parapoint.cpython-313.pyc
pbr_atlas/baselines/__pycache__/base.cpython-313.pyc
pbr_atlas/baselines/__pycache__/blender_uv.cpython-313.pyc
pbr_atlas/baselines/__pycache__/partuv.cpython-313.pyc
pbr_atlas/baselines/__pycache__/flatten_anything.cpython-313.pyc
pbr_atlas/baselines/__pycache__/xatlas_classical.cpython-313.pyc
paper/sections/6_limitations.tex

exec
/bin/zsh -lc 'ls -la datasets configs scripts paper paper/tables paper/sections pbr_atlas/data pbr_atlas/eval pbr_atlas/baselines' in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
configs:
total 48
drwxr-xr-x  10 jacksonhuang  staff   320 Apr 30 13:02 .
drwxr-xr-x@ 28 jacksonhuang  staff   896 May  1 20:51 ..
-rw-r--r--   1 jacksonhuang  staff   395 Apr 27 20:54 B1_sanity.yaml
-rw-r--r--   1 jacksonhuang  staff  1328 Apr 28 00:48 B2_matched.yaml
-rw-r--r--@  1 jacksonhuang  staff  1463 May  1 12:42 B3_main.yaml
drwxr-xr-x  20 jacksonhuang  staff   640 Apr 28 19:45 B4_ablations
drwxr-xr-x   7 jacksonhuang  staff   224 Apr 29 10:24 B5
-rw-r--r--   1 jacksonhuang  staff   553 Apr 29 11:17 B7_robustness.yaml
-rw-r--r--   1 jacksonhuang  staff   559 Apr 29 11:17 B7_transfer.yaml
-rw-r--r--   1 jacksonhuang  staff  1714 Apr 30 13:02 pg_real_meshes_A.json

datasets:
total 0
drwxr-xr-x   3 jacksonhuang  staff   96 Apr 30 13:01 .
drwxr-xr-x@ 28 jacksonhuang  staff  896 May  1 20:51 ..
drwxr-xr-x  16 jacksonhuang  staff  512 Apr 30 13:01 pg_real_meshes_local

paper:
total 46416
drwxr-xr-x  45 jacksonhuang  staff     1440 May  3 11:33 .
drwxr-xr-x@ 28 jacksonhuang  staff      896 May  1 20:51 ..
-rw-r--r--   1 jacksonhuang  staff     4324 Apr 29 16:57 PAPER_IMPROVEMENT_LOG.md
-rw-r--r--   1 jacksonhuang  staff    15303 Apr 29 16:23 REVIEW_R1.md
-rw-r--r--   1 jacksonhuang  staff     9588 Apr 29 16:37 REVIEW_R2.md
-rw-r--r--   1 jacksonhuang  staff    10361 Apr 30 14:19 REVIEW_R3.md
-rw-r--r--@  1 jacksonhuang  staff    11630 May  1 12:24 REVIEW_R4.md
-rw-r--r--@  1 jacksonhuang  staff     8222 May  2 01:01 REVIEW_R5.md
-rw-r--r--@  1 jacksonhuang  staff     4672 May  2 01:07 REVIEW_R6.md
-rw-r--r--@  1 jacksonhuang  staff     5107 May  3 01:50 REVIEW_R8.md
-rw-r--r--@  1 jacksonhuang  staff     5250 May  3 11:33 REVIEW_R9.md
-rw-r--r--@  1 jacksonhuang  staff      177 May  1 12:48 compile.log
drwxr-xr-x@ 42 jacksonhuang  staff     1344 Apr 29 16:10 egPublStyle-PG2026
drwxr-xr-x   2 jacksonhuang  staff       64 Apr 29 16:06 figures
-rw-r--r--@  1 jacksonhuang  staff    39076 May  3 11:28 main.aux
-rw-r--r--@  1 jacksonhuang  staff    10973 May  2 00:52 main.bbl
-rw-r--r--@  1 jacksonhuang  staff      933 May  2 00:52 main.blg
-rw-r--r--@  1 jacksonhuang  staff     3860 May  3 11:28 main.brf
-rw-r--r--@  1 jacksonhuang  staff    21190 May  1 12:53 main.fdb_latexmk
-rw-r--r--@  1 jacksonhuang  staff    27942 May  1 12:53 main.fls
-rw-r--r--@  1 jacksonhuang  staff       23 May  3 11:28 main.lbl
-rw-r--r--@  1 jacksonhuang  staff    34693 May  3 11:28 main.log
-rw-r--r--@  1 jacksonhuang  staff  3298110 May  3 11:28 main.pdf
-rw-r--r--   1 jacksonhuang  staff     2931 Apr 29 16:51 main.tex
-rw-r--r--   1 jacksonhuang  staff   605209 Apr 29 16:18 main_round0_original.pdf
-rw-r--r--   1 jacksonhuang  staff   607624 Apr 29 16:31 main_round1.pdf
-rw-r--r--@  1 jacksonhuang  staff   663485 May  2 01:00 main_round10_post_r5_fixes.pdf
-rw-r--r--@  1 jacksonhuang  staff  2151188 May  2 12:45 main_round11_visual.pdf
-rw-r--r--@  1 jacksonhuang  staff  2152842 May  2 12:46 main_round12_visual_runtime.pdf
-rw-r--r--@  1 jacksonhuang  staff  2735348 May  2 12:52 main_round13_visual_v2.pdf
-rw-r--r--@  1 jacksonhuang  staff  2734967 May  2 12:53 main_round14_r7_addressed.pdf
-rw-r--r--@  1 jacksonhuang  staff  3298110 May  3 11:28 main_round15_xatlas_visual.pdf
-rw-r--r--   1 jacksonhuang  staff   638117 Apr 29 16:56 main_round2.pdf
-rw-r--r--   1 jacksonhuang  staff   642686 Apr 30 14:24 main_round3_pgenh.pdf
-rw-r--r--@  1 jacksonhuang  staff   645462 May  1 12:20 main_round4_realmesh.pdf
-rw-r--r--@  1 jacksonhuang  staff   649437 May  1 12:53 main_round5_split.pdf
-rw-r--r--@  1 jacksonhuang  staff   650820 May  1 13:07 main_round6_pre_a1.pdf
-rw-r--r--@  1 jacksonhuang  staff   652177 May  2 00:50 main_round7_a1complete.pdf
-rw-r--r--@  1 jacksonhuang  staff   662126 May  2 00:52 main_round8_real_meshes.pdf
-rw-r--r--@  1 jacksonhuang  staff   663398 May  2 00:53 main_round9_r5_ready.pdf
-rw-r--r--@  1 jacksonhuang  staff     1840 May  1 12:45 math_commands.tex
-rw-r--r--@  1 jacksonhuang  staff     3036 May  1 20:54 r5_review_prompt.md
-rw-r--r--@  1 jacksonhuang  staff    13797 May  2 00:52 references.bib
drwxr-xr-x  11 jacksonhuang  staff      352 May  3 11:28 sections
drwxr-xr-x  14 jacksonhuang  staff      448 May  2 12:45 tables

paper/sections:
total 152
drwxr-xr-x  11 jacksonhuang  staff    352 May  3 11:28 .
drwxr-xr-x  45 jacksonhuang  staff   1440 May  3 11:33 ..
-rw-r--r--@  1 jacksonhuang  staff   2050 May  2 00:52 0_abstract.tex
-rw-r--r--@  1 jacksonhuang  staff   7387 May  2 00:53 1_introduction.tex
-rw-r--r--   1 jacksonhuang  staff   6119 Apr 29 16:49 2_related.tex
-rw-r--r--@  1 jacksonhuang  staff  12404 May  1 12:58 3_method.tex
-rw-r--r--@  1 jacksonhuang  staff  13185 May  3 11:28 4_experiments.tex
-rw-r--r--@  1 jacksonhuang  staff   6769 May  2 00:50 5_confounds.tex
-rw-r--r--@  1 jacksonhuang  staff   2812 May  2 00:53 6_limitations.tex
-rw-r--r--   1 jacksonhuang  staff   1200 Apr 29 16:28 7_conclusion.tex
-rw-r--r--@  1 jacksonhuang  staff   5278 May  2 12:46 A_appendix.tex

paper/tables:
total 96
drwxr-xr-x  14 jacksonhuang  staff   448 May  2 12:45 .
drwxr-xr-x  45 jacksonhuang  staff  1440 May  3 11:33 ..
-rw-r--r--@  1 jacksonhuang  staff   761 May  1 12:52 table10_curvature.tex
-rw-r--r--@  1 jacksonhuang  staff   771 May  2 00:50 table11_a1_split.tex
-rw-r--r--@  1 jacksonhuang  staff   977 May  2 12:45 table12_runtime.tex
-rw-r--r--@  1 jacksonhuang  staff  2228 May  2 01:00 table1_main.tex
-rw-r--r--   1 jacksonhuang  staff  2171 Apr 29 16:51 table2_ablation.tex
-rw-r--r--@  1 jacksonhuang  staff  1612 May  1 13:06 table3_matched.tex
-rw-r--r--   1 jacksonhuang  staff  1840 Apr 29 16:50 table4_transfer.tex
-rw-r--r--   1 jacksonhuang  staff   837 Apr 29 16:03 table5_robustness.tex
-rw-r--r--   1 jacksonhuang  staff   645 Apr 30 12:45 table7_purity.tex
-rw-r--r--   1 jacksonhuang  staff  1140 Apr 30 12:45 table7_robust_extended.tex
-rw-r--r--   1 jacksonhuang  staff  1080 Apr 30 12:45 table8_extended_transfer.tex
-rw-r--r--@  1 jacksonhuang  staff  1357 May  2 00:51 table9_real_mesh.tex

pbr_atlas/baselines:
total 176
drwxr-xr-x  16 jacksonhuang  staff    512 Apr 28 02:41 .
drwxr-xr-x  11 jacksonhuang  staff    352 Apr 28 19:36 ..
-rw-r--r--   1 jacksonhuang  staff   1637 Apr 28 00:45 __init__.py
drwxr-xr-x  15 jacksonhuang  staff    480 Apr 28 10:36 __pycache__
-rw-r--r--   1 jacksonhuang  staff  18395 Apr 28 00:49 base.py
-rw-r--r--   1 jacksonhuang  staff   3002 Apr 28 00:43 baseline_failure_table.py
-rw-r--r--   1 jacksonhuang  staff   5909 Apr 28 01:46 blender_uv.py
-rw-r--r--   1 jacksonhuang  staff   1767 Apr 28 00:45 flatten_anything.py
-rw-r--r--   1 jacksonhuang  staff   2991 Apr 28 02:41 flexpara.py
-rw-r--r--   1 jacksonhuang  staff   2753 Apr 28 00:45 matched_oracle.py
-rw-r--r--   1 jacksonhuang  staff   8659 Apr 28 00:43 matched_protocol.py
-rw-r--r--   1 jacksonhuang  staff   2230 Apr 28 00:45 otuvgs.py
-rw-r--r--   1 jacksonhuang  staff   1756 Apr 28 00:45 parapoint.py
-rw-r--r--   1 jacksonhuang  staff   9115 Apr 28 02:35 partuv.py
-rw-r--r--   1 jacksonhuang  staff   2584 Apr 28 00:45 visibility_param.py
-rw-r--r--   1 jacksonhuang  staff   1861 Apr 28 00:45 xatlas_classical.py

pbr_atlas/data:
total 152
drwxr-xr-x   8 jacksonhuang  staff    256 Apr 29 11:07 .
drwxr-xr-x  11 jacksonhuang  staff    352 Apr 28 19:36 ..
-rw-r--r--   1 jacksonhuang  staff    876 Apr 29 11:07 __init__.py
drwxr-xr-x   7 jacksonhuang  staff    224 Apr 29 17:17 __pycache__
-rw-r--r--   1 jacksonhuang  staff   6151 Apr 27 20:50 asset_registry.py
-rw-r--r--   1 jacksonhuang  staff  49463 Apr 29 17:17 generated_mesh_loader.py
-rw-r--r--   1 jacksonhuang  staff   6111 Apr 27 20:54 mesh_loader.py
-rw-r--r--   1 jacksonhuang  staff   3940 Apr 28 10:31 oracle_pbr.py

pbr_atlas/eval:
total 64
drwxr-xr-x   8 jacksonhuang  staff   256 May  1 12:41 .
drwxr-xr-x  11 jacksonhuang  staff   352 Apr 28 19:36 ..
-rw-r--r--@  1 jacksonhuang  staff   896 May  1 12:41 __init__.py
drwxr-xr-x   7 jacksonhuang  staff   224 May  1 12:48 __pycache__
-rw-r--r--@  1 jacksonhuang  staff  5824 May  1 12:41 chart_curvature.py
-rw-r--r--   1 jacksonhuang  staff  5908 Apr 29 17:12 chart_purity.py
-rw-r--r--   1 jacksonhuang  staff  4108 Apr 27 20:50 metrics.py
-rw-r--r--   1 jacksonhuang  staff  1139 Apr 27 20:50 residual_attribution.py

scripts:
total 568
drwxr-xr-x  30 jacksonhuang  staff    960 May  3 11:26 .
drwxr-xr-x@ 28 jacksonhuang  staff    896 May  1 20:51 ..
drwxr-xr-x  22 jacksonhuang  staff    704 May  1 12:48 __pycache__
-rw-r--r--   1 jacksonhuang  staff   6182 Apr 28 00:48 collect_B2_table.py
-rw-r--r--@  1 jacksonhuang  staff   9925 May  1 12:43 collect_B3_table.py
-rwxr-xr-x   1 jacksonhuang  staff   6122 Apr 28 19:43 collect_B4_table.py
-rwxr-xr-x   1 jacksonhuang  staff   7134 Apr 29 10:25 collect_B5_table.py
-rw-r--r--   1 jacksonhuang  staff  12112 Apr 29 11:11 collect_B7_table.py
-rw-r--r--   1 jacksonhuang  staff   3692 Apr 27 20:52 determinism_check.py
-rw-r--r--@  1 jacksonhuang  staff   4994 May  1 13:00 digest_a1_split.py
-rw-r--r--   1 jacksonhuang  staff   5706 Apr 30 13:25 fetch_real_meshes_C.py
-rwxr-xr-x   1 jacksonhuang  staff   4387 Apr 30 12:43 ingest_user_provided_mesh.py
-rwxr-xr-x   1 jacksonhuang  staff  12673 Apr 29 16:55 render_B6_figures.py
-rw-r--r--@  1 jacksonhuang  staff   9535 May  3 11:26 render_visual_figure.py
-rw-r--r--   1 jacksonhuang  staff   2085 Apr 28 00:48 reproduce_baselines.sh
-rwxr-xr-x@  1 jacksonhuang  staff   1528 May  1 12:47 run_A_structural_fix_cases.sh
-rw-r--r--   1 jacksonhuang  staff  11603 Apr 28 10:31 run_B1.py
-rw-r--r--   1 jacksonhuang  staff  14916 Apr 28 00:48 run_B2.py
-rw-r--r--@  1 jacksonhuang  staff  32876 May  1 12:40 run_B3.py
-rwxr-xr-x   1 jacksonhuang  staff   9898 Apr 29 10:06 run_B4_ablation.py
-rwxr-xr-x   1 jacksonhuang  staff   3277 Apr 28 19:45 run_B4_grid.sh
-rwxr-xr-x   1 jacksonhuang  staff  10598 Apr 29 10:24 run_B5.py
-rw-r--r--   1 jacksonhuang  staff  13414 Apr 30 12:46 run_B7_robustness.py
-rw-r--r--   1 jacksonhuang  staff   9428 Apr 29 11:17 run_B7_transfer.py
-rw-r--r--   1 jacksonhuang  staff   9287 Apr 29 17:15 run_PG_enh1_real_generated.py
-rw-r--r--   1 jacksonhuang  staff   9570 Apr 29 17:18 run_PG_enh2_purity.py
-rw-r--r--@  1 jacksonhuang  staff  11013 May  1 12:49 run_PG_enh2_v2_curvature.py
-rw-r--r--   1 jacksonhuang  staff   8167 Apr 29 17:14 run_PG_enh3_robust.py
-rw-r--r--   1 jacksonhuang  staff   1088 Apr 27 20:52 setup_data_b1.py
-rw-r--r--   1 jacksonhuang  staff   1896 Apr 29 11:07 setup_data_b7.py

exec
/bin/zsh -lc 'rg -n "DiLiGenT|diligent|captured|Poly Haven|PartUV|matched_oracle|matched|seed|bootstrap|Wilcoxon|sign" .' in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 118ms:
./runs/B1_sanity/20260428_001949_spot_seed42/summary.md:4:- seed: 42
./runs/PG_enh1_data_test/PG_ENH1_REAL_GENERATED_MANIFEST.json:15:      "seed": 7101,
./runs/PG_enh1_data_test/PG_ENH1_REAL_GENERATED_MANIFEST.json:31:      "seed": 7102,
./runs/B1_sanity/20260428_001949_spot_seed42/metrics.json:17:    "metrics": "/data/dip_1_ws/runs/B1_sanity/20260428_001949_spot_seed42/metrics.json",
./runs/B1_sanity/20260428_001949_spot_seed42/metrics.json:18:    "residual_npz": "/data/dip_1_ws/runs/B1_sanity/20260428_001949_spot_seed42/residual_atlas.npz",
./runs/B1_sanity/20260428_001949_spot_seed42/metrics.json:19:    "residual_png": "/data/dip_1_ws/runs/B1_sanity/20260428_001949_spot_seed42/residual_atlas.png",
./runs/B1_sanity/20260428_001949_spot_seed42/metrics.json:20:    "summary": "/data/dip_1_ws/runs/B1_sanity/20260428_001949_spot_seed42/summary.md"
./runs/B1_sanity/20260428_001949_spot_seed42/metrics.json:440:  "seed": 42,
./runs/B1_sanity/20260428_001833_bunny_seed42/summary.md:4:- seed: 42
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:152:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:272:    "matched_protocol_after_repair": {
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:277:      "matched_constraint_violated": true,
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1164:  "matched_protocol_initial": {
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1169:    "matched_constraint_violated": true,
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1200:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1201:    "metrics": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1202:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1203:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1204:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1205:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:1206:    "summary": "/data/dip_1_ws/runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/light_holdout6_spot_partuv_ours_seed42/metrics.json:2044:  "seed": 42,
./runs/B1_sanity/20260428_001833_bunny_seed42/metrics.json:17:    "metrics": "/data/dip_1_ws/runs/B1_sanity/20260428_001833_bunny_seed42/metrics.json",
./runs/B1_sanity/20260428_001833_bunny_seed42/metrics.json:18:    "residual_npz": "/data/dip_1_ws/runs/B1_sanity/20260428_001833_bunny_seed42/residual_atlas.npz",
./runs/B1_sanity/20260428_001833_bunny_seed42/metrics.json:19:    "residual_png": "/data/dip_1_ws/runs/B1_sanity/20260428_001833_bunny_seed42/residual_atlas.png",
./runs/B1_sanity/20260428_001833_bunny_seed42/metrics.json:20:    "summary": "/data/dip_1_ws/runs/B1_sanity/20260428_001833_bunny_seed42/summary.md"
./runs/B1_sanity/20260428_001833_bunny_seed42/metrics.json:1343:  "seed": 42,
./runs/PG_enh1_data_test/PG_ENH1_SOURCE_FAILURES.json:9:      "seed": 0,
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:152:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:272:    "matched_protocol_after_repair": {
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:277:      "matched_constraint_violated": true,
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1164:  "matched_protocol_initial": {
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1169:    "matched_constraint_violated": true,
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1200:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1201:    "metrics": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1202:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1203:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1204:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1205:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:1206:    "summary": "/data/dip_1_ws/runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/view_holdout4_spot_partuv_ours_seed42/metrics.json:2044:  "seed": 42,
./runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/summary.md:4:- seed: 42
./runs/PG_enh1_data_test/PG_ENH1_LOCAL_SOURCES.json:16:      "seed": 7101,
./runs/PG_enh1_data_test/PG_ENH1_LOCAL_SOURCES.json:32:      "seed": 7102,
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:94:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:214:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:219:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:1461:    "seed": 7104,
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2659:  "matched_protocol_initial": {
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2664:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2694:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2695:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2696:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2697:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2698:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2699:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:2700:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42/metrics.json:4191:  "seed": 42,
./runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/metrics.json:17:    "metrics": "/data/dip_1_ws/runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/metrics.json",
./runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/metrics.json:18:    "residual_npz": "/data/dip_1_ws/runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/residual_atlas.npz",
./runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/metrics.json:19:    "residual_png": "/data/dip_1_ws/runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/residual_atlas.png",
./runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/metrics.json:20:    "summary": "/data/dip_1_ws/runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/summary.md"
./runs/B1_sanity/determinism_20260428_001910_bunny_seed42_a/metrics.json:1343:  "seed": 42,
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:948:    "seed": 7103,
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1761:  "matched_protocol_initial": {
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1766:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1795:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1796:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1797:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1798:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1799:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1800:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:1801:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_crumpled_box_partuv_baseline_only_seed42/metrics.json:2614:  "seed": 42,
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:168:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:288:    "matched_protocol_after_repair": {
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:293:      "matched_constraint_violated": true,
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1188:  "matched_protocol_initial": {
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1193:    "matched_constraint_violated": true,
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1224:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1225:    "metrics": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1226:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1227:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1228:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1229:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:1230:    "summary": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:2191:    "seed": 42,
./runs/B7_robustness/noise_sigma0p02_spot_partuv_ours_seed42/metrics.json:2195:  "seed": 42,
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:158:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:311:    "matched_protocol_after_repair": {
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:316:      "matched_constraint_violated": true,
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:3485:        "seed": 42,
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:3490:      "seed": 42,
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:3493:    "seed": 42,
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6613:  "matched_protocol_initial": {
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6618:    "matched_constraint_violated": true,
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6649:    "atlas_npz": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/atlas.npz",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6650:    "metrics": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6651:    "repair_log": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/repair_log.json",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6652:    "residual_chain_png": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/residual_chain.png",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6653:    "residual_npz": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/residual_atlas.npz",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6654:    "residual_png": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/residual_atlas.png",
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:6655:    "summary": "/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/summary.md"
./runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42/metrics.json:10214:  "seed": 42,
./runs/B5_matched/grid_run.log:3:/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42
./runs/B5_matched/grid_run.log:4:/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42
./runs/B5_matched/grid_run.log:8:/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42
./runs/B5_matched/grid_run.log:9:/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42
./runs/B5_matched/grid_run.log:13:/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42
./runs/B5_matched/grid_run.log:14:/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42
./runs/B5_matched/grid_run.log:18:/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42
./runs/B5_matched/grid_run.log:19:/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42
./runs/B5_matched/grid_run.log:23:/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42
./runs/B5_matched/grid_run.log:24:/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42
./runs/B5_matched/grid_run.log:28:/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:29:/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:33:/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:34:/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:38:/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:39:/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:43:/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:44:/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:48:/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42
./runs/B5_matched/grid_run.log:49:/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:202:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:322:    "matched_protocol_after_repair": {
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:327:      "matched_constraint_violated": true,
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:3713:      "seed": 7104,
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:3716:    "seed": 7104,
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7053:  "matched_protocol_initial": {
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7058:    "matched_constraint_violated": true,
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7088:    "atlas_npz": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/atlas.npz",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7089:    "metrics": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7090:    "repair_log": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/repair_log.json",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7091:    "residual_chain_png": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/residual_chain.png",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7092:    "residual_npz": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/residual_atlas.npz",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7093:    "residual_png": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/residual_atlas.png",
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:7094:    "summary": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/summary.md"
./runs/PG_enh1_real_generated/proc_warped_cylinder_partuv_ours_seed42/metrics.json:11156:  "seed": 42,
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:176:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:296:    "matched_protocol_after_repair": {
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:301:      "matched_constraint_violated": true,
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1200:  "matched_protocol_initial": {
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1205:    "matched_constraint_violated": true,
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1236:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1237:    "metrics": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1238:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1239:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1240:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1241:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:1242:    "summary": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:2205:    "seed": 42,
./runs/B7_robustness/noise_sigma0p05_spot_partuv_ours_seed42/metrics.json:2209:  "seed": 42,
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:104:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:191:    "matched_protocol_after_repair": {
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:196:      "matched_constraint_violated": true,
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1088:  "matched_protocol_initial": {
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1093:    "matched_constraint_violated": true,
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1123:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1124:    "metrics": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1125:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1126:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1127:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1128:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1129:    "summary": "/data/dip_1_ws/runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1835:    "seed": 42,
./runs/B7_robustness/noise_sigma0p01_spot_partuv_ours_seed42/metrics.json:1839:  "seed": 42,
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:152:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:272:    "matched_protocol_after_repair": {
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:277:      "matched_constraint_violated": true,
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1164:  "matched_protocol_initial": {
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1169:    "matched_constraint_violated": true,
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1200:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1201:    "metrics": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1202:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1203:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1204:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1205:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:1206:    "summary": "/data/dip_1_ws/runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/view_holdout12_spot_partuv_ours_seed42/metrics.json:2044:  "seed": 42,
./runs/B5_matched/B5_5_spot_partuv_seed42/repair_log.json:98:        "matched_ok": true,
./runs/B5_matched/B5_5_spot_partuv_seed42/repair_log.json:99:        "name": "All strict matched controls",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:152:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:272:    "matched_protocol_after_repair": {
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:277:      "matched_constraint_violated": true,
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1164:  "matched_protocol_initial": {
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1169:    "matched_constraint_violated": true,
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1200:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1201:    "metrics": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1202:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1203:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1204:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1205:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:1206:    "summary": "/data/dip_1_ws/runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/view_holdout8_spot_partuv_ours_seed42/metrics.json:2044:  "seed": 42,
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:1453:    "seed": 7108,
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2770:  "matched_protocol_initial": {
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2775:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2805:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2806:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2807:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2808:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2809:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2810:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:2811:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_pinched_ico_partuv_baseline_only_seed42/metrics.json:4128:  "seed": 42,
./runs/B5_matched/B5_5_spot_partuv_seed42/summary.md:4:- condition name: All strict matched controls
./runs/B5_matched/B5_5_spot_partuv_seed42/summary.md:9:- matched OK: True
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:1925:    "seed": 7106,
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3713:  "matched_protocol_initial": {
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3718:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3749:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3750:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3751:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3752:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3753:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3754:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:3755:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:5543:  "seed": 42,
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:152:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:272:    "matched_protocol_after_repair": {
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:277:      "matched_constraint_violated": true,
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1164:  "matched_protocol_initial": {
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1169:    "matched_constraint_violated": true,
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1200:    "atlas_npz": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/atlas.npz",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1201:    "metrics": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1202:    "repair_log": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/repair_log.json",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1203:    "residual_chain_png": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/residual_chain.png",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1204:    "residual_npz": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1205:    "residual_png": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/residual_atlas.png",
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:1206:    "summary": "/data/dip_1_ws/runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/summary.md"
./runs/B7_robustness/light_holdout8_spot_partuv_ours_seed42/metrics.json:2044:  "seed": 42,
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:4364:      "seed": 7106,
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:4367:    "seed": 7106,
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8589:  "matched_protocol_initial": {
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8594:    "matched_constraint_violated": true,
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8625:    "atlas_npz": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/atlas.npz",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8626:    "metrics": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8627:    "repair_log": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/repair_log.json",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8628:    "residual_chain_png": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/residual_chain.png",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8629:    "residual_npz": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8630:    "residual_png": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/residual_atlas.png",
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:8631:    "summary": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/summary.md"
./runs/PG_enh1_real_generated/proc_noisy_capsule_partuv_baseline_only_seed42/metrics.json:12853:  "seed": 42,
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:63:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:64:    "path": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:67:  "baseline_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:68:  "block": "B5_matched",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:128:      "matched_ok": true,
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:129:      "name": "All strict matched controls",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:200:          "matched_ok": true,
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:201:          "name": "All strict matched controls",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:236:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:241:      "matched_constraint_violated": true,
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:276:  "condition_name": "All strict matched controls",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1131:  "matched_protocol_initial": {
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1136:    "matched_constraint_violated": true,
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1167:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1168:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1169:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1170:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1171:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1172:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1173:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_5_spot_partuv_seed42/summary.md"
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1755:    "name": "All strict matched controls",
./runs/B5_matched/B5_5_spot_partuv_seed42/metrics.json:1758:  "seed": 42,
./runs/B5_matched/B5_RESULTS.md:7:- spot/B5.1: matched=yes, verdict=accept, gain_vs_initial=14.6685, d_vs_B3_ACCEPT=0.0000.
./runs/B5_matched/B5_RESULTS.md:8:- spot/B5.2: matched=yes, verdict=accept, gain_vs_initial=14.6685, d_vs_B3_ACCEPT=0.0000.
./runs/B5_matched/B5_RESULTS.md:9:- spot/B5.3: matched=yes, verdict=rollback, gain_vs_initial=0.0000, d_vs_B3_ACCEPT=-14.6685.
./runs/B5_matched/B5_RESULTS.md:10:- spot/B5.4: matched=yes, verdict=rollback, gain_vs_initial=0.0000, d_vs_B3_ACCEPT=-14.6685.
./runs/B5_matched/B5_RESULTS.md:11:- spot/B5.5: matched=yes, verdict=rollback, gain_vs_initial=0.0000, d_vs_B3_ACCEPT=-14.6685.
./runs/B5_matched/B5_RESULTS.md:12:- bunny/B5.1: matched=yes, verdict=accept, gain_vs_initial=10.2337, d_vs_B3_ACCEPT=0.0000.
./runs/B5_matched/B5_RESULTS.md:13:- bunny/B5.2: matched=yes, verdict=accept, gain_vs_initial=10.2337, d_vs_B3_ACCEPT=0.0000.
./runs/B5_matched/B5_RESULTS.md:14:- bunny/B5.3: matched=yes, verdict=rollback, gain_vs_initial=0.0000, d_vs_B3_ACCEPT=-10.2337.
./runs/B5_matched/B5_RESULTS.md:15:- bunny/B5.4: matched=yes, verdict=rollback, gain_vs_initial=0.0000, d_vs_B3_ACCEPT=-10.2337.
./runs/B5_matched/B5_RESULTS.md:16:- bunny/B5.5: matched=yes, verdict=rollback, gain_vs_initial=0.0000, d_vs_B3_ACCEPT=-10.2337.
./runs/B5_matched/B5_RESULTS.md:20:- matched OK count: 10/10
./runs/B5_matched/B5_RESULTS.md:26:- B5.2: Delta PSNR over the PartUV initial atlas should remain at least +0.3 dB.
./runs/B5_matched/B5_TABLE.md:3:| Asset | Condition | ours_PSNR | dPSNR vs ACCEPT | matched_OK | c5_verdict | Gain vs initial | Strict violations |
./runs/B5_matched/B5_TABLE.md:9:| spot | B5.5 All strict matched controls | 30.3207 | -14.6685 | yes | rollback | 0.0000 | - |
./runs/B5_matched/B5_TABLE.md:14:| bunny | B5.5 All strict matched controls | 28.2974 | -10.2337 | yes | rollback | 0.0000 | - |
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:190:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:277:    "matched_protocol_after_repair": {
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:282:      "matched_constraint_violated": true,
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:4279:      "seed": 7102,
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:4282:    "seed": 7102,
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8230:  "matched_protocol_initial": {
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8235:    "matched_constraint_violated": true,
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8266:    "atlas_npz": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/atlas.npz",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8267:    "metrics": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8268:    "repair_log": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/repair_log.json",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8269:    "residual_chain_png": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/residual_chain.png",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8270:    "residual_npz": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/residual_atlas.npz",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8271:    "residual_png": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/residual_atlas.png",
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:8272:    "summary": "/data/dip_1_ws/runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/summary.md"
./runs/PG_enh1_real_generated/proc_dented_torus_partuv_ours_seed42/metrics.json:12853:  "seed": 42,
./runs/B5_matched/B5_3_bunny_partuv_seed42/repair_log.json:53:        "matched_ok": true,
./runs/B5_matched/B5_3_bunny_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_2_bunny_partuv_seed42/repair_log.json:74:        "matched_ok": true,
./runs/B5_matched/B5_2_bunny_partuv_seed42/repair_log.json:142:        "matched_ok": true,
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:184:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:271:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:276:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:2632:    "seed": 7107,
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4945:  "matched_protocol_initial": {
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4950:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4980:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4981:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4982:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4983:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4984:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4985:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:4986:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_ridged_sphere_partuv_ours_seed42/metrics.json:7878:  "seed": 42,
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:29:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:30:    "path": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:33:  "baseline_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:34:  "block": "B5_matched",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:83:      "matched_ok": true,
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:144:          "matched_ok": true,
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:180:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:185:      "matched_constraint_violated": true,
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2856:  "matched_protocol_initial": {
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2861:    "matched_constraint_violated": true,
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2891:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2892:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2893:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2894:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2895:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2896:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:2897:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_3_bunny_partuv_seed42/summary.md"
./runs/B5_matched/B5_3_bunny_partuv_seed42/metrics.json:4323:  "seed": 42,
./runs/B5_matched/B5_2_bunny_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:47:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:48:    "path": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:51:  "baseline_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:52:  "block": "B5_matched",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:104:      "matched_ok": true,
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:168:          "matched_ok": true,
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:236:          "matched_ok": true,
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:274:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:279:      "matched_constraint_violated": true,
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:313:  "condition_expected": "Delta PSNR over the PartUV initial atlas should remain at least +0.3 dB.",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2951:  "matched_protocol_initial": {
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2956:    "matched_constraint_violated": true,
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2986:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2987:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2988:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2989:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2990:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2991:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:2992:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_2_bunny_partuv_seed42/summary.md"
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:4460:    "expected": "Delta PSNR over the PartUV initial atlas should remain at least +0.3 dB.",
./runs/B5_matched/B5_2_bunny_partuv_seed42/metrics.json:4466:  "seed": 42,
./runs/B5_matched/B5_1_bunny_partuv_seed42/summary.md:9:- matched OK: True
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:1249:    "seed": 7105,
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2362:  "matched_protocol_initial": {
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2367:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2397:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2398:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2399:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2400:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2401:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2402:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:2403:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_twisted_cone_partuv_baseline_only_seed42/metrics.json:3516:  "seed": 42,
./runs/B5_matched/B5_3_spot_partuv_seed42/repair_log.json:87:        "matched_ok": true,
./runs/B5_matched/B5_3_spot_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_4_bunny_partuv_seed42/repair_log.json:53:        "matched_ok": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:47:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:48:    "path": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:51:  "baseline_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:52:  "block": "B5_matched",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:103:      "matched_ok": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:166:          "matched_ok": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:233:          "matched_ok": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:271:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:276:      "matched_constraint_violated": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2948:  "matched_protocol_initial": {
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2953:    "matched_constraint_violated": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2983:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2984:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2985:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2986:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2987:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2988:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:2989:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_1_bunny_partuv_seed42/summary.md"
./runs/B5_matched/B5_1_bunny_partuv_seed42/metrics.json:4508:  "seed": 42,
./runs/B5_matched/B5_5_bunny_partuv_seed42/repair_log.json:64:        "matched_ok": true,
./runs/B5_matched/B5_5_bunny_partuv_seed42/repair_log.json:65:        "name": "All strict matched controls",
./runs/B5_matched/B5_4_bunny_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:63:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:64:    "path": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:67:  "baseline_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:68:  "block": "B5_matched",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:117:      "matched_ok": true,
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:178:          "matched_ok": true,
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:214:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:219:      "matched_constraint_violated": true,
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1109:  "matched_protocol_initial": {
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1114:    "matched_constraint_violated": true,
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1145:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1146:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1147:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1148:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1149:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1150:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1151:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_3_spot_partuv_seed42/summary.md"
./runs/B5_matched/B5_3_spot_partuv_seed42/metrics.json:1794:  "seed": 42,
./runs/B5_matched/B5_5_bunny_partuv_seed42/summary.md:4:- condition name: All strict matched controls
./runs/B5_matched/B5_5_bunny_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_1_bunny_partuv_seed42/repair_log.json:73:        "matched_ok": true,
./runs/B5_matched/B5_1_bunny_partuv_seed42/repair_log.json:140:        "matched_ok": true,
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:64:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:151:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:156:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:2261:    "seed": 7102,
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4322:  "matched_protocol_initial": {
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4327:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4358:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4359:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4360:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4361:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4362:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4363:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:4364:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_dented_torus_partuv_ours_seed42/metrics.json:6518:  "seed": 42,
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:29:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:30:    "path": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:33:  "baseline_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:34:  "block": "B5_matched",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:94:      "matched_ok": true,
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:95:      "name": "All strict matched controls",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:166:          "matched_ok": true,
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:167:          "name": "All strict matched controls",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:202:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:207:      "matched_constraint_violated": true,
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:241:  "condition_name": "All strict matched controls",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2878:  "matched_protocol_initial": {
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2883:    "matched_constraint_violated": true,
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2913:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2914:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2915:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2916:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2917:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2918:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:2919:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_5_bunny_partuv_seed42/summary.md"
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:4324:    "name": "All strict matched controls",
./runs/B5_matched/B5_5_bunny_partuv_seed42/metrics.json:4327:  "seed": 42,
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:29:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:30:    "path": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:33:  "baseline_run": "/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:34:  "block": "B5_matched",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:83:      "matched_ok": true,
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:144:          "matched_ok": true,
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:180:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:185:      "matched_constraint_violated": true,
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2856:  "matched_protocol_initial": {
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2861:    "matched_constraint_violated": true,
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2891:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2892:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2893:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2894:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2895:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2896:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:2897:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_4_bunny_partuv_seed42/summary.md"
./runs/B5_matched/B5_4_bunny_partuv_seed42/metrics.json:4323:  "seed": 42,
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:150:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:237:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:242:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:1597:    "seed": 7101,
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2909:  "matched_protocol_initial": {
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2914:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2944:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2945:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2946:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2947:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2948:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2949:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:2950:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_lumpy_ico_partuv_ours_seed42/metrics.json:4733:  "seed": 42,
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:202:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:289:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:294:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:2132:    "seed": 7106,
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3926:  "matched_protocol_initial": {
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3931:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3962:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3963:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3964:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3965:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3966:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3967:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:3968:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_noisy_capsule_partuv_ours_seed42/metrics.json:6449:  "seed": 42,
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:152:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:239:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:244:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:1400:    "seed": 7105,
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2513:  "matched_protocol_initial": {
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2518:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2548:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2549:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2550:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2551:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2552:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2553:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:2554:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_twisted_cone_partuv_ours_seed42/metrics.json:4138:  "seed": 42,
./runs/B5_matched/B5_2_spot_partuv_seed42/repair_log.json:142:        "matched_ok": true,
./runs/B5_matched/B5_2_spot_partuv_seed42/repair_log.json:210:        "matched_ok": true,
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:1334:    "seed": 7104,
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2532:  "matched_protocol_initial": {
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2537:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2567:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2568:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2569:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2570:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2571:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2572:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:2573:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_warped_cylinder_partuv_baseline_only_seed42/metrics.json:3771:  "seed": 42,
./runs/B5_matched/B5_2_spot_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_1_spot_partuv_seed42/repair_log.json:141:        "matched_ok": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/repair_log.json:208:        "matched_ok": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_4_spot_partuv_seed42/repair_log.json:87:        "matched_ok": true,
./runs/B5_matched/B5_4_spot_partuv_seed42/summary.md:9:- matched OK: True
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:115:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:116:    "path": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:119:  "baseline_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:120:  "block": "B5_matched",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:172:      "matched_ok": true,
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:236:          "matched_ok": true,
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:304:          "matched_ok": true,
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:342:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:347:      "matched_constraint_violated": true,
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:381:  "condition_expected": "Delta PSNR over the PartUV initial atlas should remain at least +0.3 dB.",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1237:  "matched_protocol_initial": {
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1242:    "matched_constraint_violated": true,
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1273:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1274:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1275:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1276:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1277:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1278:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1279:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_2_spot_partuv_seed42/summary.md"
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1992:    "expected": "Delta PSNR over the PartUV initial atlas should remain at least +0.3 dB.",
./runs/B5_matched/B5_2_spot_partuv_seed42/metrics.json:1998:  "seed": 42,
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:2449:    "seed": 7107,
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4762:  "matched_protocol_initial": {
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4767:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4797:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4798:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4799:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4800:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4801:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4802:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:4803:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_ridged_sphere_partuv_baseline_only_seed42/metrics.json:7116:  "seed": 42,
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:1448:    "seed": 7101,
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2760:  "matched_protocol_initial": {
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2765:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2795:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2796:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2797:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2798:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2799:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2800:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:2801:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_lumpy_ico_partuv_baseline_only_seed42/metrics.json:4113:  "seed": 42,
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:63:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:64:    "path": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:67:  "baseline_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:68:  "block": "B5_matched",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:117:      "matched_ok": true,
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:178:          "matched_ok": true,
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:214:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:219:      "matched_constraint_violated": true,
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1109:  "matched_protocol_initial": {
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1114:    "matched_constraint_violated": true,
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1145:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1146:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1147:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1148:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1149:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1150:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1151:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_4_spot_partuv_seed42/summary.md"
./runs/B5_matched/B5_4_spot_partuv_seed42/metrics.json:1794:  "seed": 42,
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:115:    "cached_b3_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:116:    "path": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42/initial_atlas.npz",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:119:  "baseline_run": "/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:120:  "block": "B5_matched",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:171:      "matched_ok": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:234:          "matched_ok": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:301:          "matched_ok": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:339:    "matched_protocol_after_repair": {
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:344:      "matched_constraint_violated": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1234:  "matched_protocol_initial": {
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1239:    "matched_constraint_violated": true,
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1270:    "atlas_npz": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/atlas.npz",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1271:    "metrics": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1272:    "repair_log": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/repair_log.json",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1273:    "residual_chain_png": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/residual_chain.png",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1274:    "residual_npz": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/residual_atlas.npz",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1275:    "residual_png": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/residual_atlas.png",
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:1276:    "summary": "/data/dip_1_ws/runs/B5_matched/B5_1_spot_partuv_seed42/summary.md"
./runs/B5_matched/B5_1_spot_partuv_seed42/metrics.json:2120:  "seed": 42,
./refine-logs/B7_RESULTS.md:7:## B7.1 Generated Transfer (8 procedural noisy meshes × PartUV baseline)
./refine-logs/B7_RESULTS.md:21:- 1/8 ACCEPT（warped_cylinder ΔPSNR +10.74 dB），与 B3 spot/bunny+partuv 一致 — method 在 PartUV produce 出"明显欠佳"的 atlas 时才触发
./refine-logs/B7_RESULTS.md:22:- 7/8 ROLLBACK：procedural shape 的 PartUV 输出已经接近最优，method 没有可改善的空间
./refine-logs/B7_RESULTS.md:61:- σ=0.01 的 noise 让 PartUV 产生了边缘 case 的 atlas（chart 数变化等）
./refine-logs/B7_RESULTS.md:62:- 而 σ=0.02/0.05 的 noise 反而让 PartUV 输出严重欠佳，method 触发并修复
./refine-logs/B7_RESULTS.md:89:2. **触发条件**：当 PartUV produce 明显欠佳的 atlas（low PSNR, low utilization, unconstrained chart structure）时才触发；其他情况 C5 rollback
./refine-logs/FINAL_PROPOSAL.md:5:AI-generated 或 noisy mesh 即使已有可用 UV atlas，也经常在固定 DCC texture budget 下出现 PBR baking residual、mip leakage、seam ringing 与 relighting artifact。本文不重新发明全局 UV unwrapping，而是在 PartUV/FlexPara/classical unwrap 的初始化上，只对 high-residual charts 做局部 repair、texel reallocation 与 cross-channel seam control。核心问题是：在相同 atlas size、padding、chart-count/distortion guard 下，如何让标准单套 UV atlas 更好地服务 albedo/normal/roughness/metallic 的 bake 与 relight。成功标准是 synthetic oracle PBR 与 generated predicted-PBR 两条线都显示 relit error、channel residual 和 seam map 稳定下降，而几何 distortion 与 DCC 可用性不退化。
./refine-logs/FINAL_PROPOSAL.md:13:到 2026-04，PartUV (arXiv:2511.16659v2) 已经覆盖 AI-generated mesh 的 part-aware unwrapping，FlexPara (arXiv:2504.19210v3) 已经覆盖 flexible neural parameterization，OT-UVGS (arXiv:2604.19127v1) 也把 Gaussian UV 写成 fixed-budget capacity allocation。新的 bar 不应是“再做一个 unwrap”，而应证明 UV atlas 是否真正改善 generated asset 在 PBR baking、mip、seam 和 relighting 下的可用性。PG/CGF 评审会要求同等 atlas size、padding、chart-count 和 distortion guard，因此本文把贡献压到 residual attribution、local edit、mip allocation、cross-channel seam coupling 和 matched-control validation。这个 framing 比 PartUV/FlexPara 高一档，因为它评价并优化 downstream appearance physics，而不是只优化 chart geometry。
./refine-logs/FINAL_PROPOSAL.md:79:- **训练时 vs 推理时行为**: 训练阶段只学习 edit weights 和 thresholds；推理阶段固定 PartUV/FlexPara/classical output 为 \(U_0\)，执行 deterministic top-\(K\) local repair，并输出 edit budget 报告。
./refine-logs/FINAL_PROPOSAL.md:109:- **训练时 vs 推理时行为**: 训练阶段在 oracle set 上拟合 \(\alpha,\beta,\gamma,\delta,\tau\) 的小网格或 tiny MLP scorer；推理阶段使用固定 scorer 重新缩放 charts，并保持 atlas size、padding、chart count matched controls。
./refine-logs/FINAL_PROPOSAL.md:137:- **Input → Output**: baseline atlas \(U_0\)、candidate atlas \(U'\)、matched settings \((S,padding,|\mathcal{C}|,D_{tail})\)、held-out views/lights → accept/reject decision、residual atlas → chart edit → relit/seam improvement 主图。
./refine-logs/FINAL_PROPOSAL.md:175:  4. 用固定 1K/2K atlas、相同 padding、相同 baker，对 PartUV/FlexPara/classical UV 和本方法 bake PBR maps。
./refine-logs/FINAL_PROPOSAL.md:182:| PartUV: Part-Based UV Unwrapping of 3D Meshes | 2511.16659v2 | 最直接的 AI/noisy mesh UV baseline，覆盖 part-aware charting、少 chart count、低 seam length；本方法固定其输出再做 local repair | inference-only；作为 initialization 与 baseline |
./refine-logs/FINAL_PROPOSAL.md:183:| FlexPara: Flexible Neural Surface Parameterization | 2504.19210v3 | neural global/multi-chart parameterization baseline，覆盖 flexible chart assignment；用于证明不是 another neural parameterization | 若代码/checkpoint 可用则 inference-only，否则复现实验小子集 |
./refine-logs/FINAL_PROPOSAL.md:211:## Ablations（≥7，含 ≥2 反向证明 design choice 必要性）
./refine-logs/FINAL_PROPOSAL.md:218:6. **Reverse proof A, overbuilt global re-unwrap**: 允许全局重新 parameterization；若 distortion/chart count 改善但 matched relit gain 不稳定，证明本文 local repair 更克制且可解释。
./refine-logs/FINAL_PROPOSAL.md:229:| W1 | B1 oracle PBR baker、held-out view/light split、metric determinism、on-the-fly rendering cache policy | B2 xatlas/Blender/UVAtlas + PartUV install，40-asset baseline pilot | residual attribution sanity table；确认 `/data` 不缓存 multi-light renders |
./refine-logs/FINAL_PROPOSAL.md:232:| W4 | B3 finish: Thingi10K stress、generated subset、selected 2K reruns；B6 residual-chain figure seed | B5 matched controls + B4 A10-A13: utilization、distortion、padding、chart-count | **first PR-able results**: main table + matched-control table + residual atlas -> chart edit -> relight/seam figure |
./refine-logs/FINAL_PROPOSAL.md:241:| PartUV/FlexPara baseline 跑不通 | MEDIUM | W2 结束仍不能稳定生成 atlas 或 license/代码阻塞 | 用 xatlas/Blender/UVAtlas + PartUV sample + FlexPara verified subset；失败率进 appendix，不静默丢弃 |
./refine-logs/FINAL_PROPOSAL.md:243:| C3 gain 来自 packing utilization | MEDIUM | matched-utilization control 后 relit PSNR gain < +0.3 dB | 降低 C3 claim，转为 mip leakage diagnostic；主 claim 改由 C1+C2+C4 支撑 |
./refine-logs/FINAL_PROPOSAL.md:253:若 PG 6 周内主实验或 PartUV/FlexPara matched controls 不完整，降级为 PRCV2026 framing：题目改为 **Benchmarking and Local Repair of PBR Baking Artifacts in Generated Mesh Atlases**。贡献从 PG 的 principled atlas optimization 降为 CV/PR 友好的 generated asset post-processing benchmark + lightweight local repair；主表只保留 ShapeNet/Objaverse/Thingi10K 三个 subset、PartUV/classical/mesh-adapted capacity 三类 baseline、C1/C2/C4 三个核心 ablation。删除 user study 和部分 2K 结果，把重点放在 oracle vs predicted-PBR confound、residual heatmap 可解释性、以及 generated mesh cleanup pipeline 可复现性。
./refine-logs/B2_RESULTS.md:6:**Verdict**: ⚠️ **PARTIAL** — scaffold + matched-protocol enforcement in place; 2/9 baselines fully verified, 4/9 proxy (real repos cloned but not integrated), 3/9 failed
./refine-logs/B2_RESULTS.md:12:| ✅ Real & matched-OK | 1 | xatlas_classical | 完整 xatlas Python API；matched-protocol 全部满足 |
./refine-logs/B2_RESULTS.md:13:| ✅ Real & matched-violator | 1 | blender_uv | Blender 3.0.1 Smart UV；不同范式（chart 数 ≪ xatlas），matched-protocol 违规属预期 |
./refine-logs/B2_RESULTS.md:14:| ⚠️ Real reference (理论上界) | 1 | matched_oracle | 自实现 ground-truth UV reference（PSNR=∞） |
./refine-logs/B2_RESULTS.md:24:| bunny | matched_oracle | inf | 1.000 | 0.000 | 0.0000 | 0.727 | 8 | 0.371 | 20.0 | ❌ util |
./refine-logs/B2_RESULTS.md:27:| spot | matched_oracle | inf | 1.000 | 0.000 | 0.0000 | 0.666 | 91 | 0.374 | 28.0 | ❌ util |
./refine-logs/B2_RESULTS.md:30:| objaverse | matched_oracle | inf | 1.000 | 0.000 | 0.0000 | 0.883 | 6 | 0.713 | 1.3 | ✅ |
./refine-logs/B2_RESULTS.md:34:PartUV / FlexPara / OT-UVGS / VisibilityParam (arXiv:2509.25094v3 attempt) 都使用启发式 proxy 替代真实 repo inference。结果数字仅供 sanity，**绝不能在 paper 中作为"我们 reproduce 了 X 方法"的 claim**。
./refine-logs/B2_RESULTS.md:43:| matched_protocol enforce + violator detection | yes | 完整实现 + 13/27 pass + 6/27 violator + 8/27 N/A | ✅ |
./refine-logs/B2_RESULTS.md:51:**可作为 B3 主结果对照的"真"baseline 只有 2 个**：xatlas_classical（强对照）+ matched_oracle（理论上界）。
./refine-logs/B2_RESULTS.md:54:1. 至少把 PartUV (arXiv:2511.16659v2) 真正接入 — repo 已 clone 在 `/data/dip_1_ws/baseline_repos/PartUV/`
./refine-logs/B2_RESULTS.md:56:3. 不接入也行，但 paper §Baselines 必须**显式说明** PartUV/FlexPara 在我们环境无法复现，failure table 在 appendix 列出，且去除"我们和 PartUV 比"的措辞，改为"我们参考 PartUV gap analysis"
./refine-logs/B2_RESULTS.md:71:- 代码: `pbr_atlas/baselines/{base,xatlas_classical,blender_uv,partuv,flexpara,otuvgs,flatten_anything,parapoint,visibility_param,matched_oracle,matched_protocol,baseline_failure_table}.py`
./refine-logs/B3_RESULTS.md:25:| spot | matched_oracle | inf | inf | -- | ROLLBACK | 2348 | 14 |
./refine-logs/B3_RESULTS.md:29:| bunny | matched_oracle | inf | inf | -- | ROLLBACK | 1606 | 2 |
./refine-logs/B3_RESULTS.md:33:| objaverse | matched_oracle | inf | inf | -- | ROLLBACK | 132 | 1 |
./refine-logs/B3_RESULTS.md:39:| ACCEPT (rollback=False) | 2 | True | True | 真改善：matched-protocol 满足 + ΔPSNR ≥ threshold + ΔSeam ≤ threshold |
./refine-logs/B3_RESULTS.md:40:| ROLLBACK (rollback=True) | 10 | True | False | 改善不足：matched-protocol 满足但 ΔPSNR / ΔSeam 未达阈值 → 回退 baseline |
./refine-logs/B3_RESULTS.md:41:| HARD_REJECT | 0 | False | -- | matched-protocol 违反（atlas size/padding/chart-count/distortion 越界） |
./refine-logs/B3_RESULTS.md:72:| C5 Gain 不来自 predictor bias / 大 atlas / 松约束 | ⏳ 待 B5 | matched-control 已 enforce + rollback 已 verify；matched_after_repair 仍 violation 待补 |
./refine-logs/B3_RESULTS.md:85:- B5: matched-control confounds（关键守门）
./refine-logs/B3_RESULTS.md:93:- Code: `pbr_atlas/method/{chart_repair,texel_alloc,seam_coupling,signals}.py` + `scripts/run_B3.py`
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:160:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:247:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:252:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:1612:    "seed": 7108,
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2929:  "matched_protocol_initial": {
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2934:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2964:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2965:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2966:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2967:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2968:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2969:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:2970:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_pinched_ico_partuv_ours_seed42/metrics.json:4812:  "seed": 42,
./refine-logs/B1_RESULTS.md:14:| Metric determinism (same seed → same output) | e_f / E_c / G_l diff=0 | diff=0 全部 | ✅ |
./refine-logs/B1_RESULTS.md:51:### Determinism Check (Bunny, seed=42, 跑两次)
./refine-logs/B1_RESULTS.md:74:4. **Determinism 保证**：CUBLAS_WORKSPACE_CONFIG warning 无影响（可选 export 提升严格度），seed 固定下完全 reproducible
./refine-logs/B1_RESULTS.md:85:- PartUV (arXiv:2511.16659v2) atlas → C1 bake on bunny/spot/objaverse
./refine-logs/B1_RESULTS.md:94:  - 20260428_001833_bunny_seed42/ (metrics.json, residual_atlas.npz/png, summary.md)
./refine-logs/B1_RESULTS.md:95:  - 20260428_001949_spot_seed42/
./refine-logs/B1_RESULTS.md:96:  - determinism_20260428_001910_bunny_seed42_{a,b}/ + .json verdict
./refine-logs/PIPELINE_SUMMARY.md:12:| Ablations | 11 | 18, including matched utilization/distortion/padding/chart-count and texture/BRDF/light sweeps |
./refine-logs/PIPELINE_SUMMARY.md:13:| Baselines / controls | 4-5 | 8: PartUV, FlexPara, xatlas/classical, OT-UVGS-adapted, Flatten Anything, ParaPoint, TexSpot, Chord |
./refine-logs/PIPELINE_SUMMARY.md:23:| W1 | B1 baker sanity, metric determinism, storage-safe on-the-fly rendering; xatlas/PartUV pilot. |
./refine-logs/PIPELINE_SUMMARY.md:26:| W4 | B3 finish on GPU0 while B5 matched controls and A10-A13 run on GPU1; B6 residual-chain seed starts. |
./refine-logs/PIPELINE_SUMMARY.md:37:- Early ablation evidence: C1-C4 removal plus matched-control deltas.
./refine-logs/B4_RESULTS.md:4:**Block**: B4 Full Design-Choice Ablation Matrix (290 GPU h budget; **used: ~17 GPU h**)
./refine-logs/B4_RESULTS.md:6:**Verdict**: ✅ **C1/C2/C3/C5 design choices VALIDATED**；2-3 个 ablation 需 code review (A1/A5/A9 zero-signal)
./refine-logs/B4_RESULTS.md:25:**Matched controls A10-A13**：全 0 ΔPSNR（matched_OK=yes）→ C5 锁定 atlas size/util/distortion/chart-count 时无 spurious gain，证 method 不偷数。
./refine-logs/B4_RESULTS.md:40:| A10-A13 | matched 仍 +0.3dB / seam -8% | **all 0.00 + matched OK** | ⚠️ 锁住后 method 无 gain → 待修：method 应在 matched-control 下仍能改善 |
./refine-logs/B4_RESULTS.md:50:2. **A10-A13 matched control 锁定后 method 无 gain**：暗示 spot/partuv 的 +14.67 dB 部分来自 atlas size/util 变化，不全是 method 本身。需 paper 中诚实承认
./refine-logs/B4_RESULTS.md:71:- **B5 Matched-Control**: A10-A13 已部分覆盖；显示 method 在 matched constraint 下 ΔPSNR=0 → 必须重新设计 method 或承认部分 gain 来自 unconstrained variation
./refine-logs/B4_RESULTS.md:79:- 代码: `pbr_atlas/ablations/{a1..a18}_*.py + matched_controls.py + sweeps.py`
./refine-logs/B5_RESULTS.md:25:- ✅ **Atlas size**: locked at PartUV's default; method still works
./refine-logs/B5_RESULTS.md:27:- ✅ **Chart count**: locked at PartUV's count ±5%; method still works
./refine-logs/B5_RESULTS.md:33:- → Method's design intent: **trade higher distortion at high-residual charts for better PBR bake fidelity**
./refine-logs/B5_RESULTS.md:37:> Our method's gain over PartUV requires admitting localized changes in two
./refine-logs/B5_RESULTS.md:72:- `/data/dip_1_ws/runs/B5_matched/`（10 dirs + B5_TABLE.md）
./refine-logs/B5_RESULTS.md:73:- `pbr_atlas/ablations/b5_strict_matched.py`
./refine-logs/B2_REAL_BASELINES_REPORT.md:11:| **xatlas_classical** | xatlas Python pkg ✅ | real | ✅ REAL | matched-protocol pass on all 3 assets |
./refine-logs/B2_REAL_BASELINES_REPORT.md:12:| **blender_uv** | apt blender 3.0.1 ✅ | real（patched OBJ import API） | ✅ REAL | matched-protocol violator (Smart UV 不同范式，预期) |
./refine-logs/B2_REAL_BASELINES_REPORT.md:13:| **partuv** | repo cloned + bpy 4.5.9 ✅ | real（subprocess + UV island detection） | ✅ REAL | spot 19 charts / bunny 2 / objaverse 2；matched-protocol violator |
./refine-logs/B2_REAL_BASELINES_REPORT.md:14:| **matched_oracle** | self-implemented ✅ | real | ✅ REAL | 理论上界 PSNR=∞ |
./refine-logs/B2_REAL_BASELINES_REPORT.md:21:## 真实接入的 PartUV 数字（关键）
./refine-logs/B2_REAL_BASELINES_REPORT.md:23:| Asset | xatlas PSNR | partuv PSNR | xatlas charts | partuv charts | matched OK (xatlas) | matched OK (partuv) |
./refine-logs/B2_REAL_BASELINES_REPORT.md:29:PartUV 的低 PSNR 反映了其**部件感知 UV** 的设计：用更少更大的 chart 换取 part 边界对齐，distortion 显著高于 xatlas 但 chart 数大幅下降。这是真实 PartUV 行为，可作 paper 主对比的"part-aware UV vs distortion-min UV"叙事。
./refine-logs/B2_REAL_BASELINES_REPORT.md:49:PartUV wrapper 通过 subprocess 调用 partuv env 的 python，input mesh 经临时 OBJ 写入 → `demo/partuv_demo.py --pack_method blender` → 解析 `final_components.obj` + UV island detection → BaselineAtlas。
./refine-logs/B2_REAL_BASELINES_REPORT.md:54:1. **xatlas_classical**（matched-protocol 完全 pass，强基准）
./refine-logs/B2_REAL_BASELINES_REPORT.md:55:2. **PartUV**（matched-protocol violator 但 honest，证明部件感知 UV 与 distortion-min UV 的差异化）
./refine-logs/B2_REAL_BASELINES_REPORT.md:56:3. **matched_oracle**（理论上界）
./refine-logs/B2_REAL_BASELINES_REPORT.md:65:- `/data/dip_1_ws/baseline_repos/PartUV/`（clone + bpy + ckpt 全部就位）
./refine-logs/B2_REAL_BASELINES_REPORT.md:68:- `/data/dip_1_ws/runs/B2_baseline/{spot,bunny,objaverse}_partuv_seed42/`（真实 PartUV 输出）
./refine-logs/B2_REAL_BASELINES_REPORT.md:75:- [x] matched-protocol enforcement 真实工作（chart_count/util/distortion 都正确捕获 violator）
./refine-logs/EXPERIMENT_PLAN.md:13:| C2: High-residual local chart repair improves bake quality without becoming a new global UV parameterization method. | This keeps novelty away from PartUV/FlexPara and makes the contribution a constrained atlas repair loop. | Edited chart ratio <=15%, chart-count delta <=8%, distortion Q95 <= baseline +3%, seam residual -12% or better. | B3, B4, B5 |
./refine-logs/EXPERIMENT_PLAN.md:14:| C3: Mip-aware texel allocation improves relighting and leakage under the same atlas size. | It rules out the trivial explanation that gains come from more texture capacity. | Mip leakage G_c -15%, relit PSNR +0.3 dB after matched-utilization and matched-padding controls. | B3, B4, B5 |
./refine-logs/EXPERIMENT_PLAN.md:16:| C5: Gains are not explained by predictor bias, bigger atlas area, chart count, padding, or looser distortion. | This is the main rebuttal shield for PG/CGF. | Oracle-PBR keeps >=70% of predicted-PBR gain; matched-utilization, matched-distortion, matched-padding, and matched-chart-count controls remain positive. | B2, B5, B7 |
./refine-logs/EXPERIMENT_PLAN.md:20:- **Main paper must prove**: C1 residual attribution, C2 local repair, C3 fixed-budget mip allocation, C5 matched controls, and a visually interpretable residual atlas -> chart edit -> relight/seam improvement chain.
./refine-logs/EXPERIMENT_PLAN.md:21:- **Main paper should include**: B1 sanity, B2 baseline protocol, B3 main result, B4 core ablation summary, B5 matched controls, and B6 qualitative channel stress figures.
./refine-logs/EXPERIMENT_PLAN.md:29:| PartUV: Part-Based UV Unwrapping of 3D Meshes | 2511.16659v2 | github.com/EricWang12/PartUV | Strong generated/noisy mesh UV baseline and primary initialization. | Inference-only on all main assets when valid. |
./refine-logs/EXPERIMENT_PLAN.md:41:- **Main execution subset**: B3 uses 240 assets: ShapeNet oracle 80, Objaverse oracle/predicted 100, Thingi10K stress 40, generated stress 20. B2/B4/B5 use matched representative subsets to keep the 18 ablations within budget.
./refine-logs/EXPERIMENT_PLAN.md:42:- **Atlas settings**: 1K for all full-set comparisons; 2K for representative main assets; 4K only for A14 texture-size sweep. Padding defaults to 8 px unless matched-padding control changes it.
./refine-logs/EXPERIMENT_PLAN.md:53:- **Compared systems**: xatlas, PartUV if install succeeds, ours evaluator-only without repair.
./refine-logs/EXPERIMENT_PLAN.md:55:- **Setup details**: PyTorch3D/nvdiffrast or Mitsuba/Blender oracle; GGX default; Adam for texel maps, 300 iterations per asset; seeds=3 on 10 stochastic assets.
./refine-logs/EXPERIMENT_PLAN.md:67:- **Compared systems**: PartUV, FlexPara, xatlas/Blender/UVAtlas, mesh-adapted OT-UVGS, Flatten Anything, ParaPoint subset, TexSpot adjacent, Chord predictor control.
./refine-logs/EXPERIMENT_PLAN.md:71:- **Failure interpretation**: If a neural baseline blocks, move it to verified subset and keep PartUV + xatlas + FlexPara subset + OT-UVGS control complete.
./refine-logs/EXPERIMENT_PLAN.md:81:- **Compared systems**: strongest valid baseline per asset, PartUV init + ours, FlexPara init + ours, xatlas init + ours, OT-UVGS-adapted allocation control.
./refine-logs/EXPERIMENT_PLAN.md:83:- **Setup details**: final method C1+C2+C3+C4+C5; top-K <=15% charts; distortion guard Q95 <= baseline +3%; chart-count delta <=8%; seeds=3 on 60 stochastic assets.
./refine-logs/EXPERIMENT_PLAN.md:90:### B4: Full Design-Choice Ablation Matrix
./refine-logs/EXPERIMENT_PLAN.md:93:- **Why this block exists**: The paper needs reverse proof that each design choice prevents a specific failure mode.
./refine-logs/EXPERIMENT_PLAN.md:97:- **Setup details**: GPU1 runs most B4 variants while GPU0 runs B3; seeds=3 for A1-A9, seeds=1 for mechanical sweeps A10-A18 unless variance is high.
./refine-logs/EXPERIMENT_PLAN.md:106:| ID | Ablation / Control | Design Choice Tested | Expected Metric Delta vs Final Method |
./refine-logs/EXPERIMENT_PLAN.md:108:| A1 | No C1 differentiable PBR baker, distortion-only objective | PBR residual is the right signal. | relit PSNR -0.5 to -0.8 dB; LPIPS +0.012; residual localization hit rate -20 pp. |
./refine-logs/EXPERIMENT_PLAN.md:132:- **Compared systems**: final method vs strongest baseline under matched utilization, matched distortion Q95, matched padding, matched chart count +/-5%, same atlas size.
./refine-logs/EXPERIMENT_PLAN.md:134:- **Setup details**: C5 accept/reject guard is enforced before metrics are counted; unmatched outputs are reported as guard failures.
./refine-logs/EXPERIMENT_PLAN.md:135:- **Success criterion**: matched-utilization PSNR gain >=+0.3 dB; matched-distortion seam residual <=-8%; matched-padding seam residual <=-8%; matched-chart-count chart delta <=5% with positive relit/seam gains.
./refine-logs/EXPERIMENT_PLAN.md:136:- **Failure interpretation**: If matched controls erase all gains, pivot to diagnostic benchmark. If only C3 disappears, keep C1+C2+C4 as main claim and move C3 to appendix.
./refine-logs/EXPERIMENT_PLAN.md:146:- **Compared systems**: final method, no C4, RGB-only baker, xatlas, PartUV, FlexPara subset.
./refine-logs/EXPERIMENT_PLAN.md:175:- **Compared systems**: ours vs strongest baseline per asset, ours vs xatlas/classical, and ours vs PartUV/FlexPara where available.
./refine-logs/EXPERIMENT_PLAN.md:178:- **Success criterion**: >=60% prefer ours over the strongest baseline; >=75% prefer ours over classical xatlas; binomial confidence reported with participant-level bootstrap.
./refine-logs/EXPERIMENT_PLAN.md:189:- **Compared systems**: final method with frame-wise repair, temporal-warm-start repair, xatlas/PartUV baseline where applicable.
./refine-logs/EXPERIMENT_PLAN.md:202:| W1 | B1 oracle baker, metric determinism, on-the-fly rendering cache policy | B2 xatlas/PartUV install and 40-asset baseline pilot | B1 PSNR >=28 dB and residual maps sensible | Sanity table, storage-safe pipeline |
./refine-logs/EXPERIMENT_PLAN.md:205:| W4 | Finish B3 main tables, start B6 channel stress / residual-chain figures | B5 matched controls plus B4 A10-A13 | First PR-able result: main table + matched controls + residual chain | PR-able package for review |
./refine-logs/EXPERIMENT_PLAN.md:228:- **Biggest bottleneck**: baseline reproducibility and matched-control bookkeeping, not model training.
./refine-logs/EXPERIMENT_PLAN.md:233:- **B2 baseline reproduction incomplete by end of W2**: keep xatlas + PartUV + FlexPara subset + mesh-adapted OT-UVGS; move failed neural baselines to documented appendix subset.
./refine-logs/EXPERIMENT_PLAN.md:237:- **B5 matched controls erase gains**: if all erased, downgrade to diagnostic benchmark; if only C3 erased, keep C1+C2+C4.
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:64:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:149:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:154:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1009:    "seed": 7103,
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1822:  "matched_protocol_initial": {
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1827:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1856:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/atlas.npz",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1857:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1858:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/repair_log.json",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1859:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/residual_chain.png",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1860:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1861:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/residual_atlas.png",
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:1862:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/summary.md"
./runs/B7_transfer/proc_crumpled_box_partuv_ours_seed42/metrics.json:2768:  "seed": 42,
./refine-logs/EXPERIMENT_TRACKER.md:5:| B1-001 | B1 | bunny (procedural fallback), seed=42, 1024px atlas, 6 train + 4 holdout view, 4+4 light, bf16 | 0.003 | ✅ DONE | PSNR 27.88 / SSIM 0.857 / LPIPS 0.234 / max e_f 0.326 / G_l 0.889 / peak mem 0.57 GB / wall 9.6s | C1 baker forward+backward 跑通；procedural fallback bunny normals 较 noisy 导致 normal MAE 40°；output 0.08 MB ✅ storage-safe |
./refine-logs/EXPERIMENT_TRACKER.md:6:| B1-DET | B1 | bunny, seed=42, run twice | 0.006 | ✅ DONE | e_f / E_c / G_l diff = 0 全部精确一致 | Determinism check **PASS**；CUBLAS_WORKSPACE_CONFIG warning 无影响实际确定性 |
./refine-logs/EXPERIMENT_TRACKER.md:7:| B1-002 | B1 | spot (real UV mesh), seed=42, same config | 0.003 | ✅ DONE | PSNR 33.40 / SSIM 0.932 / LPIPS 0.095 / max e_f 0.082 / G_l 0.0 / peak mem 0.57 GB | 真实 UV → 显著好于 procedural bunny；G_l=0 说明 Spot atlas 无 mip 漏色（baseline 验证 method 在干净 atlas 上行为正确）|
./refine-logs/EXPERIMENT_TRACKER.md:8:| B1-003 (待跑) | B1 | objaverse (procedural fallback), seed=42 | ~0.003 | PENDING | — | objaverse HF 实时下载未启用，procedural fallback 有效；可选作 robustness sanity |
./refine-logs/EXPERIMENT_TRACKER.md:17:- Determinism PASS：同 seed 完全 reproducible
./refine-logs/EXPERIMENT_TRACKER.md:24:- ✅ Determinism guaranteed under fixed seed
./refine-logs/EXPERIMENT_TRACKER.md:30:进入 B2 Baseline Reproduction（PartUV / FlexPara / classical xatlas / OT-UVGS adapted），或先在 1-2 个 Objaverse 真实 asset 上做扩展 sanity（B1-extra）。
./refine-logs/BEAST_8.0_PLAN.md:2:The real ceiling is not writing. R9 is reacting to a claim-evidence mismatch: [Sec. 3 explicitly says real production needs captured validation renders or a trusted estimator, then says that regime is not evaluated](/Users/jacksonhuang/project/dip_1_ws/paper/sections/3_method.tex:18). The current evidence is strong only for selective repair of weak PartUV-style atlases: [2/12 main accepts](/Users/jacksonhuang/project/dip_1_ws/paper/sections/4_experiments.tex:27), [3/20 headline accepts](/Users/jacksonhuang/project/dip_1_ws/paper/sections/5_confounds.tex:31), and [2/5 SDS-init real accepts](/Users/jacksonhuang/project/dip_1_ws/paper/sections/4_experiments.tex:70). To cross 8.0, you need one acceptance-critical new evidence block, not more polish.
./refine-logs/BEAST_8.0_PLAN.md:8:| 1 | **Captured-Relighting Validation on DiLiGenT-MV**. Add a small “captured target signal” benchmark where `I*` is real imagery, not oracle renders. DiLiGenT-MV has 5 objects, 20 views, 96 calibrated lights/view, and GT meshes. This directly answers R9 critical. | Experimental +0.7, soundness +0.2, overall +0.35–0.55. | Use `mesh_Gt.ply`; simplify to 5k–15k faces; generate xatlas/Blender/PartUV where feasible. Split captured images into proposal/gate/test over views/lights. Fit/bake atlas textures from proposal subset, C5 on gate, report masked captured PSNR/SSIM/LPIPS on test. Bootstrap over view-light pairs; paired object-level sign/permutation test. | 70–120 GPU h, 1.5–2 weeks. | 0.55. Dataset is small, but BRDF/camera mismatch may dominate. | If positive: main paper. If mixed: show C5 mostly rolls back and title becomes “when captured validation renders are available.” If negative: production claim must be demoted. |
./refine-logs/BEAST_8.0_PLAN.md:9:| 2 | **OpenSubstance/PolyHaven Two-Tier Real-PBR Track**. OpenSubstance is ideal but huge; Poly Haven is not captured validation, but gives CC0 artist/photoscanned PBR assets. Use as fallback “production PBR asset” validation, not a substitute for captured. | Experimental +0.2–0.4, visual +0.2. | First try 3–5 OpenSubstance rigid objects if accessible; otherwise 12 Poly Haven models with CC0 PBR maps + HDRI relighting. Same baselines, same C5, report trigger/failure taxonomy. | 30–80 GPU h, 1 week. | 0.65 for Poly Haven, 0.25 for OpenSubstance access. | If no captured images, label it “production-PBR asset proxy,” not “captured-PBR.” |
./refine-logs/BEAST_8.0_PLAN.md:10:| 3 | **Replace FlexPara Chase with Semantic-Visibility UV Baseline**. FlexPara is still a poor critical path: repo wants Python 3.9, Torch 1.10.1/cu111, CD/EMD custom ops, and 10k per-mesh training; your local wrapper documents the same blockers in [flexpara.py](/Users/jacksonhuang/project/dip_1_ws/pbr_atlas/baselines/flexpara.py:3). The 2025/ICLR2026 semantic-visibility UV repo is more relevant and cu128-aligned. | Baselines +0.5–0.7, novelty positioning +0.1, overall +0.12–0.22. | Run visibility-only pipeline on spot/bunny/Objaverse + 5 DiLiGenT/PolyHaven meshes. Compare xatlas, PartUV, SemVis-UV, ours-on-PartUV. Metrics: relit error, seam visibility, chart count, distortion, semantic/visibility seam proxy. | 40–80 GPU h, 1 week. | 0.45. Still custom CD/EMD, but newer stack is closer. | If fails, cite as attempted 2026 baseline with precise failure; do not spend more than 3 days. |
./refine-logs/BEAST_8.0_PLAN.md:11:| 4 | **PartUV Cache + Simplified Real-Mesh Sweep**. Current bottleneck is upstream PartUV, not your baker; the wrapper invokes `demo/partuv_demo.py` with a 600s timeout in [partuv.py](/Users/jacksonhuang/project/dip_1_ws/pbr_atlas/baselines/partuv.py:80). Cache outputs by mesh hash, call PartUV API directly, and decimate large meshes. | Experimental +0.3–0.5, reproducibility +0.3. | For the 18 deferred meshes: decimate to 5k/10k/20k faces; cache `final_components.obj`; run xatlas and PartUV only once per mesh; run ours with 3 split seeds only on accepts and 3 representative rollbacks. | 50–90 GPU h, 1 week. | 0.60. Decimation may alter PartUV semantics but is defensible if logged. | If PartUV still stalls, report xatlas/SemVis/Blender real sweep and keep PartUV deferred. |
./refine-logs/BEAST_8.0_PLAN.md:12:| 5 | **Target-Signal Confound Test**. Synthetic but decisive: separate UV error from material-estimator error so reviewers trust captured/predicted targets. | Soundness +0.3, reproducibility +0.1. | 30 controlled assets: UV-only defect, material-only noise, mixed defect. Success if C5 accepts UV-only, rolls back material-only, and residual boundary concentration predicts accept. Metrics: false accept, false rollback, residual-boundary Gini, PSNR. | 15–25 GPU h, 3–4 days. | 0.75. You control the stress. | If C5 repairs material-only noise, tighten claim and add limitation. |
./refine-logs/BEAST_8.0_PLAN.md:14:| 7 | **Mip Leakage Isolation**. Current A18 is weak because mip is only one term in a demand mix; [texel_alloc.py](/Users/jacksonhuang/project/dip_1_ws/pbr_atlas/method/texel_alloc.py:93) lets residual/visibility/frequency dominate. | Soundness +0.1. | Equal-residual synthetic charts with high-frequency roughness/albedo near boundaries; render minified far/grazing views. Compare mip-only, no-mip, residual-only. Metrics: `G_l`, far-view LPIPS, halo width. | 15–25 GPU h, 3 days. | 0.60. Easy to force signal if implementation is real. | If weak, demote explicit mip term; keep C3 as residual allocation. |
./refine-logs/BEAST_8.0_PLAN.md:15:| 8 | **Statistical Power Upgrade**. Cheap credibility lift. | Experimental +0.2, reproducibility +0.2. | n=10 splits for spot/PartUV, bunny/PartUV, warped-cylinder, 2 real accepts, 4 rollback controls. Report mean±CI, paired bootstrap, Wilcoxon/sign test over assets, and C5 threshold sensitivity. | 20–40 GPU h, 4 days. | 0.85. Existing runs are cheap. | If variance is high, show gate stability and failure modes. |
./refine-logs/BEAST_8.0_PLAN.md:16:| 9 | **Visual Final Push**. The current figure is improved but dark/dense. | Visual +0.4–0.6, overall +0.08–0.12. | Split Fig. 4 into main 2-row figure + supplemental gallery. Add bright exposure, seam/mip zoom insets, xatlas side panel, chart overlay, and captured validation crops. | 5–10 GPU h, 4–5 days. | 0.90. Mostly rendering/layout. | If captured fails, still use accepted controlled/real cases. |
./refine-logs/BEAST_8.0_PLAN.md:17:| 10 | **Reframe and Scope Lock**. Yes, the paper benefits from renarration. Make it “PBR relighting residual as a deployment signal for selective local atlas repair,” not a deployment-ready generated-asset UV method. | Claim alignment +0.2, reduces reviewer friction. | Rewrite title/abstract/contribs around available target signal; move C4/mip weak claims to diagnostics; stop implying Trellis/GET3D breadth unless new data lands. | 0 GPU h, 3 days. | 0.95. | If captured succeeds, keep production language but only for “with validation renders.” |
./refine-logs/BEAST_8.0_PLAN.md:21:Best ROI: reframe, visual insets, stats/CI, target-signal confound, DiLiGenT-MV captured validation, SemVis baseline, PartUV real sweep, C4/mip stress, FlexPara salvage. I would explicitly **not** put FlexPara on the critical path; the official repo itself still asks for the old Torch/cu111 stack, while PartUV and Semantic-Visibility have more current installation paths.
./refine-logs/BEAST_8.0_PLAN.md:23:Useful external sources: DiLiGenT-MV has the exact small captured-lighting/GT-mesh structure you need; OpenIllumination is real multi-illumination but huge and not mesh-ground-truth focused; OpenSubstance is best-in-class but likely access/size risky; Poly Haven is CC0 PBR asset proxy; Objects With Lighting is useful for relighting protocol but not direct mesh-UV validation. Sources: [DiLiGenT-MV](https://sites.google.com/site/photometricstereodata/mv), [OpenIllumination](https://huggingface.co/datasets/OpenIllumination/OpenIllumination), [OpenSubstance](https://openaccess.thecvf.com/content/ICCV2025/html/Pei_OpenSubstance_A_High-quality_Measured_Dataset_of_Multi-View_and_-Lighting_Images_ICCV_2025_paper.html), [Poly Haven](https://polyhaven.com/), [Objects With Lighting](https://github.com/isl-org/objects-with-lighting), [Semantic-Visibility UV](https://github.com/AHHHZ975/Semantic-Visibility-UV-Param), [FlexPara](https://github.com/AidenZhao/FlexPara), [PartUV](https://github.com/EricWang12/PartUV).
./refine-logs/BEAST_8.0_PLAN.md:25:Honest verdict: 8.0 is attainable only if the captured-relighting block works or the SemVis/real-sweep block is surprisingly strong. Without that, the paper is structurally capped around 7.6–7.8: useful, honest, narrow, but not enough external validation for PG/CGF. With a positive DiLiGenT-MV result plus better visuals and stats, I can see a fresh reviewer giving 8.0–8.2 despite novelty staying around 7.2.
./refine-logs/BEAST_8.0_PLAN.md:29:Week 1: Freeze narrower claims; implement captured-image target adapter; download DiLiGenT-MV; add PartUV atlas cache/hash; start visual redesign.
./refine-logs/BEAST_8.0_PLAN.md:30:Week 2: Run DiLiGenT-MV 5-object captured validation with xatlas/Blender/PartUV-feasible/ours; run target-signal confound test; install SemVis-UV with a 3-day kill switch.
./refine-logs/BEAST_8.0_PLAN.md:31:Week 3: Expand real-PBR proxy set via Poly Haven or OpenSubstance subset; run SemVis baseline if alive; run PartUV simplified/cache sweep on deferred meshes; start n=10 split reruns.
./refine-logs/BEAST_8.0_PLAN.md:32:Week 4: Run C4 and mip stress tests only if Week 2–3 are not blocked; finalize bootstrap/sign-test analysis; rebuild main visual figure with zoomed captured and accepted-case crops.
./refine-logs/BEAST_8.0_PLAN.md:33:Week 5: Rewrite title/abstract/contribs around captured/validated target signal; demote failed C4/mip/FlexPara honestly; compile, sanity-review, and get one fresh external read.
./refine-logs/BEAST_8.0_PLAN.md:42:- Reframe as a selective deployment-signal paper, not a production-ready generated-asset UV method.
./refine-logs/BEAST_8.0_PLAN.md:45:- If captured validation is negative, target a narrower benchmark/post-processing venue or defer PG until a real captured-PBR/real-asset benchmark is genuinely complete.
./refine-logs/BEAST_8.0_PLAN.md:49:The real ceiling is not writing. R9 is reacting to a claim-evidence mismatch: [Sec. 3 explicitly says real production needs captured validation renders or a trusted estimator, then says that regime is not evaluated](/Users/jacksonhuang/project/dip_1_ws/paper/sections/3_method.tex:18). The current evidence is strong only for selective repair of weak PartUV-style atlases: [2/12 main accepts](/Users/jacksonhuang/project/dip_1_ws/paper/sections/4_experiments.tex:27), [3/20 headline accepts](/Users/jacksonhuang/project/dip_1_ws/paper/sections/5_confounds.tex:31), and [2/5 SDS-init real accepts](/Users/jacksonhuang/project/dip_1_ws/paper/sections/4_experiments.tex:70). To cross 8.0, you need one acceptance-critical new evidence block, not more polish.
./refine-logs/BEAST_8.0_PLAN.md:55:| 1 | **Captured-Relighting Validation on DiLiGenT-MV**. Add a small “captured target signal” benchmark where `I*` is real imagery, not oracle renders. DiLiGenT-MV has 5 objects, 20 views, 96 calibrated lights/view, and GT meshes. This directly answers R9 critical. | Experimental +0.7, soundness +0.2, overall +0.35–0.55. | Use `mesh_Gt.ply`; simplify to 5k–15k faces; generate xatlas/Blender/PartUV where feasible. Split captured images into proposal/gate/test over views/lights. Fit/bake atlas textures from proposal subset, C5 on gate, report masked captured PSNR/SSIM/LPIPS on test. Bootstrap over view-light pairs; paired object-level sign/permutation test. | 70–120 GPU h, 1.5–2 weeks. | 0.55. Dataset is small, but BRDF/camera mismatch may dominate. | If positive: main paper. If mixed: show C5 mostly rolls back and title becomes “when captured validation renders are available.” If negative: production claim must be demoted. |
./refine-logs/BEAST_8.0_PLAN.md:56:| 2 | **OpenSubstance/PolyHaven Two-Tier Real-PBR Track**. OpenSubstance is ideal but huge; Poly Haven is not captured validation, but gives CC0 artist/photoscanned PBR assets. Use as fallback “production PBR asset” validation, not a substitute for captured. | Experimental +0.2–0.4, visual +0.2. | First try 3–5 OpenSubstance rigid objects if accessible; otherwise 12 Poly Haven models with CC0 PBR maps + HDRI relighting. Same baselines, same C5, report trigger/failure taxonomy. | 30–80 GPU h, 1 week. | 0.65 for Poly Haven, 0.25 for OpenSubstance access. | If no captured images, label it “production-PBR asset proxy,” not “captured-PBR.” |
./refine-logs/BEAST_8.0_PLAN.md:57:| 3 | **Replace FlexPara Chase with Semantic-Visibility UV Baseline**. FlexPara is still a poor critical path: repo wants Python 3.9, Torch 1.10.1/cu111, CD/EMD custom ops, and 10k per-mesh training; your local wrapper documents the same blockers in [flexpara.py](/Users/jacksonhuang/project/dip_1_ws/pbr_atlas/baselines/flexpara.py:3). The 2025/ICLR2026 semantic-visibility UV repo is more relevant and cu128-aligned. | Baselines +0.5–0.7, novelty positioning +0.1, overall +0.12–0.22. | Run visibility-only pipeline on spot/bunny/Objaverse + 5 DiLiGenT/PolyHaven meshes. Compare xatlas, PartUV, SemVis-UV, ours-on-PartUV. Metrics: relit error, seam visibility, chart count, distortion, semantic/visibility seam proxy. | 40–80 GPU h, 1 week. | 0.45. Still custom CD/EMD, but newer stack is closer. | If fails, cite as attempted 2026 baseline with precise failure; do not spend more than 3 days. |
./refine-logs/BEAST_8.0_PLAN.md:58:| 4 | **PartUV Cache + Simplified Real-Mesh Sweep**. Current bottleneck is upstream PartUV, not your baker; the wrapper invokes `demo/partuv_demo.py` with a 600s timeout in [partuv.py](/Users/jacksonhuang/project/dip_1_ws/pbr_atlas/baselines/partuv.py:80). Cache outputs by mesh hash, call PartUV API directly, and decimate large meshes. | Experimental +0.3–0.5, reproducibility +0.3. | For the 18 deferred meshes: decimate to 5k/10k/20k faces; cache `final_components.obj`; run xatlas and PartUV only once per mesh; run ours with 3 split seeds only on accepts and 3 representative rollbacks. | 50–90 GPU h, 1 week. | 0.60. Decimation may alter PartUV semantics but is defensible if logged. | If PartUV still stalls, report xatlas/SemVis/Blender real sweep and keep PartUV deferred. |
./refine-logs/BEAST_8.0_PLAN.md:59:| 5 | **Target-Signal Confound Test**. Synthetic but decisive: separate UV error from material-estimator error so reviewers trust captured/predicted targets. | Soundness +0.3, reproducibility +0.1. | 30 controlled assets: UV-only defect, material-only noise, mixed defect. Success if C5 accepts UV-only, rolls back material-only, and residual boundary concentration predicts accept. Metrics: false accept, false rollback, residual-boundary Gini, PSNR. | 15–25 GPU h, 3–4 days. | 0.75. You control the stress. | If C5 repairs material-only noise, tighten claim and add limitation. |
./refine-logs/BEAST_8.0_PLAN.md:61:| 7 | **Mip Leakage Isolation**. Current A18 is weak because mip is only one term in a demand mix; [texel_alloc.py](/Users/jacksonhuang/project/dip_1_ws/pbr_atlas/method/texel_alloc.py:93) lets residual/visibility/frequency dominate. | Soundness +0.1. | Equal-residual synthetic charts with high-frequency roughness/albedo near boundaries; render minified far/grazing views. Compare mip-only, no-mip, residual-only. Metrics: `G_l`, far-view LPIPS, halo width. | 15–25 GPU h, 3 days. | 0.60. Easy to force signal if implementation is real. | If weak, demote explicit mip term; keep C3 as residual allocation. |
./refine-logs/BEAST_8.0_PLAN.md:62:| 8 | **Statistical Power Upgrade**. Cheap credibility lift. | Experimental +0.2, reproducibility +0.2. | n=10 splits for spot/PartUV, bunny/PartUV, warped-cylinder, 2 real accepts, 4 rollback controls. Report mean±CI, paired bootstrap, Wilcoxon/sign test over assets, and C5 threshold sensitivity. | 20–40 GPU h, 4 days. | 0.85. Existing runs are cheap. | If variance is high, show gate stability and failure modes. |
./refine-logs/BEAST_8.0_PLAN.md:63:| 9 | **Visual Final Push**. The current figure is improved but dark/dense. | Visual +0.4–0.6, overall +0.08–0.12. | Split Fig. 4 into main 2-row figure + supplemental gallery. Add bright exposure, seam/mip zoom insets, xatlas side panel, chart overlay, and captured validation crops. | 5–10 GPU h, 4–5 days. | 0.90. Mostly rendering/layout. | If captured fails, still use accepted controlled/real cases. |
./refine-logs/BEAST_8.0_PLAN.md:64:| 10 | **Reframe and Scope Lock**. Yes, the paper benefits from renarration. Make it “PBR relighting residual as a deployment signal for selective local atlas repair,” not a deployment-ready generated-asset UV method. | Claim alignment +0.2, reduces reviewer friction. | Rewrite title/abstract/contribs around available target signal; move C4/mip weak claims to diagnostics; stop implying Trellis/GET3D breadth unless new data lands. | 0 GPU h, 3 days. | 0.95. | If captured succeeds, keep production language but only for “with validation renders.” |
./refine-logs/BEAST_8.0_PLAN.md:68:Best ROI: reframe, visual insets, stats/CI, target-signal confound, DiLiGenT-MV captured validation, SemVis baseline, PartUV real sweep, C4/mip stress, FlexPara salvage. I would explicitly **not** put FlexPara on the critical path; the official repo itself still asks for the old Torch/cu111 stack, while PartUV and Semantic-Visibility have more current installation paths.
./refine-logs/BEAST_8.0_PLAN.md:70:Useful external sources: DiLiGenT-MV has the exact small captured-lighting/GT-mesh structure you need; OpenIllumination is real multi-illumination but huge and not mesh-ground-truth focused; OpenSubstance is best-in-class but likely access/size risky; Poly Haven is CC0 PBR asset proxy; Objects With Lighting is useful for relighting protocol but not direct mesh-UV validation. Sources: [DiLiGenT-MV](https://sites.google.com/site/photometricstereodata/mv), [OpenIllumination](https://huggingface.co/datasets/OpenIllumination/OpenIllumination), [OpenSubstance](https://openaccess.thecvf.com/content/ICCV2025/html/Pei_OpenSubstance_A_High-quality_Measured_Dataset_of_Multi-View_and_-Lighting_Images_ICCV_2025_paper.html), [Poly Haven](https://polyhaven.com/), [Objects With Lighting](https://github.com/isl-org/objects-with-lighting), [Semantic-Visibility UV](https://github.com/AHHHZ975/Semantic-Visibility-UV-Param), [FlexPara](https://github.com/AidenZhao/FlexPara), [PartUV](https://github.com/EricWang12/PartUV).
./refine-logs/BEAST_8.0_PLAN.md:72:Honest verdict: 8.0 is attainable only if the captured-relighting block works or the SemVis/real-sweep block is surprisingly strong. Without that, the paper is structurally capped around 7.6–7.8: useful, honest, narrow, but not enough external validation for PG/CGF. With a positive DiLiGenT-MV result plus better visuals and stats, I can see a fresh reviewer giving 8.0–8.2 despite novelty staying around 7.2.
./refine-logs/BEAST_8.0_PLAN.md:76:Week 1: Freeze narrower claims; implement captured-image target adapter; download DiLiGenT-MV; add PartUV atlas cache/hash; start visual redesign.
./refine-logs/BEAST_8.0_PLAN.md:77:Week 2: Run DiLiGenT-MV 5-object captured validation with xatlas/Blender/PartUV-feasible/ours; run target-signal confound test; install SemVis-UV with a 3-day kill switch.
./refine-logs/BEAST_8.0_PLAN.md:78:Week 3: Expand real-PBR proxy set via Poly Haven or OpenSubstance subset; run SemVis baseline if alive; run PartUV simplified/cache sweep on deferred meshes; start n=10 split reruns.
./refine-logs/BEAST_8.0_PLAN.md:79:Week 4: Run C4 and mip stress tests only if Week 2–3 are not blocked; finalize bootstrap/sign-test analysis; rebuild main visual figure with zoomed captured and accepted-case crops.
./refine-logs/BEAST_8.0_PLAN.md:80:Week 5: Rewrite title/abstract/contribs around captured/validated target signal; demote failed C4/mip/FlexPara honestly; compile, sanity-review, and get one fresh external read.
./refine-logs/BEAST_8.0_PLAN.md:89:- Reframe as a selective deployment-signal paper, not a production-ready generated-asset UV method.
./refine-logs/BEAST_8.0_PLAN.md:92:- If captured validation is negative, target a narrower benchmark/post-processing venue or defer PG until a real captured-PBR/real-asset benchmark is genuinely complete.
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:37:    "repo": "/data/dip_1_ws/baseline_repos/PartUV",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:88:    "matched_protocol_after_repair": {
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:93:      "matched_constraint_violated": true,
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:2197:    "seed": 7102,
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4258:  "matched_protocol_initial": {
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4263:    "matched_constraint_violated": true,
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4293:    "atlas_npz": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/atlas.npz",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4294:    "metrics": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4295:    "repair_log": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/repair_log.json",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4296:    "residual_chain_png": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/residual_chain.png",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4297:    "residual_npz": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/residual_atlas.npz",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4298:    "residual_png": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/residual_atlas.png",
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:4299:    "summary": "/data/dip_1_ws/runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/summary.md"
./runs/B7_transfer/proc_dented_torus_partuv_baseline_only_seed42/metrics.json:6360:  "seed": 42,

web search: 
web search: 
web search: 
web search: https://sites.google.com/site/photometricstereodata/mv
exec
/bin/zsh -lc "sed -n '1,220p' configs/B3_main.yaml" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
seed: 42
data_root: /data/dip_1_ws/datasets/sample
output_root: /data/dip_1_ws/runs/B3_main
atlas_resolution: 1024
render_resolution: 256
visualization_resolution: 1024
views:
  proposal: 6
  gate: 4
  test: 4
lights:
  proposal: 4
  gate: 4
  test: 4
brdf:
  model: ggx
oracle_pbr:
  pattern: "voronoi_albedo+smooth_normal+region_roughness"
  num_voronoi_seeds: 16
repair:
  top_k_ratio: 0.15
  top_k_max: 32
  beam_size: 4
  outer_iters: 3
  edit_budget: 0.15
  distortion_area_max: 2.0
  distortion_angle_max: 35.0
  eta_seam: 0.25
  lambda_d: 1.0
  lambda_theta: 0.01
  lambda_n: 0.02
  lambda_b: 0.25
  lambda_render: 1.0
  render_eval_views: 1
  render_eval_lights: 1
allocator:
  w_mip: 1.0
  w_vis: 0.5
  w_freq: 0.5
  w_residual: 1.0
  temperature: 1.0
  min_texel_fraction: 0.05
seam_loss:
  channel_weights:
    albedo: 0.5
    normal: 1.0
    roughness: 1.0
    metallic: 1.0
matched_protocol:
  atlas_size: 1024
  padding: 8
  chart_count_window: 0.08
  utilization_min: 0.5
  distortion_tol: 1.5
  raster_resolution: 256
c5_guard:
  delta_psnr_min: 0.3
  seam_residual_drop_min: 0.12
  distortion_tail_epsilon: 3.0
precision: bf16
gradient_checkpointing: true
mip_levels: 4
baselines:
  xatlas_classical: {}
  blender_uv:
    blender_bin: blender
    angle_limit_deg: 66.0
    island_margin: 0.015625
  partuv:
    repo_root: /data/dip_1_ws/baseline_repos/PartUV
    external_atlas: /data/dip_1_ws/atlases/B2/partuv/{asset}.npz
  matched_oracle: {}

exec
/bin/zsh -lc "sed -n '1,220p' scripts/run_B3.py" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
#!/usr/bin/env python
"""B3 main anchor runner: C1 baseline bake + C2/C3/C4 repair pipeline."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one B3 main-method evaluation.")
    parser.add_argument("--asset", required=True, help="Asset name (built-in or procedural/generated registered via patch_prepare_asset)")
    parser.add_argument("--baseline", required=True, choices=["xatlas_classical", "partuv", "blender_uv", "matched_oracle"])
    parser.add_argument("--method", default="ours", choices=["ours", "baseline_only"])
    parser.add_argument("--config", default="configs/B3_main.yaml")
    parser.add_argument("--gpu", type=int, default=None, help="CUDA device index before visibility remapping.")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--split-seed", type=int, default=None, help="Seed for disjoint proposal/gate/test view-light splits.")
    parser.add_argument("--atlas-resolution", type=int, default=None)
    parser.add_argument("--render-resolution", type=int, default=None)
    parser.add_argument("--precision", default=None, choices=["fp32", "float32", "fp16", "float16", "bf16", "bfloat16"])
    parser.add_argument("--no-lpips", action="store_true")
    return parser.parse_args()


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _format_placeholders(node: Any, values: dict[str, Any]) -> Any:
    if isinstance(node, str):
        try:
            return node.format(**values)
        except Exception:
            return node
    if isinstance(node, dict):
        return {key: _format_placeholders(value, values) for key, value in node.items()}
    if isinstance(node, list):
        return [_format_placeholders(value, values) for value in node]
    return node


def _metric_or_none(value: Any):
    if value is None:
        return None
    if value == float("inf"):
        return "inf"
    return float(value)


def _round_list(tensor, digits: int = 8) -> list[float]:
    values = tensor.detach().to("cpu").flatten().tolist()
    return [round(float(v), digits) for v in values]


def _numeric(value: Any) -> float | None:
    if value is None or value == "inf":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _repair_config_from_mapping(payload: dict[str, Any]):
    from pbr_atlas.method import RepairConfig

    fields = RepairConfig.__dataclass_fields__
    return RepairConfig(**{key: value for key, value in dict(payload or {}).items() if key in fields})


def _split_counts(
    mapping: dict[str, Any],
    *,
    legacy_train: str,
    legacy_holdout: str,
    default_proposal: int,
    default_gate: int,
    default_test: int,
) -> dict[str, int]:
    """Read A1 split counts, with backward compatibility for train/holdout configs."""

    if any(key in mapping for key in ("proposal", "gate", "test")):
        return {
            "proposal": int(mapping.get("proposal", mapping.get(legacy_train, default_proposal))),
            "gate": int(mapping.get("gate", mapping.get(legacy_holdout, default_gate))),
            "test": int(mapping.get("test", mapping.get(legacy_holdout, default_test))),
        }
    train = int(mapping.get(legacy_train, default_proposal))
    holdout = int(mapping.get(legacy_holdout, default_gate))
    return {"proposal": train, "gate": holdout, "test": int(mapping.get("test", default_test if legacy_holdout not in mapping else holdout))}


def _residual_stats(residual) -> dict[str, Any]:
    return {
        "e_f": _round_list(residual.e_f),
        "E_c": _round_list(residual.E_c),
        "G_l": _round_list(residual.G_l),
        "e_f_mean": float(residual.e_f.mean().detach().cpu()) if residual.e_f.numel() else 0.0,
        "e_f_max": float(residual.e_f.max().detach().cpu()) if residual.e_f.numel() else 0.0,
        "E_c_mean": float(residual.E_c.mean().detach().cpu()) if residual.E_c.numel() else 0.0,
        "G_l_mean": float(residual.G_l.mean().detach().cpu()) if residual.G_l.numel() else 0.0,
        "seam_residual_mean": float(residual.seam_residual.mean().detach().cpu()) if residual.seam_residual.numel() else 0.0,
    }


def _evaluate_atlas(
    *,
    baker,
    mesh,
    atlas,
    face_values,
    target_mesh,
    target_maps,
    target_images,
    views,
    lights,
    mip_levels: int,
    compute_lpips: bool,
    seam_loss_fn,
) -> dict[str, Any]:
    import torch

    from pbr_atlas.baker.residual import compute_residual_attribution
    from pbr_atlas.baselines import clone_mesh_with_atlas
    from pbr_atlas.eval.metrics import image_metrics, normal_angular_error, per_channel_mae
    from pbr_atlas.method import channel_seam_metrics

    with torch.no_grad():
        candidate_mesh = clone_mesh_with_atlas(mesh, atlas, device=baker.device)
        maps = baker.bake(candidate_mesh, face_values)
        pred_render = baker.render(candidate_mesh, maps, views, lights)
    relit_metrics = image_metrics(pred_render.images, target_images, compute_lpips=compute_lpips)
    pbr_mae = per_channel_mae(
        {
            "albedo": maps.albedo,
            "roughness": maps.roughness,
            "metallic": maps.metallic,
        },
        {
            "albedo": target_maps.albedo,
            "roughness": target_maps.roughness,
            "metallic": target_maps.metallic,
        },
    )
    pbr_mae["normal_angular_error_deg"] = normal_angular_error(maps.normal, target_maps.normal)
    residual = compute_residual_attribution(
        pred=pred_render.images,
        target=target_images,
        face_ids=pred_render.face_ids,
        alpha=pred_render.alpha,
        mesh=candidate_mesh,
        maps=maps,
        chart_ids=candidate_mesh.chart_ids,
        mip_levels=int(mip_levels),
    )
    seam_loss = seam_loss_fn(maps, candidate_mesh, candidate_mesh.chart_ids)
    return {
        "mesh": candidate_mesh,
        "maps": maps,
        "pred_images": pred_render.images,
        "relit": {key: _metric_or_none(value) for key, value in relit_metrics.items()},
        "pbr_channel": pbr_mae,
        "residual": residual,
        "residual_stats": _residual_stats(residual),
        "c4": {
            "loss": float(seam_loss.detach().cpu()),
            **channel_seam_metrics(maps, candidate_mesh, candidate_mesh.chart_ids),
        },
    }


def _c5_guard(
    *,
    mesh,
    baseline_atlas,
    candidate_atlas,
    initial_eval: dict[str, Any],
    final_eval: dict[str, Any],
    matched_cfg,
    c5_cfg: dict[str, Any],
) -> dict[str, Any]:
    from pbr_atlas.baselines.matched_protocol import compute_atlas_stats

    base_stats = compute_atlas_stats(mesh, baseline_atlas, raster_resolution=matched_cfg.raster_resolution)
    cand_stats = compute_atlas_stats(mesh, candidate_atlas, raster_resolution=matched_cfg.raster_resolution)
    chart_delta = int(cand_stats.chart_count - base_stats.chart_count)
    max_chart_delta = max(1, int(base_stats.chart_count * float(matched_cfg.chart_count_window) + 0.999))
    distortion_limit = float(base_stats.max_distortion_q95 + float(c5_cfg.get("distortion_tail_epsilon", 3.0)))

    violations: list[str] = []
    if int(candidate_atlas.atlas_size) != int(baseline_atlas.atlas_size):
        violations.append("atlas_size_changed")
    if int(candidate_atlas.padding) != int(baseline_atlas.padding):
        violations.append("padding_changed")
    if abs(chart_delta) > max_chart_delta:
        violations.append(f"chart_delta={chart_delta} exceeds {max_chart_delta}")
    if cand_stats.max_distortion_q95 > distortion_limit:
        violations.append(f"distortion_q95={cand_stats.max_distortion_q95:.4f} exceeds {distortion_limit:.4f}")

    initial_psnr = _numeric(initial_eval["relit"].get("psnr"))
    final_psnr = _numeric(final_eval["relit"].get("psnr"))
    delta_psnr = None if initial_psnr is None or final_psnr is None else final_psnr - initial_psnr
    initial_seam = float(initial_eval["residual_stats"].get("seam_residual_mean", 0.0))
    final_seam = float(final_eval["residual_stats"].get("seam_residual_mean", 0.0))

exec
/bin/zsh -lc 'python scripts/run_B3.py --help' in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
usage: run_B3.py [-h] --asset ASSET
                 --baseline {xatlas_classical,partuv,blender_uv,matched_oracle}
                 [--method {ours,baseline_only}] [--config CONFIG] [--gpu GPU]
                 [--output-root OUTPUT_ROOT] [--data-root DATA_ROOT]
                 [--run-id RUN_ID] [--seed SEED] [--split-seed SPLIT_SEED]
                 [--atlas-resolution ATLAS_RESOLUTION]
                 [--render-resolution RENDER_RESOLUTION]
                 [--precision {fp32,float32,fp16,float16,bf16,bfloat16}]
                 [--no-lpips]

Run one B3 main-method evaluation.

options:
  -h, --help            show this help message and exit
  --asset ASSET         Asset name (built-in or procedural/generated
                        registered via patch_prepare_asset)
  --baseline {xatlas_classical,partuv,blender_uv,matched_oracle}
  --method {ours,baseline_only}
  --config CONFIG
  --gpu GPU             CUDA device index before visibility remapping.
  --output-root OUTPUT_ROOT
  --data-root DATA_ROOT
  --run-id RUN_ID
  --seed SEED
  --split-seed SPLIT_SEED
                        Seed for disjoint proposal/gate/test view-light
                        splits.
  --atlas-resolution ATLAS_RESOLUTION
  --render-resolution RENDER_RESOLUTION
  --precision {fp32,float32,fp16,float16,bf16,bfloat16}
  --no-lpips

exec
/bin/zsh -lc 'python scripts/run_B7_transfer.py --help' in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 820ms:
usage: run_B7_transfer.py [-h] [--asset ASSET]
                          [--baseline {xatlas_classical,partuv,blender_uv,matched_oracle}]
                          [--method {ours,baseline_only,all}]
                          [--config CONFIG] [--gpu GPU]
                          [--output-root OUTPUT_ROOT] [--data-root DATA_ROOT]
                          [--manifest MANIFEST] [--count COUNT] [--seed SEED]
                          [--force-setup] [--no-lpips] [--dry-run] [--collect]

Run B7 generated transfer experiments.

options:
  -h, --help            show this help message and exit
  --asset ASSET         B7 generated asset id or 'all'.
  --baseline {xatlas_classical,partuv,blender_uv,matched_oracle}
  --method {ours,baseline_only,all}
  --config CONFIG
  --gpu GPU
  --output-root OUTPUT_ROOT
  --data-root DATA_ROOT
                        B7 generated mesh cache root.
  --manifest MANIFEST   Optional B7 remote/local source manifest.
  --count COUNT
  --seed SEED
  --force-setup
  --no-lpips
  --dry-run
  --collect             Run collect_B7_table.py after runs finish.

exec
/bin/zsh -lc "sed -n '1,240p' pbr_atlas/data/asset_registry.py" in /Users/jacksonhuang/project/dip_1_ws
exec
/bin/zsh -lc "sed -n '1,220p' pbr_atlas/data/mesh_loader.py" in /Users/jacksonhuang/project/dip_1_ws
exec
/bin/zsh -lc "sed -n '220,520p' scripts/run_B3.py" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
"""Mesh loader with UV extraction/generation for B1 C1 baker."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

import numpy as np
import torch


@dataclass
class MeshData:
    vertices: torch.Tensor
    faces: torch.Tensor
    uv: torch.Tensor
    face_uv: torch.Tensor
    normals_per_face: torch.Tensor
    normals_per_vertex: torch.Tensor
    chart_ids: torch.Tensor
    source_path: str = ""

    def to(self, device: torch.device) -> "MeshData":
        return replace(
            self,
            vertices=self.vertices.to(device),
            faces=self.faces.to(device),
            uv=self.uv.to(device),
            face_uv=self.face_uv.to(device),
            normals_per_face=self.normals_per_face.to(device),
            normals_per_vertex=self.normals_per_vertex.to(device),
            chart_ids=self.chart_ids.to(device),
        )


def load_mesh(path: str | Path, device: Optional[torch.device] = None) -> MeshData:
    """Load OBJ/GLB/PLY through trimesh and return torch tensors.

    FINAL_PROPOSAL C1 input comment:
        Mesh M=(V,F) and UV U are the required inputs to the baker. If U is
        missing, B1 creates a deterministic xatlas unwrap; if xatlas is not
        installed, it falls back to cylindrical UVs so setup_data stays
        offline-friendly.
    """

    import trimesh

    device = device or torch.device("cpu")
    mesh_obj = trimesh.load(str(path), force="mesh", process=True)
    if isinstance(mesh_obj, trimesh.Scene):
        mesh_obj = trimesh.util.concatenate(tuple(mesh_obj.geometry.values()))
    if mesh_obj.vertices.size == 0 or mesh_obj.faces.size == 0:
        raise ValueError(f"Mesh has no vertices/faces: {path}")
    mesh_obj.remove_unreferenced_vertices()
    vertices_np = np.asarray(mesh_obj.vertices, dtype=np.float32)
    faces_np = np.asarray(mesh_obj.faces, dtype=np.int64)
    vertices_np = _normalize_vertices(vertices_np)
    uv_np, face_uv_np = _extract_or_generate_uv(mesh_obj, vertices_np, faces_np)
    normals_face_np = np.asarray(mesh_obj.face_normals, dtype=np.float32)
    normals_vertex_np = np.asarray(mesh_obj.vertex_normals, dtype=np.float32)
    if normals_face_np.shape[0] != faces_np.shape[0]:
        normals_face_np = _compute_face_normals(vertices_np, faces_np)
    if normals_vertex_np.shape[0] != vertices_np.shape[0]:
        normals_vertex_np = _compute_vertex_normals(vertices_np, faces_np, normals_face_np)
    chart_ids = _infer_chart_ids(face_uv_np)
    return MeshData(
        vertices=torch.from_numpy(vertices_np).to(device),
        faces=torch.from_numpy(faces_np).to(device),
        uv=torch.from_numpy(uv_np.astype(np.float32)).to(device),
        face_uv=torch.from_numpy(face_uv_np.astype(np.int64)).to(device),
        normals_per_face=torch.from_numpy(normals_face_np.astype(np.float32)).to(device),
        normals_per_vertex=torch.from_numpy(normals_vertex_np.astype(np.float32)).to(device),
        chart_ids=torch.from_numpy(chart_ids.astype(np.int64)).to(device),
        source_path=str(path),
    )


def _normalize_vertices(vertices: np.ndarray) -> np.ndarray:
    center = vertices.mean(axis=0, keepdims=True)
    centered = vertices - center
    scale = np.linalg.norm(centered, axis=1).max()
    if scale < 1.0e-8:
        scale = 1.0
    return centered / scale


def _extract_or_generate_uv(mesh_obj, vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    visual_uv = getattr(getattr(mesh_obj, "visual", None), "uv", None)
    if visual_uv is not None:
        uv = np.asarray(visual_uv, dtype=np.float32)
        if uv.ndim == 2 and uv.shape[0] == vertices.shape[0] and uv.shape[1] == 2:
            return np.mod(uv, 1.0).astype(np.float32), faces.astype(np.int64)
    try:
        import xatlas  # type: ignore

        vmapping, indices, uvs = xatlas.parametrize(vertices.astype(np.float32), faces.astype(np.uint32))
        del vmapping
        return np.asarray(uvs, dtype=np.float32).clip(0.0, 1.0), np.asarray(indices, dtype=np.int64).reshape(-1, 3)
    except Exception:
        return _cylindrical_uv(vertices), faces.astype(np.int64)


def _cylindrical_uv(vertices: np.ndarray) -> np.ndarray:
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    theta = np.arctan2(z, x)
    u = (theta + np.pi) / (2.0 * np.pi)
    v = (y - y.min()) / max(float(y.max() - y.min()), 1.0e-8)
    return np.stack([u, v], axis=1).astype(np.float32)


def _compute_face_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norm = np.linalg.norm(normal, axis=1, keepdims=True)
    return normal / np.maximum(norm, 1.0e-8)


def _compute_vertex_normals(vertices: np.ndarray, faces: np.ndarray, face_normals: np.ndarray) -> np.ndarray:
    out = np.zeros_like(vertices)
    for face_idx, face in enumerate(faces):
        out[face] += face_normals[face_idx]
    norm = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norm, 1.0e-8)


def _infer_chart_ids(face_uv: np.ndarray) -> np.ndarray:
    """Infer connected UV charts from shared UV edges."""

    face_count = face_uv.shape[0]
    parent = np.arange(face_count, dtype=np.int64)

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return int(x)

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    edge_to_face: dict[tuple[int, int], int] = {}
    for f_idx, fuv in enumerate(face_uv.tolist()):
        for a, b in ((fuv[0], fuv[1]), (fuv[1], fuv[2]), (fuv[2], fuv[0])):
            key = (min(a, b), max(a, b))
            if key in edge_to_face:
                union(f_idx, edge_to_face[key])
            else:
                edge_to_face[key] = f_idx
    roots = np.array([find(i) for i in range(face_count)], dtype=np.int64)
    _, chart_ids = np.unique(roots, return_inverse=True)
    return chart_ids.astype(np.int64)

 succeeded in 0ms:
"""Small B1 sample asset registry with offline-friendly fallbacks."""

from __future__ import annotations

import os
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable

DEFAULT_DATA_ROOT = Path(os.environ.get("PBR_ATLAS_DATA_ROOT", "/data/dip_1_ws/datasets/sample"))

BUNNY_URL = "http://graphics.stanford.edu/data/3Dscanrep/bunnyrep/bunny_reduced.tar.gz"
SPOT_URL = "https://www.cs.cmu.edu/~kmcrane/Projects/ModelRepository/spot.zip"


def resolve_asset(asset: str, data_root: str | Path = DEFAULT_DATA_ROOT) -> Path:
    """Return the expected local mesh path for a B1 asset."""

    root = Path(data_root)
    aliases = {"objaverse_sample": "objaverse", "objaverse1": "objaverse"}
    asset = aliases.get(asset, asset)
    candidates = {
        "bunny": _find_mesh(root / "bunny"),
        "spot": _find_mesh(root / "spot"),
        "objaverse": _find_mesh(root / "objaverse"),
    }
    if asset not in candidates:
        raise ValueError(f"Unknown B1 asset {asset!r}; expected bunny, spot, or objaverse")
    path = candidates[asset]
    if path is None:
        raise FileNotFoundError(f"Asset {asset!r} is not prepared under {root}")
    return path


def prepare_asset(asset: str, data_root: str | Path = DEFAULT_DATA_ROOT, offline_ok: bool = True) -> Path:
    """Prepare a single B1 sample asset.

    B1 registry comment:
        The sample set is intentionally tiny: Stanford bunny, Spot cow, and one
        optional Objaverse GLB. Failed downloads fall back to generated
        trimesh primitives with xatlas/cylindrical UVs added by mesh_loader.
    """

    aliases = {"objaverse_sample": "objaverse", "objaverse1": "objaverse"}
    asset = aliases.get(asset, asset)
    root = Path(data_root)
    root.mkdir(parents=True, exist_ok=True)
    if asset == "bunny":
        return _prepare_download_or_fallback("bunny", root / "bunny", BUNNY_URL, "bunny_reduced.tar.gz", "icosphere", offline_ok)
    if asset == "spot":
        return _prepare_download_or_fallback("spot", root / "spot", SPOT_URL, "spot.zip", "box", offline_ok)
    if asset == "objaverse":
        return _prepare_objaverse(root / "objaverse", offline_ok)
    raise ValueError(f"Unknown B1 asset {asset!r}")


def prepare_all(data_root: str | Path = DEFAULT_DATA_ROOT, offline_ok: bool = True) -> list[Path]:
    return [prepare_asset(asset, data_root, offline_ok=offline_ok) for asset in ("bunny", "spot", "objaverse")]


def _prepare_download_or_fallback(
    name: str,
    target_dir: Path,
    url: str,
    archive_name: str,
    primitive: str,
    offline_ok: bool,
) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_mesh(target_dir)
    if existing is not None:
        return existing
    archive = target_dir / archive_name
    try:
        _download(url, archive)
        _extract_archive(archive, target_dir)
        found = _find_mesh(target_dir)
        if found is not None:
            return found
    except Exception:
        if not offline_ok:
            raise
    return _write_primitive(target_dir / f"{name}_fallback.obj", primitive)


def _prepare_objaverse(target_dir: Path, offline_ok: bool) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_mesh(target_dir)
    if existing is not None:
        return existing
    try:
        from huggingface_hub import hf_hub_download  # type: ignore

        # A tiny public GLB-like sample path cannot be guaranteed stable across
        # Objaverse mirrors, so this is intentionally best-effort. The fallback
        # keeps B1 deterministic when the network or token is unavailable.
        path = hf_hub_download(
            repo_id="allenai/objaverse",
            filename="glbs/000-000/000a52e0c1614bd68a234d3f1fbfca55.glb",
            repo_type="dataset",
            local_dir=str(target_dir),
        )
        return Path(path)
    except Exception:
        if not offline_ok:
            raise
    return _write_primitive(target_dir / "objaverse_fallback.obj", "cylinder")


def _download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "pbr-atlas-b1/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        path.write_bytes(response.read())


def _extract_archive(archive: Path, target_dir: Path) -> None:
    suffixes = "".join(archive.suffixes)
    if suffixes.endswith(".tar.gz") or suffixes.endswith(".tgz"):
        with tarfile.open(archive, "r:gz") as tf:
            _safe_extract_tar(tf, target_dir)
    elif suffixes.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target_dir)
    else:
        raise ValueError(f"Unsupported archive: {archive}")


def _safe_extract_tar(tf: tarfile.TarFile, target_dir: Path) -> None:
    target_root = target_dir.resolve()
    for member in tf.getmembers():
        member_path = (target_dir / member.name).resolve()
        if not str(member_path).startswith(str(target_root)):
            raise RuntimeError(f"Unsafe tar member path: {member.name}")
    tf.extractall(target_dir)


def _find_mesh(root: Path) -> Path | None:
    if not root.exists():
        return None
    for ext in ("*.obj", "*.glb", "*.ply", "*.stl"):
        matches = sorted(root.rglob(ext))
        if matches:
            return matches[0]
    return None


def _write_primitive(path: Path, primitive: str) -> Path:
    import trimesh

    path.parent.mkdir(parents=True, exist_ok=True)
    if primitive == "icosphere":
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    elif primitive == "cylinder":
        mesh = trimesh.creation.cylinder(radius=0.65, height=1.5, sections=48)
    else:
        mesh = trimesh.creation.box(extents=(1.4, 0.9, 1.1))
    mesh.export(path)
    return path


def iter_prepared_assets(data_root: str | Path = DEFAULT_DATA_ROOT) -> Iterable[Path]:
    for asset in ("bunny", "spot", "objaverse"):
        try:
            yield resolve_asset(asset, data_root)
        except FileNotFoundError:
            continue


 succeeded in 0ms:
    final_seam = float(final_eval["residual_stats"].get("seam_residual_mean", 0.0))
    seam_relative_delta = 0.0 if initial_seam <= 1.0e-8 else (final_seam - initial_seam) / initial_seam
    delta_psnr_min = float(c5_cfg.get("delta_psnr_min", 0.3))
    seam_drop_min = float(c5_cfg.get("seam_residual_drop_min", 0.12))
    metric_accept = (delta_psnr is not None and delta_psnr >= delta_psnr_min) and (seam_relative_delta <= -seam_drop_min)
    hard_accept = not violations
    return {
        "hard_accept": hard_accept,
        "metric_accept": bool(metric_accept),
        "accept": bool(hard_accept and metric_accept),
        "violations": violations,
        "delta_psnr": delta_psnr,
        "seam_relative_delta": seam_relative_delta,
        "chart_count_delta": chart_delta,
        "chart_count_delta_limit": max_chart_delta,
        "distortion_q95": cand_stats.max_distortion_q95,
        "distortion_q95_limit": distortion_limit,
        "baseline_stats": base_stats.to_dict(),
        "candidate_stats": cand_stats.to_dict(),
    }


def _failure_summary(asset: str, baseline: str, method: str, reason: str) -> str:
    return (
        "# B3 Main Summary\n\n"
        f"- asset: {asset}\n"
        f"- baseline: {baseline}\n"
        f"- method: {method}\n"
        "- repro_status: failed\n"
        f"- failure_reason: {reason}\n"
    )


def main() -> None:
    args = parse_args()
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    import torch

    from pbr_atlas.baker import DifferentiablePBRBaker, make_view_light_splits, sample_face_pbr_from_maps
    from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
    from pbr_atlas.baselines.base import BaselineAtlas, repack_existing_charts
    from pbr_atlas.baselines.matched_protocol import MatchedProtocolConfig, enforce
    from pbr_atlas.data import generate_synthetic_oracle_pbr, prepare_asset
    from pbr_atlas.data.mesh_loader import load_mesh
    from pbr_atlas.method import (
        CrossChannelSeamLoss,
        LocalChartRepair,
        MipAwareAllocator,
        allocation_to_chart_scales,
        estimate_face_pbr_frequency,
        estimate_face_visibility,
    )
    from pbr_atlas.utils import (
        atomic_write_json,
        directory_size_mb,
        ensure_dir,
        save_npz,
        save_residual_atlas_png,
        save_residual_chain_png,
        set_global_seed,
        write_text,
    )

    cfg = load_config(args.config)
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    split_seed = int(args.split_seed if args.split_seed is not None else cfg.get("split_seed", seed))
    atlas_resolution = int(args.atlas_resolution or cfg.get("atlas_resolution", 1024))
    render_resolution = int(args.render_resolution or cfg.get("render_resolution", 256))
    precision = args.precision or cfg.get("precision", "bf16")
    output_root = Path(args.output_root or cfg.get("output_root", "/data/dip_1_ws/runs/B3_main"))
    run_id = args.run_id or f"{args.asset}_{args.baseline}_{args.method}_seed{seed}_split{split_seed}"
    run_dir = ensure_dir(output_root / run_id)
    data_root = Path(args.data_root or cfg.get("data_root", "/data/dip_1_ws/datasets/sample"))
    vis_resolution = int(cfg.get("visualization_resolution", min(atlas_resolution, 1024)))
    mip_levels = int(cfg.get("mip_levels", 4))
    matched_cfg = MatchedProtocolConfig.from_mapping(cfg.get("matched_protocol"))
    padding = int(matched_cfg.padding)

    set_global_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    started = time.time()

    mesh_path = prepare_asset(args.asset, data_root=data_root, offline_ok=True)
    mesh = load_mesh(mesh_path, device=device)
    baker = DifferentiablePBRBaker(
        atlas_resolution=atlas_resolution,
        render_resolution=render_resolution,
        precision=precision,
        gradient_checkpointing=bool(cfg.get("gradient_checkpointing", True)),
        device=device,
    )

    baseline_cfg = _format_placeholders(
        dict(cfg.get("baselines", {})),
        {
            "asset": args.asset if args.asset != "objaverse_sample" else "objaverse",
            "baseline": args.baseline,
            "seed": seed,
            "atlas_size": atlas_resolution,
            "padding": padding,
            "output_root": str(output_root),
        },
    )
    xatlas_reference = create_backend("xatlas_classical", baseline_cfg.get("xatlas_classical", {})).generate(mesh, atlas_resolution, padding)
    if xatlas_reference.repro_status == "failed":
        xatlas_reference = BaselineAtlas(
            name="xatlas_reference_fallback",
            uv=mesh.uv.detach().cpu(),
            face_uv=mesh.face_uv.detach().cpu(),
            chart_ids=mesh.chart_ids.detach().cpu(),
            atlas_size=atlas_resolution,
            padding=padding,
            metadata={"warning": "xatlas reference unavailable; fell back to input mesh UV."},
            repro_status="partial",
            failure_reason="xatlas reference unavailable",
        )

    oracle_reference = create_backend("matched_oracle", baseline_cfg.get("matched_oracle", {})).generate(mesh, atlas_resolution, padding)
    if oracle_reference.repro_status == "failed":
        oracle_reference = xatlas_reference

    baseline_backend = create_backend(args.baseline, baseline_cfg.get(args.baseline, {}))
    candidate_atlas = (
        xatlas_reference
        if args.baseline == "xatlas_classical"
        else oracle_reference
        if args.baseline == "matched_oracle"
        else baseline_backend.generate(mesh, atlas_resolution, padding)
    )
    matched_report = enforce(mesh, candidate_atlas, xatlas_reference, matched_cfg)
    save_npz(run_dir / "initial_atlas.npz", uv=candidate_atlas.uv, face_uv=candidate_atlas.face_uv, chart_ids=candidate_atlas.chart_ids)

    base_metrics = {
        "block": "B3_main",
        "asset": args.asset,
        "baseline": args.baseline,
        "method": args.method,
        "seed": seed,
        "split_seed": split_seed,
        "device": str(device),
        "precision": precision,
        "atlas_resolution": atlas_resolution,
        "render_resolution": render_resolution,
        "padding": padding,
        "mesh_path": str(mesh_path),
        "repro_status": candidate_atlas.repro_status,
        "failure_reason": candidate_atlas.failure_reason,
        "baseline_metadata": candidate_atlas.metadata,
        "matched_protocol_initial": matched_report.to_dict(),
    }
    if candidate_atlas.repro_status == "failed":
        metrics = dict(base_metrics)
        atomic_write_json(run_dir / "metrics.json", metrics)
        write_text(run_dir / "summary.md", _failure_summary(args.asset, args.baseline, args.method, candidate_atlas.failure_reason or "unknown failure"))
        print(str(run_dir))
        return

    view_cfg = cfg.get("views", {})
    light_cfg = cfg.get("lights", {})
    split_counts = {
        "views": _split_counts(
            dict(view_cfg),
            legacy_train="train",
            legacy_holdout="holdout",
            default_proposal=6,
            default_gate=4,
            default_test=4,
        ),
        "lights": _split_counts(
            dict(light_cfg),
            legacy_train="train",
            legacy_holdout="holdout",
            default_proposal=4,
            default_gate=4,
            default_test=4,
        ),
    }
    splits = make_view_light_splits(split_counts["views"], split_counts["lights"], split_seed=split_seed, device=device)
    proposal_views, proposal_lights = splits.proposal.views, splits.proposal.lights
    gate_views, gate_lights = splits.gate.views, splits.gate.lights
    test_views, test_lights = splits.test.views, splits.test.lights
    base_metrics["splits"] = splits.to_metadata()

    oracle_cfg = cfg.get("oracle_pbr", {})
    oracle_maps = generate_synthetic_oracle_pbr(
        mesh,
        seed=seed,
        pattern=str(oracle_cfg.get("pattern", "voronoi_albedo+smooth_normal+region_roughness")),
        resolution=atlas_resolution,
        num_voronoi_seeds=int(oracle_cfg.get("num_voronoi_seeds", 16)),
        device=device,
    )
    oracle_mesh = clone_mesh_with_atlas(mesh, oracle_reference, device=device)
    face_values = sample_face_pbr_from_maps(oracle_mesh, oracle_maps)
    with torch.no_grad():
        oracle_baked_maps = baker.bake(oracle_mesh, face_values)
        proposal_target_render = baker.render(oracle_mesh, oracle_baked_maps, proposal_views, proposal_lights)
        gate_target_render = baker.render(oracle_mesh, oracle_baked_maps, gate_views, gate_lights)
        test_target_render = baker.render(oracle_mesh, oracle_baked_maps, test_views, test_lights)

    seam_loss_fn = CrossChannelSeamLoss(cfg.get("seam_loss", {}).get("channel_weights", {}))
    initial_proposal_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=candidate_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=proposal_target_render.images,
        views=proposal_views,
        lights=proposal_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )
    initial_gate_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=candidate_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=gate_target_render.images,
        views=gate_views,
        lights=gate_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )
    initial_test_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=candidate_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=test_target_render.images,
        views=test_views,
        lights=test_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )

    current_atlas = candidate_atlas
    current_proposal_eval = initial_proposal_eval
    current_gate_eval = initial_gate_eval
    repair_logs: list[dict[str, Any]] = []
    allocation_logs: list[dict[str, Any]] = []
    c5_history: list[dict[str, Any]] = []

    if args.method == "ours":
        repair_cfg_payload = dict(cfg.get("repair", {}))
        outer_iters = int(repair_cfg_payload.get("outer_iters", 3))
        repair_cfg = _repair_config_from_mapping(repair_cfg_payload)
        allocator_cfg = dict(cfg.get("allocator", {}))
        allocator = MipAwareAllocator(
            atlas_size=atlas_resolution,
            w_mip=float(allocator_cfg.get("w_mip", 1.0)),
            w_vis=float(allocator_cfg.get("w_vis", 0.5)),
            w_freq=float(allocator_cfg.get("w_freq", 0.5)),
            w_residual=float(allocator_cfg.get("w_residual", 1.0)),
            temperature=float(allocator_cfg.get("temperature", 1.0)),
            min_texel_fraction=float(allocator_cfg.get("min_texel_fraction", 0.05)),
        )
        for outer_idx in range(max(1, outer_iters)):
            repairer = LocalChartRepair(repair_cfg)
            repaired_atlas, repair_log = repairer.repair(
                baker,
                mesh,
                current_atlas,
                oracle_maps,
                current_proposal_eval["residual"],
                proposal_views=proposal_views,
                proposal_lights=proposal_lights,
            )
            repair_logs.append({"outer_iter": outer_idx, **repair_log.to_dict()})

            repaired_proposal_eval = _evaluate_atlas(
                baker=baker,
                mesh=mesh,
                atlas=repaired_atlas,
                face_values=face_values,
                target_mesh=oracle_mesh,
                target_maps=oracle_baked_maps,
                target_images=proposal_target_render.images,
                views=proposal_views,
                lights=proposal_lights,
                mip_levels=mip_levels,
                compute_lpips=not args.no_lpips,
                seam_loss_fn=seam_loss_fn,
            )
            view_visibility = estimate_face_visibility(repaired_proposal_eval["mesh"], proposal_views)
            pbr_frequency = estimate_face_pbr_frequency(repaired_proposal_eval["mesh"], repaired_proposal_eval["maps"])
            allocation = allocator.allocate(repaired_atlas, repaired_proposal_eval["residual"], view_visibility, pbr_frequency)
            chart_scales = allocation_to_chart_scales(repaired_atlas, allocation)
            alloc_uv, alloc_face_uv, alloc_chart_ids = repack_existing_charts(

web search: 
web search: 
web search: 
web search: "DiLiGenT-MV.zip" "drive.google.com" file id
codex
I’m using the `experiment-plan` skill for the W1 run order, because this is now a claim-driven execution roadmap rather than a general review.
exec
/bin/zsh -lc "sed -n '1,220p' /Users/jacksonhuang/.codex/skills/experiment-plan/SKILL.md" in /Users/jacksonhuang/project/dip_1_ws
 succeeded in 0ms:
---
name: "experiment-plan"
description: "Turn a refined research proposal or method idea into a detailed, claim-driven experiment roadmap. Use after `research-refine`, or when the user asks for a detailed experiment plan, ablation matrix, evaluation protocol, run order, compute budget, or paper-ready validation that supports the core problem, novelty, simplicity, and any LLM / VLM / Diffusion / RL-based contribution."
---

# Experiment Plan: Claim-Driven, Paper-Oriented Validation

Refine and concretize: **$ARGUMENTS**

## Overview

Use this skill after the method is stable enough that the next question becomes: **what exact experiments should we run, in what order, to defend the paper?** If the user wants the full chain in one request, prefer `/research-refine-pipeline`.

The goal is not to generate a giant benchmark wishlist. The goal is to turn a proposal into a **claim -> evidence -> run order** roadmap that supports four things:

1. the method actually solves the anchored problem
2. the dominant contribution is real and focused
3. the method is elegant enough that extra complexity is unnecessary
4. any frontier-model-era component is genuinely useful, not decorative

## Constants

- **OUTPUT_DIR = `refine-logs/`** — Default destination for experiment planning artifacts.
- **MAX_PRIMARY_CLAIMS = 2** — Prefer one dominant claim plus one supporting claim.
- **MAX_CORE_BLOCKS = 5** — Keep the must-run experimental story compact.
- **MAX_BASELINE_FAMILIES = 3** — Prefer a few strong baselines over many weak ones.
- **DEFAULT_SEEDS = 3** — Use 3 seeds when stochastic variance matters and budget allows.

## Workflow

### Phase 0: Load the Proposal Context

Read the most relevant existing files first if they exist:

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/REVIEW_SUMMARY.md`
- `refine-logs/REFINEMENT_REPORT.md`

Extract:

- **Problem Anchor**
- **Dominant contribution**
- **Optional supporting contribution**
- **Critical reviewer concerns**
- **Data / compute / timeline constraints**
- **Which frontier primitive is central, if any**

If these files do not exist, derive the same information from the user's prompt.

### Phase 1: Freeze the Paper Claims

Before proposing experiments, write down the claims that must be defended.

Use this structure:

- **Primary claim**: the main mechanism-level contribution
- **Supporting claim**: optional, only if it directly strengthens the main paper story
- **Anti-claim to rule out**: e.g. "the gain only comes from more parameters," "the gain only comes from a larger search space," or "the modern component is just decoration"
- **Minimum convincing evidence**: what would make each claim believable to a strong reviewer?

Do not exceed `MAX_PRIMARY_CLAIMS` unless the paper truly has multiple inseparable claims.

### Phase 2: Build the Experimental Storyline

Design the paper around a compact set of experiment blocks. Default to the following blocks and delete any that are not needed:

1. **Main anchor result** — does the method solve the actual bottleneck?
2. **Novelty isolation** — does the dominant contribution itself matter?
3. **Simplicity / elegance check** — can a bigger or more fragmented version be avoided?
4. **Frontier necessity check** — if an LLM / VLM / Diffusion / RL-era component is central, is it actually the right tool?
5. **Failure analysis or qualitative diagnosis** — what does the method still miss?

For each block, decide whether it belongs in:

- **Main paper** — essential to defend the core claims
- **Appendix** — useful but non-blocking
- **Cut** — interesting, but not worth the paper budget

Prefer one strong baseline family over many weak baselines. If a stronger modern baseline exists, use it instead of padding the list.

### Phase 3: Specify Each Experiment Block

For every kept block, fully specify:

- **Claim tested**
- **Why this block exists**
- **Dataset / split / task**
- **Compared systems**: strongest baselines, ablations, and variants only
- **Metrics**: decisive metrics first, secondary metrics second
- **Setup details**: backbone, frozen vs trainable parts, key hyperparameters, training budget, seeds
- **Success criterion**: what outcome would count as convincing evidence?
- **Failure interpretation**: if the result is negative, what does it mean?
- **Table / figure target**: where this result should appear in the paper

Special rules:

- A **simplicity check** should usually compare the final method against either an overbuilt variant or a tempting extra component that the paper intentionally rejects.
- A **frontier necessity check** should usually compare the chosen modern primitive against the strongest plausible simpler or older alternative.
- If the proposal is intentionally non-frontier, say so explicitly and skip the frontier block instead of forcing one.

### Phase 4: Turn the Plan Into an Execution Order

Build a realistic run order so the user knows what to do first.

Use this milestone structure:

1. **Sanity stage** — data pipeline, metric correctness, one quick overfit or toy split
2. **Baseline stage** — reproduce the strongest baseline(s)
3. **Main method stage** — run the final method on the primary setting
4. **Decision stage** — run the decisive ablations for novelty, simplicity, and frontier necessity
5. **Polish stage** — robustness, qualitative figures, appendix extras

For each milestone, estimate:

- compute cost
- expected turnaround time
- stop / go decision gate
- risk and mitigation

Separate **must-run** from **nice-to-have** experiments.

### Phase 5: Write the Outputs

#### Step 5.1: Write `refine-logs/EXPERIMENT_PLAN.md`

Use this structure:

```markdown
# Experiment Plan

**Problem**: [problem]
**Method Thesis**: [one-sentence thesis]
**Date**: [today]

## Claim Map
| Claim | Why It Matters | Minimum Convincing Evidence | Linked Blocks |
|-------|-----------------|-----------------------------|---------------|
| C1    | ...             | ...                         | B1, B2        |

## Paper Storyline
- Main paper must prove:
- Appendix can support:
- Experiments intentionally cut:

## Experiment Blocks

### Block 1: [Name]
- Claim tested:
- Why this block exists:
- Dataset / split / task:
- Compared systems:
- Metrics:
- Setup details:
- Success criterion:
- Failure interpretation:
- Table / figure target:
- Priority: MUST-RUN / NICE-TO-HAVE

### Block 2: [Name]
...

## Run Order and Milestones
| Milestone | Goal | Runs | Decision Gate | Cost | Risk |
|-----------|------|------|---------------|------|------|
| M0        | ...  | ...  | ...           | ...  | ...  |

## Compute and Data Budget
- Total estimated GPU-hours:
- Data preparation needs:
- Human evaluation needs:
- Biggest bottleneck:

## Risks and Mitigations
- [Risk]:
- [Mitigation]:

## Final Checklist
- [ ] Main paper tables are covered
- [ ] Novelty is isolated
- [ ] Simplicity is defended
- [ ] Frontier contribution is justified or explicitly not claimed
- [ ] Nice-to-have runs are separated from must-run runs
```

#### Step 5.2: Write `refine-logs/EXPERIMENT_TRACKER.md`

Use this structure:

```markdown
# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|--------|-----------|---------|------------------|-------|---------|----------|--------|-------|
| R001   | M0        | sanity  | ...              | ...   | ...     | MUST     | TODO   | ...   |
```

Keep the tracker compact and execution-oriented.

#### Step 5.3: Present a Brief Summary to the User

```
Experiment plan ready.

Must-run blocks:
- [Block 1]
- [Block 2]

Highest-risk assumption:
- [risk]

First three runs to launch:
1. [run]
2. [run]
3. [run]

Plan file: refine-logs/EXPERIMENT_PLAN.md
Tracker file: refine-logs/EXPERIMENT_TRACKER.md
```

## Output Protocols

web search: 
web search: PRCV 2026 submission deadline May 30 2026 simultaneous submission policy
codex
=== PER-ITEM DECISIONS ===
R1: adjust to "Captured-Target Residuals for Selective UV Atlas Repair".
R2: go, with fixed protocol: 5 objects, GT mesh only, proposal/gate/test disjoint by views/lights, `mask.png` eroded 2 px, 16-bit linear PNG normalized by RGB `light_intensities.txt`, no gamma/tone mapping, saturated pixels excluded.
R3: go, but renumber to 4 contributions: channel-aware baker, local repair, residual allocation, holdout gate; C4/mip become diagnostics only.
R4: adjust to "xatlas / Blender Smart UV / PartUV / SemVis-UV; matched_oracle only in synthetic confound; cite but do not run UVSegNet".
R5: go.
R6: adjust to n=5 for DiLiGenT core baselines, n=3 for SemVis/transfer, n=10 only for final top-2 accepted and top-2 rollback rows if variance is borderline.
R7: adjust to "main figure must use DiLiGenT captured rows if positive; spot/bunny only as temporary fallback".
R8: go.
R9: adjust to "prepare PRCV fork, but do not dual-submit a substantially same archival paper; submit PRCV only if PG gate fails or PG is skipped/withdrawn".

=== KEY ADDITIONS YOU RECOMMEND I ADD ===
- Target-signal confound: UV defect vs material noise vs mixed defect.
- Dataset/protocol audit table for DiLiGenT-MV normalization, masks, splits, exclusions.
- C5 accept/rollback taxonomy table, including negative captured cases.
- SemVis-UV 3-day kill-switch log.
- References checked: DiLiGenT-MV official dataset, PartUV, SemVis-UV.

=== W1 EXECUTION ORDER (specific, runnable) ===
Day 1 (today, 5/3): download DiLiGenT-MV; freeze new title/contribs; create `configs/DILIGENT_MV.yaml`; start `pbr_atlas/data/diligent_mv.py` loader.

Day 2 (5/4): finish loader and `scripts/setup_diligent_mv.py`; verify one object loads mesh, cameras, masks, 96 lights, normalized images; run one low-res xatlas captured smoke.

Day 3 (5/5): implement `scripts/run_diligent_mv.py`; run Bear/Cow with xatlas + Blender, seed 0, baseline_only and ours, low-res no-LPIPS.

Day 4 (5/6): run all 5 objects x xatlas/Blender seed 0; add PartUV cache/decimation; start SemVis install timer.

Day 5 (5/7): launch DiLiGenT core grid: 5 objects x xatlas/Blender/PartUV-feasible x seeds 0-4; run SemVis seed 0 if installed.

Day 6 (5/8): implement `scripts/collect_diligent_mv_table.py` with bootstrap CI and paired tests; generate first captured `table1_main.tex`; build 2-row captured figure draft.

Day 7 (5/9): decision gate: if captured signal is positive, rewrite abstract/intro/method around captured targets; if mixed, keep captured as selective-validation; if negative, demote PG and switch to PRCV/Poly Haven fallback.

=== EXACT FIRST 3 SHELL COMMANDS / SCRIPTS I SHOULD RUN NOW ===
1. `cd /Users/jacksonhuang/project/dip_1_ws && mkdir -p datasets/diligent_mv/raw datasets/diligent_mv/processed runs/W1_diligent_mv refine-logs`
2. `cd /Users/jacksonhuang/project/dip_1_ws && python -m pip install -U kaggle scipy imageio opencv-python-headless`
3. `cd /Users/jacksonhuang/project/dip_1_ws && kaggle datasets download -d zaiyanyang/diligentmv -p datasets/diligent_mv/raw --unzip && find datasets/diligent_mv/raw -maxdepth 6 \( -name mesh_Gt.ply -o -name light_intensities.txt -o -name Calib_Results.mat \) | sort | head -40`

=== ABORT CRITERIA ===
If by EOD Day 2 no verified DiLiGenT loader, switch to Poly Haven HDR-relit as main real-target proxy.

If by EOD Day 5 DiLiGenT mean accepted-case gain is < +0.3 dB or all bootstrap CIs cross 0, demote captured from headline.

If SemVis-UV is not running within 3 calendar days, log failure and drop it.

If PartUV succeeds on <3/5 DiLiGenT objects, use xatlas/Blender/SemVis main and move PartUV to partial baseline.
tokens used
