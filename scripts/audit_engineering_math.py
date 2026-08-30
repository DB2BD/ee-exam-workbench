#!/usr/bin/env python3
"""Build a reproducible audit manifest for PE engineering-math solutions.

This first pass is intentionally conservative: it detects shared/template
solution bodies and records provenance, but never declares a solution
verified.  Solver/Verifier evidence can then update individual entries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard-data.js"
CROP_MANIFEST = ROOT / "data" / "pe-question-crops.json"
DEFAULT_OUTPUT = ROOT / "data" / "engineering-math-audit.json"
BATCH_QIDS = {
    "EE-114-03-3", "EE-113-03-1", "EE-113-03-2", "EE-112-03-1",
    "EE-111-03-1", "EE-111-03-2", "EE-110-03-1", "EE-110-03-2",
    "EE-109-03-1", "EE-109-03-2",
}


def load_dashboard() -> list[list]:
    text = DASHBOARD.read_text(encoding="utf-8")
    match = re.search(r"questions:\s*(\[.*?\]),\s*\n\s*sevenLayers:", text, re.S)
    if not match:
        raise ValueError("dashboard-data.js questions array not found")
    return json.loads(match.group(1))


def load_crops() -> dict[str, dict]:
    data = json.loads(CROP_MANIFEST.read_text(encoding="utf-8"))
    result: dict[str, dict] = {}
    for entry in data.get("entries", []):
        for question in entry.get("questions", []):
            app_id = question.get("app_question_id")
            if app_id:
                result[app_id] = {
                    "question_crop": question.get("question_crop", ""),
                    "source_pages": question.get("source_pages", []),
                }
    return result


def extract_question(raw: str, qnum: int) -> str:
    parts = re.split(r"(?=\n##\s+(?:第\s*[一二三四五六七八九十\d]+\s*[大題題]|[一二三四五六七八九十\d]+\s*[、.：:]))", raw)
    if len(parts) <= 1:
        return raw
    for part in parts[1:]:
        match = re.search(r"##\s+(?:第\s*([一二三四五六七八九十\d]+)\s*[大題題]|([一二三四五六七八九十\d]+)\s*[、.：:])", part)
        if not match:
            continue
        token = match.group(1) or match.group(2)
        try:
            value = int(token)
        except ValueError:
            value = "一二三四五六七八九十".index(token) + 1
        if value == qnum:
            return part
    return parts[qnum] if qnum < len(parts) else raw


def solution_body(raw: str, qnum: int) -> str:
    section = extract_question(raw, qnum)
    # Ignore the question statement and ordinal headings when detecting
    # copy/paste solution bodies; retain all explanatory text and formulas.
    marker = re.search(r"###\s+(?:💡|✏️|🎯)", section)
    body = section[marker.start() :] if marker else section
    body = re.sub(r"第\s*[一二三四五六七八九十\d]+\s*題", "第 N 題", body)
    return re.sub(r"\s+", " ", body).strip()


def canonical_metadata(path: Path) -> dict[str, str]:
    """Read the small YAML front matter used by canonical question notes."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    head = text.split("---", 2)[1]
    result: dict[str, str] = {}
    for line in head.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("'\"")
    return result


def make_entries(records: list[list], crop_map: dict[str, dict], existing: dict) -> list[dict]:
    entries: list[dict] = []
    hashes: defaultdict[str, list[str]] = defaultdict(list)
    prepared: list[tuple[list, str, str, dict]] = []
    for record in records:
        if record[1] != "03":
            continue
        qid, _sid, year, qnum, topic, _tags, solution_link = record[:7]
        path = ROOT / solution_link
        raw = path.read_text(encoding="utf-8") if path.is_file() else ""
        body = solution_body(raw, qnum)
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        hashes[digest].append(qid)
        prepared.append((record, body, digest, crop_map.get(qid, {}), canonical_metadata(path)))

    for record, body, digest, crop, metadata in prepared:
        qid, _sid, year, qnum, topic, _tags, solution_link = record[:7]
        old = existing.get(qid, {})
        status = metadata.get("audit_status") or old.get("audit_status") or ("suspected_error" if len(hashes[digest]) > 1 else "not_attempted")
        entries.append({
            "qid": qid,
            "year": year,
            "question_number": qnum,
            "chapter": topic,
            "solution_link": solution_link,
            "source_crop": crop.get("question_crop", ""),
            "source_pages": crop.get("source_pages", []),
            "solution_version": metadata.get("solution_version") or (
                "canonical-1.0.0" if "/canonical/" in solution_link
                else old.get("solution_version", "legacy")
            ),
            "audit_status": status,
            "verified_at": metadata.get("verified_at") or old.get("verified_at") or (date.today().isoformat() if status == "verified" else None),
            "method": metadata.get("method", old.get("method", "template_hash_screening")),
            "evidence_hash": old.get("evidence_hash", digest),
            "solution_hash": digest,
            "duplicate_qids": hashes[digest] if len(hashes[digest]) > 1 else [],
            "solver_output": old.get("solver_output", ""),
            "review_note": old.get("review_note", ""),
            "supersedes": old.get("supersedes"),
        })
    return sorted(entries, key=lambda item: (item["year"], item["question_number"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--batch", default="all", choices=("all", "ode-laplace"))
    parser.add_argument("--write", action="store_true", help="write the manifest; otherwise print a summary")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    existing = {}
    if output.is_file():
        previous = json.loads(output.read_text(encoding="utf-8"))
        existing = {item["qid"]: item for item in previous.get("entries", [])}
    entries = make_entries(load_dashboard(), load_crops(), existing)
    if args.batch == "ode-laplace":
        entries = [item for item in entries if item["qid"] in BATCH_QIDS]
    result = {
        "schema_version": 1,
        "scope": "PE 工程數學 104-114",
        "generated_at": date.today().isoformat(),
        "status_policy": ["verified", "suspected_error", "needs_manual_review", "not_attempted"],
        "entries": entries,
        "summary": {
            "questions": len(entries),
            "verified": sum(item["audit_status"] == "verified" for item in entries),
            "suspected_error": sum(item["audit_status"] == "suspected_error" for item in entries),
            "needs_manual_review": sum(item["audit_status"] == "needs_manual_review" for item in entries),
            "not_attempted": sum(item["audit_status"] == "not_attempted" for item in entries),
        },
    }
    if args.write:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
