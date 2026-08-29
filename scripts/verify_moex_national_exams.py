# -*- coding: utf-8 -*-
"""Audit official MOEX provenance and question-level crop coverage.

This verifier deliberately does not equate file existence with authenticity.
It checks the official host, downloaded PDF digest, page count, active source
Markdown, question crops, and figure crops. Solution completeness is a
separate gate and is opt-in with ``--require-solutions`` until every question
has an independently validated derivation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = WORKSPACE / "data" / "moex-national-exams.json"
CROP_MANIFEST = WORKSPACE / "data" / "moex-question-crops.json"
OFFICIAL_HOST = "wwwq.moex.gov.tw"
SUBJECT_DIRS = {
    "電路學": "01_電路學",
    "電子學": "02_電子學_含電力電子",
    "工程數學": "03_工程數學",
    "電機機械": "04_電機機械",
    "電力系統": "05_電力系統",
}
SUBJECT_IDS = {
    "電路學": "01",
    "電子學": "02",
    "工程數學": "03",
    "電機機械": "04",
    "電力系統": "05",
}
QUESTION_NUMBERS = {
    1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
    6: "六", 7: "七", 8: "八", 9: "九", 10: "十",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def active_source_path(year: int, subject: str) -> Path:
    directory = WORKSPACE / "依考科分類" / "🏛️_國考同級參考題庫" / SUBJECT_DIRS[subject]
    return directory / f"GK_{year}年_{subject}.md"


def canonical_question_id(year: int, subject: str, question: dict) -> str:
    """Return the application-facing id, independent of manifest description ids."""
    sid = SUBJECT_IDS[subject]
    kind = question.get("question_kind", "essay")
    qnum = question.get("question_number")
    if kind in {"multiple_choice", "mc", "choice"}:
        if qnum is None:
            match = re.search(r"-MC(\d+)$", question.get("question_id", ""))
            assert_true(match is not None, f"MC question has no number: {question}")
            qnum = int(match.group(1))
        return f"GK-{year}-{sid}-MC{int(qnum):02d}"
    assert_true(qnum is not None, f"Essay question has no number: {question}")
    return f"GK-{year}-{sid}-{int(qnum)}"


def audit_sources() -> tuple[dict, dict]:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    crops = json.loads(CROP_MANIFEST.read_text(encoding="utf-8"))
    entries = source["entries"]
    crop_entries = crops["entries"]
    assert_true(len(crop_entries) == len(entries), "Crop manifest does not cover source manifest")

    downloaded = [entry for entry in entries if entry["status"] == "downloaded"]
    unavailable = [entry for entry in entries if entry["status"] != "downloaded"]
    assert_true(len(downloaded) + len(unavailable) == len(entries), "Source manifest status accounting mismatch")

    crop_by_key = {(entry["year"], entry["subject"]): entry for entry in crop_entries}
    question_count = 0
    figure_count = 0
    question_ids: set[str] = set()
    for entry in entries:
        key = (entry["year"], entry["subject"])
        crop_entry = crop_by_key.get(key)
        assert_true(crop_entry is not None, f"Missing crop entry for {key}")
        if entry["status"] != "downloaded":
            assert_true(crop_entry.get("question_count", 0) == 0, f"Unavailable slot has crops: {key}")
            assert_true(not active_source_path(*key).exists(), f"Unavailable source still active: {key}")
            continue

        url = entry["official_url"]
        assert_true(url.startswith(f"https://{OFFICIAL_HOST}/"), f"Non-official URL: {url}")
        pdf_path = WORKSPACE / entry["target_path"]
        assert_true(pdf_path.exists(), f"Missing official PDF: {pdf_path}")
        data = pdf_path.read_bytes()
        assert_true(data.startswith(b"%PDF-"), f"Not a PDF: {pdf_path}")
        assert_true(digest(pdf_path) == entry["sha256"], f"SHA-256 mismatch: {pdf_path}")
        source_path = active_source_path(*key)
        assert_true(source_path.exists(), f"Missing active source Markdown: {key}")
        source_text = source_path.read_text(encoding="utf-8")
        assert_true("source_kind: moex_official_question_pdf" in source_text, f"Missing provenance frontmatter: {key}")
        assert_true(entry["sha256"] in source_text, f"Source Markdown is not tied to PDF digest: {key}")

        for page_index in range(1, entry["page_count"] + 1):
            page_path = pdf_path.parent / "images" / "pages" / f"GK_{entry['year']}年_{entry['subject']}_p{page_index:02d}.png"
            assert_true(page_path.exists() and page_path.stat().st_size > 0, f"Missing page render: {page_path}")
        assert_true(crop_entry["question_count"] > 0, f"No questions cropped: {key}")
        assert_true(crop_entry["question_count"] == len(crop_entry["questions"]), f"Crop count mismatch: {key}")
        for question in crop_entry["questions"]:
            qid = question["question_id"]
            assert_true(qid not in question_ids, f"Duplicate question id: {qid}")
            question_ids.add(qid)
            q_path = WORKSPACE / question["question_crop"]
            assert_true(q_path.exists() and q_path.stat().st_size > 0, f"Missing question crop: {q_path}")
            for figure_path in question["figure_crops"]:
                f_path = WORKSPACE / figure_path
                assert_true(f_path.exists() and f_path.stat().st_size > 0, f"Missing figure crop: {f_path}")
                figure_count += 1
            question_count += 1

    summary = {
        "slots": len(entries),
        "official_pdfs": len(downloaded),
        "unavailable_slots": len(unavailable),
        "questions": question_count,
        "figure_crops": figure_count,
    }
    return source, summary


def audit_solutions(source: dict) -> dict:
    crops = json.loads(CROP_MANIFEST.read_text(encoding="utf-8"))
    crop_by_key = {
        (entry["year"], entry["subject"]): entry
        for entry in crops.get("entries", [])
    }
    pending = []
    invalid_entries = []
    validated = []
    total = 0
    for entry in source["entries"]:
        if entry["status"] != "downloaded":
            continue
        crop_entry = crop_by_key.get((entry["year"], entry["subject"]), {})
        # The manifest id describes the source crop.  Derive the application
        # id independently so descriptive subject names never leak into ids.
        expected_questions = {}
        for question in crop_entry.get("questions", []):
            canonical_id = canonical_question_id(entry["year"], entry["subject"], question)
            expected_questions[canonical_id] = question
        expected_ids = set(expected_questions)
        total += len(expected_ids)
        subject_dir = WORKSPACE / "📝 個人題解與錯題本" / "🏛️_國考同級題解" / SUBJECT_DIRS[entry["subject"]]
        path = subject_dir / f"GK_{entry['year']}年_{entry['subject']}_全卷完整詳細題解.md"
        if not path.exists():
            pending.extend(sorted(expected_ids))
            continue
        text = path.read_text(encoding="utf-8")
        if not re.search(rf"^source_pdf_sha256:\s*{re.escape(entry['sha256'])}\s*$", text, flags=re.MULTILINE):
            invalid_entries.append(f"{path.relative_to(WORKSPACE)} (source hash missing)")
            pending.extend(sorted(expected_ids))
            continue
        match = re.search(r"validated_question_ids:\s*\[([^\]]*)\]", text)
        listed = {
            item.strip().strip("'\"")
            for item in match.group(1).split(",")
        } if match else set()
        paper_status = re.search(r"^validation_status:\s*(\w+)\s*$", text, flags=re.MULTILINE)
        status = paper_status.group(1) if paper_status else ""
        if status not in {"partial", "validated"}:
            invalid_entries.append(f"{path.relative_to(WORKSPACE)} (invalid validation_status: {status or 'missing'})")
        if status == "validated" and listed != expected_ids:
            invalid_entries.append(
                f"{path.relative_to(WORKSPACE)} (validated paper id set does not match official questions)"
            )
        unknown = sorted(listed - expected_ids)
        if unknown:
            invalid_entries.append(f"{path.relative_to(WORKSPACE)} (unknown ids: {', '.join(unknown)})")
        for qid in sorted(expected_ids):
            if qid not in listed:
                pending.append(qid)
                continue
            question = expected_questions[qid]
            qnum = question.get("app_question_number", question.get("question_number"))
            legacy_num = question.get("question_number")
            tokens = [str(qnum)]
            if legacy_num is not None:
                tokens.append(QUESTION_NUMBERS.get(legacy_num, str(legacy_num)))
            heading = None
            for token in dict.fromkeys(tokens):
                heading = re.search(
                    rf"^##\s+(?:第\s*)?{re.escape(token)}(?:\s*[、.：:]|\s+)",
                    text,
                    flags=re.MULTILINE,
                )
                if heading:
                    break
            if not heading:
                invalid_entries.append(f"{path.relative_to(WORKSPACE)} ({qid}: solution heading missing)")
                pending.append(qid)
                continue
            next_heading = re.search(r"^##\s+", text[heading.end():], flags=re.MULTILINE)
            section_end = heading.end() + next_heading.start() if next_heading else len(text)
            section = text[heading.start():section_end]
            crop_name = Path(question["question_crop"]).name
            section_errors = []
            if len(section.strip()) < 250:
                section_errors.append("solution section too short")
            if crop_name not in section:
                section_errors.append("official question crop not referenced")
            if not any(marker in section for marker in ("獨立驗算", "驗算", "核對", "一致")):
                section_errors.append("independent check not documented")
            if section_errors:
                invalid_entries.append(
                    f"{path.relative_to(WORKSPACE)} ({qid}: {', '.join(section_errors)})"
                )
                pending.append(qid)
                continue
            validated.append(qid)
    return {
        "total_questions": total,
        "validated_questions": len(set(validated)),
        "pending_question_ids": sorted(set(pending)),
        "invalid_solution_entries": invalid_entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-solutions", action="store_true")
    args = parser.parse_args()
    try:
        source, summary = audit_sources()
        print("MOEX source and crop audit: PASS")
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        solutions = audit_solutions(source)
        pending = solutions["pending_question_ids"]
        if pending or solutions["invalid_solution_entries"]:
            print("Solution validation: PENDING")
            print(json.dumps({
                "total_questions": solutions["total_questions"],
                "validated_questions": solutions["validated_questions"],
                "pending_questions": len(pending),
                "invalid_solution_entries": solutions["invalid_solution_entries"],
            }, ensure_ascii=False, sort_keys=True))
            if args.require_solutions:
                return 1
        else:
            print("Solution validation: PASS")
            print(json.dumps({
                "total_questions": solutions["total_questions"],
                "validated_questions": solutions["validated_questions"],
            }, ensure_ascii=False, sort_keys=True))
        return 0
    except (AssertionError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"MOEX audit: FAIL — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
