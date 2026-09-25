#!/usr/bin/env python3
"""Keep the passive study route free of unresolved answer interpretations."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_DOC = ROOT / "docs" / "上榜精確解答邊界_條件題處理.md"
ROUTE_DOCS = {
    ROOT / "docs" / "上榜預設24時段_核心題路徑.md": 36,
    ROOT / "docs" / "上榜核心母題候選_104-114年.md": 18,
    ROOT / "docs" / "上榜混合橋接_六科12題.md": 12,
    ROOT / "docs" / "上榜考場得分骨架_六科.md": 12,
    ROOT / "docs" / "上榜核心路徑_現行命題大綱對照.md": 12,
    ROOT / "docs" / "上榜起手式急救卡_114-108.md": 15,
    ROOT / "docs" / "上榜被動模考_114年六科執行包.md": 29,
    ROOT / "docs" / "上榜被動複測_108年六科執行包.md": 30,
}
MANIFESTS = (
    ROOT / "data" / "pe-solution-audit.json",
    ROOT / "data" / "engineering-math-audit.json",
)
QID_RE = re.compile(r"EE-\d{3}-\d{2}-\d+")
REVIEW_FIELDS = (
    "review_disposition",
    "review_blocker",
    "review_action",
    "review_evidence",
    "official_source_url",
)


def load_entries() -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for manifest in MANIFESTS:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for entry in data["entries"]:
            qid = entry["qid"]
            if qid in entries:
                raise AssertionError(f"duplicate manifest qid: {qid}")
            entries[qid] = entry
    return entries


def main() -> int:
    entries = load_entries()
    errors: list[str] = []
    route_qids: set[str] = set()

    for path, expected_count in ROUTE_DOCS.items():
        qids = set(QID_RE.findall(path.read_text(encoding="utf-8")))
        if len(qids) != expected_count:
            errors.append(f"{path.name}: expected {expected_count} qids, found {len(qids)}")
        route_qids.update(qids)
        for qid in sorted(qids):
            entry = entries.get(qid)
            if entry is None:
                errors.append(f"{path.name}: {qid} is missing from audit manifests")
            elif entry.get("audit_status") != "verified":
                errors.append(
                    f"{path.name}: {qid} has status {entry.get('audit_status')!r}, not 'verified'"
                )

    boundary_text = BOUNDARY_DOC.read_text(encoding="utf-8")
    manual_entries = sorted(
        (entry for entry in entries.values() if entry.get("audit_status") == "needs_manual_review"),
        key=lambda entry: entry["qid"],
    )
    for entry in manual_entries:
        qid = entry["qid"]
        if qid in route_qids:
            errors.append(f"{qid}: unresolved question leaked into the passive primary route")
        if qid not in boundary_text:
            errors.append(f"{qid}: missing from precision-boundary document")
        for field in REVIEW_FIELDS:
            if not entry.get(field):
                errors.append(f"{qid}: missing {field} in audit manifest")
        solution = ROOT / entry["solution_link"]
        if not solution.is_file():
            errors.append(f"{qid}: missing canonical solution {entry['solution_link']}")
        else:
            source = solution.read_text(encoding="utf-8")
            if "audit_status: needs_manual_review" not in source:
                errors.append(f"{qid}: canonical status disagrees with manifest")

    for phrase in (
        "先寫假設",
        "條件解",
        "不當成唯一答案背誦",
        "不進入預設核心路徑",
    ):
        if phrase not in boundary_text:
            errors.append(f"precision-boundary document is missing policy phrase: {phrase}")

    if errors:
        print("Passive route status audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Passive route status audit: "
        f"{len(route_qids)} unique routed qids are verified; "
        f"{len(manual_entries)} needs_manual_review questions are isolated and documented"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
