#!/usr/bin/env python3
"""Check and synchronize corrected canonical answers in annual solution pages."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "📝 個人題解與錯題本"
NON_MATH_SUBJECTS = (
    "01_電路學",
    "02_電子學_含電力電子",
    "04_電機機械",
    "05_電力系統",
    "06_工業配電",
)
ANNUAL_SYNC = re.compile(r"^annual_sync:\s*true\s*$", re.M)
ORDINALS = "一二三四五六七八九十"
ANNUAL_HEADING = re.compile(r"^##\s+([一二三四五六七八九十]+)、.*$", re.M)


def corrected_canonicals() -> list[Path]:
    return sorted(
        path
        for subject in NON_MATH_SUBJECTS
        for path in (NOTES / subject / "canonical").glob("EE-*.md")
        if ANNUAL_SYNC.search(path.read_text(encoding="utf-8"))
    )


def qid_parts(canonical: Path) -> tuple[int, int]:
    match = re.search(r"^qid:\s*EE-(\d+)-(\d+)-(\d+)\s*$", canonical.read_text(encoding="utf-8"), re.M)
    if not match:
        raise ValueError(f"canonical note has no qid: {canonical}")
    year, _, question_number = map(int, match.groups())
    return year, question_number


def annual_for(canonical: Path) -> Path:
    year, _ = qid_parts(canonical)
    matches = sorted(canonical.parent.parent.glob(f"{year}年_*全卷完整詳細題解.md"))
    if not matches:
        raise FileNotFoundError(f"annual note missing for {canonical.name}")
    return matches[0]


def canonical_projection(canonical: Path) -> str:
    lines = canonical.read_text(encoding="utf-8").splitlines()
    fences = [index for index, line in enumerate(lines) if line.strip() == "---"]
    if len(fences) < 2:
        raise ValueError(f"canonical frontmatter missing: {canonical}")
    body = lines[fences[1] + 1 :]
    while body and not body[0].strip():
        body.pop(0)
    body = [line for line in body if not line.startswith("# ")]
    while body and not body[0].strip():
        body.pop(0)

    projected = []
    for line in body:
        if line.startswith("#### "):
            line = "##### " + line[5:]
        elif line.startswith("### "):
            line = "#### " + line[4:]
        elif line.startswith("## "):
            line = "### " + line[3:]
        projected.append(line.replace("../../../依考科分類", "../../依考科分類").rstrip())
    return "\n".join(projected).strip()


def annual_section(annual_text: str, question_number: int) -> tuple[int, int, str]:
    headings = list(ANNUAL_HEADING.finditer(annual_text))
    if question_number > len(headings):
        raise ValueError(f"annual question heading missing: question {question_number}")
    heading = headings[question_number - 1]
    end = headings[question_number].start() if question_number < len(headings) else len(annual_text)
    lines = annual_text[heading.start() : end].splitlines()
    if not lines:
        raise ValueError("annual question section is empty")
    body = lines[1:]
    while body and not body[-1].strip():
        body.pop()
    if body and body[-1].strip() == "---":
        body.pop()
        while body and not body[-1].strip():
            body.pop()
    return heading.start(), end, strip_generated_prefix("\n".join(body).strip())


def strip_generated_prefix(body: str) -> str:
    """Remove annual-page metadata that is added around the canonical body."""
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    prefixes = (
        "> 題級識別：",
        "> canonical 來源：",
        "> 題級校驗狀態：",
        "![[",
        "> 官方裁切來源：",
        "> [!WARNING] 本題仍有官方資料缺口或事件定義歧義；",
    )
    while lines:
        line = lines[0].strip()
        if not line or any(line.startswith(prefix) for prefix in prefixes):
            lines.pop(0)
            continue
        break
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def sync() -> list[str]:
    changed = []
    for canonical in corrected_canonicals():
        _, question_number = qid_parts(canonical)
        annual = annual_for(canonical)
        annual_text = annual.read_text(encoding="utf-8")
        start, end, _ = annual_section(annual_text, question_number)
        heading = annual_text[start : annual_text.find("\n", start)]
        canonical_text = canonical.read_text(encoding="utf-8")
        qid = re.search(r"^qid:\s*(EE-\d+-\d+-\d+)\s*$", canonical_text, re.M).group(1)
        status = re.search(r"^audit_status:\s*([^\n]+)", canonical_text, re.M)
        prefix = (
            f"> 題級識別：{qid}\n"
            f"> canonical 來源：[[canonical/{canonical.name}]]\n"
            f"> 題級校驗狀態：{status.group(1).strip() if status else 'unknown'}\n"
        )
        if status and status.group(1).strip() == "needs_manual_review":
            prefix += "> [!WARNING] 本題仍有官方資料缺口或事件定義歧義；請以 canonical 條件式解答為準。\n"
        replacement = heading + "\n\n" + prefix + "\n" + canonical_projection(canonical) + "\n\n---\n\n"
        new_text = (annual_text[:start] + replacement + annual_text[end:]).rstrip() + "\n"
        if new_text != annual_text:
            annual.write_text(new_text, encoding="utf-8")
            changed.append(f"{canonical.name} -> {annual.name}")
    return changed


def check() -> list[str]:
    mismatches = []
    for canonical in corrected_canonicals():
        _, question_number = qid_parts(canonical)
        annual = annual_for(canonical)
        annual_text = annual.read_text(encoding="utf-8")
        _, _, actual = annual_section(annual_text, question_number)
        normalize = lambda value: re.sub(r"\s+", " ", value)
        if normalize(actual) != normalize(canonical_projection(canonical)):
            mismatches.append(f"{canonical.name} != {annual.name} question {question_number}")
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="write corrected canonical sections into annual notes")
    args = parser.parse_args()
    if args.sync:
        changed = sync()
        print(f"Synchronized {len(changed)} annual sections")
        for item in changed:
            print(item)
    mismatches = check()
    print(f"Corrected canonical sections checked: {len(corrected_canonicals())}")
    if mismatches:
        print("Annual/canonical mismatches:")
        print("\n".join(mismatches))
        return 1
    print("Annual/canonical alignment: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
