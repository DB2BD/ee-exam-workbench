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
    "EE-112-02-1": ("conditional_numeric", "missing_parameter", "確認 V_T 或接面溫度；依官方拓撲，0.5 mA 理想電流源供應 I_C+I_B=I_E，有限 beta 分支不得把 I_C 直接設為 0.5 mA。"),
    "EE-111-02-3": ("inconsistent_data_branches", "source_conflict", "確認指定增益或 R_S 是否誤植；保留題面 3.17 mA、R_S=30 Ω 與平方律時增益應為 4.4444，若保留增益 5 則 R_S 應為 26.6667 Ω。"),
    "EE-111-02-4": ("parameterized_only", "missing_parameter", "補齊 RC、RF、RL、gm、rpi 與輸出端口開路定義後，再數值化並聯-串聯回授五量。"),
    "EE-111-04-4": ("curve_interpolation_branches", "graph_estimate", "補齊實際 OCC/SCC 曲線或官方線性插值規則；目前第（一）小題已由相量方程驗證，第（二）、（三）僅保留線性比例條件值。"),
    "EE-111-06-1": ("graph_estimate", "graph_estimate", "開啟官方原卷第 3-1 頁（檔案頁 1）與 source_crop 的 PE_111年_工業配電_Q01.png；人工只需確認兩個交點的有效位數：保留 I_e=0.15~0.25 A、2.2~2.8 A 區間，並確認 I'≥8 A／I'＜8 A 的門檻結論；不得把估讀中心值當精確解析值。"),
    "EE-111-06-2": ("conditional_numeric", "missing_parameter", "補齊馬達額定 kVA、效率與額定功因；目前以 k=η·pf_n 參數化啟動電抗與兩側電壓變動率。"),
    "EE-111-06-3": ("motor_rating_branches", "missing_parameter", "保留官方發電機 25 MW；確認發電機額定 MVA／PF_G 或題目慣例，並以 25 MVA 基準、E''=1 pu 的條件分支回代 A 點電流；另補齊每台馬達額定視在容量（或額定功因／效率）及故障前內電勢後，再鎖定 F 點三相故障貢獻。"),
    "EE-111-06-4": ("code_compliance_branches", "missing_parameter", "開啟官方原卷第 3-2 頁（檔案頁 2）與 source_crop 的 PE_111年_工業配電_Q04.png；確認 111 年適用的歷史安培容量表與導線敷設條件，並補齊 8 HP 滿載電流、導線材質／載流導線數／修正係數後，才可選定線徑與保護規格。"),
    "EE-110-06-4": ("definition_branches", "official_wording_ambiguity", "依圖面 A 點採 1.606162%／0.036720 pu；若命題解答採 B 點則為 19.052%／6.070853 pu，請確認觀測點定義。"),
    "EE-110-06-5": ("conditional_numeric", "missing_parameter", "補齊三台馬達效率與功因／額定 MVA，並確認 K=1.6 是 RMS 非對稱倍率或峰值倍率；目前以各機 k_i=η_i·pf_i 參數化次暫態貢獻與瞬時容量。"),
    "EE-109-02-3": ("conduction_mode_branches", "missing_parameter", "確認返馳式轉換器導通模式與電流定義；目前的三角波條件其實落在 DCM／臨界導通邊界，另保留 CCM 分支。"),
    "EE-108-06-2": ("source_end_PCC_impedance_model", "official_wording_ambiguity", "依官方圖固定 69 kV 電源側 PCC 為首選測定點，並確認電弧爐採額定電流或定阻抗模型；再決定串聯電抗器的設計目標與計算分支。"),
    "EE-107-06-2": ("rated_current_branches", "missing_parameter", "確認考試年度採用的 100 HP 馬達滿載電流表、107 年歷史附件或銘牌效率；現行表 258-3 的 220 V 列值為 238 A，另保留 250 A 與反算分支。"),
    "EE-106-02-2": ("parameterized_only", "missing_parameter", "補齊 R1、R2、各管 gm/ro 與尾電流源小訊號阻抗後再求唯一閉迴路量。"),
    "EE-106-06-2": ("source_per_conductor_line_line_main_model", "official_wording_ambiguity", "依圖面固定 F 為左 110 V 導體對中性點；以每導體阻抗組成完整 380 V 線間往返為首選，並確認題面是否已含往返，以及非對稱電流的觀察時刻／故障相角。"),
    "EE-105-04-5": ("flux_curve_parameterized", "missing_parameter", "補齊磁化曲線或明示未飽和條件，才能由 If=6 A 唯一決定磁通比。"),
    "EE-104-06-5": ("power_factor_parameterized", "missing_parameter", "釐清 500 kW 是整流器 DC 輸出或 AC 側有功輸入，補齊基波功因 pf_1 與效率 η，並明定「額定電流」是 AC 基波、AC 總 RMS 或 DC 額定電流。"),
}

