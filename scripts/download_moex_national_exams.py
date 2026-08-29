# -*- coding: utf-8 -*-
"""Download and attest official MOEX Senior Examination Level 3 papers.

The existing repository contains generated PDF substitutes.  This script
resolves the question links from the official MOEX result page, downloads
only PDF responses from the official host, and writes a machine-readable
manifest containing the source URL, source page, SHA-256 digest, and status.

The selected scope is the Electrical Engineering senior-exam subject set:
engineering mathematics (when it was actually offered), circuit theory,
electronics, electrical machinery, and power systems.  Subject availability
is recorded rather than guessed; in particular, engineering mathematics is
not listed for the 113 and 114 Electrical Engineering papers.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
BASE_DIR = WORKSPACE / "依考科分類" / "🏛️_國考同級參考題庫"
MANIFEST_PATH = WORKSPACE / "data" / "moex-national-exams.json"
OFFICIAL_HOST = "wwwq.moex.gov.tw"
SEARCH_PATH = "/exam/wFrmExamQandASearch.aspx"
FILE_PATH = "/exam/wHandExamQandA_File.ashx"

YEARS = {
    110: {"exam_code": "110090", "calendar_year": 2021, "class_code": "376"},
    111: {"exam_code": "111090", "calendar_year": 2022, "class_code": "370"},
    112: {"exam_code": "112090", "calendar_year": 2023, "class_code": "373"},
    113: {"exam_code": "113080", "calendar_year": 2024, "class_code": "371"},
    114: {"exam_code": "114080", "calendar_year": 2025, "class_code": "274"},
}

SUBJECTS = {
    "電路學": {"directory": "01_電路學", "filename": "電路學"},
    "電子學": {"directory": "02_電子學_含電力電子", "filename": "電子學"},
    "工程數學": {"directory": "03_工程數學", "filename": "工程數學"},
    "電機機械": {"directory": "04_電機機械", "filename": "電機機械"},
    "電力系統": {"directory": "05_電力系統", "filename": "電力系統"},
}

HEADERS = {
    "User-Agent": "ee-exam-workbench/official-source-audit",
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


def fetch(url: str) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname != OFFICIAL_HOST:
        raise ValueError(f"Refusing non-official host: {parsed.hostname}")
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def official_search_url(year: int) -> str:
    config = YEARS[year]
    query = urllib.parse.urlencode(
        {"e": config["exam_code"], "y": config["calendar_year"]}
    )
    return f"https://{OFFICIAL_HOST}{SEARCH_PATH}?{query}"


def parse_subject_links(page: bytes, year: int) -> dict[str, str]:
    """Return subject -> official question URL for the Electrical Engineering class."""

    text = page.decode("utf-8", errors="replace")
    config = YEARS[year]
    row_pattern = re.compile(
        rf"<input[^>]+id=\"[^\"]*_{re.escape(config['exam_code'])}_"
        rf"{re.escape(config['class_code'])}_[^\"]+\"[^>]*>.*?"
        rf"<label[^>]*class=\"exam-title\"[^>]*>(.*?)</label>(.*?)</tr>",
        re.IGNORECASE | re.DOTALL,
    )
    result: dict[str, str] = {}
    for match in row_pattern.finditer(text):
        subject = " ".join(re.sub(r"<[^>]+>", " ", match.group(1)).split())
        subject = html.unescape(subject)
        if subject not in SUBJECTS:
            continue
        hrefs = re.findall(
            r'href=["\']([^"\']*wHandExamQandA_File[^"\']*)["\']',
            match.group(2),
            re.IGNORECASE,
        )
        for href in hrefs:
            href = html.unescape(href)
            params = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            if params.get("t") == ["Q"]:
                result[subject] = urllib.parse.urljoin(
                    f"https://{OFFICIAL_HOST}{SEARCH_PATH}", href
                )
                break
    return result


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pdf_page_count(data: bytes) -> int | None:
    try:
        from pypdf import PdfReader

        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            handle.write(data)
            handle.flush()
            return len(PdfReader(handle.name).pages)
    except Exception:
        return None


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def build_manifest(download: bool) -> dict:
    entries: list[dict] = []
    for year, config in YEARS.items():
        source_page = official_search_url(year)
        page = fetch(source_page)
        links = parse_subject_links(page, year)
        for subject, metadata in SUBJECTS.items():
            base = {
                "year": year,
                "calendar_year": config["calendar_year"],
                "exam_code": config["exam_code"],
                "class_code": config["class_code"],
                "subject": subject,
                "source_page": source_page,
                "official_host": OFFICIAL_HOST,
                "source_type": "moex-official-question-pdf",
            }
            url = links.get(subject)
            if not url:
                entries.append(
                    {
                        **base,
                        "status": "not_available_in_selected_exam_class",
                        "official_url": None,
                        "reason": "The official result page has no question link for this subject in this year/class.",
                    }
                )
                continue

            target = (
                BASE_DIR
                / metadata["directory"]
                / f"GK_{year}年_高考三級_{metadata['filename']}.pdf"
            )
            entry = {**base, "official_url": url, "target_path": str(target.relative_to(WORKSPACE))}
            if download:
                data = fetch(url)
                if not data.startswith(b"%PDF-"):
                    raise RuntimeError(f"Official endpoint did not return PDF: {url}")
                write_atomic(target, data)
                entry.update(
                    {
                        "status": "downloaded",
                        "bytes": len(data),
                        "sha256": sha256(data),
                        "page_count": pdf_page_count(data),
                        "downloaded_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
            else:
                entry["status"] = "link_resolved"
            entries.append(entry)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_policy": {
            "official_host_allowlist": [OFFICIAL_HOST],
            "question_endpoint": f"https://{OFFICIAL_HOST}{FILE_PATH}",
            "generated_substitute_pdfs_are_not_accepted": True,
        },
        "scope": {
            "exam": "高等考試三級",
            "class": "電力工程",
            "years": sorted(YEARS),
            "subjects": list(SUBJECTS),
        },
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resolve-only",
        action="store_true",
        help="Resolve and record official links without replacing local PDFs.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Manifest output path relative to the workspace or absolute.",
    )
    args = parser.parse_args()
    manifest = build_manifest(download=not args.resolve_only)
    output = args.manifest if args.manifest.is_absolute() else WORKSPACE / args.manifest
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    available = sum(e["status"] in {"downloaded", "link_resolved"} for e in manifest["entries"])
    unavailable = len(manifest["entries"]) - available
    print(f"Wrote {output.relative_to(WORKSPACE) if output.is_relative_to(WORKSPACE) else output}")
    print(f"Entries: {len(manifest['entries'])}; available: {available}; unavailable: {unavailable}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
