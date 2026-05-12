from __future__ import annotations

import re

import numpy as np

from paper_plot_style import COLORS, read_markdown_table, save_fig, to_float
import matplotlib.pyplot as plt


def short_condition(text: str) -> str:
    match = re.match(r"(B5\.\d)\s+(.+)$", text)
    if match:
        text = match.group(2)
    replacements = {
        "Atlas-size and padding locked": "size+pad",
        "Chart count locked within +/-5%": "chart count",
        "Distortion Q95 locked": "distortion",
        "Texture utilization locked": "utilization",
        "All strict matched controls": "all locks",
    }
    return replacements.get(text, text)


def main() -> None:
    rows = read_markdown_table("runs/B5_matched/B5_TABLE.md")
    conditions = []
    for row in rows:
        cond = row["Condition"]
        if cond not in conditions:
            conditions.append(cond)
    assets = ["spot", "bunny"]
    by_key = {(r["Asset"], r["Condition"]): r for r in rows}

    x = np.arange(len(conditions))
    width = 0.36
    fig, ax = plt.subplots(figsize=(6.7, 3.1))
    colors = {"spot": COLORS["blue"], "bunny": COLORS["orange"]}

    for offset, asset in zip([-width / 2, width / 2], assets):
        vals = [to_float(by_key[(asset, c)]["Gain vs initial"]) or 0.0 for c in conditions]
        bars = ax.bar(x + offset, vals, width, color=colors[asset], edgecolor="#222222", linewidth=0.7, alpha=0.86, label=asset)
        for bar, condition in zip(bars, conditions):
            row = by_key[(asset, condition)]
            verdict = row["c5_verdict"]
            ok = row["matched_OK"].lower() == "yes"
            if verdict == "rollback":
                bar.set_hatch("///")
            mark = "\u2713" if ok and verdict == "accept" else "\u00d7"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.35,
                mark,
                ha="center",
                va="bottom",
                fontsize=9,
                fontfamily="DejaVu Sans",
            )

    ax.axhline(0, color="#333333", lw=0.7)
    ax.set_ylabel(r"$\Delta$PSNR vs. initial (dB)")
    ax.set_xticks(x)
    ax.set_xticklabels([short_condition(c) for c in conditions])
    ax.set_ylim(0, 16.8)
    ax.text(0.02, 0.96, "\u2713 matched accept; \u00d7 rollback", transform=ax.transAxes, fontsize=8, va="top", fontfamily="DejaVu Sans")
    ax.legend(frameon=False, ncols=2, loc="upper right")
    save_fig(fig, "fig5_matched")


if __name__ == "__main__":
    main()
