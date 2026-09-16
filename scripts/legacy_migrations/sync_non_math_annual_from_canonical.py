#!/usr/bin/env python3
"""Rebuild non-mathematics annual solution pages from canonical notes.

Question-level canonical notes are the audited source of truth.  The older
annual pages mixed those answers with legacy templates, which allowed a stale
numeric result to remain learner-facing.  This migration assembles each
annual page from the canonical notes while retaining the question-level audit
status and official crop provenance.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "📝 個人題解與錯題本"
SUBJECTS = {
    "01_電路學": "電路學",
    "02_電子學_含電力電子": "電子學（包括電力電子學）",
    "04_電機機械": "電機機械",
    "05_電力系統": "電力系統",
    "06_工業配電": "工業配電",
}
ORDINALS = "一二三四五六七八九十"


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


def body_without_frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("canonical note has no frontmatter")
    body = parts[2].strip()
    body = re.sub(r"^#\s+[^\n]+\n?", "", body, flags=re.M)
    body = body.replace("../../../依考科分類", "../../依考科分類").strip()
    return "\n".join(line.rstrip() for line in body.splitlines()).strip()


def demote_headings(body: str) -> str:
    return re.sub(r"^(#{1,4})\s+", lambda match: "#" * (len(match.group(1)) + 1) + " ", body, flags=re.M)


def question_title(note: Path, info: dict[str, str]) -> str:
    for line in note.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return info.get("qid", note.stem)


def build_year(year: int, subject_dir: str, subject_name: str, notes: list[Path]) -> str:
    infos = [metadata(note.read_text(encoding="utf-8")) for note in notes]
    statuses = [info.get("audit_status", "unknown") for info in infos]
    status_counts = ", ".join(
        f"{statuses.count(status)} 題 {status}"
        for status in ("verified", "reference_book_verified", "needs_manual_review", "suspected_error", "not_attempted")
        if statuses.count(status)
    )
    lines = [
        "---",
        f"考科: {subject_name}",
        f"年份: {year}",
        "主題: 題級 canonical 詳解彙編（標準 LaTeX）",
        f"校驗摘要: {status_counts}",
        "---",
        "",
        f"# 📝 {year} 年電機工程技師｜{subject_name}逐題詳解",
        "",
        "> 本頁由題級 canonical 筆記組合；每題保留官方裁切圖、校驗狀態與可追溯的推導。",
        "",
        "## 題目導覽",
    ]
    for index, (note, info) in enumerate(zip(notes, infos), start=1):
        qid = info.get("qid", note.stem)
        number = qid.rsplit("-", 1)[-1]
        title = question_title(note, info)
        label = title.split("｜", 1)[-1].split(":", 1)[-1]
        lines.append(f"- [[#{ORDINALS[index - 1]}、{title}|第 {number} 題：{label}]]")
    lines.append("")

    for index, (note, info) in enumerate(zip(notes, infos), start=1):
        title = question_title(note, info)
        qid = info.get("qid", note.stem)
        status = info.get("audit_status", "unknown")
        crop = info.get("source_crop", "")
        lines.extend(
            [
                "---",
                "",
                f"## {ORDINALS[index - 1]}、{title}",
                "",
                f"> 題級識別：`{qid}`",
                f"> canonical 來源：`canonical/{qid}.md`",
                f"> 題級校驗狀態：`{status}`",
                "",
            ]
        )
        if crop:
            lines.extend([f"![[{crop}]]", "", f"> 官方裁切來源：`{crop}`", ""])
        if status == "needs_manual_review":
            lines.extend(["> [!WARNING] 本題仍有官方資料缺口或事件定義歧義；以下條件分支不得視為唯一無條件答案。", ""])
        lines.extend([demote_headings(body_without_frontmatter(note.read_text(encoding="utf-8"))), ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    for subject_dir, subject_name in SUBJECTS.items():
        subject = NOTES / subject_dir
        for year in range(104, 115):
            notes = sorted(
                (subject / "canonical").glob(f"EE-{year:03d}-*.md"),
                key=lambda path: int(path.stem.rsplit("-", 1)[-1]),
            )
            if not notes:
                continue
            target = subject / f"{year}年_{subject_name.replace('（包括電力電子學）', '')}_全卷完整詳細題解.md"
            target.write_text(build_year(year, subject_dir, subject_name, notes), encoding="utf-8")
            print(f"synced {target.name}: {len(notes)} questions")


if __name__ == "__main__":
    main()
