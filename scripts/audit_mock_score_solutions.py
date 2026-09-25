#!/usr/bin/env python3
"""Audit score-oriented structure and annual projection for 114/108 mock solutions."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "上榜錯因修復索引_114-108.md"
NOTES = ROOT / "📝 個人題解與錯題本"
SUBJECT_DIRS = {
    "01": "01_電路學",
    "02": "02_電子學_含電力電子",
    "03": "03_工程數學",
    "04": "04_電機機械",
    "05": "05_電力系統",
    "06": "06_工業配電",
}
REQUIRED_HEADINGS = (
    "考場標準作答",
    "得分點拆解",
    "完整教學推導",
    "獨立驗算",
    "常見失分",
)
PLACEHOLDERS = ("TODO", "TBD", "待補內容", "待完成內容", "此處補上")
ORDINAL_HEADINGS = re.compile(r"^##\s+[一二三四五六七八九十]+、.*$", re.MULTILINE)


def selected_qids() -> list[str]:
    source = INDEX.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"EE-(?:114|108)-\d{2}-\d+", source)))


def canonical_path(qid: str) -> Path:
    subject = qid.split("-")[2]
    return NOTES / SUBJECT_DIRS[subject] / "canonical" / f"{qid}.md"


def annual_path(qid: str) -> Path:
    _, year, subject, _ = qid.split("-")
    matches = sorted((NOTES / SUBJECT_DIRS[subject]).glob(f"{year}年_*全卷完整詳細題解.md"))
    if len(matches) != 1:
        raise ValueError(f"{qid}: expected one annual solution page, found {len(matches)}")
    return matches[0]


def annual_question_section(qid: str, text: str) -> str:
    _, year, subject, number_text = qid.split("-")
    number = int(number_text)
    if subject == "03":
        headings = list(
            re.finditer(
                rf"^##\s+{year}\s*年第\s*(\d+)\s*題.*$",
                text,
                re.MULTILINE,
            )
        )
        target_index = next(
            (index for index, match in enumerate(headings) if int(match.group(1)) == number),
            None,
        )
        if target_index is None:
            raise ValueError(f"{qid}: annual question heading missing")
    else:
        headings = list(ORDINAL_HEADINGS.finditer(text))
        target_index = number - 1
        if target_index >= len(headings):
            raise ValueError(f"{qid}: annual question heading missing")
    start = headings[target_index].end()
    end = headings[target_index + 1].start() if target_index + 1 < len(headings) else len(text)
    return text[start:end]


def required_sections(text: str, level: int, label: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    marker = "#" * level
    matches = []
    for heading in REQUIRED_HEADINGS:
        found = list(re.finditer(rf"^{marker}\s+{re.escape(heading)}\s*$", text, re.MULTILINE))
        if len(found) != 1:
            errors.append(f"{label}: expected one '{marker} {heading}', found {len(found)}")
            continue
        matches.append((heading, found[0]))

    if len(matches) != len(REQUIRED_HEADINGS):
        return {}, errors
    positions = [match.start() for _, match in matches]
    if positions != sorted(positions):
        errors.append(f"{label}: required sections are out of order")

    same_level = re.compile(rf"^{marker}\s+(?!#).+$", re.MULTILINE)
    sections = {}
    for heading, match in matches:
        following = same_level.search(text, match.end())
        end = following.start() if following else len(text)
        body = text[match.end():end].strip()
        body = re.sub(r"\n?\s*---\s*$", "", body).strip()
        compact = re.sub(r"\s+", "", body)
        if len(compact) < 60:
            errors.append(f"{label}: '{heading}' is too short to be a substantive answer")
        if any(token in body for token in PLACEHOLDERS):
            errors.append(f"{label}: '{heading}' contains placeholder text")
        if heading in {"得分點拆解", "常見失分"}:
            bullet_count = len(re.findall(r"^\s*[-*]\s+", body, re.MULTILINE))
            if bullet_count < 2:
                errors.append(f"{label}: '{heading}' needs at least two concrete bullets")
        sections[heading] = body
    return sections, errors


def normalized(value: str) -> str:
    value = value.replace("../../../依考科分類", "../../依考科分類")
    value = re.sub(r"^#{3,}\s+", "# ", value, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", value).strip()


def audit() -> list[str]:
    qids = selected_qids()
    errors = []
    if len(qids) != 59:
        errors.append(f"repair index must select 59 qids, found {len(qids)}")
    for qid in qids:
        canonical = canonical_path(qid)
        if not canonical.is_file():
            errors.append(f"{qid}: canonical solution missing")
            continue
        canonical_sections, section_errors = required_sections(
            canonical.read_text(encoding="utf-8"),
            2,
            f"{qid} canonical",
        )
        errors.extend(section_errors)

        try:
            annual = annual_path(qid)
            annual_question = annual_question_section(qid, annual.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        annual_sections, annual_errors = required_sections(
            annual_question,
            3,
            f"{qid} annual",
        )
        errors.extend(annual_errors)

        if canonical_sections and annual_sections:
            for heading in REQUIRED_HEADINGS:
                if normalized(canonical_sections[heading]) != normalized(annual_sections[heading]):
                    errors.append(f"{qid}: annual '{heading}' differs from canonical")
    return errors


def main() -> int:
    errors = audit()
    if errors:
        print(f"Mock score-solution audit failed with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Mock score-solution audit: 59/59 canonical and annual solutions have aligned five-part scoring structure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
