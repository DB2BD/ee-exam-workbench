#!/usr/bin/env python3
"""Materialize question-level notes for the 104--110 circuit/electronics batch.

This deliberately marks generated copies as needs_manual_review.  Splitting a
long annual note is not mathematical verification; the status must not imply
that merely having a section proves its arithmetic.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
subjects = {
    "01": ("電路學", "電路學", "01_電路學", "電路學"),
    # Annual notes use the shorter filename, while the official PDF/crop
    # title contains the parenthetical qualification.
    "02": ("電子學_含電力電子", "電子學（包括電力電子學）", "02_電子學_含電力電子", "電子學"),
}
years = range(104, 111)

def split_questions(text):
    starts = list(re.finditer(r"(?m)^##\s+([一二三四五六七八九十0-9]+)[、.：:]", text))
    cmap = {c:i for i,c in enumerate("一二三四五六七八九十", 1)}
    out = {}
    for i, m in enumerate(starts):
        token = m.group(1)
        n = int(token) if token.isdigit() else cmap.get(token)
        if n:
            out[n] = text[m.start(): starts[i+1].start() if i+1 < len(starts) else len(text)].strip()
    return out

def main():
    count = 0
    for sid, (folder, title, short, filename_title) in subjects.items():
        dest = ROOT / "📝 個人題解與錯題本" / short / "canonical"
        dest.mkdir(parents=True, exist_ok=True)
        for year in years:
            annual = ROOT / "📝 個人題解與錯題本" / short / f"{year}年_{filename_title}_全卷完整詳細題解.md"
            if not annual.is_file():
                continue
            sections = split_questions(annual.read_text(encoding="utf-8"))
            for qnum, body in sections.items():
                if qnum > 5:
                    continue
                qid = f"EE-{year}-{sid}-{qnum}"
                target = dest / f"{qid}.md"
                if target.exists():
                    continue
                crop = f"依考科分類/{short}/images/questions/PE_{year}年_{title}_Q{qnum:02d}.png"
                front = ("---\n" f"qid: {qid}\n" f"year: {year}\n" f"subject: {folder}\n"
                         "chapter: 待依教科書章節覆核\n"
                         "audit_status: needs_manual_review\n"
                         "verified_at: null\n"
                         "method: question-level extraction only; independent recalculation pending\n"
                         f"source_crop: {crop}\n---\n\n")
                note = (front + f"# {year} 年{folder}第 {qnum} 題\n\n"
                        "> ⚠️ 本檔由年度詳解分割產生；尚未完成獨立逐步重算，禁止視為已校驗答案。\n\n"
                        + body + "\n")
                target.write_text(note, encoding="utf-8")
                count += 1
    print(f"created {count} canonical notes")

if __name__ == "__main__":
    main()
