"""Rebuild the optional progress dashboard and canonical year landing pages."""

from pathlib import Path

from build_year_readmes import write_year_readmes


ROOT = Path(__file__).resolve().parents[1]
YEARS = tuple(range(114, 103, -1))
SUBJECTS = (
    ("01_電路學", "電路學"),
    ("02_電子學_含電力電子", "電子學（包括電力電子學）"),
    ("03_工程數學", "工程數學"),
    ("04_電機機械", "電機機械"),
    ("05_電力系統", "電力系統"),
    ("06_工業配電", "工業配電"),
)


def build_optional_dashboard() -> str:
    lines = [
        "# 電機工程技師｜可選備考紀錄（104～114 年）",
        "",
        "> 目標：通過電機工程技師考試；錄取判定請以當年度官方規定為準。",
        "> 本表只供自選留存。固定上榜路徑不等待勾選、分數或任何回填。",
        "",
        "## 固定被動路徑",
        "",
        "1. 先完成 [24 個核心時段](./docs/上榜預設24時段_核心題路徑.md)，不等待弱科分析。",
        "2. 依序完成 [114 年六科基線](./docs/上榜被動模考_114年六科執行包.md)。",
        "3. 再完成 [108 年六科複測](./docs/上榜被動複測_108年六科執行包.md)，以不同試卷比較得分證據。",
        "",
        "## 六科資料入口",
        "",
        "| 科目 | 歷屆份數 | 使用者狀態 | 題庫 | 核心考點 |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for folder, name in SUBJECTS:
        lines.append(
            f"| {name} | 11 | 未由專案推定 | "
            f"[題庫](./依考科分類/{folder}.md) | [核心考點](./🧠%20核心考點知識庫/{folder}/) |"
        )

    lines.extend(
        [
            "",
            "## 66 份試卷自選紀錄",
            "",
            "下表不是前置條件。只有你想自行留存時才在答案紙或本檔標記；空白不會阻擋固定路徑。",
            "",
            "| 年度 | 科目 | 年度入口 | 自選狀態 |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for year in YEARS:
        for folder, name in SUBJECTS:
            lines.append(
                f"| {year} | {name} | [開啟](./依考科分類/{folder}.md#{year}年) | — |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    (ROOT / "📊 備考進度儀表板.md").write_text(build_optional_dashboard(), encoding="utf-8")
    write_year_readmes()


if __name__ == "__main__":
    main()
