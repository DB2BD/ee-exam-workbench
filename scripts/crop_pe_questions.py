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
from PIL import Image, ImageDraw


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = WORKSPACE / "data" / "pe-question-crops.json"
DEFAULT_DPI = 180
# A same-page question boundary this close is almost always a clipped heading
# (rather than a real question).  Short one-line questions are still retained,
# but their boundary must leave enough room for the PDF text line and its
# descenders.  This gate caught the original PE-109 circuit Q02 boundary.
MIN_BOUNDARY_GAP_POINTS = 24.0
# One text line (~16pt) plus a little lead; the start gap above already
# rejects clipped headings.
MIN_SEGMENT_POINTS = 18.0
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
    # On page 2, Q4 begins with the heading/table/diagram at y=41.5pt and
    # ends at y=286.8pt.  The former y=210pt start kept only the body, while
    # the old Q5/Q6 boundaries clipped the final lines by a few points.
    (109, "電力系統"): [(1, 240), (1, 360), (1, 496), (2, 32), (2, 296), (2, 397)],
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
    # Q5 begins at y=216pt on page 2; the former 390pt start produced a blank
    # Q5 crop and leaked all of Q5 into Q4.
    (114, "工業配電"): [(1, 240), (1, 350), (1, 635), (2, 60), (2, 204)],
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


# Running page furniture printed by the exam board.  Strong markers are masked
# wherever they appear; weak markers only inside the header/footer bands so a
# question that mentions e.g. 「科目」 is never blanked.
CHROME_STRONG = re.compile(r"代號：|頁次：|請接背面|請接第|請翻頁|全一張|專門職業及技術人員")
CHROME_WEAK = re.compile(
    r"等\s*別\s*：|類\s*科\s*：|科\s*目\s*：|考試時間|座\s*號|※注意|不必抄題|不予計分|電子計算器|"
    r"（正面）|（背面）|技師|考試試題"
)
# Lines that only occur in the exam header block.  Older papers set 等／類／科
# in a separate text line from 「別：」「科：」「目：」, so match either half.
HEADER_LINE = re.compile(
    r"專門職業|考試試題|考試時間|座\s*號|※注意|不必抄題|不予計分|本科目除專門名詞|應使用本國文字|"
    r"^(等\s*)?別\s*：|^(類\s*)?科\s*：|^(科\s*)?目\s*："
)
HEADER_BAND = 0.30
FOOTER_BAND = 0.12
MASK_PAD = 2.0


