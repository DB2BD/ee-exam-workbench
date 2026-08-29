# -*- coding: utf-8 -*-
"""Render official MOEX papers and create question/figure crop manifests.

Question boundaries are derived from the text coordinates in the official
PDF.  The crop is full-width so that a circuit diagram is never discarded
because it is positioned beside the prose.  Embedded PDF images are emitted
as separate figure crops and every output is linked back to the source PDF
and its SHA-256 digest in ``data/moex-question-crops.json``.
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
DEFAULT_INPUT = WORKSPACE / "data" / "moex-national-exams.json"
DEFAULT_OUTPUT = WORKSPACE / "data" / "moex-question-crops.json"
NUMERALS = "一二三四五六七八九十"
NUMERAL_VALUES = {char: index for index, char in enumerate(NUMERALS, 1)}
MAJOR_HEADING = re.compile(rf"(?<!圖)(?<!第)([{NUMERALS}]+)、")
FIGURE_QUESTION = re.compile(rf"如圖([{NUMERALS}]+)")
MC_HEADING = re.compile(r"^\s*([0-9]{1,2})(?=\s|$)")
MC_ENGINEERING_YEARS = {110, 111, 112}


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE))


def page_png(page: fitz.Page, clip: fitz.Rect | None, dpi: int = 220) -> bytes:
    scale = dpi / 72.0
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(scale, scale),
        clip=clip,
        alpha=False,
        annots=True,
    )
    return pixmap.tobytes("png")


def write_png(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def question_starts(doc: fitz.Document) -> list[dict]:
    """Find top-level Chinese-numbered questions, including unnumbered 113 electronics."""

    starts: list[dict] = []
    for page_index, page in enumerate(doc):
        for block in page.get_text("blocks"):
            x0, y0, x1, y1, text = block[:5]
            if x0 > 82:
                continue
            clean = " ".join(text.split())
            match = MAJOR_HEADING.search(clean)
            if match:
                starts.append(
                    {
                        "page": page_index,
                        "y": max(0.0, y0 - 12.0),
                        "heading": match.group(1),
                        "text": clean,
                    }
                )
                continue
            # The official 113 electronics PDF omits the Chinese numerals,
            # but each top-level question begins with 如圖一/二/三/四.
            figure_match = FIGURE_QUESTION.search(clean)
            if figure_match:
                starts.append(
                    {
                        "page": page_index,
                        "y": max(0.0, y0 - 12.0),
                        "heading": figure_match.group(1),
                        "text": clean,
                    }
                )

    # Keep only a strictly increasing top-level sequence.  PDF text extraction
    # can split a heading across blocks or misread a figure caption such as
    # 圖一、 as a new heading.  A real paper's major-question numbering is
    # monotonic, so a repeated or regressing numeral is not a boundary.
    starts.sort(key=lambda item: (item["page"], item["y"]))
    unique: list[dict] = []
    last_value = 0
    for item in starts:
        value = NUMERAL_VALUES.get(item["heading"], 0)
        if value <= last_value:
            continue
        item["number"] = len(unique) + 1
        unique.append(item)
        last_value = value
    return unique


def multiple_choice_starts(doc: fitz.Document) -> list[dict]:
    """Find MC question starts in the 110--112 engineering-math papers.

    The official PDFs place the Arabic question number at the left margin.
    Restricting detection to x < 50 and requiring the exact sequence 1..20
    avoids mistaking matrix entries, answer choices, or page headers for a
    question boundary.
    """

    marker: tuple[int, float] | None = None
    for page_index, page in enumerate(doc):
        for block in page.get_text("blocks"):
            x0, y0, _x1, _y1, text = block[:5]
            if x0 < 50 and "乙、測驗題部分" in text:
                marker = (page_index, y0)
                break
        if marker:
            break
    if marker is None:
        return []

    starts: list[dict] = []
    expected = 1
    for page_index in range(marker[0], doc.page_count):
        page = doc[page_index]
        blocks = sorted(page.get_text("blocks"), key=lambda item: (item[1], item[0]))
        words = page.get_text("words")
        candidates: list[tuple[float, int, str]] = []
        block_numbers: set[int] = set()
        for block in blocks:
            x0, y0, _x1, _y1, text = block[:5]
            if x0 >= 50 or (page_index == marker[0] and y0 <= marker[1]):
                continue
            clean = " ".join(text.split())
            match = MC_HEADING.match(clean)
            if not match:
                continue
            number = int(match.group(1))
            block_numbers.add(number)
            number_words = [
                word
                for word in words
                if word[0] < 50
                and y0 <= word[1] <= _y1
                and word[4].strip() == str(number)
            ]
            candidate_y = min((word[1] for word in number_words), default=y0)
            candidates.append((candidate_y, number, clean))

        # A few PDF text layers merge the next question number into the
        # previous question's answer-choice block.  Use the actual word box
        # at the left margin so that the crop starts at that number, not at
        # the beginning of the merged block.
        for word in words:
            x0, y0, _x1, _y1, text = word[:5]
            if x0 >= 50 or (page_index == marker[0] and y0 <= marker[1]):
                continue
            if text.strip().isdigit() and 1 <= int(text.strip()) <= 20:
                number = int(text.strip())
                if number not in block_numbers:
                    candidates.append((y0, number, text.strip()))

        for y0, number, clean in sorted(candidates, key=lambda item: item[0]):
            if number != expected:
                continue
            starts.append(
                {
                    "page": page_index,
                    "y": max(0.0, y0 - 1.0),
                    "number": expected,
                    "text": clean,
                }
            )
            expected += 1
            if expected == 21:
                return starts
    return starts


def segment_bounds(
    doc: fitz.Document,
    starts: list[dict],
    index: int,
    page_index: int,
    end_override: float | None = None,
) -> fitz.Rect:
    start = starts[index]
    top = start["y"] if page_index == start["page"] else 18.0
    if end_override is not None and page_index == starts[index]["page"]:
        bottom = end_override
    elif index + 1 < len(starts) and page_index == starts[index + 1]["page"]:
        bottom = starts[index + 1]["y"] - 8.0
    elif index + 1 < len(starts) and page_index == starts[index + 1]["page"] - 1:
        bottom = doc[page_index].rect.height - 18.0
    else:
        bottom = doc[page_index].rect.height - 18.0
    return fitz.Rect(0, max(0.0, top), doc[page_index].rect.width, max(top + 1.0, bottom))


def multiple_choice_bounds(
    doc: fitz.Document, starts: list[dict], index: int, page_index: int
) -> fitz.Rect:
    start = starts[index]
    top = start["y"] if page_index == start["page"] else 18.0
    if index + 1 < len(starts) and page_index == starts[index + 1]["page"]:
        bottom = starts[index + 1]["y"] - 8.0
    else:
        bottom = doc[page_index].rect.height - 18.0
    return fitz.Rect(0, max(0.0, top), doc[page_index].rect.width, max(top + 1.0, bottom))


def figure_rects(page: fitz.Page, segment: fitz.Rect) -> list[fitz.Rect]:
    rects: list[fitz.Rect] = []
    for image in page.get_images(full=True):
        for rect in page.get_image_rects(image):
            if rect.intersects(segment) and rect.width * rect.height > 500:
                rects.append(rect)
    if rects:
        return rects

    # Some older MOEX PDFs draw figures with many separate vector paths.  The
    # circuit is one visual object even though the PDF stores each wire,
    # symbol, and label separately, so group all meaningful paths into one
    # bounding box instead of emitting a misleading tiny fragment.
    vector_rects: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if not rect or (rect.width < 2 and rect.height < 2) or rect.x0 < 45 or rect.y0 < 120:
            continue
        if rect.intersects(segment):
            vector_rects.append(rect)
    if not vector_rects:
        return []
    union = vector_rects[0]
    for rect in vector_rects[1:]:
        union |= rect
    return [union]


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


def process_entry(entry: dict, dpi: int) -> dict:
    pdf_path = WORKSPACE / entry["target_path"]
    doc = fitz.open(pdf_path)
    paper_slug = f"GK_{entry['year']}年_{entry['subject']}"
    image_dir = pdf_path.parent / "images"
    page_dir = image_dir / "pages"
    question_dir = image_dir / "questions"
    figure_dir = image_dir / "figures"
    starts = question_starts(doc)
    mc_starts = (
        multiple_choice_starts(doc)
        if entry["subject"] == "工程數學" and entry["year"] in MC_ENGINEERING_YEARS
        else []
    )
    questions: list[dict] = []

    for page_index, page in enumerate(doc):
        rendered = page_png(page, None, dpi=dpi)
        write_png(page_dir / f"{paper_slug}_p{page_index + 1:02d}.png", rendered)
        if page_index == 0:
            write_png(image_dir / f"{paper_slug}_p1.png", rendered)

    for index, start in enumerate(starts):
        parts: list[bytes] = []
        page_ranges: list[dict] = []
        figure_paths: list[str] = []
        for page_index in range(start["page"], doc.page_count):
            if index + 1 < len(starts) and page_index > starts[index + 1]["page"]:
                break
            mc_end = mc_starts[0]["y"] - 8.0 if index == 3 and mc_starts else None
            if mc_end is not None and page_index > mc_starts[0]["page"]:
                break
            segment = segment_bounds(doc, starts, index, page_index, end_override=mc_end)
            parts.append(page_png(doc[page_index], segment, dpi=dpi))
            page_ranges.append(
                {
                    "page": page_index + 1,
                    "crop_rect": [round(value, 2) for value in segment],
                }
            )
            for figure_index, rect in enumerate(figure_rects(doc[page_index], segment), 1):
                expanded = fitz.Rect(
                    max(0, rect.x0 - 8),
                    max(segment.y0, rect.y0 - 8),
                    min(doc[page_index].rect.width, rect.x1 + 8),
                    min(segment.y1, rect.y1 + 8),
                )
                figure_name = f"{paper_slug}_Q{index + 1:02d}_figure-{len(figure_paths) + 1:02d}.png"
                figure_path = figure_dir / figure_name
                write_png(figure_path, page_png(doc[page_index], expanded, dpi=dpi))
                figure_paths.append(rel(figure_path))

        question_path = question_dir / f"{paper_slug}_Q{index + 1:02d}.png"
        write_png(question_path, stitch(parts))
        questions.append(
            {
                "question_id": f"GK-{entry['year']}-{entry['subject']}-Q{index + 1:02d}",
                "question_kind": "essay",
                "question_number": index + 1,
                "app_question_number": index + 1,
                "essay": True,
                "source_heading": start["heading"],
                "source_text_excerpt": start["text"][:500],
                "source_pages": page_ranges,
                "question_crop": rel(question_path),
                "figure_crops": figure_paths,
            }
        )

    for index, start in enumerate(mc_starts):
        parts: list[bytes] = []
        page_ranges: list[dict] = []
        for page_index in range(start["page"], doc.page_count):
            if index + 1 < len(mc_starts) and page_index > mc_starts[index + 1]["page"]:
                break
            segment = multiple_choice_bounds(doc, mc_starts, index, page_index)
            parts.append(page_png(doc[page_index], segment, dpi=dpi))
            page_ranges.append(
                {
                    "page": page_index + 1,
                    "crop_rect": [round(value, 2) for value in segment],
                }
            )
        question_path = question_dir / f"{paper_slug}_MC{index + 1:02d}.png"
        write_png(question_path, stitch(parts))
        questions.append(
            {
                "question_id": f"GK-{entry['year']}-{entry['subject']}-MC{index + 1:02d}",
                "question_kind": "multiple_choice",
                "question_number": index + 1,
                "app_question_number": index + 101,
                "essay": False,
                "source_heading": str(index + 1),
                "source_text_excerpt": start["text"][:500],
                "source_pages": page_ranges,
                "question_crop": rel(question_path),
                "figure_crops": [],
            }
        )
    doc.close()
    return {**entry, "question_count": len(questions), "questions": questions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=220)
    args = parser.parse_args()
    input_path = args.input if args.input.is_absolute() else WORKSPACE / args.input
    output_path = args.output if args.output.is_absolute() else WORKSPACE / args.output
    source = json.loads(input_path.read_text(encoding="utf-8"))
    processed = []
    for entry in source["entries"]:
        if entry["status"] != "downloaded":
            processed.append({**entry, "question_count": 0, "questions": []})
            continue
        print(f"Processing {entry['year']} {entry['subject']}")
        processed.append(process_entry(entry, dpi=args.dpi))
    result = {
        "schema_version": 1,
        "source_manifest": rel(input_path),
        "render_dpi": args.dpi,
        "question_boundary_policy": "top-level Chinese-numbered question; official 113 electronics 如圖一至四 fallback; 110-112 engineering-math MC 1..20 at left margin after 乙、測驗題部分",
        "entries": processed,
        "summary": {
            "papers": sum(e["status"] == "downloaded" for e in processed),
            "unavailable_papers": sum(e["status"] != "downloaded" for e in processed),
            "questions": sum(e["question_count"] for e in processed),
            "figure_crops": sum(len(q["figure_crops"]) for e in processed for q in e["questions"]),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
