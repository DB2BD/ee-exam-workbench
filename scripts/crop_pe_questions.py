# -*- coding: utf-8 -*-
"""Create question-level crops for the 66 electrician-engineer PE papers.

The PE PDFs are not uniform: several years have a damaged or missing text
layer, while other papers put diagrams between the question text and the next
heading.  This script therefore uses PDF text coordinates only when the
numbered sequence is complete and uses a small, audited coordinate table for
the known text-layer exceptions.  It never silently falls back to an evenly
spaced crop (which can cut a question in half).

Outputs:

* ``data/pe-question-crops.json`` - qid -> source page rectangles and image
  paths, including the boundary method and confidence.
* ``依考科分類/*/images/questions/PE_*.png`` - one stitched image per
  question, preserving all pages occupied by that question.

Run from the repository root::

    python3 scripts/crop_pe_questions.py

The source PDFs remain untouched.  Crop coordinates are PDF points; generated
PNGs are rendered at a fixed DPI so the output is reproducible.
"""

from __future__ import annotations

import argparse
import io
import json
import re
from pathlib import Path

import fitz
from PIL import Image


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = WORKSPACE / "data" / "pe-question-crops.json"
DEFAULT_DPI = 180
# A same-page question boundary this close is almost always a clipped heading
# (rather than a real question).  Short one-line questions are still retained,
# but their boundary must leave enough room for the PDF text line and its
# descenders.  This gate caught the original PE-109 circuit Q02 boundary.
MIN_BOUNDARY_GAP_POINTS = 24.0
CN_NUMERALS = "一二三四五六七八九十"
CN_VALUES = {char: index for index, char in enumerate(CN_NUMERALS, 1)}

# The text layer in these PDFs does not expose a complete numbered sequence.
# Coordinates are the top of the first text/figure region for each real PE
# question.  They are deliberately explicit rather than guessed from equal
# page partitions; the crop audit stores ``manual_audit`` for these entries.
# Values are PDF points and use 1-based page numbers.
MANUAL_STARTS: dict[tuple[int, str], list[tuple[int, float]]] = {
    (109, "工業配電"): [(1, 240), (1, 335), (1, 468), (2, 32), (2, 155)],
    (109, "工程數學"): [(1, 240), (1, 292), (1, 354), (1, 430), (1, 482)],
    (109, "電力系統"): [(1, 240), (1, 360), (1, 496), (2, 210), (2, 290), (2, 390)],
    (109, "電子學（包括電力電子學）"): [(1, 240), (1, 530), (2, 75), (2, 445)],
    (109, "電機機械"): [(1, 240), (2, 65), (2, 240), (2, 375), (3, 60)],
    # Q02 is genuinely a one-line question, but the next heading begins at
    # 475.9pt.  460pt clipped the bottom of the line (y1=462.2pt), so keep a
    # 468pt effective boundary (the renderer subtracts 8pt before Q03) and
    # leave the next heading in Q03.
    (109, "電路學"): [(1, 245), (1, 430), (1, 476), (2, 60)],
    (112, "工業配電"): [(1, 245), (1, 305), (1, 580), (2, 60), (2, 450)],
    (112, "工程數學"): [(1, 245), (1, 325), (1, 400), (1, 540), (1, 600), (2, 60)],
    (112, "電機機械"): [(1, 245), (1, 545), (2, 200), (2, 410), (3, 60)],
    (112, "電路學"): [(1, 245), (1, 455), (2, 60), (2, 340)],
    (113, "工業配電"): [(1, 245), (1, 575), (2, 60), (2, 390), (3, 60)],
    (113, "電力系統"): [(1, 245), (1, 570), (2, 60), (2, 200)],
    (113, "電機機械"): [(1, 245), (1, 565), (1, 665), (2, 60), (2, 400)],
    (114, "工業配電"): [(1, 240), (1, 350), (1, 635), (2, 60), (2, 390)],
}

# A few source Markdown files predate the official paper transcription and
# omit a real top-level question.  Keep the crop manifest faithful to the PDF
# itself; the application id is still deterministic for a future data sync.
COUNT_OVERRIDES = {
    (109, "電子學（包括電力電子學）"): 4,
    (112, "工程數學"): 6,
}


def subject_from_filename(path: Path) -> str:
    name = path.stem
    prefix = re.match(r"\d{3}年_電機工程技師_(.*)$", name)
    if not prefix:
        raise ValueError(f"Unexpected PE PDF filename: {path.name}")
    return prefix.group(1)


def pdf_paths() -> list[Path]:
    return sorted((WORKSPACE / "依年度分類").glob("*/*.pdf"))


def markdown_question_count(year: int, subject: str) -> int:
    """Read the existing PE source note to determine the app question count."""

    subject_file = {
        "電路學": "01_電路學.md",
        "電子學（包括電力電子學）": "02_電子學_含電力電子.md",
        "工程數學": "03_工程數學.md",
        "電機機械": "04_電機機械.md",
        "電力系統": "05_電力系統.md",
        "工業配電": "06_工業配電.md",
    }[subject]
    text = (WORKSPACE / "依考科分類" / subject_file).read_text(encoding="utf-8")
    sections = list(re.finditer(r"^##\s+(\d{3})\s*年", text, re.MULTILINE))
    for index, match in enumerate(sections):
        if int(match.group(1)) != year:
            continue
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        section = text[match.start():end]
        return len(re.findall(r"^####\s+[一二三四五六七八九十]+\s*[、.]", section, re.MULTILINE))
    raise ValueError(f"No PE source note section for {year} {subject}")