def page_lines(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                lines.append((fitz.Rect(line["bbox"]), text))
    return lines


def chrome_rects(page: fitz.Page) -> list[fitz.Rect]:
    """Return page rectangles holding exam-board headers, footers and page ids.

    When the full exam header (title + 等別／類科／科目) is repeated on a page,
    the whole band above its last line is chrome, including title lines that
    carry no keyword of their own.
    """

    height, width = page.rect.height, page.rect.width
    rects: list[fitz.Rect] = []
    header_bottom = 0.0
    for bbox, text in page_lines(page):
        in_header = bbox.y1 <= height * HEADER_BAND
        in_footer = bbox.y0 >= height * (1 - FOOTER_BAND)
        weak = CHROME_WEAK.search(text) or HEADER_LINE.search(text)
        if CHROME_STRONG.search(text) or ((in_header or in_footer) and weak):
            rects.append(fitz.Rect(bbox.x0 - MASK_PAD, bbox.y0 - MASK_PAD, bbox.x1 + MASK_PAD, bbox.y1 + MASK_PAD))
            if in_header and HEADER_LINE.search(text):
                header_bottom = max(header_bottom, bbox.y1)
    if header_bottom:
        rects.append(fitz.Rect(0, 0, width, header_bottom + MASK_PAD))
    # Rules and boxes drawn around the 代號／頁次 label belong to the chrome.
    strong = list(rects)
    for drawing in page.get_drawings():
        rect = fitz.Rect(drawing["rect"])
        if rect.width > 200 or rect.height > 40:
            continue
        if any((mask + (-4, -4, 4, 4)).intersects(rect) for mask in strong):
            rects.append(rect + (-MASK_PAD, -MASK_PAD, MASK_PAD, MASK_PAD))
    return rects


def has_question_content(bands: list[tuple[float, float]], clip: fitz.Rect) -> bool:
    """True when ``clip`` holds any non-chrome ink (text, figure or rule)."""

    return any(y1 > clip.y0 + 0.5 and y0 < clip.y1 - 0.5 for y0, y1 in bands)


HEADING_PAD = 3.0
LINE_HEADING = re.compile(r"^\s*[一二三四五六七八九十]+\s*[、．.]")


def heading_top(page: fitz.Page, block: fitz.Rect, numeral: str) -> float:
    """Crop top for a heading block: the visual row of its numbered line.

    Blocks can merge the running 代號／頁次 header with the first question
    line, and a fixed lead above the block clipped captions that end just
    above the next heading; the numbered line's row top is exact.
    """

    for bbox, text in page_lines(page):
        if block.contains(bbox) and LINE_HEADING.match(text) and text.lstrip().startswith(numeral[0]):
            return max(0.0, row_top(page, bbox) - HEADING_PAD)
    return max(0.0, block.y0 - 12.0)


INK_SCALE = 2.0
INK_LEVEL = 200
MAX_SNAP_UP = 40.0


def ink_bands(page: fitz.Page) -> list[tuple[float, float]]:
    """Vertical runs (in PDF points) of rows holding non-chrome ink.

    Figure captions, display-math brackets and diagrams are often vector
    graphics absent from the text layer, so boundaries are placed using the
    rendered page rather than text lines.
    """

    pixmap = page.get_pixmap(matrix=fitz.Matrix(INK_SCALE, INK_SCALE), alpha=False)
    image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("L")
    draw = ImageDraw.Draw(image)
    for mask in chrome_rects(page):
        draw.rectangle([mask.x0 * INK_SCALE, mask.y0 * INK_SCALE, mask.x1 * INK_SCALE, mask.y1 * INK_SCALE], fill=255)
    # Column-wise minimum per row: a row has ink if any pixel is dark.
    width, height = image.size
    data = image.tobytes()
    bands: list[tuple[float, float]] = []
    start = None
    for row in range(height):
        dark = min(data[row * width:(row + 1) * width]) < INK_LEVEL
        if dark and start is None:
            start = row
        elif not dark and start is not None:
            bands.append((start / INK_SCALE, row / INK_SCALE))
            start = None
    if start is not None:
        bands.append((start / INK_SCALE, height / INK_SCALE))
    return bands


def snap_to_gap(bands: list[tuple[float, float]], y: float) -> float:
    """Move a question boundary into the blank gap just above the ink at ``y``.

    ``y`` points at (or just above) the next question's first row.  The band
    holding it may begin higher when display math or a bracket rises above
    the numbered line; the cut goes midway into the gap above that band, so
    the previous question keeps its trailing caption or formula.
    """

    holder = next((band for band in bands if band[1] > y), None)
    if holder is None:
        return y
    top = holder[0]
    if y - top > MAX_SNAP_UP:
        return y
    above = [band[1] for band in bands if band[1] <= top]
    gap = top - max(above) if above else top
    return max(0.0, top - min(HEADING_PAD, gap / 2.0))


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
                "y": heading_top(page, fitz.Rect(block[:4]), match.group(0)),
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


def row_top(page: fitz.Page, bbox: fitz.Rect) -> float:
    """Top of the visual row whose first text line is ``bbox``.

    Display math (a matrix typed as separate glyph lines) can start above the
    text line it sits on.  Grow upward through small elements lying within the
    row's horizontal extent and touching it (3pt), at most 40pt.
    """

    lines = page_lines(page)
    row = [rect for rect, _text in lines if abs(rect.y0 - bbox.y0) < 2.0]
    x0, x1 = min(rect.x0 for rect in row), max(rect.x1 for rect in row)
    elements = [rect for rect, _text in lines]
    elements += [fitz.Rect(drawing["rect"]) for drawing in page.get_drawings()]
    elements = [
        rect for rect in elements
        if rect.height < 30 and rect.x0 >= x0 - 1 and rect.x1 <= x1 + 1 and rect.y0 < bbox.y0
    ]
    top = bbox.y0
    changed = True
    while changed:
        changed = False
        for rect in elements:
            if rect.y0 < top and rect.y1 >= top - 3.0 and bbox.y0 - rect.y0 <= 40.0:
                top, changed = rect.y0, True
    return top


SUBITEM_GLYPHS = "\ue129\ue12a\ue12b\ue12c\ue12d\ue12e"


def ink_heading_starts(doc: fitz.Document) -> list[dict]:
    """Detect question starts when the 「一、」 numerals are missing from the text layer.

    In these papers the numeral is rendered but not extractable, so the first
    body line of each question sits at the hanging indent with ink in the
    left gutter.  Continuation and sub-item lines have an empty gutter.
    """

    scale = 4.0
    starts: list[dict] = []
    for page_index, page in enumerate(doc):
        top = content_top(page) if page_index == 0 else 0.0
        gutter = fitz.Rect(28, 0, 62, page.rect.height)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=gutter, alpha=False)
        image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("L")
        pixels = image.load()
        masks = chrome_rects(page)
        for bbox, text in page_lines(page):
            if bbox.y0 < top or not 60 <= bbox.x0 <= 70 or bbox.width < 60:
                continue
            if text[0] in SUBITEM_GLYPHS or any(mask.contains(bbox) for mask in masks):
                continue
            rows = range(int(bbox.y0 * scale), min(int(bbox.y1 * scale), image.height))
            ink = sum(1 for y in rows for x in range(image.width) if pixels[x, y] < 128)
            if ink > 40:
                starts.append({
                    "page": page_index + 1,
                    # The numeral shares this line, so a small lead suffices
                    # and keeps one-line questions (109 電路學 Q02) intact.
                    "y": max(0.0, row_top(page, bbox) - HEADING_PAD),
                    "number": len(starts) + 1,
                    "text": text[:500],
                })
    return starts


