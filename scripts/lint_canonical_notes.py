#!/usr/bin/env python3
"""Lint PE canonical solution notes for precision and redundancy defects.

Every note is checked for markup that cannot render and for answer coverage.
Notes migrated to the lean template (frontmatter ``template: lean-v1``) are
additionally held to the section, metadata and redundancy rules of
the lean-v1 題解版型 (internal work record, unpublished).

Usage::

    python3 scripts/lint_canonical_notes.py              # summary of all notes
    python3 scripts/lint_canonical_notes.py --strict     # fail on any lean-v1 violation
    python3 scripts/lint_canonical_notes.py EE-114-05-3 --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "📝 個人題解與錯題本"
DASHBOARD = ROOT / "dashboard-data.js"

LEAN = "lean-v1"
REQUIRED_SECTIONS = ("已知與所求", "考場標準作答", "驗算", "失分點")
# ``compact: true`` short questions keep only the answer and its check.
COMPACT_SECTIONS = ("考場標準作答", "驗算")
COMPACT_MAX_POINTS = 10
COMPACT_MAX_CHARS = 700
OPTIONAL_SECTIONS = ("條件與疑義", "計算機按法")
REQUIRED_FRONTMATTER = ("qid", "year", "subject", "audit_status", "verified_at", "method", "source_crop")
# Audit history belongs to frontmatter / data/pe-solution-audit.json, not the
# learner-facing body.
META_HISTORY = re.compile(r"狀態升級|升級為|原詳解|本次修正|移除原|校驗紀錄|稽核紀錄|audit_status|`verified`")
# A LaTeX command whose backslash was lost (e.g. "(1,ldots,10)").
BROKEN_COMMAND = re.compile(r"(?<![\\A-Za-z])(ldots|cdots|frac|sqrt|cdot|mathrm|boxed|infty|circ|pm)(?![A-Za-z])")
MATH = re.compile(r"\$\$.+?\$\$|(?<!\\)\\\[.+?(?<!\\)\\\]|\\\(.+?\\\)|\$[^$\n]+?\$", re.S)
# Commands, superscripts or subscripts left in prose mean math delimiters were
# lost (e.g. "(135^\\circ)" instead of "\\(135^\\circ\\)").
LATEX_OUTSIDE = re.compile(r"\\(?:frac|sqrt|circ|Omega|omega|theta|phi|pi|mathrm|text|times|cdot|angle|boxed|left|right)\b|\^\{|\^\\|_\{")
SUBITEM = re.compile(r"[（(]\s*[一二三四五六七八九十]\s*[）)]|[㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩]")
MAX_TRAPS = 3


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    _, head, body = text.split("---", 2)
    fields = {}
    for line in head.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip("'\"")
    return fields, body


def strip_code(body: str) -> str:
    return re.sub(r"```.*?```", "", body, flags=re.S)


def boxed_values(body: str) -> list[str]:
    values = []
    for match in re.finditer(r"\\boxed\{", body):
        depth, index = 1, match.end()
        while index < len(body) and depth:
            depth += {"{": 1, "}": -1}.get(body[index], 0)
            index += 1
        values.append(re.sub(r"\s+", "", body[match.end():index - 1]))
    return values


def stems() -> dict[str, str]:
    text = DASHBOARD.read_text(encoding="utf-8")
    records = json.loads(re.search(r"questions: (\[.*?\]),\n\n  sevenLayers", text, re.S).group(1))
    return {record[0]: record[4] for record in records if record[0].startswith("EE-")}


def expected_subitems(stem: str) -> int:
    return len({re.sub(r"[\s（）()]", "", item) for item in SUBITEM.findall(stem)})


def total_points(stem: str) -> int:
    """Total marks of a question: 「共 N 分」 when stated, else the sum of 「（N 分）」."""

    stated = re.findall(r"共\s*(\d+)\s*分", stem)
    if stated:
        return max(int(value) for value in stated)
    return sum(int(value) for value in re.findall(r"[（(]\s*(\d+)\s*分\s*[）)]", stem))


def sections(body: str) -> list[str]:
    return [heading.strip() for heading in re.findall(r"^##\s+(.+?)\s*$", body, re.M)]


def lint(path: Path, stem: str) -> dict:
    text = path.read_text(encoding="utf-8")
    fields, body = frontmatter(text)
    prose = strip_code(body)
    errors: list[str] = []
    warnings: list[str] = []

    # Rendering and coverage rules apply to every note.
    for name in sorted(set(BROKEN_COMMAND.findall(prose))):
        errors.append(f"broken-latex:{name}")
    if prose.count("$$") % 2:
        errors.append("unbalanced:$$")
    for opening, closing in (("[", "]"), ("(", ")")):
        # ``\\[4pt]`` is a row break with spacing, not a display delimiter.
        opens = len(re.findall(r"(?<!\\)\\" + re.escape(opening), prose))
        closes = len(re.findall(r"(?<!\\)\\" + re.escape(closing), prose))
        if opens != closes:
            errors.append(f"unbalanced:\\{opening}\\{closing}")
    outside = MATH.sub(" ", re.sub(r"`[^`]*`", " ", prose))
    leaked = LATEX_OUTSIDE.search(outside)
    if leaked:
        errors.append("latex-outside-math:" + leaked.group(0)[:20])
    boxed = boxed_values(prose)
    needed = max(1, expected_subitems(stem))
    if fields.get("audit_status") != "needs_manual_review" and len(boxed) < needed:
        errors.append(f"boxed-coverage:{len(boxed)}<{needed}")

    lean = fields.get("template") == LEAN
    if lean:
        missing = [key for key in REQUIRED_FRONTMATTER if not fields.get(key)]
        if missing:
            errors.append("frontmatter-missing:" + ",".join(missing))
        found = sections(body)
        allowed = REQUIRED_SECTIONS + OPTIONAL_SECTIONS
        for heading in found:
            if heading not in allowed:
                errors.append(f"section-not-allowed:{heading}")
        order = [heading for heading in found if heading in allowed]
        compact = fields.get("compact") == "true"
        if compact:
            points = total_points(stem)
            if points > COMPACT_MAX_POINTS and len(body.strip()) > COMPACT_MAX_CHARS:
                errors.append(f"compact-not-allowed:{points}分")
        for heading in COMPACT_SECTIONS if compact else REQUIRED_SECTIONS:
            if heading not in found:
                errors.append(f"section-missing:{heading}")
        if order != sorted(order, key=allowed.index):
            errors.append("section-order")
        if fields.get("audit_status") == "needs_manual_review" and "條件與疑義" not in found:
            errors.append("section-missing:條件與疑義")
        if META_HISTORY.search(prose):
            errors.append("meta-history:" + META_HISTORY.search(prose).group(0))
        crop = fields.get("source_crop", "")
        if crop and prose.count(Path(crop).name) > 1:
            errors.append("metadata-restated:source_crop")
        if "![官方題目裁切圖](" not in prose:
            errors.append("crop-image-missing")
        duplicates = [value for value, count in Counter(boxed).items() if count > 1]
        if duplicates:
            errors.append("boxed-duplicate:" + "|".join(duplicates)[:80])
        traps = re.search(r"^##\s+失分點\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
        if traps and len(re.findall(r"^\s*[-*]\s", traps.group(1), re.M)) > MAX_TRAPS:
            errors.append(f"too-many-traps>{MAX_TRAPS}")
    else:
        warnings.append("not-migrated")

    return {
        "qid": fields.get("qid", path.stem),
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "template": fields.get("template", ""),
        "chars": len(body.strip()),
        "errors": errors,
        "warnings": warnings,
    }


def canonical_paths(qids: list[str]) -> list[Path]:
    paths = sorted(NOTES.glob("0*/canonical/EE-*.md"))
    if qids:
        wanted = set(qids)
        paths = [path for path in paths if path.stem in wanted]
        missing = wanted - {path.stem for path in paths}
        if missing:
            raise SystemExit(f"unknown qid(s): {', '.join(sorted(missing))}")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qids", nargs="*", help="limit to these QIDs")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any checked note has an error")
    parser.add_argument("--json", action="store_true", help="print per-note results as JSON")
    args = parser.parse_args(argv)

    stem_map = stems()
    results = [lint(path, stem_map.get(path.stem, "")) for path in canonical_paths(args.qids)]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        codes = Counter(error.split(":")[0] for result in results for error in result["errors"])
        lean = sum(result["template"] == LEAN for result in results)
        print(f"notes={len(results)} lean-v1={lean} chars={sum(result['chars'] for result in results)}")
        print(f"notes-with-errors={sum(bool(result['errors']) for result in results)}")
        for code, count in codes.most_common():
            print(f"  {code}: {count}")
        for result in results:
            if result["errors"] and (args.qids or result["template"] == LEAN):
                print(f"{result['qid']}: {'; '.join(result['errors'])}")
    failed = any(result["errors"] for result in results)
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    sys.exit(main())
