"""Build year landing pages from official PDF headers and canonical audits.

The generated pages describe repository evidence only. They never infer that a
learner has attempted, mastered, or passed a subject without an actual answer.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YEARS = tuple(range(114, 103, -1))
SUBJECTS = (
    ("01", "01_電路學", "電路學", "電路學"),
    ("02", "02_電子學_含電力電子", "電子學（包括電力電子學）", "電子學（包括電力電子學）"),
    ("03", "03_工程數學", "工程數學", "工程數學"),
    ("04", "04_電機機械", "電機機械", "電機機械"),
    ("05", "05_電力系統", "電力系統", "電力系統"),
    ("06", "06_工業配電", "工業配電", "工業配電"),
)
AUDIT_ORDER = ("verified", "reference_book_verified", "needs_manual_review")


def official_pdf(year: int, pdf_subject: str) -> Path:
    return ROOT / "依年度分類" / f"{year}年" / f"{year}年_電機工程技師_{pdf_subject}.pdf"


def read_pdf_header(pdf_path: Path) -> tuple[str, str]:
    """Return the exam code and calculator rule printed on page one."""
    result = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "1", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    header = result.stdout
    code_match = re.search(r"代號\s*[：:]\s*(\d+)", header)
    if not code_match:
        raise ValueError(f"找不到試題代號：{pdf_path}")

    if "禁止使用電子計算器" in header or "不得使用電子計算器" in header:
        calculator_rule = "禁止使用電子計算器"
    elif "可以使用電子計算器" in header:
        calculator_rule = "可以使用電子計算器"
    else:
        raise ValueError(f"找不到計算器規範：{pdf_path}")
    return code_match.group(1), calculator_rule


def audit_summary(year: int, subject_code: str, subject_folder: str) -> tuple[int, str]:
    canonical_dir = ROOT / "📝 個人題解與錯題本" / subject_folder / "canonical"
    paths = sorted(canonical_dir.glob(f"EE-{year}-{subject_code}-*.md"))
    if not paths:
        raise ValueError(f"找不到 canonical 題目：{year} / {subject_folder}")

    counts: Counter[str] = Counter()
    for path in paths:
        source = path.read_text(encoding="utf-8")
        match = re.search(r"^audit_status:\s*(\S+)\s*$", source, re.MULTILINE)
        if not match:
            raise ValueError(f"缺少 audit_status：{path}")
        counts[match.group(1)] += 1

    unknown = sorted(set(counts) - set(AUDIT_ORDER))
    if unknown:
        raise ValueError(f"未知 audit_status：{unknown}")
    summary = "、".join(f"`{status}` × {counts[status]}" for status in AUDIT_ORDER if counts[status])
    return len(paths), summary


def route_link(year: int) -> str:
    if year == 114:
        return "[114 年六科被動模考執行包](../../docs/上榜被動模考_114年六科執行包.md)"
    if year == 108:
        return "[108 年六科被動複測執行包](../../docs/上榜被動複測_108年六科執行包.md)"
    return "[固定上榜路徑](../../docs/上榜預設24時段_核心題路徑.md)"


def render_year_readme(year: int) -> str:
    lines = [
        f"# {year} 年電機工程技師全真模擬試卷",
        "",
        f"> 民國 {year} 年，共 6 科；每科官方卷面時間 120 分鐘、滿分 100 分。錄取判定請以該次考試官方規定為準。",
        f"> 本頁不預設任何科目已掌握。直接入口：{route_link(year)}。",
        "",
        "## 六科官方試卷與完整題解",
        "",
        "試題代號與計算器規範取自各科官方 PDF 第一頁；題解稽核狀態取自題號級 canonical 筆記。",
        "",
        "| 順序 | 科目 | 試題代號 | 時間 | 計算器規範 | 題數與稽核狀態 | 官方原卷 | 完整題解 |",
        "| ---: | --- | :---: | ---: | --- | --- | --- | --- |",
    ]

    for index, (subject_code, subject_folder, subject_name, pdf_subject) in enumerate(SUBJECTS, start=1):
        pdf_path = official_pdf(year, pdf_subject)
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        exam_code, calculator_rule = read_pdf_header(pdf_path)
        question_count, audits = audit_summary(year, subject_code, subject_folder)
        solution_subject = "電子學" if subject_code == "02" else subject_name
        solution_name = f"{year}年_{solution_subject}_全卷完整詳細題解.md"
        solution_path = ROOT / "📝 個人題解與錯題本" / subject_folder / solution_name
        if not solution_path.exists():
            raise FileNotFoundError(solution_path)
        solution_href = f"../../📝%20個人題解與錯題本/{subject_folder}/{solution_name}"
        lines.append(
            f"| {index} | {subject_name} | `{exam_code}` | 120 分鐘 | {calculator_rule} | "
            f"{question_count} 題；{audits} | [PDF](./{pdf_path.name}) | [完整題解]({solution_href}) |"
        )

    lines.extend(
        [
            "",
            "## 固定使用方式",
            "",
            "1. 只開官方原卷，依卷首計算器規範閉卷作答 120 分鐘；時間到立即停筆。",
            "2. 再開完整題解，在自己的答案紙標出完整證據 `○`、部分證據 `△`、空白或錯起手 `×`。",
            "3. 選最高配分的 `△／×` 題，關閉題解後重寫一次；錯因與分數不需回填專案。",
            "4. `verified` 只代表題解通過專案題級查核，不代表使用者已掌握，也不等於官方逐步配分。",
            "",
        ]
    )
    return "\n".join(lines)


def write_year_readmes(*, check: bool = False) -> bool:
    clean = True
    for year in YEARS:
        destination = ROOT / "依年度分類" / f"{year}年" / "README.md"
        expected = render_year_readme(year)
        current = destination.read_text(encoding="utf-8") if destination.exists() else None
        if check:
            if current != expected:
                clean = False
                print(f"STALE: {destination.relative_to(ROOT)}")
        else:
            destination.write_text(expected, encoding="utf-8")
            print(f"UPDATED: {destination.relative_to(ROOT)}")
    return clean


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated pages differ")
    args = parser.parse_args()
    return 0 if write_year_readmes(check=args.check) else 1


if __name__ == "__main__":
    sys.exit(main())
