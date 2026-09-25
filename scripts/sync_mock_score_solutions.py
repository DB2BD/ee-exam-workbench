#!/usr/bin/env python3
"""Deterministically rebuild the 108/114 passive-mock annual solution pages."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from audit_mock_score_solutions import INDEX, NOTES, SUBJECT_DIRS, selected_qids


YEARS = (108, 114)
ORDINALS = "一二三四五六七八九十"
SUBJECT_NAMES = {
    "01": "電路學",
    "02": "電子學（包括電力電子學）",
    "03": "工程數學",
    "04": "電機機械",
    "05": "電力系統",
    "06": "工業配電",
}


def metadata(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        raise ValueError("canonical note has no front matter")
    raw = text.split("---", 2)[1]
    result = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def question_title(text: str, qid: str) -> str:
    return next(
        (line[2:].strip() for line in text.splitlines() if line.startswith("# ")),
        qid,
    )


def projected_body(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("canonical note has no front matter")
    lines = parts[2].splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    lines = [line for line in lines if not line.startswith("# ")]
    while lines and not lines[0].strip():
        lines.pop(0)
    projected = []
    for line in lines:
        if line.startswith("#### "):
            line = "##### " + line[5:]
        elif line.startswith("### "):
            line = "#### " + line[4:]
        elif line.startswith("## "):
            line = "### " + line[3:]
        projected.append(
            line.replace("../../../依考科分類", "../../依考科分類").rstrip()
        )
    return "\n".join(projected).strip()


def annual_target(subject: str, year: int) -> Path:
    matches = sorted((NOTES / SUBJECT_DIRS[subject]).glob(f"{year}年_*全卷完整詳細題解.md"))
    if len(matches) != 1:
        raise ValueError(
            f"EE-{year}-{subject}: expected one annual solution page, found {len(matches)}"
        )
    return matches[0]


def build_annual(subject: str, year: int, qids: list[str]) -> str:
    records = []
    for qid in sorted(qids, key=lambda item: int(item.rsplit("-", 1)[-1])):
        path = NOTES / SUBJECT_DIRS[subject] / "canonical" / f"{qid}.md"
        text = path.read_text(encoding="utf-8")
        info = metadata(text)
        if info.get("qid") != qid:
            raise ValueError(f"{qid}: front-matter qid mismatch")
        records.append((qid, text, info, question_title(text, qid)))

    statuses = Counter(info.get("audit_status", "unknown") for _, _, info, _ in records)
    status_summary = "；".join(
        f"{count} 題 {status}" for status, count in sorted(statuses.items())
    )
    subject_name = SUBJECT_NAMES[subject]
    lines = [
        "---",
        f"考科: {subject_name}",
        f"年份: {year}",
        "主題: 題級 canonical 詳解彙編（標準 LaTeX）",
        f"校驗摘要: {status_summary}",
        "---",
        "",
        f"# 📝 {year} 年電機工程技師｜{subject_name}逐題詳解",
        "",
        "> 本頁由題級 canonical 筆記組合；每題保留 QID、官方裁切、校驗狀態與完整得分型解答。",
        "",
        "## 題目導覽",
    ]

    for index, (qid, _, _, title) in enumerate(records, start=1):
        number = int(qid.rsplit("-", 1)[-1])
        label = title.split("｜", 1)[-1].split(":", 1)[-1].strip()
        anchor_title = title if subject == "03" else f"{ORDINALS[index - 1]}、{title}"
        lines.append(f"- [[#{anchor_title}|第 {number} 題：{label}]]")

    for index, (qid, text, info, title) in enumerate(records, start=1):
        heading = title if subject == "03" else f"{ORDINALS[index - 1]}、{title}"
        status = info.get("audit_status", "unknown")
        crop = info.get("source_crop", "")
        lines.extend(
            [
                "",
                "---",
                "",
                f"## {heading}",
                "",
                f"> 題級識別：`{qid}`",
                f"> canonical 來源：`canonical/{qid}.md`",
                f"> 題級校驗狀態：`{status}`",
                "",
            ]
        )
        if crop:
            lines.extend(
                [
                    f"![[{crop}]]",
                    "",
                    f"> 官方裁切來源：`{crop}`",
                    "",
                ]
            )
        if status in {"needs_manual_review", "ambiguous", "suspected_error"}:
            lines.extend(
                [
                    "> [!WARNING] 本題仍有官方資料缺口或事件定義歧義；以下條件分支不得視為唯一無條件答案。",
                    "",
                ]
            )
        lines.extend([projected_body(text), ""])
    return "\n".join(lines).rstrip() + "\n"


def expected_pages() -> dict[Path, str]:
    grouped: dict[tuple[str, int], list[str]] = defaultdict(list)
    for qid in selected_qids():
        _, year, subject, _ = qid.split("-")
        grouped[(subject, int(year))].append(qid)
    expected = {}
    for subject in SUBJECT_DIRS:
        for year in YEARS:
            qids = grouped[(subject, year)]
            if not qids:
                raise ValueError(f"missing selected qids for {year}-{subject}")
            expected[annual_target(subject, year)] = build_annual(subject, year, qids)
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="return non-zero when a generated annual page is stale",
    )
    args = parser.parse_args()
    pages = expected_pages()
    stale = []
    for path, expected in pages.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual == expected:
            continue
        stale.append(path)
        if not args.check:
            path.write_text(expected, encoding="utf-8")

    if stale and args.check:
        for path in stale:
            print(f"stale: {path.relative_to(INDEX.parent.parent)}", file=sys.stderr)
        return 1
    action = "generated" if stale else "current"
    print(f"{action}: {len(pages)} annual passive-mock solution pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
