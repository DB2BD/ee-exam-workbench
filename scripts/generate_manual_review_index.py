#!/usr/bin/env python3
"""Generate a single, traceable queue for all unresolved solution reviews."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "manual-review-index.md"
MANIFESTS = (ROOT / "data" / "pe-solution-audit.json", ROOT / "data" / "engineering-math-audit.json")
SUBJECT_NAMES = {
    "01": "電路學",
    "02": "電子學（含電力電子）",
    "03": "工程數學",
    "04": "電機機械",
    "05": "電力系統",
    "06": "工業配電",
    # Canonical notes historically used several textual aliases for subject 02.
    # Normalize them to the same textbook-facing label used by the UI/report.
    "電子學_含電力電子": "電子學（含電力電子）",
    "電子學（包括電力電子學）": "電子學（含電力電子）",
    "電子學（含電力電子）": "電子學（含電力電子）",
}


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    values: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def escape_cell(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).replace("|", "\\|").strip()


def main() -> None:
    rows = []
    for manifest_path in MANIFESTS:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            if entry.get("audit_status") != "needs_manual_review":
                continue
            note = ROOT / entry["solution_link"]
            meta = frontmatter(note)
            source = meta.get("official_source_url", "")
            source_cell = f"[官方試題]({source})" if source.startswith("https://") else "—"
            public_urls = [
                url.strip() for url in meta.get("public_reference_urls", "").split(";")
                if url.strip().startswith("https://")
            ]
            public_cell = "、".join(
                f"[來源{i + 1}]({url})" for i, url in enumerate(public_urls)
            ) or "—"
            raw_subject = meta.get("subject", meta.get("考科", entry.get("subject_id", "")))
            chapter = meta.get("chapter", meta.get("章節", "")).strip()
            if not chapter:
                chapter = "待依教科書章節覆核"
            rows.append({
                "qid": entry["qid"],
                "subject": SUBJECT_NAMES.get(raw_subject, raw_subject),
                "year": entry.get("year", ""),
                "number": entry.get("question_number", ""),
                # The manifest chapter field is the extracted topic/question text;
                # canonical frontmatter is the authoritative textbook taxonomy.
                # Never expose raw question text as a pseudo-chapter when metadata
                # is missing; leave an explicit taxonomy follow-up instead.
                "chapter": chapter,
                "blocker": meta.get("review_blocker", ""),
                "action": meta.get("review_action", ""),
                "note": f"[{entry['qid']}]({entry['solution_link']})",
                "source": source_cell,
                "public": public_cell,
            })
    rows.sort(key=lambda row: (str(row["subject"]), int(row["year"]), int(row["number"])))
    lines = [
        "# 人工覆核索引",
        "",
        f"> 產生日期：{date.today().isoformat()}；此清單只收錄 audit manifest 中 `needs_manual_review` 題目。",
        "> 任何題目在缺參數、圖形估讀或來源衝突未解除前，不得升級為 `verified`。",
        "",
        f"目前共 **{len(rows)} 題**待人工覆核。",
        "> 公開參考欄僅供方法／題幹交叉比對；若與官方原卷不一致，以官方原卷為準，且不得以二手資料解除缺參數阻擋。",
        "",
        "| 題號 | 科目／年度 | 教科書章節 | 阻擋原因 | 收斂所需動作 | 詳解 | 官方來源 | 公開參考 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join([
            row["qid"],
            f"{row['subject']}／{row['year']} 年第 {row['number']} 題",
            escape_cell(row["chapter"]),
            escape_cell(row["blocker"]),
            escape_cell(row["action"]),
            row["note"],
            row["source"],
            row["public"],
        ]) + " |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated {OUT} with {len(rows)} manual-review rows")


if __name__ == "__main__":
    main()
