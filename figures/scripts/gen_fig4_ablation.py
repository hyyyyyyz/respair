from __future__ import annotations

import re
from collections import defaultdict

import numpy as np

from paper_plot_style import (
    COLORS,
    expected_direction,
    format_num,
    legend_for_match,
    match_hatch,
    observed_match,
    read_expected_delta,
    read_markdown_table,
    save_fig,
    to_float,
)
import matplotlib.pyplot as plt


def main() -> None:
    rows = read_markdown_table("runs/B4_ablation/B4_TABLE.md")
    expected = read_expected_delta()
    # Match LaTeX Table 2 ablation rows; A10/A11/A13 are not in the headline
    # table (A10/A11 have no completed run, A13 is folded into matched-control).
    ids = [
        "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9",
        "A12", "A14", "A15", "A16", "A17", "A18",
    ]
    assets = ["spot", "bunny"]

    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        aid = row["Ablation"]
        match = re.search(r"([^/]+)/partuv", row["Case (asset/baseline)"])
        if not match:
            continue
        asset = match.group(1)
        val = to_float(row["dPSNR vs ours"])
        if val is not None:
            grouped[(aid, asset)].append(val)

    y = np.arange(len(ids))
    height = 0.34
    fig, ax = plt.subplots(figsize=(7.0, 6.6))
    asset_colors = {"spot": COLORS["blue"], "bunny": COLORS["orange"]}

    for dy, asset in zip([-height / 2, height / 2], assets):
        values = []
        hatches = []
        for aid in ids:
            vals = grouped.get((aid, asset), [])
            value = min(vals) if vals else 0.0
            values.append(value)
            direction = expected_direction(expected.get(aid, ""))
            match = observed_match([to_float(v) for v in vals], direction)
            hatches.append(match_hatch(match))
        bars = ax.barh(
            y + dy,
            values,
            height,
            color=asset_colors[asset],
            edgecolor="#222222",
            linewidth=0.6,
            alpha=0.84,
            label=asset,
        )
        for bar, aid, hatch in zip(bars, ids, hatches):
            bar.set_hatch(hatch)
            vals = grouped.get((aid, asset), [])
            if not vals:
                ax.text(0.15, bar.get_y() + bar.get_height() / 2, "n/a", va="center", fontsize=7, color=COLORS["gray"])
            elif abs(bar.get_width()) >= 0.35:
                x_text = bar.get_width() - 0.15 if bar.get_width() < 0 else bar.get_width() + 0.15
                ha = "right" if bar.get_width() < 0 else "left"
                ax.text(x_text, bar.get_y() + bar.get_height() / 2, format_num(bar.get_width(), 1, signed=True), va="center", ha=ha, fontsize=7)

    ax.axvline(0, color="#333333", lw=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(ids)
    ax.invert_yaxis()
    ax.set_xlabel(r"$\Delta$PSNR vs. full method (dB); worst completed variant per ablation")
    ax.set_xlim(-15.8, 2.6)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles + legend_for_match(), labels + ["expected matched", "direction mismatch", "not completed"], frameon=False, loc="lower left", ncols=2)
    save_fig(fig, "fig4_ablation")


if __name__ == "__main__":
    main()
