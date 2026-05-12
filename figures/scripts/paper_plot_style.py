from __future__ import annotations

import csv
import json
import math
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/dip_1_ws_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/dip_1_ws_cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "figures" / "main"
TABLE_DIR = ROOT / "paper" / "tables"
DPI = 300
FONT_SIZE = 9

# Okabe-Ito colorblind-safe palette, with grayscale-distinct values.
COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "yellow": "#F0E442",
    "black": "#000000",
    "gray": "#666666",
    "light_gray": "#D9D9D9",
}

plt.rcParams.update(
    {
        "font.size": FONT_SIZE,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "axes.labelsize": FONT_SIZE,
        "axes.titlesize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE - 1,
        "ytick.labelsize": FONT_SIZE - 1,
        "legend.fontsize": FONT_SIZE - 1,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "text.usetex": False,
        "mathtext.fontset": "stix",
    }
)


def ensure_dirs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def save_fig(fig: plt.Figure, name: str) -> None:
    ensure_dirs()
    for ext in ("pdf", "png"):
        out = FIG_DIR / f"{name}.{ext}"
        fig.savefig(out)
        print(f"Saved: {out.relative_to(ROOT)}")
    plt.close(fig)


def read_markdown_table(path: Path | str) -> list[dict[str, str]]:
    path = ROOT / path if not isinstance(path, Path) else path
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            current.append(line.strip())
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    for block in blocks:
        if len(block) < 2:
            continue
        if not re.match(r"^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|$", block[1]):
            continue
        header = _split_md_row(block[0])
        rows = []
        for row_line in block[2:]:
            fields = _split_md_row(row_line)
            if len(fields) != len(header):
                continue
            rows.append(dict(zip(header, fields)))
        return rows
    raise ValueError(f"No markdown table found in {path}")


def _split_md_row(line: str) -> list[str]:
    return [cell.strip() for cell in next(csv.reader([line.strip().strip("|")], delimiter="|"))]


def read_expected_delta(path: Path | str = "runs/B4_ablation/B4_RESULTS.md") -> dict[str, str]:
    path = ROOT / path
    expected: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- (A\d+):\s*(.+)$", line.strip())
        if match:
            expected[match.group(1)] = match.group(2)
    return expected


def to_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text in {"", "-", "--", "nan", "None"}:
        return None
    if text.lower() in {"inf", "+inf", "infinity"}:
        return math.inf
    if text.lower() == "-inf":
        return -math.inf
    try:
        return float(text)
    except ValueError:
        return None


def format_num(value: object, digits: int = 2, signed: bool = False) -> str:
    val = to_float(value)
    if val is None:
        return "--"
    if math.isinf(val):
        return r"$\infty$" if val > 0 else r"$-\infty$"
    fmt = f"{{:{'+' if signed else ''}.{digits}f}}"
    return fmt.format(val)


def format_delta(value: object, digits: int = 2, bold_positive: bool = False) -> str:
    val = to_float(value)
    if val is None:
        return "--"
    text = format_num(val, digits=digits, signed=True)
    if bold_positive and val > 1e-9:
        return rf"\textbf{{{text}}}"
    return text


def latex_escape(text: object) -> str:
    text = str(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def short_baseline(name: str) -> str:
    return {
        "xatlas_classical": "xatlas",
        "partuv": "PartUV",
        "blender_uv": "Blender UV",
        "matched_oracle": "oracle",
    }.get(name, name)


def load_json(path: Path | str) -> dict:
    path = ROOT / path if not isinstance(path, Path) else path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def b3_metrics(asset: str, baseline: str) -> dict | None:
    path = ROOT / "runs" / "B3_main" / f"{asset}_{baseline}_ours_seed42" / "metrics.json"
    return load_json(path) if path.exists() else None


def verdict_from_metrics(metrics: dict | None) -> str:
    if not metrics:
        return "missing"
    return "accept" if metrics.get("c5", {}).get("accept") else "rollback"


def add_zero_line(ax: plt.Axes) -> None:
    ax.axvline(0, color="#333333", lw=0.7, zorder=0)


def match_hatch(match: str) -> str:
    if match == "yes":
        return ""
    if match == "no":
        return "///"
    return "xx"


def expected_direction(text: str) -> str:
    lower = text.lower()
    if not text:
        return "not run"
    if ">= +" in lower or "positive" in lower or "keep >=70%" in lower or "remains >= +0.3" in lower:
        return "gain kept"
    if "psnr +0 to +0.1" in lower or "psnr <= +0.1" in lower:
        return "weak / rollback"
    if "psnr -" in lower or "relit psnr -" in lower or "held-out psnr -" in lower or "mip leakage +" in lower:
        return "negative"
    if "seam residual +10" in lower or "normal seam +" in lower:
        return "negative"
    if "remains <= -8%" in lower:
        return "matched gain"
    return "diagnostic"


def observed_match(values: list[float | None], direction: str) -> str:
    vals = [v for v in values if v is not None and not math.isinf(v)]
    if not vals:
        return "n/a"
    worst = min(vals)
    best = max(vals)
    if direction in {"gain kept", "matched gain"}:
        return "yes" if best >= 0.25 or worst >= -0.1 else "no"
    if direction == "negative":
        return "yes" if worst < -0.1 else "no"
    if direction == "weak / rollback":
        return "yes" if max(abs(v) for v in vals) <= 0.15 or worst < -5.0 else "no"
    return "yes"


def table_preamble(caption: str, label: str, columns: str) -> list[str]:
    return [
        r"\begin{table}[t]",
        r"\centering",
        r"\scriptsize",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        rf"\begin{{tabular}}{{@{{}}{columns}@{{}}}}",
        r"\toprule",
    ]


def write_table(path: Path, lines: list[str]) -> None:
    ensure_dirs()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved: {path.relative_to(ROOT)}")


def row(cells: list[str]) -> str:
    return " & ".join(cells) + r" \\"


def legend_for_match() -> list[Patch]:
    return [
        Patch(facecolor="white", edgecolor=COLORS["gray"], label="expected matched"),
        Patch(facecolor="white", edgecolor=COLORS["gray"], hatch="///", label="direction mismatch"),
        Patch(facecolor="white", edgecolor=COLORS["gray"], hatch="xx", label="not completed"),
    ]
