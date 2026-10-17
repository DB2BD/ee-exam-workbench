#!/usr/bin/env python3
"""Check the hand-drawn SVG figures of canonical PE solution notes (v1.5.0).

Figures live in ``02_題解/技師題解/0X_科目/figures/<QID>-<簡名>.svg`` and are
referenced from the same subject's canonical notes as
``![圖 N：說明](../figures/<QID>-<簡名>.svg)``.

Per SVG file:
    parse         well-formed XML whose root element is <svg>
    viewbox       a viewBox whose width is 480-720
    background    a white <rect> (fill #fff / #ffffff / white) covering the viewBox
    size          smaller than 30 KB
    external      no external references (href / url() / @import), no raster
                  <image>, no <script>, <foreignObject>, <style> imports or data: URIs
    name          file name starts with a PE QID (EE-YYY-SS-N-)
Per reference / pairing:
    exists        every referenced figure exists in the same subject's figures/
    referenced    every figure is referenced by at least one canonical note
    form          .svg images in canonical notes use the ``../figures/`` form
    caption       alt text starts with 「圖 N：」

Usage::

    python3 scripts/check_solution_figures.py          # exit 1 on any problem
    python3 scripts/check_solution_figures.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "02_題解/技師題解"

MAX_BYTES = 30 * 1024
VIEWBOX_WIDTH = (480, 720)
WHITE = {"#fff", "#ffffff", "white", "#FFF", "#FFFFFF", "rgb(255,255,255)"}
NAME = re.compile(r"^EE-\d{3}-\d{2}-\d+-[^/]+\.svg$")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\n]+)\)")
FIGURE_REF = re.compile(r"^\.\./figures/([^/]+\.svg)$")
CAPTION = re.compile(r"^\s*圖\s*\d+\s*[:：]")
EXTERNAL_URL = re.compile(r"url\(\s*['\"]?\s*(?!#)", re.I)
FORBIDDEN_TAGS = {"image", "script", "foreignobject", "iframe", "object", "embed", "audio", "video"}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def number(value: str | None) -> float | None:
    match = re.match(r"\s*(-?\d+(?:\.\d+)?)\s*(?:px)?\s*$", value or "")
    return float(match.group(1)) if match else None


def covers_viewbox(rect: ET.Element, box: list[float]) -> bool:
    x, y = number(rect.get("x", "0")) or 0.0, number(rect.get("y", "0")) or 0.0
    width_attr, height_attr = rect.get("width", ""), rect.get("height", "")
    width = box[2] if width_attr.strip() == "100%" else number(width_attr)
    height = box[3] if height_attr.strip() == "100%" else number(height_attr)
    if width is None or height is None:
        return False
    return x <= box[0] and y <= box[1] and x + width >= box[0] + box[2] and y + height >= box[1] + box[3]


def fill_of(element: ET.Element) -> str:
    fill = element.get("fill", "")
    style = element.get("style", "")
    match = re.search(r"(?:^|;)\s*fill\s*:\s*([^;]+)", style)
    return (match.group(1) if match else fill).strip()


def check_svg(path: Path) -> list[str]:
    """Problems of one SVG file (empty list when it passes)."""

    problems: list[str] = []
    data = path.read_bytes()
    if len(data) >= MAX_BYTES:
        problems.append(f"size:{len(data)}B>={MAX_BYTES}B")
    if not NAME.match(path.name):
        problems.append("name:expected EE-YYY-SS-N-<簡名>.svg")
    text = data.decode("utf-8", errors="replace")
    if re.search(r"data:|@import|<!ENTITY", text, re.I):
        problems.append("external:data-uri-or-import-or-entity")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        return problems + [f"parse:{error}"]
    if local(root.tag) != "svg":
        return problems + ["parse:root-is-not-svg"]

    box: list[float] | None = None
    viewbox = re.split(r"[\s,]+", root.get("viewBox", "").strip())
    if len(viewbox) == 4:
        try:
            box = [float(part) for part in viewbox]
        except ValueError:
            box = None
    if box is None:
        problems.append("viewbox:missing-or-invalid")
    elif not VIEWBOX_WIDTH[0] <= box[2] <= VIEWBOX_WIDTH[1] or box[3] <= 0:
        problems.append(f"viewbox:width {box[2]:g} not in {VIEWBOX_WIDTH[0]}-{VIEWBOX_WIDTH[1]}")

    white = False
    for element in root.iter():
        tag = local(element.tag)
        if tag in FORBIDDEN_TAGS:
            problems.append(f"external:<{tag}>")
        for name, value in element.attrib.items():
            name = local(name)
            if name == "href" and not value.startswith("#"):
                problems.append(f"external:href={value[:40]}")
            if name.startswith("on"):
                problems.append(f"external:event-handler={name}")
            if EXTERNAL_URL.search(value):
                problems.append(f"external:url({value[:40]})")
        if tag == "style" and element.text and EXTERNAL_URL.search(element.text):
            problems.append("external:style-url")
        if box and tag == "rect" and not white and fill_of(element).replace(" ", "") in WHITE and covers_viewbox(element, box):
            white = True
    if not white:
        problems.append("background:no white <rect> covering the viewBox")
    return sorted(set(problems))


def collect(notes_root: Path = NOTES) -> dict:
    """Run every check under ``notes_root`` and return the findings."""

    problems: list[tuple[str, str]] = []     # (path relative to notes_root, problem)
    figures = {path: check_svg(path) for path in sorted(notes_root.glob("0*/figures/*.svg"))}
    for path, found in figures.items():
        problems.extend((str(path.relative_to(notes_root)), item) for item in found)

    referenced: set[Path] = set()
    refs = 0
    for note in sorted(notes_root.glob("0*/canonical/EE-*.md")):
        text = re.sub(r"```.*?```", "", note.read_text(encoding="utf-8"), flags=re.S)
        for alt, target in IMAGE.findall(text):
            target = unquote(target.strip())
            if not target.lower().split("?", 1)[0].split("#", 1)[0].endswith(".svg"):
                continue
            refs += 1
            label = str(note.relative_to(notes_root))
            match = FIGURE_REF.match(target)
            if not match:
                problems.append((label, f"form:{target} (use ../figures/<file>.svg)"))
                continue
            figure = note.parent.parent / "figures" / match.group(1)
            if not figure.is_file():
                problems.append((label, f"exists:{target}"))
            else:
                referenced.add(figure)
                if not match.group(1).startswith(note.stem + "-"):
                    problems.append((label, f"name:{match.group(1)} does not start with {note.stem}-"))
            if not CAPTION.match(alt):
                problems.append((label, f"caption:alt text must start with 「圖 N：」 ({alt[:20]})"))
    for path in figures:
        if path not in referenced:
            problems.append((str(path.relative_to(notes_root)), "referenced:no canonical note references this figure"))
    return {"figures": len(figures), "references": refs, "problems": sorted(set(problems))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=NOTES, help="notes root (default 02_題解/技師題解)")
    args = parser.parse_args(argv)
    result = collect(args.root)
    if args.json:
        print(json.dumps({**result, "problems": [list(item) for item in result["problems"]]}, ensure_ascii=False, indent=2))
    else:
        for path, problem in result["problems"]:
            print(f"{path}: {problem}")
        status = "OK" if not result["problems"] else f"{len(result['problems'])} problem(s)"
        print(f"solution figures: {result['figures']} svg, {result['references']} reference(s) -> {status}")
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
