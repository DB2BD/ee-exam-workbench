# -*- coding: utf-8 -*-
"""Build the reproducible PE topic-coverage report from canonical data.

The report deliberately measures historical coverage instead of predicting
future questions. Every question contributes to exactly one primary chapter,
as recorded in ``QUESTION_TAXONOMY_MAP``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from scripts.question_schema import load_questions_from_bundle
except ModuleNotFoundError:
    from question_schema import load_questions_from_bundle


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "dashboard-data.js"
DAG_PATH = ROOT / "src" / "data" / "knowledge-dag.js"
OUTPUT = (
    ROOT
    / "🧠 核心考點知識庫"
    / "📊_電機工程技師_6大考科11年高頻考點統計與命中率分析.md"
)

SUBJECT_NAMES = {
    "01": "電路學",
    "02": "電子學（含電力電子）",
    "03": "工程數學",
    "04": "電機機械",
    "05": "電力系統",
    "06": "工業配電",
}

DIST_FLICKER_QIDS = {"EE-104-06-3", "EE-110-06-4", "EE-113-06-3", "EE-114-06-2"}
DIST_HARMONIC_QIDS = {"EE-104-06-5", "EE-105-06-5", "EE-106-06-5"}
DC_DC_CONVERTER_QIDS = {
    "EE-106-02-5", "EE-107-02-3", "EE-107-02-4", "EE-108-02-5",
    "EE-109-02-2", "EE-109-02-3", "EE-111-02-2", "EE-112-02-3",
    "EE-113-02-3", "EE-113-02-4",
}
DC_DC_SWITCHING_RL_QIDS = {"EE-114-02-3"}


def _load_js_binding(path: Path, binding: str) -> Any:
    script = r"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const sandbox = { console: { log() {} } };
vm.runInNewContext(source + `\nglobalThis.__value = ${process.argv[2]};`, sandbox);
process.stdout.write(JSON.stringify(sandbox.__value));
"""
    completed = subprocess.run(
        ["node", "-e", script, str(path), binding],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _build_model() -> tuple[list[list], dict[str, Any], dict[str, Any]]:
    questions = load_questions_from_bundle(BUNDLE)
    taxonomy = _load_js_binding(BUNDLE, "QUESTION_TAXONOMY_MAP")
    dag = _load_js_binding(DAG_PATH, "KNOWLEDGE_DAG")

    qids = {row[0] for row in questions}
    if set(taxonomy) != qids:
        missing = sorted(qids - set(taxonomy))
        extra = sorted(set(taxonomy) - qids)
        raise ValueError(f"taxonomy mismatch: missing={missing}, extra={extra}")

    for row in questions:
        qid, subject = row[0], row[1]
        chapter = taxonomy[qid].get("primaryChapter")
        if chapter not in dag:
            raise ValueError(f"{qid}: unknown primary chapter {chapter!r}")
        if dag[chapter].get("subject") != subject:
            raise ValueError(f"{qid}: chapter {chapter!r} belongs to another subject")

    return questions, taxonomy, dag


def build_report() -> str:
    questions, taxonomy, dag = _build_model()
    years = sorted({row[2] for row in questions}, reverse=True)
    subject_totals = Counter(row[1] for row in questions)
    chapter_questions: dict[str, list[list]] = defaultdict(list)
    for row in questions:
        chapter_questions[taxonomy[row[0]]["primaryChapter"]].append(row)

    lines = [
        "# 電機工程技師 104–114 年客觀章節覆蓋統計",
        "",
        "> 本頁由 `scripts/analyze_topic_frequency.py` 直接依題庫重建；它是歷史覆蓋證據，不是未來命中率預測。",
        "> 若只想直接開始，依 [24 個核心時段](../docs/上榜預設24時段_核心題路徑.md) 順序練習即可，不需要回填進度。",
        "",
        "## 統計與考試規則",
        "",
        f"- 資料範圍：民國 {min(years)}–{max(years)} 年，共 {len(years)} 個年度、{len(questions)} 道大題。",
        "- 分類口徑：每題只計入 `QUESTION_TAXONOMY_MAP.primaryChapter` 指定的一個主章節。",
        "- 排序口徑：先比出題年度數，再比題數，最後依章節名稱排序；避免同一年多題過度放大單一章節。",
        "- 百分比口徑：章節題數 ÷ 該科實際題數。不同年度的每科題數不一定相同。",
        "- 用途限制：覆蓋率只決定複習先後，不代表下一年必考、保證得分或可以放棄未列章節。",
        "- 現行及格規則（2026-09-22 查核）：一般全科為 6 科，總成績以各科平均計算，原則上滿 60 分為及格；任一科 0 分不予及格。若及格人數未達全程到考人數 16%，另依排名前 16%、總成績至少 50 分且無任一科 0 分等規定辦理；缺考科目視為 0 分。來源：[現行《專門職業及技術人員高等考試技師考試規則》第 10 條](https://law.exam.gov.tw/LawContent.aspx?id=FL016893)。",
        "",
        "## 六科總覽",
        "",
        "| 科目 | 實際題數 | 年度數 | 前 2 章題數占比 | 前 3 章題數占比 | 固定路徑 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]

    ranked_by_subject: dict[str, list[tuple[str, list[list]]]] = {}
    for subject in SUBJECT_NAMES:
        ranked = sorted(
            (
                (chapter_id, rows)
                for chapter_id, rows in chapter_questions.items()
                if dag[chapter_id]["subject"] == subject
            ),
            key=lambda item: (
                -len({row[2] for row in item[1]}),
                -len(item[1]),
                dag[item[0]]["name"],
            ),
        )
        ranked_by_subject[subject] = ranked
        total = subject_totals[subject]
        top2 = sum(len(rows) for _, rows in ranked[:2]) / total * 100
        top3 = sum(len(rows) for _, rows in ranked[:3]) / total * 100
        lines.append(
            f"| {subject} {SUBJECT_NAMES[subject]} | {total} | {len(years)} | "
            f"{top2:.1f}% | {top3:.1f}% | [24 時段](../docs/上榜預設24時段_核心題路徑.md) |"
        )

    lines.extend(
        [
            "",
            "## 各科優先章節",
            "",
            "下列每科列出前 5 個主章節，只用於安排先後順序。公式、列式與驗算一律以連結的已驗證題解為準。",
        ]
    )

    for subject, subject_name in SUBJECT_NAMES.items():
        total = subject_totals[subject]
        lines.extend(
            [
                "",
                f"### {subject} {subject_name}",
                "",
                f"本科實際收錄 {total} 題。",
                "",
                "| 排名 | 主章節 | 題數 | 覆蓋年度 | 本科題數占比 |",
                "| ---: | --- | ---: | --- | ---: |",
            ]
        )
        for rank, (chapter_id, rows) in enumerate(ranked_by_subject[subject][:5], start=1):
            chapter = dag[chapter_id]
            covered_years = sorted({row[2] for row in rows}, reverse=True)
            year_text = "、".join(str(year) for year in covered_years)
            pct = len(rows) / total * 100
            lines.append(
                f"| {rank} | {chapter['name']} | {len(rows)} | "
                f"{len(covered_years)} 年（{year_text}） | {pct:.1f}% |"
            )
        if subject == "02":
            dc_dc_rows = chapter_questions["el-pe-buck-boost"]
            dc_dc_qids = {row[0] for row in dc_dc_rows}
            if dc_dc_qids != DC_DC_CONVERTER_QIDS | DC_DC_SWITCHING_RL_QIDS:
                raise ValueError("electronics DC-DC subtopic register is stale")
            converter_years = {row[2] for row in dc_dc_rows if row[0] in DC_DC_CONVERTER_QIDS}
            lines.append("")
            lines.append(
                f"註：第 2 名的廣義開關電力電子分類節點共 {len(dc_dc_qids)} 題／{len({row[2] for row in dc_dc_rows})} 年；"
                f"其中真正 DC–DC 轉換器 {len(DC_DC_CONVERTER_QIDS)} 題／{len(converter_years)} 年，"
                "另 1 題為 114 年開關 RL 暫態。不可把整個節點數字當作 buck-boost 題型命中率。"
            )
        if subject == "06":
            quality_qids = {row[0] for row in chapter_questions["dist-harmonics-mitigation"]}
            if quality_qids != DIST_FLICKER_QIDS | DIST_HARMONIC_QIDS:
                raise ValueError("industrial power-quality subtopic register is stale")
            lines.append("")
            lines.append(
                f"註：第 2 名是廣義電力品質統計，共 {len(quality_qids)} 題；其中電弧爐電壓閃爍／變動 {len(DIST_FLICKER_QIDS)} 題、諧波／共振 {len(DIST_HARMONIC_QIDS)} 題。這不表示單獨的諧波方法覆蓋 6 個年度。"
            )

    lines.extend(
        [
            "",
            "## 被動執行順序",
            "",
            "1. 先完成 [24 個核心時段](../docs/上榜預設24時段_核心題路徑.md)：每科前 2 個高年度覆蓋章節，走母題 → 同型題 → 變式題。",
            "2. 用 [六科 12 題混合橋接](../docs/上榜混合橋接_六科12題.md) 拿掉章節提示重做變式題。",
            "3. 接著完成 [114 年六科計時模考](../docs/上榜被動模考_114年六科執行包.md)。",
            "4. 再完成 [108 年六科被動複測](../docs/上榜被動複測_108年六科執行包.md)。",
            "5. 失分題直接用 [59 題錯因修復索引](../docs/上榜錯因修復索引_114-108.md) 重寫，不要求把結果輸入專案。",
            "",
            "更細的前 3 章與母題連結見 [核心母題候選表](../docs/上榜核心母題候選_104-114年.md)。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="return non-zero when the committed report is stale",
    )
    args = parser.parse_args()
    expected = build_report()

    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if actual != expected:
            print(f"stale generated report: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"current: {OUTPUT.relative_to(ROOT)}")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"generated: {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