def starts_for(doc: fitz.Document, year: int, subject: str, count: int) -> tuple[list[dict], str]:
    manual = MANUAL_STARTS.get((year, subject))
    if manual:
        detected = ink_heading_starts(doc)
        if len(detected) == count:
            return detected, "pdf_ink_heading"
        if len(manual) != count:
            raise ValueError(f"Manual crop table/count mismatch for {year} {subject}")
        return [
            {"page": page, "y": y, "number": index + 1, "text": "manual audited boundary", "gap": 8.0}
            for index, (page, y) in enumerate(manual)
        ], "manual_audit"

    candidates = heading_candidates(doc)
    sequence = complete_numbered_sequence(candidates, count)
    if sequence is None:
        raise ValueError(
            f"No complete numbered sequence for {year} {subject}; add an audited MANUAL_STARTS entry"
        )
    return sequence, "pdf_text_sequence"


def page_png(page: fitz.Page, clip: fitz.Rect, dpi: int, masks: list[fitz.Rect] = ()) -> bytes:
    """Render ``clip`` and paint page chrome white, then trim blank margins."""

    scale = dpi / 72.0
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False, annots=True)
    image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGB")
    draw = ImageDraw.Draw(image)
    for mask in masks:
        visible = mask & clip
        if visible.is_empty:
            continue
        draw.rectangle(
            [
                (visible.x0 - clip.x0) * scale,
                (visible.y0 - clip.y0) * scale,
                (visible.x1 - clip.x0) * scale,
                (visible.y1 - clip.y0) * scale,
            ],
            fill="white",
        )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return trim_whitespace(buffer.getvalue(), padding=0)


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
        # Detected starts are exact row tops, so questions abut; manual
        # coordinates keep the historical 8pt safety gap.
        bottom = starts[index + 1]["y"] - starts[index + 1].get("gap", 0.0)
    elif index + 1 < len(starts) and page_number == starts[index + 1]["page"] - 1:
        bottom = doc[page_index].rect.height - 18.0
    else:
        bottom = doc[page_index].rect.height - 18.0
    if page_number == start["page"] and bottom < top + MIN_SEGMENT_POINTS:
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
    bands_by_page: dict[int, list[tuple[float, float]]] = {}
    for start in starts:
        bands = bands_by_page.setdefault(start["page"], ink_bands(doc[start["page"] - 1]))
        anchor = start["y"] + (start.get("gap", 0.0) if "gap" in start else HEADING_PAD)
        start["y"] = snap_to_gap(bands, anchor)
        start["gap"] = 0.0
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
            page = doc[page_number - 1]
            segment = segment_bounds(doc, starts, index, page_number)
            masks = [mask for mask in chrome_rects(page) if mask.intersects(segment)]
            bands = bands_by_page.setdefault(page_number, ink_bands(page))
            # A continuation page that only adds the running header/footer is
            # not part of the question.
            if not has_question_content(bands, segment):
                if page_number == start["page"]:
                    raise ValueError(
                        f"Empty crop for {year} {subject} Q{index + 1:02d} on page {page_number}; "
                        "fix the audited boundary"
                    )
                continue
            parts.append(page_png(page, segment, dpi, masks))
            source_pages.append({
                "page": page_number,
                "crop_rect": [round(value, 2) for value in segment],
                "masked_rects": [[round(value, 2) for value in mask] for mask in masks],
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
            "boundary_confidence": {
                "manual_audit": "audited",
                "pdf_ink_heading": "ink_heading",
            }.get(boundary_method, "text_sequence"),
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
        "boundary_policy": "audited PDF text sequence; gutter-ink heading detection for damaged text layers, falling back to explicit manual coordinates; page chrome masked; no equal-page fallback",
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
