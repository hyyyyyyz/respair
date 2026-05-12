#!/usr/bin/env python
"""Apply the W1 paper restructure once DiLiGenT-MV captured results land.

Replaces title, swaps abstract, inserts Section 3 "Target signal regime"
subsection, drops C4/mip from contributions list (intro + method overview),
and inserts the captured-target headline table reference in Section 4.

Usage:
  python scripts/apply_restructure.py --dry-run    # preview diff
  python scripts/apply_restructure.py              # apply in place
  python scripts/apply_restructure.py --revert     # restore from .preW1 backup
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1] / "paper"
BACKUP_SUFFIX = ".preW1"

NEW_TITLE_LONG = "Captured-Target Residuals for Selective UV Atlas Repair"
NEW_TITLE_SHORT = "Captured-Target UV Atlas Repair"

ABSTRACT_DRAFT = PAPER.parent / "refine-logs" / "ABSTRACT_RESTRUCTURED_DRAFT.tex"
TARGET_REGIME_DRAFT = PAPER.parent / "refine-logs" / "SECTION3_TARGET_REGIME_DRAFT.tex"

PATCHES: list[tuple[str, str, str]] = [
    # (relative path, find, replace)
    (
        "main.tex",
        "\\title[PBR Baking-Error Atlases]%\n      {PBR Baking-Error Atlases for Selective UV Atlas Repair}",
        f"\\title[{NEW_TITLE_SHORT}]%\n      {{{NEW_TITLE_LONG}}}",
    ),
    (
        "sections/1_introduction.tex",
        "This paper makes four contributions. We also report an additional cross-channel seam diagnostic transparently despite its limited isolated signal in the present ablation hooks.",
        "This paper makes four contributions. We additionally report a cross-channel seam diagnostic and an explicit mip term as instrumented diagnostics rather than validated components, with their honest limitations disclosed in \\cref{sec:limitations}.",
    ),
    (
        "sections/3_method.tex",
        "The method has four deployment components plus one reported diagnostic: C1 differentiable PBR baking, C2 residual-attributed chart repair, C3 mip-aware texel reallocation, C4 cross-channel seam diagnostic, and C5 matched-control validation.",
        "The method has four deployment components plus reported diagnostics: C1 differentiable PBR baking, C2 residual-attributed chart repair, C3 residual-aware texel allocation, and C5 matched-control validation. A cross-channel seam diagnostic and an explicit mip term are kept as instrumentation but are not claimed as validated contributions; their isolation evidence is explicitly weak in \\cref{sec:limitations}.",
    ),
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _backup(path: Path) -> None:
    bak = path.with_suffix(path.suffix + BACKUP_SUFFIX)
    if not bak.exists():
        shutil.copy2(path, bak)


def _restore(path: Path) -> bool:
    bak = path.with_suffix(path.suffix + BACKUP_SUFFIX)
    if bak.exists():
        shutil.copy2(bak, path)
        return True
    return False


def _apply_patches(dry_run: bool) -> list[str]:
    msgs: list[str] = []
    for rel, find, replace in PATCHES:
        path = PAPER / rel
        if not path.exists():
            msgs.append(f"  skip {rel}: file missing")
            continue
        text = _read(path)
        if find not in text:
            msgs.append(f"  skip {rel}: pattern not found (already applied?)")
            continue
        if dry_run:
            msgs.append(f"  would patch {rel}: {len(find)} chars -> {len(replace)} chars")
            continue
        _backup(path)
        _write(path, text.replace(find, replace, 1))
        msgs.append(f"  patched {rel}")
    return msgs


def _swap_abstract(dry_run: bool) -> str:
    abstract_path = PAPER / "sections" / "0_abstract.tex"
    if not ABSTRACT_DRAFT.exists():
        return f"  skip abstract: draft missing at {ABSTRACT_DRAFT}"
    body = _read(ABSTRACT_DRAFT)
    body = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("%"))
    body = body.strip() + "\n"
    if dry_run:
        return f"  would replace abstract ({len(body)} chars)"
    _backup(abstract_path)
    _write(abstract_path, body)
    return "  swapped abstract"


def _insert_target_regime(dry_run: bool) -> str:
    method_path = PAPER / "sections" / "3_method.tex"
    if not TARGET_REGIME_DRAFT.exists():
        return f"  skip target_regime: draft missing"
    text = _read(method_path)
    if "\\subsection{Target signal regime}" in text:
        return "  skip target_regime: already inserted"
    anchor = "\\subsection{C5: matched-control deployment gate}"
    if anchor not in text:
        return "  skip target_regime: anchor not found"
    insert_body = _read(TARGET_REGIME_DRAFT)
    insert_body = "\n".join(line for line in insert_body.splitlines() if not line.lstrip().startswith("%"))
    insert_body = insert_body.strip() + "\n\n"
    if dry_run:
        return f"  would insert target_regime ({len(insert_body)} chars) before C5 subsection"
    _backup(method_path)
    new_text = text.replace(anchor, insert_body + anchor, 1)
    _write(method_path, new_text)
    return "  inserted Target signal regime subsection"


def _revert_all() -> list[str]:
    msgs: list[str] = []
    for rel, _, _ in PATCHES:
        path = PAPER / rel
        msgs.append(f"  {'reverted' if _restore(path) else 'no backup'}: {rel}")
    for rel in ["sections/0_abstract.tex", "sections/3_method.tex"]:
        path = PAPER / rel
        if rel != "sections/3_method.tex":  # already in PATCHES list won't double, but abstract/method here are separate
            msgs.append(f"  {'reverted' if _restore(path) else 'no backup'}: {rel}")
    return msgs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--revert", action="store_true")
    args = parser.parse_args()

    if args.revert:
        print("Reverting paper sections from .preW1 backups:")
        for m in _revert_all():
            print(m)
        return

    print(f"{'DRY-RUN' if args.dry_run else 'APPLY'} restructure to {PAPER}:")
    for m in _apply_patches(args.dry_run):
        print(m)
    print(_swap_abstract(args.dry_run))
    print(_insert_target_regime(args.dry_run))

    if args.dry_run:
        print("\nNothing modified. Re-run without --dry-run to apply.")
    else:
        print("\nDone. Recompile with: cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex")


if __name__ == "__main__":
    main()
