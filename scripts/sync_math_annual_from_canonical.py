#!/usr/bin/env python3
"""Rebuild engineering-math annual notes from question-level canonical notes.

The old annual files were broad teaching templates and could disagree with the
official cropped questions.  Canonical notes are the source of truth; this
script only assembles them into a readable annual Obsidian page and preserves
each question's audit status and crop provenance.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "📝 個人題解與錯題本" / "03_工程數學"
CANONICAL = SUBJECT / "canonical"


def metadata(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    head = text.split("---", 2)[1]
    result: dict[str, str] = {}
    for line in head.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def demote_headings(body: str) -> str:
    """Nest canonical headings below the annual question heading."""
    return re.sub(r"^(#{1,5})\s+", lambda m: "#" * (len(m.group(1)) + 1) + " ", body, flags=re.M)


def build_year(year: int, notes: list[Path]) -> str:
    statuses = [metadata(p.read_text(encoding="utf-8")).get("audit_status", "unknown") for p in notes]
    verified = statuses.count("verified")
    manual = statuses.count("needs_manual_review")
    lines = [
        "---",
        "考科: 工程數學",
        f"年份: {year}",
        "主題: 題級 canonical 詳解彙編（標準 LaTeX）",
        f"校驗摘要: {verified} 題 verified；{manual} 題 needs_manual_review",
        "---",
        "",
        f"# 📝 {year} 年電機工程技師｜工程數學逐題詳解",
        "",
        "> 本頁由題級 canonical 筆記組合；每題保留官方裁切圖、校驗狀態與標準 LaTeX 公式。",
        "",
        "## 題目導覽",
    ]
    for note in notes:
        info = metadata(note.read_text(encoding="utf-8"))
        qid = info.get("qid", note.stem)
        number = qid.rsplit("-", 1)[-1]
        title = next((line[2:].strip() for line in note.read_text(encoding="utf-8").splitlines() if line.startswith("# ")), qid)
        lines.append(f"- [[#{title}|第 {number} 題：{title.split('｜', 1)[-1]}]]")
    lines.append("")

    for note in notes:
        raw = note.read_text(encoding="utf-8")
        info = metadata(raw)
        body = raw.split("---", 2)[-1].strip()
        body = re.sub(r"^#\s+[^\n]+\n?", "", body, count=1)
        title = next((line[2:].strip() for line in raw.splitlines() if line.startswith("# ")), info.get("qid", note.stem))
        status = info.get("audit_status", "unknown")
        crop = info.get("source_crop", "")
        lines.extend(["---", "", f"## {title}", "", f"> 題級校驗狀態：`{status}`", ""])
        if crop:
            lines.extend([f"![[{crop}]]", "", f"> 官方裁切來源：`{crop}`", ""])
        if status == "needs_manual_review":
            lines.extend(["> [!WARNING] 本題仍有官方資料缺口或事件定義歧義；以下條件分支不得視為唯一無條件答案。", ""])
        lines.extend([demote_headings(body), ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    for year in range(104, 115):
        notes = sorted(
            CANONICAL.glob(f"EE-{year:03d}-03-*.md"),
            key=lambda path: int(path.stem.rsplit("-", 1)[-1]),
        )
        if not notes:
            continue
        target = SUBJECT / f"{year}年_工程數學_全卷完整詳細題解.md"
        target.write_text(build_year(year, notes), encoding="utf-8")
        print(f"synced {target.name}: {len(notes)} questions")


if __name__ == "__main__":
    main()