def question_count(year: int, subject: str) -> int:
    return COUNT_OVERRIDES.get((year, subject), markdown_question_count(year, subject))


def clean_block(text: str) -> str:
    return " ".join(text.split())


def content_top(page: fitz.Page) -> float:
    """Return a conservative top margin below the paper instructions."""

    blocks = page.get_text("blocks")
    instruction_bottom = 0.0
    for block in blocks:
        y0, y1, text = block[1], block[3], clean_block(block[4])
        if "※注意" in text or "不必抄題" in text or "不必抄題" in text:
            instruction_bottom = max(instruction_bottom, y1)
    return instruction_bottom + 5 if instruction_bottom else 18.0


def heading_candidates(doc: fitz.Document) -> list[dict]:
    """Find top-level Chinese-numbered headings in PDF text blocks."""

    pattern = re.compile(r"(?<!圖)(?<!第)([一二三四五六七八九十]+)\s*[、．.]")
    candidates: list[dict] = []
    for page_index, page in enumerate(doc):
        top = content_top(page)
        for block in page.get_text("blocks"):
            x0, y0, _x1, _y1, raw = block[:5]
            text = clean_block(raw)
            if not text or y0 < top:
                continue
            match = pattern.search(text)
            if not match:
                continue
            value = CN_VALUES.get(match.group(1))
            if value is None:
                continue
            candidates.append({
                "page": page_index + 1,
                "y": max(0.0, y0 - 12.0),
                "number": value,
                "text": text[:500],
            })
    return sorted(candidates, key=lambda item: (item["page"], item["y"]))


def complete_numbered_sequence(candidates: list[dict], count: int) -> list[dict] | None:
    """Use candidates only when 1..count appears in order with no ambiguity."""

    chosen: list[dict] = []
    expected = 1
    for candidate in candidates:
        if candidate["number"] != expected:
            continue
        chosen.append(candidate)
        expected += 1
        if expected > count:
            return chosen
    return None


def starts_for(doc: fitz.Document, year: int, subject: str, count: int) -> tuple[list[dict], str]:
    manual = MANUAL_STARTS.get((year, subject))
    if manual:
        if len(manual) != count:
            raise ValueError(f"Manual crop table/count mismatch for {year} {subject}")
        return [
            {"page": page, "y": y, "number": index + 1, "text": "manual audited boundary"}
            for index, (page, y) in enumerate(manual)
        ], "manual_audit"

    candidates = heading_candidates(doc)
    sequence = complete_numbered_sequence(candidates, count)
    if sequence is None:
        raise ValueError(
            f"No complete numbered sequence for {year} {subject}; add an audited MANUAL_STARTS entry"
        )
    return sequence, "pdf_text_sequence"


def page_png(page: fitz.Page, clip: fitz.Rect, dpi: int) -> bytes:
    scale = dpi / 72.0
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False, annots=True)
    return pixmap.tobytes("png")


def stitch(parts: list[bytes], gap: int = 18) -> bytes:
    images = [Image.open(io.BytesIO(part)).convert("RGB") for part in parts]
    width = max(image.width for image in images)
    height = sum(image.height for image in images) + gap * (len(images) - 1)
    output = Image.new("RGB", (width, height), "white")
    y = 0
    for image in images:
        output.paste(image, (0, y))
        y += image.height + gap
    buffer = io.BytesIO()
    output.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def trim_whitespace(data: bytes, padding: int = 16) -> bytes:
    """Remove blank render margin while preserving a small visual border.

    The source rectangles in the manifest remain the authoritative audited
    boundaries.  Trimming only prevents the final question in a PDF from
    becoming a mostly-empty full-page PNG in the UI.
    """

    image = Image.open(io.BytesIO(data)).convert("RGB")
    # Pure white page backgrounds are common, while anti-aliased text and
    # diagrams remain below this threshold.
    mask = image.convert("L").point(lambda pixel: 255 if pixel < 245 else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return data
    left, top, right, bottom = bbox
    bbox = (
        max(0, left - padding),
        max(0, top - padding),
        min(image.width, right + padding),
        min(image.height, bottom + padding),
    )
    output = image.crop(bbox)
    buffer = io.BytesIO()
    output.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def validate_starts(starts: list[dict], year: int, subject: str) -> None:
    """Reject manual/automatic boundaries that can only produce tiny crops."""

    for previous, current in zip(starts, starts[1:]):
        if previous["page"] != current["page"]:
            continue
        gap = float(current["y"]) - float(previous["y"])
        if gap < MIN_BOUNDARY_GAP_POINTS:
            raise ValueError(
                f"Question boundary gap is too small for {year} {subject}: "
                f"p{current['page']} y={previous['y']} -> y={current['y']} "
                f"({gap:.1f}pt); add an audited boundary"
            )


def segment_bounds(doc: fitz.Document, starts: list[dict], index: int, page_number: int) -> fitz.Rect:
    start = starts[index]
    page_index = page_number - 1
    top = start["y"] if page_number == start["page"] else 18.0
    if index + 1 < len(starts) and page_number == starts[index + 1]["page"]:
        bottom = starts[index + 1]["y"] - 8.0
    elif index + 1 < len(starts) and page_number == starts[index + 1]["page"] - 1:
        bottom = doc[page_index].rect.height - 18.0
    else:
        bottom = doc[page_index].rect.height - 18.0
    if page_number == start["page"] and bottom < top + MIN_BOUNDARY_GAP_POINTS:
        raise ValueError(
            f"Question segment is too small on page {page_number}: "
            f"y={top:.1f}..{bottom:.1f}"
        )
    return fitz.Rect(0, max(0.0, top), doc[page_index].rect.width, max(top + 1.0, bottom))


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE)).replace("\\", "/")