# Optional evidence can narrow a branch without pretending that the official
# crop supplied the missing datum.  Keep the source link in the note so a
# reviewer can reproduce the decision before promoting the question.
REVIEW_EVIDENCE = {
    "EE-113-02-2": (
        "官方裁切圖已確認 α=0.99、I_E=0.5 mA、R_sig=75 Ω、R_C=R_L=12 kΩ 與基極交流接地；"
        "canonical 推導以 T 模型及 R_C∥R_L 回代，V_T=25 mV 得 A_v=47.52 V/V，V_T=25.85 mV 得 46.882399 V/V。"
        "題圖未提供 V_T，故分支差異是可重現的輸入條件缺口。"
        "公開影音與圖像解答均將本題辨識為共基極 T 模型題，僅作方法交叉，未用來補填官方缺漏。"
        "來源：https://kentchen1980.pixnet.net/blog/posts/10357159118；https://www.youtube.com/watch?v=oe_n90CtJcI"
    ),
    "EE-113-04-4": (
        "官方裁切圖逐項讀得 220 V、60 Hz、1120 rpm、Z_1=0.1+j0.25 Ω、Z_2=0.2/s+j0.35 Ω、R_c=60 Ω、X_m=15 Ω；"
        "考選部官方文字另在提示明載機械負載電阻 0.1(1−s)/s，與圖示 0.2/s 不一致；"
        "canonical 已以每相電壓及滑差獨立回代兩模型，故保留來源矛盾而不混用。"
        "來源：https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0711&t=Q"
    ),
    "EE-112-02-1": (
        "官方裁切圖已確認 β=100、I_Q=0.5 mA、C_π=10 pF、C_μ=1 pF、R_s=50 Ω、R_E=0.5 kΩ、R_B=100 kΩ、R_L=1 kΩ；"
        "電流源接在集極節點且基極直流電流經 R_B 返回該節點，故 KCL 給 I_Q=I_C+I_B=I_E。"
        "V_T=25 mV 時 I_C=0.4950495 mA、g_m=19.80198 mS、f_Hπ=668.451 MHz、f_Hμ=160.746 MHz、A_v=9.336153。"
        "題圖未給 V_T，故仍保留 25/25.85/26 mV 分支。"
        "來源：https://yamol.tw/exam-112%E5%B9%B4%2B%2B112%E5%B9%B4%2B%E5%B0%88%E6%8A%80%E9%AB%98%E8%80%83_%E9%9B%BB%E6%A9%9F%E5%B7%A5%E7%A8%8B%E6%8A%80%E5%B8%AB%EF%BC%9A%E9%9B%BB%E5%AD%B8%EF%BC%88%E5%8C%85%E6%8B%AC%E9%9B%BB%E5%8A%9B%E9%9B%BB%E5%AD%B8%EF%BC%89117584-117584.htm；"
        "https://www.scribd.com/document/1031258563/112%E5%B9%B4%E9%9B%BB%E6%A9%9F%E6%8A%80%E5%B8%AB%E9%9B%BB%E5%AD%B8%E8%A7%A3%E7%AD%94"
    ),
    "EE-107-06-2": (
        "經濟部《用戶用電設備裝置規則》要求馬達導線與保護依表 258-1～258-3 的滿載電流檢核；"
        "現行表 258-3 三相感應電動機 220 V、100 HP 列值為 238 A，但表下注明 60 HP 以上得採製造廠資料，"
        "107 年歷史版第 152 條另規定原則上採銘牌全載電流、一般用電動機才得以國家標準值為準；"
        "題圖未附銘牌或 107 年表格附件，故僅作官方交叉證據，不能取代題幹缺漏。"
        "公開題目鏡像逐字確認 100 HP、220 V、120 m 與阻抗數值，但未提供可核對的逐步詳解。 "
        "來源：https://law.moea.gov.tw/LawContentHistory.aspx?hid=50617；"
        "https://law.moea.gov.tw/LawContent.aspx?id=FL011045&kw=E%26M；"
        "https://gazette.nat.gov.tw/EG_FileManager/eguploadpub/eg028166/ch04/type3/gov31/num7/images/BB.pdf；"
        "https://www.scribd.com/document/941350020/107%E5%B9%B4%E5%B7%A5%E6%A5%AD%E9%85%8D%E9%9B%BB"
    ),
    "EE-111-06-4": (
        "官方原卷第 3-2 頁（檔案頁 2）的 source_crop（PE_111年_工業配電_Q04.png）完整包含題幹，但沒有馬達銘牌或安培容量表。111 年適用的歷史規章表 163-7-3 可核對 220 V 三相感應馬達 20 HP=54 A、10 HP=28 A、7.5 HP=22 A；"
        "8 HP 未列值，不能逕自四捨五入成 7.5 HP。現行表 258-3 另列 20 HP=55 A、10 HP=28 A、7.5 HP=21 A，"
        "僅作版本交叉檢查；導線安培容量仍取決於材質、配管載流導線數、修正係數與規範版本。 "
        "來源：https://law.moea.gov.tw/LawContent.aspx?id=FL011045&kw=E%26M；"
        "https://gazette.nat.gov.tw/EG_FileManager/eguploadpub/eg028166/ch04/type3/gov31/num7/images/BB.pdf"
    ),
    "EE-111-02-3": (
        "官方裁切圖同時給 |A_v|=5、I_DS=3.17 mA、μ_nC_ox=200 μA/V²、R_S=30 Ω、R_D=200 Ω，並指定 V_S=V_OV；"
        "由增益反推 g_m=0.100000 S，由平方律與 I_DS 反推 g_m=0.0666667 S，兩者回代結果分別為 5 與 4.444444。"
        "因 V_OV=I_D R_S 時 g_m=2I_D/V_OV=2/R_S，改變 I_D 不能消除矛盾；若保留增益 5，最小修正是 R_S=26.666667 Ω，"
        "此時 g_m=0.075 S、W/L=4436.120。"
    ),
    "EE-111-02-4": (
        "官方裁切圖只提供 Q1 共射、Q2 共集、R_F 跨接回授及 R_L 負載的拓撲，未標示 R_C、R_F、R_L、g_m、r_π 或 β 數值；"
        "輸入端是電流並聯混合、輸出端是電流串聯取樣，拓撲為並聯-串聯（Shunt-Series／Current-Current Feedback）；"
        "canonical 已列出節點 KCL、電流輸入／電流輸出定義及測試源阻抗公式，任何數值答案都必須先補齊這些參數與輸出端口開路定義。"
    ),
    "EE-111-04-4": (
        "官方原卷第 3-3 頁及裁切圖提供額定電壓、電流、功因與 X_s，故電壓調整率 68.6414% 已可由相量方程唯一回代；"
        "該頁只有「由 OCC／SCC 曲線來看」的文字，未附任何曲線或插值點，118.595 A 與 110.264 A 只能是明示線性比例假設下的條件值。"
    ),
    "EE-111-06-1": (
        "官方原卷（代號 01160）第 3-1 頁（檔案頁 1）與 source_crop（PE_111年_工業配電_Q01.png）均含完整曲線的官方裁切圖、等效圖、100/5 變比、Z'=0.082 Ω 及 Z_B=0.8/3.0 Ω；"
        "已轉成共同方程 E'=(10−I_e)(Z'+Z_B)。兩個交點分別估讀 I_e≈0.20 A、2.5 A 並回代 8 A 繼電器門檻；"
        "Z_B=3.0 Ω 交點位於膝點附近，剩餘不確定性是圖解有效位數而非方程或裁切缺漏。"
        "來源：https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0612&t=Q"
    ),
    "EE-111-06-2": (
        "官方裁切圖提供 3.3 kV／69 kV 電壓、短路容量、變壓器阻抗及全壓啟動倍數；canonical 已建立兩側標么壓降公式，"
        "並以 k=η·pf_n 列出 0.80、0.85、0.90、1.00 的敏感度。啟動功因為 0 ≠ 額定運轉功因，題目只給 3000 kW，"
        "不能直接視為 3000 kVA，且未給 η 或額定功因。"
    ),
    "EE-111-06-3": (
        "官方裁切圖明確畫出三個 M 支路，F 位於中間馬達支路前、A 位於發電機／變壓器支路；因此支路數量 N_M=3 已確認。"
        "官方發電機額定逐字為 25 MW，不等於已知 25 MVA；canonical 以題目指定 25 MVA 基準、E_G''=1 pu，並把 PF_G=1 視為條件分支，回代 A 點 21.869 kA。一般式為 I_A''=I_b/(0.12PF_G+0.08)。"
        "三支路均投入且 ηpf=1 得 42.864 kA、ηpf=0.9 得 45.196 kA，另列單一支路敏感度；題目仍未給發電機額定 MVA／PF_G、每台馬達由 6000 kW 換算額定 MVA所需的額定功因／效率或故障前內電勢，故無法鎖定唯一數值。"
    ),
    "EE-110-06-4": (
        "官方裁切圖已確認 69 kV 饋線前的 A 點、主變／爐變與電弧爐串聯阻抗；canonical 對 A 點回代 1.606162% 與 0.036720 pu，"
        "另以 B 點重現年度答案 19.0520% 與 6.070853 pu。差異只來自觀測點定義。"
    ),
    "EE-110-06-5": (
        "官方裁切圖已確認 MVAsc=1500 MVA、F1 故障網路與三台馬達支路；100 MVA 是 canonical 解題時自行選定的共同基準。canonical 以 k_i=η_i·pf_i 建立每台馬達次暫態貢獻，"
        "並以 k=0.80/0.85/0.90/1.00 回代 K 倍容量 24.0672/23.7376/23.4435/22.9411 kA。題圖未給三台 k_i 或額定 MVA，"
        "且未定義 K=1.6 是 RMS 非對稱倍率或峰值倍率，不能在同一解讀內把同一個 K 再乘一次。"
    ),
    "EE-109-02-3": (
        "官方裁切圖已確認 N_p/N_s=4、V_o=24 V、D=0.75、f=1.5 kHz 與 L_p=274.4 μH；"
        "canonical 回算 I_p,max=60 A 且 t_demag=t_off=166.67 μs，故位於 DCM／臨界導通邊界。若題意採 CCM，平均與峰值定義需改寫。"
    ),
    "EE-108-06-2": (
        "官方裁切圖已確認 2500 MVA 電源、69 kV 線路 j0.405 Ω、30 MVA 主變、15 MVA 爐變及 12.5 MVA 電弧爐；"
        "圖示測定點位於 69 kV 電源側，canonical 以 source/PCC 為首選定阻抗分壓（3.0261%、XR=0.403448 pu=1.748 Ω/相），"
        "並分開列出額定電流分支 0.5000%／0.6063%／3.5230% 與線路受端替代值 3.6696%、XR=0.573580 pu=2.485 Ω/相。"
        "負載擾動與電流模型未由題面唯一指定，故不把任一分支升格為官方唯一答案。"
    ),
    "EE-106-02-2": (
        "官方裁切圖只提供 MOSFET 差動／回授拓撲，並以文字要求考慮所有 MOSFET 的 r_o；圖中未提供 V_A、R_1、R_2、各管 g_m、r_o、尾電流源阻抗或輸出端口數值；"
        "canonical 已保留參數化 A_f=A/(1+Aβ) 及測試源阻抗定義。M_2 閘極不取電流，故輸出端所見分壓器負載為 R_1+R_2，而非 R_1∥R_2。"
    ),
    "EE-106-06-2": (
        "官方裁切圖將 F 標在 T2 左側 110 V 導體端、中央中性點接地，且 T2 一次側跨兩相 380 V；"
        "canonical 以每導體阻抗形成完整線間往返為首選，回代 I_sym=9.927 kA、X/R=1.6195，最不利第一峰值約 19.36 kA；"
        "並分開列出全單一路徑 11.318 kA／19.1841 kA／22.49 kA 與僅饋線加倍 10.516 kA 替代分支。剩餘缺口是阻抗是否已含往返，以及故障相角、觀察時刻與系統頻率。"
    ),
    "EE-105-04-5": (
        "官方裁切圖給額定電壓、電樞電阻、額定電流及 If=12→6 A，但沒有磁化曲線；canonical 已推得 E_a1=240 V、E_a2=180 V，"
        "並明示 n_2=1200 rpm 僅在線性未飽和 Φ_2/Φ_1=0.5 假設下成立。"
    ),
    "EE-104-06-5": (
        "官方裁切圖已確認 380 V、250 MVA、2 MVA 變壓器、400/200 kvar 電容器及 6% 電抗器；canonical 以第五次諧波三支路並聯回代 V_5=3.2211 V、"
        "幹線 74.6606 A、A/B 支路 51.5158/25.7579 A，並以同一比例重算 pf_1=0.95 與 η=0.90 的四個輸出。題面只寫新設整流器 500 kW，未說明是 DC 輸出或 AC 側有功輸入，也未給基波功因與效率；"
        "DC 輸出分支反推出的仍是 AC 輸入線電流，並按 1/(η·pf_1) 參數化。題面也未明定 20% 的分母是 AC 基波、AC 總 RMS 或 DC 額定電流。"
    ),
}

