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
    "EE-113-02-2": ("conditional_numeric", "missing_parameter", "確認命題採用的熱電壓 V_T 或溫度；目前列出 25、25.85、26 mV 三個可回代分支。"),
    "EE-113-04-4": ("source_conflict_branches", "source_conflict", "確認官方圖示與機械負載提示的基準；目前以圖示每相參數列出兩種啟動電流。"),
    "EE-112-02-1": ("conditional_numeric", "missing_parameter", "確認 V_T 與高頻模型的教材慣例；目前保留有限 beta 與 V_T=25 mV 分支。"),
    "EE-112-05-4": ("impedance_type_branches", "missing_parameter", "確認故障阻抗 0.01 pu 為複數阻抗或純電抗；目前保留兩個臨界清除角分支。"),
    "EE-111-02-3": ("inconsistent_data_branches", "source_conflict", "確認指定增益或平方律參數是否有誤植；題面 3.17 mA 對應增益 4.4444，指定增益 5 則反推 4.755 mA，兩組候選均保留。"),
    "EE-111-02-4": ("parameterized_only", "missing_parameter", "補齊 RC、RF、RL、gm、rpi 與輸出量定義後再數值化回授五量。"),
    "EE-111-04-3": ("curve_interpolation_branches", "graph_estimate", "確認激磁電阻設定與磁化曲線取點／插值規則；目前保留曲線估讀區間。"),
    "EE-111-04-4": ("curve_interpolation_branches", "graph_estimate", "提供高解析 OCC/SCC 曲線或指定插值點後，再鎖定電壓調整率。"),
    "EE-111-05-3": ("frequency_parameterized", "missing_parameter", "確認系統頻率；目前以臺灣常用 60 Hz 參數化清除時間。"),
    "EE-111-06-1": ("graph_estimate", "graph_estimate", "提供高解析 CT 激磁曲線並確認交點讀值；目前僅呈現可回代的估讀範圍。"),
    "EE-111-06-2": ("conditional_numeric", "missing_parameter", "補齊馬達額定 kVA、效率與額定功因；目前以 k=η·pf_n 參數化啟動電抗與兩側電壓變動率。"),
    "EE-111-06-3": ("motor_rating_branches", "missing_parameter", "確認馬達數量、額定容量與內電勢假設後，再鎖定三相故障貢獻。"),
    "EE-111-06-4": ("code_compliance_branches", "missing_parameter", "補齊導線材質、敷設、環境修正與效率／規範版本；現行表可作交叉檢查，但 8 HP 無精確列值，仍須確認考試年度表。"),
    "EE-110-06-4": ("definition_branches", "official_wording_ambiguity", "依圖面 A 點採 1.606162%／0.036720 pu；若命題解答採 B 點則為 19.052%／6.070853 pu，請確認觀測點定義。"),
    "EE-110-06-5": ("conditional_numeric", "missing_parameter", "補齊三台馬達效率與功因／額定 MVA；目前以各機 k_i=η_i·pf_i 參數化次暫態貢獻與瞬時容量。"),
    "EE-109-02-3": ("conduction_mode_branches", "missing_parameter", "確認返馳式轉換器導通模式與電流定義；目前的三角波條件其實落在 DCM／臨界導通邊界，另保留 CCM 分支。"),
    "EE-108-06-2": ("physical_inconsistency", "official_wording_ambiguity", "確認串聯電抗器用途與允許壓降／功因條件；目前指出被動電抗與題意方向矛盾。"),
    "EE-107-06-2": ("rated_current_branches", "missing_parameter", "確認考試年度採用的 100 HP 馬達滿載電流表或銘牌效率；現行表 258-3 的 220 V 列值為 238 A，另保留 250 A 與反算分支。"),
    "EE-106-02-2": ("parameterized_only", "missing_parameter", "補齊 R1、R2、各管 gm/ro 與尾電流源小訊號阻抗後再求唯一閉迴路量。"),
    "EE-106-05-3": ("multiple_power_flow_branches", "model_branch_ambiguity", "若題意採正常穩態，選高電壓分支；目前以 Jacobian 診斷高／低分支並保留題面未指定的低電壓解。"),
    "EE-106-06-2": ("fault_definition_branches", "official_wording_ambiguity", "確認 F 點故障型式、饋線阻抗是否含往返與非對稱觀察時刻。"),
    "EE-105-04-5": ("flux_curve_parameterized", "missing_parameter", "補齊磁化曲線或明示未飽和條件，才能由 If=6 A 唯一決定磁通比。"),
    "EE-104-05-3": ("given_current_vs_recalculation", "source_conflict", "確認 2.5/3.0 kA 是否為直接給定量或需由 X''+XT 反算，並補正常功因／勵磁。"),
    "EE-104-06-1": ("regulation_version_branches", "regulation_version", "確認考試年度台電規章版本、供電地區與契約圖說後再定門檻與責任位置。"),
    "EE-104-06-5": ("power_factor_parameterized", "missing_parameter", "補齊整流器基波功因或額定交流電流定義；目前以 pf=1 條件分支回代。"),
}

