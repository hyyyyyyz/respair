from __future__ import annotations

import math

import numpy as np

from paper_plot_style import COLORS, b3_metrics, format_num, read_markdown_table, save_fig, short_baseline, to_float, verdict_from_metrics
import matplotlib.pyplot as plt


def main() -> None:
    rows = read_markdown_table("runs/B3_main/MAIN_TABLE.md")
    assets = ["spot", "bunny"]
    baselines = ["xatlas_classical", "partuv", "blender_uv", "matched_oracle"]
    asset_colors = {"spot": COLORS["blue"], "bunny": COLORS["orange"]}

    by_key = {(r["Asset"], r["Baseline"]): r for r in rows}
    x = np.arange(len(baselines))
    width = 0.36
    fig, ax = plt.subplots(figsize=(6.6, 3.0))

    for offset, asset in zip([-width / 2, width / 2], assets):
        vals = []
        verdicts = []
        labels = []
        for baseline in baselines:
            row = by_key[(asset, baseline)]
            val = to_float(row["dPSNR"])
            if val is None or math.isinf(val):
                val = 0.0
                labels.append("n/a")
            else:
                labels.append(format_num(val, 1, signed=True))
            metrics = b3_metrics(asset, baseline)
            verdicts.append(verdict_from_metrics(metrics))
            vals.append(val)

        bars = ax.bar(
            x + offset,
            vals,
            width,
            label=asset,
            color=asset_colors[asset],
            edgecolor="#222222",
            linewidth=0.7,
            alpha=0.86,
        )
        for bar, verdict, label in zip(bars, verdicts, labels):
            if verdict == "rollback":
                bar.set_hatch("///")
            y = bar.get_height()
            text_y = y + 0.35 if y >= 0 else 0.35
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                text_y,
                "A" if verdict == "accept" else "R",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color="#111111",
            )
            if label == "n/a":
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    0.05,
                    "n/a",
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    rotation=90,
                    color=COLORS["gray"],
                )

    ax.axhline(0, color="#333333", lw=0.7)
    ax.set_ylabel(r"$\Delta$PSNR vs. initial (dB)")
    ax.set_xticks(x)
    ax.set_xticklabels([short_baseline(b) for b in baselines])
    ax.set_ylim(-0.5, 16.8)
    ax.text(0.01, 0.96, "A = accepted, R = rollback", transform=ax.transAxes, fontsize=8, va="top")
    ax.legend(frameon=False, ncols=2, loc="upper right")
    save_fig(fig, "fig3_comparison")


if __name__ == "__main__":
    main()