# Public, non-primary references discovered during the cross-check.  These
# links are deliberately separate from ``official_source_url``: a public
# worked answer can validate a method or expose a common convention, but it
# must never silently supply a number omitted from the official crop.
PUBLIC_REFERENCES = {
    "EE-112-02-1": (
        "https://www.scribd.com/document/1031258563/112%E5%B9%B4%E9%9B%BB%E6%A9%9F%E6%8A%80%E5%B8%AB%E9%9B%BB%E5%AD%B8%E8%A7%A3%E7%AD%94;"
        "https://yamol.tw/exam-112%E5%B9%B4%2B%2B112%E5%B9%B4%2B%E5%B0%88%E6%8A%80%E9%AB%98%E8%80%83_%E9%9B%BB%E6%A9%9F%E5%B7%A5%E7%A8%8B%E6%8A%80%E5%B8%AB%EF%BC%9A%E9%9B%BB%E5%AD%B8%EF%BC%88%E5%8C%85%E6%8B%AC%E9%9B%BB%E5%8A%9B%E9%9B%BB%E5%AD%B8%EF%BC%89117584-117584.htm"
    ),
    "EE-113-02-2": (
        "https://kentchen1980.pixnet.net/blog/posts/10357159118;"
        "https://www.youtube.com/watch?v=oe_n90CtJcI"
    ),
    "EE-107-06-2": "https://www.scribd.com/document/941350020/107%E5%B9%B4%E5%B7%A5%E6%A5%AD%E9%85%8D%E9%9B%BB",
}

