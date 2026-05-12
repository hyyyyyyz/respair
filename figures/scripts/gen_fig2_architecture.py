from __future__ import annotations

from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "figures" / "main"


def write_mermaid_source() -> None:
    source = """flowchart LR
    I[mesh + UV] --> C1[C1 PBR Baker]
    C1 -->|residual| C2[C2 Local Chart Repair]
    C2 -->|repair| C3[C3 Mip Allocator]
    C3 -->|alloc| C4[C4 Seam Diagnostic<br/>(diagnostic only)]
    C4 -->|seam| C5[C5 Validation Loop]
    C5 -->|final atlas or rollback| O[final atlas]
    style C4 stroke-dasharray: 5 5
"""
    (OUT_DIR / "fig2_architecture.mmd").write_text(source, encoding="utf-8")


def draw_block(page: fitz.Page, rect: fitz.Rect, heading: str, body: str, fill: tuple[float, ...], dashed: bool = False) -> None:
    if dashed:
        page.draw_rect(rect, color=(0.12, 0.12, 0.12), fill=fill, width=1.1, dashes="[4 3] 0")
    else:
        page.draw_rect(rect, color=(0.12, 0.12, 0.12), fill=fill, width=1.1)
    page.insert_textbox(
        fitz.Rect(rect.x0 + 8, rect.y0 + 12, rect.x1 - 8, rect.y0 + 34),
        heading,
        fontsize=11,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
        color=(0.05, 0.05, 0.05),
    )
    page.insert_textbox(
        fitz.Rect(rect.x0 + 8, rect.y0 + 40, rect.x1 - 8, rect.y1 - 8),
        body,
        fontsize=8.5,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
        color=(0.12, 0.12, 0.12),
    )


def draw_arrow(page: fitz.Page, start: tuple[float, float], end: tuple[float, float], label: str) -> None:
    color = (0.16, 0.16, 0.16)
    page.draw_line(start, end, color=color, width=1.15)
    x, y = end
    tri = [(x, y), (x - 7, y - 4), (x - 7, y + 4), (x, y)]
    page.draw_polyline(tri, color=color, fill=color, width=0.8)
    midx = (start[0] + end[0]) / 2
    midy = (start[1] + end[1]) / 2
    page.insert_textbox(
        fitz.Rect(midx - 34, midy + 12, midx + 34, midy + 28),
        label,
        fontsize=8,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
        color=(0.18, 0.18, 0.18),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_mermaid_source()

    doc = fitz.open()
    page = doc.new_page(width=860, height=260)
    page.draw_rect(fitz.Rect(0, 0, 860, 260), fill=(1, 1, 1), color=(1, 1, 1))

    blocks = [
        ("C1", "PBR Baker", "mesh + UV\nheld-out relighting\nPBR residual", (0.88, 0.94, 0.98)),
        ("C2", "Local Chart Repair", "top-K charts\nsplit / merge\nboundary slide", (0.91, 0.97, 0.93)),
        ("C3", "Mip Allocator", "fixed texel budget\nvisibility + residual\nmip demand", (1.00, 0.95, 0.86)),
        ("C4", "Seam Diagnostic", "diagnostic only\nchannel-normalized\nreported seam audit", (0.96, 0.91, 0.96)),
        ("C5", "Validation Loop", "accept if relit improves\notherwise rollback", (0.96, 0.96, 0.96)),
    ]
    x0, y0, w, h, gap = 36, 74, 132, 92, 32
    rects = []
    for idx, (cid, title, body, fill) in enumerate(blocks):
        rect = fitz.Rect(x0 + idx * (w + gap), y0, x0 + idx * (w + gap) + w, y0 + h)
        rects.append(rect)
        draw_block(page, rect, f"{cid} {title}", body, fill, dashed=(cid == "C4"))

    labels = ["residual", "repair", "alloc", "seam"]
    for left, right, label in zip(rects[:-1], rects[1:], labels):
        draw_arrow(page, (left.x1, left.y0 + h / 2), (right.x0 - 4, right.y0 + h / 2), label)

    page.insert_textbox(
        fitz.Rect(25, 40, 180, 60),
        "mesh + UV",
        fontsize=9,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
        color=(0.10, 0.10, 0.10),
    )
    page.draw_line((104, 64), (104, 73), color=(0.18, 0.18, 0.18), width=1)
    page.insert_textbox(
        fitz.Rect(692, 176, 840, 206),
        "final atlas\nor baseline rollback",
        fontsize=9,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
        color=(0.10, 0.10, 0.10),
    )
    page.draw_line((758, 166), (758, 176), color=(0.18, 0.18, 0.18), width=1)

    pdf_path = OUT_DIR / "fig2_architecture.pdf"
    png_path = OUT_DIR / "fig2_architecture.png"
    doc.save(pdf_path)
    pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0), alpha=False)
    pix.save(png_path)
    doc.close()
    print(f"Saved: {pdf_path.relative_to(ROOT)}")
    print(f"Saved: {png_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
