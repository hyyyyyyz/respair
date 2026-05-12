from __future__ import annotations

import re
from collections import defaultdict

from paper_plot_style import (
    ROOT,
    TABLE_DIR,
    b3_metrics,
    expected_direction,
    format_delta,
    format_num,
    latex_escape,
    observed_match,
    read_expected_delta,
    read_markdown_table,
    row,
    short_baseline,
    table_preamble,
    to_float,
    verdict_from_metrics,
    write_table,
)


def finish_table(lines: list[str]) -> list[str]:
    return lines + [r"\bottomrule", r"\end{tabular}", r"\end{table}"]


def gen_table1() -> None:
    rows = read_markdown_table("runs/B3_main/MAIN_TABLE.md")
    lines = table_preamble(
        "Main B3 results across assets and UV baselines. C5 accepts only residual-backed repairs; rollback rows report the deployed baseline result.",
        "tab:main",
        "llrrrrlr",
    )
    lines.append(row(["Asset", "Baseline", "Init PSNR", "Final PSNR", r"$\Delta$PSNR", "C5", "Edited \\#"]))
    lines.append(r"\midrule")
    for r in rows:
        metrics = b3_metrics(r["Asset"], r["Baseline"])
        lines.append(
            row(
                [
                    latex_escape(r["Asset"]),
                    latex_escape(short_baseline(r["Baseline"])),
                    format_num(r["Baseline PSNR"], 2),
                    format_num(r["Ours PSNR"], 2),
                    format_delta(r["dPSNR"], 2, bold_positive=True),
                    verdict_from_metrics(metrics),
                    format_num(r["Edit Chart Count"], 0),
                ]
            )
        )
    write_table(TABLE_DIR / "table1_main.tex", finish_table(lines))


def gen_table2() -> None:
    source_rows = read_markdown_table("runs/B4_ablation/B4_TABLE.md")
    expected = read_expected_delta()
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    variants: dict[str, set[str]] = defaultdict(set)
    for r in source_rows:
        aid = r["Ablation"]
        variant = r["Variant"] if r["Variant"] != "-" else "base"
        variants[aid].add(variant)
        match = re.search(r"([^/]+)/partuv", r["Case (asset/baseline)"])
        if not match:
            continue
        val = to_float(r["dPSNR vs ours"])
        if val is not None:
            grouped[(aid, match.group(1))].append(val)

    lines = table_preamble(
        "B4 ablation summary. Deltas are worst completed variants versus the full method; missing entries indicate no completed metric row in B4_TABLE.",
        "tab:ablation",
        "llrrll",
    )
    lines.append(row(["ID", "Variant set", r"Spot $\Delta$", r"Bunny $\Delta$", "Expected", "Match"]))
    lines.append(r"\midrule")
    for idx in range(1, 19):
        aid = f"A{idx}"
        spot_vals = grouped.get((aid, "spot"), [])
        bunny_vals = grouped.get((aid, "bunny"), [])
        direction = expected_direction(expected.get(aid, ""))
        match = observed_match([*spot_vals, *bunny_vals], direction)
        match_text = {"yes": r"$\checkmark$", "no": r"$\times$", "n/a": "--"}[match]
        variant_text = ",".join(sorted(variants.get(aid, {"--"})))
        lines.append(
            row(
                [
                    aid,
                    latex_escape(variant_text),
                    format_delta(min(spot_vals), 2) if spot_vals else "--",
                    format_delta(min(bunny_vals), 2) if bunny_vals else "--",
                    latex_escape(direction),
                    match_text,
                ]
            )
        )
    write_table(TABLE_DIR / "table2_ablation.tex", finish_table(lines))


def gen_table3() -> None:
    rows = read_markdown_table("runs/B5_matched/B5_TABLE.md")
    by_condition: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for r in rows:
        by_condition[r["Condition"]][r["Asset"]] = r
    lines = table_preamble(
        "Strict matched-control results. The gain survives atlas-size, padding, and chart-count locks, but disappears under distortion, utilization, or all-lock protocols.",
        "tab:matched",
        "lrrll",
    )
    lines.append(row(["Condition", r"Spot $\Delta$", r"Bunny $\Delta$", "matched OK", "C5"]))
    lines.append(r"\midrule")
    for condition, assets in by_condition.items():
        spot = assets.get("spot", {})
        bunny = assets.get("bunny", {})
        verdicts = sorted({spot.get("c5_verdict", "--"), bunny.get("c5_verdict", "--")})
        matched = sorted({spot.get("matched_OK", "--"), bunny.get("matched_OK", "--")})
        lines.append(
            row(
                [
                    latex_escape(condition),
                    format_delta(spot.get("Gain vs initial"), 2, bold_positive=True),
                    format_delta(bunny.get("Gain vs initial"), 2, bold_positive=True),
                    "/".join(matched),
                    "/".join(verdicts),
                ]
            )
        )
    write_table(TABLE_DIR / "table3_matched.tex", finish_table(lines))


def gen_table4() -> None:
    rows = read_markdown_table("runs/B7_transfer/B7_TABLE.md")
    lines = table_preamble(
        "Generated/procedural transfer results. Candidate repairs are deployed only when C5 accepts; rollback rows indicate no final change.",
        "tab:transfer",
        "lrrrl",
    )
    lines.append(row(["Generated mesh", "Baseline PSNR", "Ours PSNR", r"$\Delta$PSNR", "C5"]))
    lines.append(r"\midrule")
    for r in rows:
        lines.append(
            row(
                [
                    latex_escape(r["Generated Mesh"]),
                    format_num(r["Baseline PSNR"], 2),
                    format_num(r["Ours PSNR"], 2),
                    format_delta(r["dPSNR"], 2, bold_positive=True),
                    latex_escape(r["c5_verdict"]),
                ]
            )
        )
    write_table(TABLE_DIR / "table4_transfer.tex", finish_table(lines))


def gen_table5() -> None:
    rows = read_markdown_table("runs/B7_robustness/B7_ROBUSTNESS_TABLE.md")
    lines = table_preamble(
        "Robustness sweeps on the spot/PartUV accepted case. Positive drop means lower PSNR than the sweep reference; the noise sigma=0.01 anomaly is retained.",
        "tab:robustness",
        "lrrrl",
    )
    lines.append(row(["Sweep", "Level", "PSNR", "Drop", "C5"]))
    lines.append(r"\midrule")
    for r in rows:
        lines.append(
            row(
                [
                    latex_escape(r["Sweep"]),
                    format_num(r["Level"], 2),
                    format_num(r["PSNR"], 2),
                    format_delta(r["Drop"], 2),
                    latex_escape(r["c5_verdict"]),
                ]
            )
        )
    write_table(TABLE_DIR / "table5_robustness.tex", finish_table(lines))


def main() -> None:
    gen_table1()
    gen_table2()
    gen_table3()
    gen_table4()
    gen_table5()


if __name__ == "__main__":
    main()