PUBLIC_REFERENCE_NOTES = {
    "EE-112-02-1": "Scribd 為公開逐步解答（採 V_T=25 mV）；阿摩頁面為題目索引。兩者僅支持該假設分支。",
    "EE-113-02-2": "Kentchen 圖像解答與 KENT CHEN 影音解析可交叉確認題型；頁面未提供可引用的完整數值文本。",
    "EE-107-06-2": "Scribd 為公開題目鏡像，非逐步解答；用來核對題幹文字，不取代銘牌／效率缺口。",
}

# Stable official question endpoints discovered during the public cross-check.
# These are question PDFs/text pages (not claims that a public worked answer
# exists); unresolved notes keep their manual status until every quantity can
# be independently reproduced from the stated data.
OFFICIAL_SOURCES = {
    "EE-104-05-3": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=104170&q=1&s=0611&t=Q",
    "EE-105-04-5": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=105170&q=1&s=0610&t=Q",
    "EE-106-02-2": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=106180&q=1&s=0601&t=Q",
    "EE-106-06-2": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=106180&q=1&s=0612&t=Q",
    "EE-107-06-2": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=107180&q=1&s=0612&t=Q",
    "EE-108-06-2": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=108180&q=1&s=0612&t=Q",
    "EE-109-02-3": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=109180&q=1&s=0601&t=Q",
    "EE-110-06-5": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=110180&q=1&s=0612&t=Q",
    "EE-111-02-3": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0601&t=Q",
    "EE-111-02-4": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0601&t=Q",
    "EE-111-04-4": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0610&t=Q",
    "EE-111-06-1": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0612&t=Q",
    "EE-111-06-2": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0612&t=Q",
    "EE-111-06-3": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0612&t=Q",
    "EE-111-06-4": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0612&t=Q",
    "EE-112-02-1": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=112190&q=1&s=0701&t=Q",
    "EE-113-02-2": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0701&t=Q",
    "EE-113-04-4": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0711&t=Q",
    "EE-104-06-5": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=104170&q=1&s=0612&t=Q",
}


