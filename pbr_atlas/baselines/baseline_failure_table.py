"""Failure/partial bookkeeping for B2 baseline reproduction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pbr_atlas.utils.io import atomic_write_json, ensure_dir, write_text


@dataclass
class FailureRecord:
    baseline: str
    asset: str
    repro_status: str
    reason: str
    paper_id: Optional[str] = None
    run_dir: Optional[str] = None
    timestamp: str = ""
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        if not payload["timestamp"]:
            payload["timestamp"] = datetime.now().isoformat(timespec="seconds")
        return payload


def _records_path(output_root: str | Path) -> Path:
    return ensure_dir(output_root) / "failure_records.json"


def record_failure(output_root: str | Path, record: FailureRecord) -> Path:
    path = _records_path(output_root)
    payload = {"records": load_failure_records(output_root)}
    normalized = record.to_dict()
    for existing in payload["records"]:
        if existing.get("baseline") == normalized["baseline"] and existing.get("asset") == normalized["asset"]:
            existing.update(normalized)
            break
    else:
        payload["records"].append(normalized)
    atomic_write_json(path, payload)
    return path


def load_failure_records(output_root: str | Path) -> List[Dict[str, Any]]:
    path = _records_path(output_root)
    if not path.exists():
        return []
    import json

    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle) or {}
    records = payload.get("records", [])
    if not isinstance(records, list):
        return []
    return [dict(item) for item in records]


def write_failure_report(output_root: str | Path, records: Optional[Iterable[Dict[str, Any]]] = None) -> Path:
    root = ensure_dir(output_root)
    entries = sorted(list(records if records is not None else load_failure_records(root)), key=lambda item: (item.get("baseline", ""), item.get("asset", "")))
    lines = [
        "# B2 Failure Table",
        "",
        "| Baseline | Asset | Status | Reason | Paper | Notes |",
        "|---|---|---|---|---|---|",
    ]
    if not entries:
        lines.append("| - | - | - | No failures recorded. | - | - |")
    for item in entries:
        lines.append(
            "| {baseline} | {asset} | {repro_status} | {reason} | {paper_id} | {notes} |".format(
                baseline=item.get("baseline", "-"),
                asset=item.get("asset", "-"),
                repro_status=item.get("repro_status", "-"),
                reason=str(item.get("reason", "-")).replace("\n", " "),
                paper_id=item.get("paper_id", "-") or "-",
                notes=item.get("notes", "-") or "-",
            )
        )
    path = root / "B2_FAILURE_TABLE.md"
    write_text(path, "\n".join(lines) + "\n")
    return path
