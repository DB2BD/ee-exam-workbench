# -*- coding: utf-8 -*-
"""Build active question-bank Markdown from the attested MOEX crop manifest.

The generated Markdown is a source transcription, not a solution.  The
question image is kept as the authoritative representation because PDF text
extraction can damage mathematical glyphs and circuit labels.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import fitz


WORKSPACE = Path(__file__).resolve().parents[1]
MANIFEST = WORKSPACE / "data" / "moex-question-crops.json"
BASE = WORKSPACE / "依考科分類" / "🏛️_國考同級參考題庫"

SUBJECT_DIRS = {
    "電路學": "01_電路學",
    "電子學": "02_電子學_含電力電子",
    "工程數學": "03_工程數學",
    "電機機械": "04_電機機械",
    "電力系統": "05_電力系統",
}

CONTROL_GLYPHS = {
    "\ue129": "（一）",
    "\ue12a": "（二）",
    "\ue12b": "（三）",
    "\ue12c": "（四）",
}


def clean_text(text: str) -> str:
    for source, replacement in CONTROL_GLYPHS.items():
        text = text.replace(source, replacement)
    text = re.sub(
        r"代號：.*?頁次：.*?(?=[一二三四五六七八九十]+、)",
        "",
        text,
        flags=re.DOTALL,
    )
    lines = []
    for line in text.splitlines():
        line = " ".join(line.split()).strip()
        if not line:
            continue
        if "代號：" in line and "頁次：" in line:
            continue
        if "年公務人員高等考試三級考試試題" in line:
            continue
        lines.append(line)
    return "\n".join(lines)


def question_text(pdf_path: Path, question: dict) -> str:
    doc = fitz.open(pdf_path)
    chunks = []
    for page_info in question["source_pages"]:
        page = doc[page_info["page"] - 1]
        rect = fitz.Rect(*page_info["crop_rect"])
        chunks.append(page.get_text("text", clip=rect))
    doc.close()
    return clean_text("\n".join(chunks))


def relative_to_subject(subject_dir: Path, path_string: str) -> str:
    path = Path(path_string)
    if not path.is_absolute():
        path = WORKSPACE / path
    return path.relative_to(subject_dir).as_posix()


def render_entry(entry: dict) -> None:
    if entry["status"] != "downloaded":
        return
    pdf_path = WORKSPACE / entry["target_path"]
    subject_dir = pdf_path.parent
    source_path = subject_dir / f"GK_{entry['year']}年_{entry['subject']}.md"
    sections = []
    for question in entry["questions"]:
        qtext = question_text(pdf_path, question)
        image = relative_to_subject(subject_dir, question["question_crop"])
        figures = [relative_to_subject(subject_dir, path) for path in question["figure_crops"]]
        kind = question.get("question_kind", "essay")
        question_number = question.get("question_number")
        app_question_number = question.get("app_question_number", question_number)
        if kind == "multiple_choice":
            heading = f"測驗題 {question_number}"
            heading_text = re.sub(rf"^\s*{re.escape(str(question_number))}\s+", "", qtext, count=1)
        else:
            heading = question["source_heading"]
            heading_text = re.sub(rf"^{re.escape(heading)}、\s*", "", qtext)
        figure_lines = "\n".join(f"![]({path})" for path in figures)
        section = (
            f"#### {heading}、{heading_text}\n\n"
            f"<!-- question_kind: {kind}; question_number: {question_number}; app_question_number: {app_question_number} -->\n\n"
            f"### 原始題目裁切\n\n![]({image})\n\n"
            f"### 原始圖形裁切\n\n{figure_lines or '本題原始 PDF 未含獨立嵌入圖形。'}\n"
        )
        sections.append(section)
    frontmatter = (
        "---\n"
        "source_kind: moex_official_question_pdf\n"
        f"year: {entry['year']}\n"
        f"subject: {entry['subject']}\n"
        f"official_url: {entry['official_url']}\n"
        f"official_search_page: {entry['source_page']}\n"
        f"source_pdf_sha256: {entry['sha256']}\n"
        f"source_pdf_pages: {entry['page_count']}\n"
        "transcription_policy: crop_is_authoritative\n"
        "---\n\n"
    )
    title = f"# 公務人員高等考試三級（{entry['year']}年）{entry['subject']} 原始試題\n\n"
    note = (
        "> 本檔只保存考選部原始試題的轉錄與裁切圖，不含解答。數學符號、電路接線與圖中文字以原始題目裁切圖為準。\n\n"
    )
    source_path.write_text(frontmatter + title + note + "\n".join(sections), encoding="utf-8")
    print(f"Wrote {source_path.relative_to(WORKSPACE)} ({len(entry['questions'])} questions)")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["entries"]:
        render_entry(entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