def find_note(qid: str) -> Path:
    matches = list(CANONICAL.glob(f"*/canonical/{qid}.md"))
    if len(matches) != 1:
        raise SystemExit(f"expected one canonical note for {qid}, found {matches}")
    return matches[0]


def update_frontmatter(path: Path, qid: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"missing frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise SystemExit(f"unterminated frontmatter: {path}")
    fm = text[4:end]
    # Replace existing generated fields so the script is idempotent.
    for key in (
        "review_disposition", "review_blocker", "review_action", "review_evidence",
        "public_reference_urls", "public_reference_note",
    ):
        fm = re.sub(rf"^{re.escape(key)}:.*$\n?", "", fm, flags=re.M)
    # A question that has since been promoted must not retain stale manual-
    # review metadata.  Keep the explicit REVIEWS entry as an audit breadcrumb,
    # but make the generated note and dashboard reflect the verified state.
    status = re.search(r"^audit_status:\s*(\S+)\s*$", fm, flags=re.M)
    if status and status.group(1) in {"verified", "reference_book_verified"}:
        path.write_text("---\n" + fm.rstrip() + "\n---\n" + text[end + len("\n---\n"):], encoding="utf-8")
        return False

    # Official endpoints are generated from the explicit table above so that
    # every unresolved note has a reproducible primary source.  Replace rather
    # than append to keep reruns idempotent.  Do this only for manual notes;
    # verified notes retain their existing provenance unchanged.
    fm = re.sub(r"^official_source_url:.*$\n?", "", fm, flags=re.M)

    disposition, blocker, action = REVIEWS[qid]
    fm = fm.rstrip() + (
        f"\nreview_disposition: {disposition}"
        f"\nreview_blocker: {blocker}"
        f"\nreview_action: {action}"
    )
    official_url = OFFICIAL_SOURCES.get(qid)
    if official_url:
        fm += f"\nofficial_source_url: {official_url}"
    evidence = REVIEW_EVIDENCE.get(qid)
    if evidence:
        fm += f"\nreview_evidence: {evidence}"
    public_urls = PUBLIC_REFERENCES.get(qid)
    if public_urls:
        fm += f"\npublic_reference_urls: {public_urls}"
    public_note = PUBLIC_REFERENCE_NOTES.get(qid)
    if public_note:
        fm += f"\npublic_reference_note: {public_note}"
    path.write_text("---\n" + fm + "\n---\n" + text[end + len("\n---\n"):], encoding="utf-8")
    return True


def main() -> None:
    annotated = sum(update_frontmatter(find_note(qid), qid) for qid in REVIEWS)
    print(f"annotated {annotated} manual-review notes ({len(REVIEWS) - annotated} verified notes skipped)")


if __name__ == "__main__":
    main()
