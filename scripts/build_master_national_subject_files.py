# -*- coding: utf-8 -*-
"""Build GK subject master indexes from the MOEX provenance manifest.

Importing this module is side-effect free.  The five indexes contain source
links and solution-validation status, never copied legacy question text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


WORKSPACE = Path(__file__).resolve().parents[1]
MANIFEST = WORKSPACE / "data" / "moex-national-exams.json"
PDF_DIRECTORY = WORKSPACE / "data" / "official_pdfs" / "gk"
MASTER_DIRECTORY = WORKSPACE / "依考科分類" / "🏛️_國考同級參考題庫"
SOLUTION_DIRECTORY = WORKSPACE / "📝 個人題解與錯題本" / "🏛️_國考同級題解"
MOEX_QUERY = "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx"

SUBJECT_DIRS = {
    "電路學": "01_電路學",
    "電子學": "02_電子學_含電力電子",
    "工程數學": "03_工程數學",
    "電機機械": "04_電機機械",
    "電力系統": "05_電力系統",
}
SUBJECT_TITLES = {"電子學": "電子學（含電力電子）"}
YEARS = (114, 113, 112, 111, 110)
EXPECTED_KEYS = {(year, subject) for year in YEARS for subject in SUBJECT_DIRS}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_entries() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])
    by_key = {(entry.get("year"), entry.get("subject")): entry for entry in entries}
    if len(entries) != 25 or len(by_key) != 25 or set(by_key) != EXPECTED_KEYS:
        raise ValueError("MOEX manifest must contain exactly the 25 expected year/subject slots")
    downloaded = [entry for entry in entries if entry.get("status") == "downloaded"]
    unavailable = [entry for entry in entries if entry.get("status") == "not_available_in_selected_exam_class"]
    if len(downloaded) != 23 or len(unavailable) != 2:
        raise ValueError("Expected 23 downloaded official sources and 2 unavailable slots")
    for entry in entries:
        if entry.get("status") == "downloaded":
            official_url = urlparse(entry.get("official_url", ""))
            if official_url.scheme != "https" or official_url.hostname != "wwwq.moex.gov.tw":
                raise ValueError(f"Invalid official URL for {entry['year']} {entry['subject']}")
            if not entry.get("target_path") or not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")):
                raise ValueError(f"Missing official PDF path/hash for {entry['year']} {entry['subject']}")
        elif entry.get("status") == "not_available_in_selected_exam_class":
            if entry.get("official_url") is not None or entry.get("target_path") or entry.get("sha256"):
                raise ValueError(
                    f"Unavailable slot must not claim a PDF source: {entry['year']} {entry['subject']}"
                )
        else:
            raise ValueError(f"Unexpected source status: {entry.get('status')}")
    return entries


def verify_pdf_directory(entries: list[dict]) -> None:
    official = [entry for entry in entries if entry["status"] == "downloaded"]
    expected_names = {Path(entry["target_path"]).name for entry in official}
    if len(expected_names) != len(official):
        raise ValueError("MOEX manifest contains duplicate official PDF filenames")
    actual_names = {
        path.name
        for path in PDF_DIRECTORY.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    }
    if actual_names != expected_names:
        raise ValueError(
            "Official GK PDF directory mismatch: "
            f"missing={sorted(expected_names - actual_names)}, extra={sorted(actual_names - expected_names)}"
        )
    for entry in official:
        path = WORKSPACE / entry["target_path"]
        try:
            path.resolve().relative_to(WORKSPACE.resolve())
        except ValueError as error:
            raise ValueError(f"Official PDF path escapes the workspace: {entry['target_path']}") from error
        if not path.is_file():
            raise ValueError(f"Missing official PDF link/file: {entry['target_path']}")
        if sha256(path) != entry["sha256"]:
            raise ValueError(f"Official PDF SHA-256 mismatch: {entry['target_path']}")
        directory_copy = PDF_DIRECTORY / Path(entry["target_path"]).name
        if not directory_copy.is_file() or sha256(directory_copy) != entry["sha256"]:
            raise ValueError(
                f"Official PDF directory SHA-256 mismatch: {directory_copy.name}"
            )


def read_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    raw = text[4:].split("\n---\n", 1)[0]
    return {
        key: value.strip().strip("\"'")
        for key, value in re.findall(r"^([a-z0-9_]+):\s*(.*?)\s*$", raw, re.MULTILINE)
    }


def verified_annual_source_page(entry: dict) -> Path:
    source = (
        MASTER_DIRECTORY
        / SUBJECT_DIRS[entry["subject"]]
        / f"GK_{entry['year']}年_{entry['subject']}.md"
    )
    if not source.is_file():
        raise ValueError(f"Missing official annual source page: {source}")
    metadata = read_front_matter(source)
    expected_identity = {
        "source_kind": "moex_official_question_pdf",
        "year": str(entry["year"]),
        "subject": entry["subject"],
        "official_url": entry["official_url"],
    }
    mismatches = {
        key: (metadata.get(key), value)
        for key, value in expected_identity.items()
        if metadata.get(key) != value
    }
    if mismatches:
        raise ValueError(
            f"Annual source identity does not match MOEX manifest for "
            f"{entry['year']} {entry['subject']}: {mismatches}"
        )
    page_hash = metadata.get("source_pdf_sha256")
    if page_hash != entry["sha256"]:
        raise ValueError(
            f"Annual source PDF SHA-256 mismatch for {entry['year']} {entry['subject']}"
        )
    return source


def verify_annual_source_pages(entries: list[dict]) -> None:
    """Reject mismatched transcriptions; unbound legacy text remains unlinked."""
    for entry in entries:
        if entry["status"] != "downloaded":
            continue
        verified_annual_source_page(entry)


def solution_reference(entry: dict) -> tuple[str, str]:
    subject = entry["subject"]
    path = SOLUTION_DIRECTORY / SUBJECT_DIRS[subject] / (
        f"GK_{entry['year']}年_{subject}_全卷完整詳細題解.md"
    )
    if not path.is_file():
        return "尚無 repo 題解", ""
    metadata = read_front_matter(path)
    if metadata.get("source_pdf_sha256") != entry.get("sha256"):
        return "待核對（未綁定本年度官方 PDF）", ""
    expected_identity = {
        "solution_kind": "moex_question_solution",
        "year": str(entry["year"]),
        "subject": subject,
    }
    conflicts = [
        key for key, expected in expected_identity.items()
        if metadata.get(key) and metadata[key] != expected
    ]
    if conflicts:
        return "待核對（題解來源 metadata 與 manifest 不一致）", ""

    status_labels = {
        "validated": "repo 標記已驗證",
        "partial": "repo 標記部分驗證",
        "in_progress": "repo 標記處理中",
        "unverified": "repo 標記未驗證",
    }
    status = metadata.get("validation_status")
    label = status_labels.get(
        status,
        f"repo 驗證狀態未識別：{status}" if status else "repo 未標示驗證狀態",
    )
    if any(not metadata.get(key) for key in expected_identity):
        label += "（PDF 雜湊吻合；來源 metadata 待補）"
    return label, Path(os.path.relpath(path, MASTER_DIRECTORY)).as_posix()


def render_master(subject: str, entries: list[dict]) -> str:
    title = SUBJECT_TITLES.get(subject, subject)
    selected = sorted((item for item in entries if item["subject"] == subject), key=lambda item: item["year"], reverse=True)
    lines = [
        f"# 🏛️ 高等考試三級（電力工程類科）歷屆試題索引 — {title}（110–114 年）",
        "",
        "> 本頁只列可追溯來源與解答狀態，不複製未核實題幹、代號、題數或配分。",
        "> 官方來源狀態以 `data/moex-national-exams.json` 為準；解答狀態以 repo 題解的驗證標記及來源 PDF 雜湊為準。",
        "",
        "| 年度 | 官方來源狀態 | 官方年度原題頁／PDF | repo 題解狀態 |",
        "| :---: | :--- | :--- | :--- |",
    ]
    for entry in selected:
        year = entry["year"]
        if entry["status"] == "downloaded":
            source = verified_annual_source_page(entry)
            pdf_path = WORKSPACE / entry["target_path"]
            pdf_rel = Path(os.path.relpath(pdf_path, MASTER_DIRECTORY))
            transcript = f"[官方年度原題頁]({(Path(SUBJECT_DIRS[subject]) / source.name).as_posix()})"
            pdf_link = f"[MOEX PDF]({pdf_rel.as_posix()})"
            solution_status, solution_rel = solution_reference(entry)
            solution = f"[{solution_status}]({solution_rel})" if solution_rel else solution_status
            source_cell = f"{transcript} · {pdf_link} · [MOEX 查詢]({entry['source_page']})"
            state = "官方 PDF 已下載並以 manifest 雜湊驗證"
        else:
            source_cell = f"[考選部查詢]({entry.get('source_page') or MOEX_QUERY})；所選類科未提供官方來源，不列為官方試題"
            state = "所選類科官方原題不可用"
            solution = "無可對應官方原題之 repo 題解"
        lines.append(f"| {year} | {state} | {source_cell} | {solution} |")
    return "\n".join(lines) + "\n"


def expected_outputs(entries: list[dict]) -> dict[Path, str]:
    return {
        MASTER_DIRECTORY / f"{SUBJECT_DIRS[subject]}.md": render_master(subject, entries)
        for subject in SUBJECT_DIRS
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated indexes without writing")
    args = parser.parse_args(argv)
    try:
        entries = load_entries()
        verify_pdf_directory(entries)
        verify_annual_source_pages(entries)
        outputs = expected_outputs(entries)
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if args.check:
            if stale:
                print("Stale or missing GK master indexes:", *(str(path.relative_to(WORKSPACE)) for path in stale), sep="\n- ", file=sys.stderr)
                return 1
            print("GK source indexes valid: 25 slots, 23 official sources, 2 unavailable slots; PDF directory and hashes match.")
            return 0
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
            print(f"Updated {path.relative_to(WORKSPACE)}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"GK master index build failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
