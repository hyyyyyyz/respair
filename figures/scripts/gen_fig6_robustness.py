from __future__ import annotations

from collections import defaultdict

from paper_plot_style import COLORS, read_markdown_table, save_fig, to_float
import matplotlib.pyplot as plt


def main() -> None:
    rows = read_markdown_table("runs/B7_robustness/B7_ROBUSTNESS_TABLE.md")
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["Sweep"]].append(row)

    order = [
        ("noise", r"Noise $\sigma$"),
        ("view", "Held-out views"),
        ("light", "Held-out lights"),
    ]
    colors = {"noise": COLORS["red"], "view": COLORS["blue"], "light": COLORS["green"]}
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.65), sharey=False)

    for ax, (sweep, xlabel) in zip(axes, order):
        data = sorted(grouped[sweep], key=lambda r: to_float(r["Level"]) or 0.0)
        xs = [to_float(r["Level"]) or 0.0 for r in data]
        ys = [to_float(r["PSNR"]) or 0.0 for r in data]
        ref = to_float(data[0]["Ref PSNR"]) or ys[0]
        ax.plot(xs, ys, marker="o", ms=4.0, lw=1.5, color=colors[sweep], label="ours")
        ax.axhline(ref, color=COLORS["gray"], lw=0.9, ls="--", label="reference")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("PSNR (dB)")
        ax.text(0.05, 0.92, sweep, transform=ax.transAxes, fontsize=8, va="top")
        if sweep == "noise":
            for row, x, y in zip(data, xs, ys):
                if abs(x - 0.01) < 1e-9:
                    ax.scatter([x], [y], s=120, facecolors="none", edgecolors=COLORS["red"], linewidths=1.5, zorder=4)
                    ax.annotate(
                        r"$\sigma=0.01$",
                        xy=(x, y),
                        xytext=(x + 0.009, y + 3.0),
                        arrowprops={"arrowstyle": "->", "lw": 0.7, "color": COLORS["red"]},
                        fontsize=7.5,
                        color=COLORS["red"],
                    )
        ax.tick_params(axis="x", rotation=0)
    axes[0].legend(frameon=False, loc="lower right", fontsize=7.5)
    fig.tight_layout(w_pad=1.0)
    save_fig(fig, "fig6_robustness")


if __name__ == "__main__":
    main()
