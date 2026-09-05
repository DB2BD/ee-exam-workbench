# 人工覆核索引

> 產生日期：2026-09-05；此清單只收錄 audit manifest 中 `needs_manual_review` 題目。
> 任何題目在缺參數、圖形估讀或來源衝突未解除前，不得升級為 `verified`。

目前共 **10 題**待人工覆核。
> 公開參考欄僅供方法／題幹交叉比對；若與官方原卷不一致，以官方原卷為準，且不得以二手資料解除缺參數阻擋。

| 題號 | 科目／年度 | 教科書章節 | 阻擋原因 | 收斂所需動作 | 詳解 | 官方來源 | 公開參考 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EE-104-06-5 | 工業配電／104 年第 5 題 | 諧波等效電路與調諧電容器 | missing_parameter | 釐清 500 kW 是整流器 DC 輸出或 AC 側有功輸入，補齊基波功因 pf_1 與效率 η，並明定「額定電流」是 AC 基波、AC 總 RMS 或 DC 額定電流。 | [EE-104-06-5](📝 個人題解與錯題本/06_工業配電/canonical/EE-104-06-5.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=104170&q=1&s=0612&t=Q) | — |
| EE-106-02-2 | 電子學（含電力電子）／106 年第 2 題 | MOSFET 差動放大器與負回授 | missing_parameter | 補齊 R1、R2、各管 gm/ro 與尾電流源小訊號阻抗後再求唯一閉迴路量。 | [EE-106-02-2](📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-106-02-2.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=106180&q=1&s=0601&t=Q) | — |
| EE-109-02-3 | 電子學（含電力電子）／109 年第 3 題 | 返馳式轉換器 CCM/DCM 電流與效率 | missing_parameter | 確認返馳式轉換器導通模式與電流定義；目前的三角波條件其實落在 DCM／臨界導通邊界，另保留 CCM 分支。 | [EE-109-02-3](📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-109-02-3.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=109180&q=1&s=0601&t=Q) | — |
| EE-111-02-3 | 電子學（含電力電子）／111 年第 3 題 | MOSFET 共源極源極退化與偏壓設計 | source_conflict | 確認指定增益或 R_S 是否誤植；保留題面 3.17 mA、R_S=30 Ω 與平方律時增益應為 4.4444，若保留增益 5 則 R_S 應為 26.6667 Ω。 | [EE-111-02-3](📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-111-02-3.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0601&t=Q) | — |
| EE-111-02-4 | 電子學（含電力電子）／111 年第 4 題 | 並聯-串聯電流回授放大器與雙極性電晶體小訊號模型 | missing_parameter | 補齊 RC、RF、RL、gm、rpi 與輸出端口開路定義後，再數值化並聯-串聯回授五量。 | [EE-111-02-4](📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-111-02-4.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0601&t=Q) | — |
| EE-112-02-1 | 電子學（含電力電子）／112 年第 1 題 | BJT 共基極放大器與高頻響應 | missing_parameter | 確認 V_T 或接面溫度；依官方拓撲，0.5 mA 理想電流源供應 I_C+I_B=I_E，有限 beta 分支不得把 I_C 直接設為 0.5 mA。 | [EE-112-02-1](📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-112-02-1.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=112190&q=1&s=0701&t=Q) | [來源1](https://www.scribd.com/document/1031258563/112%E5%B9%B4%E9%9B%BB%E6%A9%9F%E6%8A%80%E5%B8%AB%E9%9B%BB%E5%AD%B8%E8%A7%A3%E7%AD%94)、[來源2](https://yamol.tw/exam-112%E5%B9%B4%2B%2B112%E5%B9%B4%2B%E5%B0%88%E6%8A%80%E9%AB%98%E8%80%83_%E9%9B%BB%E6%A9%9F%E5%B7%A5%E7%A8%8B%E6%8A%80%E5%B8%AB%EF%BC%9A%E9%9B%BB%E5%AD%B8%EF%BC%88%E5%8C%85%E6%8B%AC%E9%9B%BB%E5%8A%9B%E9%9B%BB%E5%AD%B8%EF%BC%89117584-117584.htm) |
| EE-113-02-2 | 電子學（含電力電子）／113 年第 2 題 | BJT 共基極放大器與 T 模型 | missing_parameter | 確認命題採用的熱電壓 V_T 或溫度；目前列出 25、25.85、26 mV 三個可回代分支。 | [EE-113-02-2](📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-113-02-2.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0701&t=Q) | [來源1](https://kentchen1980.pixnet.net/blog/posts/10357159118)、[來源2](https://www.youtube.com/watch?v=oe_n90CtJcI) |
| EE-105-04-5 | 電機機械／105 年第 5 題 | 直流電機 (分激/串激特性與調速) | missing_parameter | 補齊磁化曲線或明示未飽和條件，才能由 If=6 A 唯一決定磁通比。 | [EE-105-04-5](📝 個人題解與錯題本/04_電機機械/canonical/EE-105-04-5.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=105170&q=1&s=0610&t=Q) | — |
| EE-111-04-4 | 電機機械／111 年第 4 題 | 同步發電機等效電路與短路比 | graph_estimate | 補齊實際 OCC/SCC 曲線或官方線性插值規則；目前第（一）小題已由相量方程驗證，第（二）、（三）僅保留線性比例條件值。 | [EE-111-04-4](📝 個人題解與錯題本/04_電機機械/canonical/EE-111-04-4.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0610&t=Q) | — |
| EE-113-04-4 | 電機機械／113 年第 4 題 | 三相感應馬達等效電路與轉矩 | source_conflict | 確認官方圖示與機械負載提示的基準；目前以圖示每相參數列出兩種啟動電流。 | [EE-113-04-4](📝 個人題解與錯題本/04_電機機械/canonical/EE-113-04-4.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0711&t=Q) | — |