# Optional evidence can narrow a branch without pretending that the official
# crop supplied the missing datum.  Keep the source link in the note so a
# reviewer can reproduce the decision before promoting the question.
REVIEW_EVIDENCE = {
    "EE-113-02-2": (
        "官方裁切圖已確認 α=0.99、I_E=0.5 mA、R_sig=75 Ω、R_C=R_L=12 kΩ 與基極交流接地；"
        "canonical 推導以 T 模型及 R_C∥R_L 回代，V_T=25 mV 得 A_v=47.52 V/V，V_T=25.85 mV 得 46.882399 V/V。"
        "題圖未提供 V_T，故分支差異是可重現的輸入條件缺口。"
    ),
    "EE-113-04-4": (
        "官方裁切圖逐項讀得 220 V、60 Hz、1120 rpm、Z_1=0.1+j0.25 Ω、Z_2=0.2/s+j0.35 Ω、R_c=60 Ω、X_m=15 Ω；"
        "考選部官方文字另在提示明載機械負載電阻 0.1(1−s)/s，與圖示 0.2/s 不一致；"
        "canonical 已以每相電壓及滑差獨立回代兩模型，故保留來源矛盾而不混用。"
        "來源：https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0711&t=Q"
    ),
    "EE-112-02-1": (
        "官方裁切圖已確認 β=100、I_Q=0.5 mA、C_π=10 pF、C_μ=1 pF、R_s=50 Ω、R_E=0.5 kΩ、R_B=100 kΩ、R_L=1 kΩ；"
        "canonical 已分別重算 C_π、C_μ 極點及中頻增益，並把 R_B 納入集極端負載。"
        "唯一未由題圖給定的是 V_T，故保留 25/26 mV 分支。"
    ),
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
    "EE-111-02-3": (
        "官方裁切圖同時給 |A_v|=5、I_DS=3.17 mA、μ_nC_ox=200 μA/V²、R_S=30 Ω、R_D=200 Ω，並指定 V_S=V_OV；"
        "由增益反推 g_m=0.100000 S，由平方律與 I_DS 反推 g_m=0.0666667 S，兩者回代結果分別為 5 與 4.444444。"
        "矛盾可由兩條獨立方程重現，並非計算未完成。"
    ),
    "EE-111-02-4": (
        "官方裁切圖只提供 Q1 共射、Q2 共集、R_F 跨接回授及 R_L 負載的拓撲，未標示 R_C、R_F、R_L、g_m、r_π 或 β 數值；"
        "canonical 已列出電流輸入／電流輸出定義、KCL 及測試源阻抗公式，任何數值答案都必須先補齊這些參數。"
    ),
    "EE-111-04-3": (
        "官方裁切圖包含 1800 rpm 磁化表的離散 (I_f,E_a) 點；canonical 已重算 R_a+R_sr 壓降、無載最大電壓及長分路場電流，"
        "並同時列出最近表格點 1.25 A 與線性插值 1.254 A。缺口是題目未指定曲線取點／插值與 R_fc 設定。"
    ),
    "EE-111-04-4": (
        "官方裁切圖提供額定電壓、電流、功因與 X_s，故電壓調整率 68.6414% 已可由相量方程唯一回代；"
        "但 OCC/SCC 曲線本身未附於裁切圖，118.595 A 與 110.264 A 只能是明示線性比例假設下的條件值。"
    ),
    "EE-111-05-3": (
        "官方裁切圖已確認 H=6.0、P_m=1.0、P_max=2.5 且故障期間 P_e=0；canonical 以等面積準則回代 δ_cr=89.3750°，"
        "並以擺動方程得到 t_cr=0.2704 s（f=60 Hz）。題圖未標系統頻率，時間保留 t_cr=0.2704√(60/f) s。"
    ),
    "EE-111-06-1": (
        "官方 CT 等效圖與 100/5 變比、Z'=0.082 Ω、Z_B=0.8/3.0 Ω 已轉成共同方程 E'=(10−I_e)(Z'+Z_B)；"
        "兩個交點已由曲線估讀並回代繼電器 8 A 門檻，Z_B=3.0 Ω 交點位於膝點附近，精確值受原圖解析度限制。"
    ),
    "EE-111-06-2": (
        "官方裁切圖提供 2 kV／69 kV 電壓、短路容量、變壓器阻抗及全壓啟動倍數；canonical 已建立兩側標么壓降公式，"
        "並以 k=η·pf_n 列出 0.80、0.90、1.00 的敏感度。題目只給 3000 kW，未給 η 或額定功因。"
    ),
    "EE-111-06-3": (
        "官方拓撲確認發電機經變壓器接 3.3 kV 母線，F 位於馬達支路前、A 位於發電機支路；canonical 已分別回代發電機分量與馬達反饋分量。"
        "圖中三個 M 的投入數量及單台額定視在容量未明，故 28.868/29.645/42.864 kA 分支均保留。"
    ),
    "EE-110-06-4": (
        "官方裁切圖已確認 69 kV 饋線前的 A 點、主變／爐變與電弧爐串聯阻抗；canonical 對 A 點回代 1.606162% 與 0.036720 pu，"
        "另以 B 點重現年度答案 19.0520% 與 6.070853 pu。差異只來自觀測點定義。"
    ),
    "EE-110-06-5": (
        "官方裁切圖已確認 100 MVA 基準、F1 故障網路與三台馬達支路；canonical 以 k_i=η_i·pf_i 建立每台馬達次暫態貢獻，"
        "並以 k=0.80/0.90/1.00 回代瞬時容量 24.0672/23.4435/22.9411 kA。題圖未給三台 k_i 或額定 MVA。"
    ),
    "EE-109-02-3": (
        "官方裁切圖已確認 N_p/N_s=4、V_o=24 V、D=0.75、f=1.5 kHz 與 L_p=274.4 μH；"
        "canonical 回算 I_p,max=60 A 且 t_demag=t_off=166.67 μs，故位於 DCM／臨界導通邊界。若題意採 CCM，平均與峰值定義需改寫。"
    ),
    "EE-108-06-2": (
        "官方裁切圖已確認 2500 MVA 電源、69 kV 線路 j0.405 Ω、30 MVA 主變、15 MVA 爐變及 12.5 MVA 電弧爐；"
        "canonical 統一至主變基準並回代 11.4 kV 母線壓降 3.5230%。被動串聯電抗器會增加壓降，與題目改善目標的方向矛盾。"
    ),
    "EE-106-02-2": (
        "官方裁切圖只提供 MOSFET 差動／回授拓撲與 V_A=∞，未提供 R_1、R_2、各管 g_m、r_o、尾電流源阻抗或輸出端口數值；"
        "canonical 已保留參數化 A_f=A/(1+Aβ) 及測試源阻抗定義，避免套用無條件理想運放公式。"
    ),
    "EE-106-05-3": (
        "官方圖的線路電抗與 Bus 2 PV、Bus 3 PQ 條件已重建成 Y_bus，Newton 法得到高／低電壓兩個正值根；"
        "兩根殘差均達數值容許，且 Jacobian 最小奇異值分別 0.59230 與 0.05141。題目未指定運轉分支。"
    ),
    "EE-106-06-2": (
        "官方圖已提供系統、T1、饋線及 T2 半繞組阻抗；canonical 以左 110 V 對中性點故障為主模型，回代 I_sym=11.318 kA、"
        "X/R=1.738 下最不利第一峰值約 22.47 kA，並另列饋線含往返時的敏感度。F 點故障型式與阻抗定義未明。"
    ),
    "EE-105-04-5": (
        "官方裁切圖給額定電壓、電樞電阻、額定電流及 If=12→6 A，但沒有磁化曲線；canonical 已推得 E_a1=240 V、E_a2=180 V，"
        "並明示 n_2=1200 rpm 僅在線性未飽和 Φ_2/Φ_1=0.5 假設下成立。"
    ),
    "EE-104-05-3": (
        "官方裁切圖同時給 X_d''=25%、X_T=15% 及兩部機組 2.5/3.0 kA 直接標示值；canonical 以共同基準檢查後得到 X'' 反算 2.3 kA/機，"
        "並保留直接給定總電流 5.5 kA 與 unity-PF 條件分支。兩組資料不能無聲混合。"
    ),
    "EE-104-06-1": (
        "官方題目是供電方式與責任分界的申論題；canonical 已依台電供電方式章節整理電壓層級、契約容量、地區網路、可靠度及分界點責任。"
        "歷史門檻與分界物理位置仍受考試年度規章、供電地區及契約圖說影響。"
    ),
    "EE-104-06-5": (
        "官方裁切圖已確認 380 V、250 MVA、2 MVA 變壓器、400/200 kvar 電容器及 6% 電抗器；canonical 以第五次諧波三支路並聯回代 V_5=3.2211 V、"
        "幹線 74.6606 A、A/B 支路 51.5158/25.7579 A。整流器基波功因未給，故結果按 1/pf_1 參數化。"
    ),
}


def find_note(qid: str) -> Path:
    matches = list(CANONICAL.glob(f"*/canonical/{qid}.md"))
    if len(matches) != 1:
        raise SystemExit(f"expected one canonical note for {qid}, found {matches}")
    return matches[0]


def update_frontmatter(path: Path, qid: str) -> None:
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

    # A question that has since been promoted must not retain stale manual-
    # review metadata.  Keep the explicit REVIEWS entry as an audit breadcrumb,
    # but make the generated note and dashboard reflect the verified state.
    status = re.search(r"^audit_status:\s*(\S+)\s*$", fm, flags=re.M)
    if status and status.group(1) == "verified":
        path.write_text("---\n" + fm.rstrip() + "\n---\n" + text[end + len("\n---\n"):], encoding="utf-8")
        return

    disposition, blocker, action = REVIEWS[qid]
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
