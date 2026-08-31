#!/usr/bin/env python3
"""Attach an explicit disposition to every unresolved canonical PE solution.

The audit intentionally keeps genuinely ambiguous questions out of ``verified``.
These fields make the remaining human-review queue actionable instead of leaving
it as an unexplained status:

* ``review_disposition`` — what the current calculation establishes;
* ``review_blocker`` — why a unique official answer is not provable; and
* ``review_action`` — the concrete datum or decision needed to close it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "📝 個人題解與錯題本"

# Keep this table deliberately explicit.  A new manual-review question must be
# classified here (and will be caught by the regression test if it is not).
REVIEWS = {
    "EE-113-02-2": ("conditional_numeric", "missing_parameter", "確認命題採用的熱電壓 V_T；目前保留 V_T=25 mV 分支。"),
    "EE-113-04-4": ("source_conflict_branches", "source_conflict", "確認官方圖示與機械負載提示的基準；目前以圖示每相參數列出兩種啟動電流。"),
    "EE-112-02-1": ("conditional_numeric", "missing_parameter", "確認 V_T 與高頻模型的教材慣例；目前保留有限 beta 與 V_T=25 mV 分支。"),
    "EE-112-05-4": ("impedance_type_branches", "missing_parameter", "確認故障阻抗 0.01 pu 為複數阻抗或純電抗；目前保留兩個臨界清除角分支。"),
    "EE-111-02-3": ("inconsistent_data_branches", "source_conflict", "確認指定增益或平方律參數是否有誤植；目前並列兩組可回代候選值。"),
    "EE-111-02-4": ("parameterized_only", "missing_parameter", "補齊 RC、RF、RL、gm、rpi 與輸出量定義後再數值化回授五量。"),
    "EE-111-04-3": ("curve_interpolation_branches", "graph_estimate", "確認激磁電阻設定與磁化曲線取點／插值規則；目前保留曲線估讀區間。"),
    "EE-111-04-4": ("curve_interpolation_branches", "graph_estimate", "提供高解析 OCC/SCC 曲線或指定插值點後，再鎖定電壓調整率。"),
    "EE-111-05-3": ("frequency_parameterized", "missing_parameter", "確認系統頻率；目前以臺灣常用 60 Hz 參數化清除時間。"),
    "EE-111-06-1": ("graph_estimate", "graph_estimate", "提供高解析 CT 激磁曲線並確認交點讀值；目前僅呈現可回代的估讀範圍。"),
    "EE-111-06-2": ("conditional_numeric", "missing_parameter", "補齊馬達額定 kVA、效率與額定功因，才能唯一化啟動電流與電壓變動率。"),
    "EE-111-06-3": ("motor_rating_branches", "missing_parameter", "確認馬達數量、額定容量與內電勢假設後，再鎖定三相故障貢獻。"),
    "EE-111-06-4": ("code_compliance_branches", "missing_parameter", "補齊導線材質、敷設、環境修正與效率／規範版本；現行表可作交叉檢查，但 8 HP 無精確列值，仍須確認考試年度表。"),
    "EE-110-06-4": ("definition_branches", "official_wording_ambiguity", "確認官方閃爍觀測點與電壓變動率定義，再決定唯一數值。"),
    "EE-110-06-5": ("conditional_numeric", "missing_parameter", "補齊三台馬達效率與功因／額定 MVA，才能唯一化共同基準短路電流。"),
    "EE-109-02-3": ("conduction_mode_branches", "missing_parameter", "確認返馳式轉換器導通模式與電流定義；目前保留 DCM 三角波條件解。"),
    "EE-108-06-2": ("physical_inconsistency", "official_wording_ambiguity", "確認串聯電抗器用途與允許壓降／功因條件；目前指出被動電抗與題意方向矛盾。"),
    "EE-107-06-2": ("rated_current_branches", "missing_parameter", "確認考試年度採用的 100 HP 馬達滿載電流表或銘牌效率；現行表 258-3 的 220 V 列值為 238 A，另保留 250 A 與反算分支。"),
    "EE-106-02-2": ("parameterized_only", "missing_parameter", "補齊 R1、R2、各管 gm/ro 與尾電流源小訊號阻抗後再求唯一閉迴路量。"),
    "EE-106-05-3": ("multiple_power_flow_branches", "model_branch_ambiguity", "若題意採正常穩態，選高電壓分支；目前以 Jacobian 診斷高／低分支並保留題面未指定的低電壓解。"),
    "EE-106-06-2": ("fault_definition_branches", "official_wording_ambiguity", "確認 F 點故障型式、饋線阻抗是否含往返與非對稱觀察時刻。"),
    "EE-105-04-5": ("flux_curve_parameterized", "missing_parameter", "補齊磁化曲線或明示未飽和條件，才能由 If=6 A 唯一決定磁通比。"),
    "EE-104-05-3": ("given_current_vs_recalculation", "source_conflict", "確認 2.5/3.0 kA 是否為直接給定量或需由 X''+XT 反算，並補正常功因／勵磁。"),
    "EE-104-06-1": ("regulation_version_branches", "regulation_version", "確認考試年度台電規章版本、供電地區與契約圖說後再定門檻與責任位置。"),
    "EE-104-06-5": ("power_factor_parameterized", "missing_parameter", "補齊整流器基波功因或額定交流電流定義；目前以 pf=1 條件分支回代。"),
    "EE-112-03-3": ("event_definition_branches", "official_wording_ambiguity", "確認第二事件是恰一發命中且由乙射擊，或以乙的命中占比定義。"),
}

# Optional evidence can narrow a branch without pretending that the official
# crop supplied the missing datum.  Keep the source link in the note so a
# reviewer can reproduce the decision before promoting the question.
REVIEW_EVIDENCE = {
    "EE-107-06-2": (
        "經濟部《用戶用電設備裝置規則》要求馬達導線與保護依表 258-1～258-3 的滿載電流檢核；"
        "現行表 258-3 三相感應電動機 220 V、100 HP 列值為 238 A，但表下注明 60 HP 以上得採製造廠資料，"
        "且考試年度版本可能不同，故僅作官方交叉證據，不能取代題幹缺漏。 "
        "來源：https://law.moea.gov.tw/LawContent.aspx?id=FL011045&kw=E%26M；"
        "https://gazette.nat.gov.tw/EG_FileManager/eguploadpub/eg028166/ch04/type3/gov31/num7/images/BB.pdf"
    ),
    "EE-111-06-4": (
        "經濟部《用戶用電設備裝置規則》馬達滿載電流表 258-3 的現行 220 V 列值為："
        "20 HP=55 A、10 HP=28 A、7.5 HP=21 A；題目為 8 HP，無精確列值，且導線安培容量仍取決於材質、"
        "配管載流導線數、修正係數與規範版本，故只能作交叉檢查。 "
        "來源：https://law.moea.gov.tw/LawContent.aspx?id=FL011045&kw=E%26M；"
        "https://gazette.nat.gov.tw/EG_FileManager/eguploadpub/eg028166/ch04/type3/gov31/num7/images/BB.pdf"
    ),
    "EE-112-05-4": (
        "公開參考解答（2024-07-17 更正）將故障阻抗明寫為 j0.01，支持純電抗分支；"
        "官方裁切仍只寫 0.01 pu，故尚不能單獨視為官方唯一條件。 "
        "來源：https://kentchen1980.pixnet.net/blog/posts/10357120259"
    ),
}


def find_note(qid: str) -> Path:
    matches = list(CANONICAL.glob(f"*/canonical/{qid}.md"))
    if len(matches) != 1:
        raise SystemExit(f"expected one canonical note for {qid}, found {matches}")
    return matches[0]


def update_frontmatter(path: Path, qid: str) -> None:
    disposition, blocker, action = REVIEWS[qid]
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"missing frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise SystemExit(f"unterminated frontmatter: {path}")
    fm = text[4:end]
    # Replace existing generated fields so the script is idempotent.
    for key in ("review_disposition", "review_blocker", "review_action", "review_evidence"):
        fm = re.sub(rf"^{re.escape(key)}:.*$\n?", "", fm, flags=re.M)
    fm = fm.rstrip() + (
        f"\nreview_disposition: {disposition}"
        f"\nreview_blocker: {blocker}"
        f"\nreview_action: {action}"
    )
    evidence = REVIEW_EVIDENCE.get(qid)
    if evidence:
        fm += f"\nreview_evidence: {evidence}"
    path.write_text("---\n" + fm + "\n---\n" + text[end + len("\n---\n"):], encoding="utf-8")


def main() -> None:
    for qid in REVIEWS:
        update_frontmatter(find_note(qid), qid)
    print(f"annotated {len(REVIEWS)} manual-review notes")


if __name__ == "__main__":
    main()