def process_pdf(pdf_path: Path, dpi: int) -> dict:
    year = int(pdf_path.parent.name[:3])
    subject = subject_from_filename(pdf_path)
    count = question_count(year, subject)
    doc = fitz.open(pdf_path)
    page_count = doc.page_count
    starts, boundary_method = starts_for(doc, year, subject, count)
    validate_starts(starts, year, subject)
    question_dir = (WORKSPACE / "依考科分類" / {
        "電路學": "01_電路學",
        "電子學（包括電力電子學）": "02_電子學_含電力電子",
        "工程數學": "03_工程數學",
        "電機機械": "04_電機機械",
        "電力系統": "05_電力系統",
        "工業配電": "06_工業配電",
    }[subject] / "images" / "questions")

    questions: list[dict] = []
    for index, start in enumerate(starts):
        parts: list[bytes] = []
        source_pages: list[dict] = []
        for page_number in range(start["page"], doc.page_count + 1):
            if index + 1 < len(starts) and page_number > starts[index + 1]["page"]:
                break
            # If the next question begins near the top of a later page, the
            # apparent continuation is only the running page header.  Do not
            # attach that header as a six-point "question" fragment.
            if (
                index + 1 < len(starts)
                and page_number == starts[index + 1]["page"]
                and page_number > start["page"]
                and starts[index + 1]["y"] <= 70
            ):
                break
            segment = segment_bounds(doc, starts, index, page_number)
            parts.append(page_png(doc[page_number - 1], segment, dpi))
            source_pages.append({
                "page": page_number,
                "crop_rect": [round(value, 2) for value in segment],
            })
        path = question_dir / f"PE_{year}年_{subject}_Q{index + 1:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(trim_whitespace(stitch(parts)))
        questions.append({
            "question_id": f"PE-{year}-{subject}-Q{index + 1:02d}",
            "app_question_id": f"EE-{year}-{subject_id(subject)}-{index + 1}",
            "question_number": index + 1,
            "question_crop": rel(path),
            "source_pages": source_pages,
            "boundary_method": boundary_method,
            "boundary_confidence": "audited" if boundary_method == "manual_audit" else "text_sequence",
        })
    doc.close()
    return {
        "year": year,
        "subject": subject,
        "pdf_path": rel(pdf_path),
        "pdf_sha256": __import__("hashlib").sha256(pdf_path.read_bytes()).hexdigest(),
        "page_count": page_count,
        "question_count": len(questions),
        "questions": questions,
    }


def subject_id(subject: str) -> str:
    return {
        "電路學": "01",
        "電子學（包括電力電子學）": "02",
        "工程數學": "03",
        "電機機械": "04",
        "電力系統": "05",
        "工業配電": "06",
    }[subject]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    parser.add_argument("--dry-run", action="store_true", help="audit boundaries without writing PNGs")
    args = parser.parse_args()
    output_path = args.output if args.output.is_absolute() else WORKSPACE / args.output

    entries = []
    for pdf_path in pdf_paths():
        if args.dry_run:
            year = int(pdf_path.parent.name[:3])
            subject = subject_from_filename(pdf_path)
            doc = fitz.open(pdf_path)
            count = question_count(year, subject)
            starts, method = starts_for(doc, year, subject, count)
            entries.append({"year": year, "subject": subject, "pdf_path": rel(pdf_path), "question_count": len(starts), "boundary_method": method})
            doc.close()
            print(f"AUDIT {year} {subject}: {len(starts)} questions ({method})")
            continue
        print(f"Processing {pdf_path.parent.name} {subject_from_filename(pdf_path)}")
        entries.append(process_pdf(pdf_path, args.dpi))

    result = {
        "schema_version": 1,
        "source_type": "official_pe_question_pdf",
        "render_dpi": args.dpi,
        "boundary_policy": "audited PDF text sequence; explicit manual coordinates for damaged text layers; no equal-page fallback",
        "entries": entries,
        "summary": {
            "papers": len(entries),
            "questions": sum(entry["question_count"] for entry in entries),
        },
    }
    if not args.dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
