# 人工覆核索引

> 產生日期：2026-09-16；此清單只收錄 audit manifest 中 `needs_manual_review` 題目。
> 任何題目在缺參數、圖形估讀或來源衝突未解除前，不得升級為 `verified`。

目前共 **7 題**待人工覆核。
> 公開參考欄僅供方法／題幹交叉比對；若與官方原卷不一致，以官方原卷為準，且不得以二手資料解除缺參數阻擋。

| 題號 | 科目／年度 | 教科書章節 | 阻擋原因 | 收斂所需動作 | 詳解 | 官方來源 | 公開參考 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EE-104-06-5 | 工業配電／104 年第 5 題 | 諧波等效電路與調諧電容器 | missing_parameter | 釐清 500 kW 是整流器 DC 輸出或 AC 側有功輸入，補齊基波功因 pf_1 與效率 η，並明定「額定電流」是 AC 基波、AC 總 RMS 或 DC 額定電流。 | [EE-104-06-5](📝 個人題解與錯題本/06_工業配電/canonical/EE-104-06-5.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=104170&q=1&s=0612&t=Q) | — |
| EE-104-03-3 | 工程數學／104 年第 3 題 | 複變函數／主值積分 | 官方題目未標示 Cauchy 主值；普通廣義積分在 x=0 與 x=4 有實軸極點而發散。 | 取得官方完整解答或閱卷口徑，確認是否將本題解讀為 Cauchy 主值；確認後才能把 -14π/225 標為唯一答案。 | [EE-104-03-3](📝 個人題解與錯題本/03_工程數學/canonical/EE-104-03-3.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=104170&q=1&s=0708&t=Q) | — |
| EE-106-05-3 | 電力系統／106 年第 3 題 | 三匯流排潮流：Ybus、PV/PQ 匯流排與無效功率流向 | 官方題面未指定 Newton 初值、正常運轉條件或電壓穩定分支；同一潮流方程存在高、低電壓兩個正值解。 | 取得官方完整解答或命題口徑確認採用的運轉分支；在此之前保留兩組根及共同可驗證的 P_1 與無效功率方向。 | [EE-106-05-3](📝 個人題解與錯題本/05_電力系統/canonical/EE-106-05-3.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=106180&q=1&s=0611&t=Q) | — |
| EE-111-05-3 | 電力系統／111 年第 3 題 | 暫態穩定度與等面積準則 | 官方逐題裁切圖未提供系統頻率；臨界清除時間依 sqrt(1/f) 變動，不能把外部台灣 60 Hz 背景直接當成題目已給條件。 | 取得官方完整題本或命題／閱卷口徑確認系統頻率；若確認採 60 Hz，再將 0.2704 s 標為條件答案，並保留 0.2704 sqrt(60/f) s 通式。 | [EE-111-05-3](📝 個人題解與錯題本/05_電力系統/canonical/EE-111-05-3.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=111180&q=1&s=0611&t=Q) | — |
| EE-112-05-2 | 電力系統／112 年第 2 題 | Wood, Wollenberg & Sheblé, Power Generation, Operation, and Control, 3rd ed., Ch. 3 — The Economic Dispatch of Thermal Units | capacity_limit_branch_not_uniquely_specified | 明確指定 800 MW 額定容量是否作硬上限，並由命題／閱卷口徑指定第二運轉點是哪一台機組到達上限後，才能選定唯一的 beta、gamma。 | [EE-112-05-2](📝 個人題解與錯題本/05_電力系統/canonical/EE-112-05-2.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=112190&q=1&s=0710&t=Q) | — |
| EE-105-04-5 | 電機機械／105 年第 5 題 | 直流電機 (分激/串激特性與調速) | missing_parameter | 補齊磁化曲線或明示未飽和條件，才能由 If=6 A 唯一決定磁通比。 | [EE-105-04-5](📝 個人題解與錯題本/04_電機機械/canonical/EE-105-04-5.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=105170&q=1&s=0610&t=Q) | — |
| EE-113-04-3 | 電機機械／113 年第 3 題 | 串激直流電動機與分流調速 | 題目未提供串激馬達磁化曲線或未飽和條件；扭矩加倍只能建立磁通與電流的關係，不能由題面唯一推出新電流、轉速與效率。 | 取得官方完整參考解答或命題口徑確認採用線性未飽和模型；若確認，再把 120 A、1762.5 rpm、94.0% 標為該模型下的條件答案。 | [EE-113-04-3](📝 個人題解與錯題本/04_電機機械/canonical/EE-113-04-3.md) | [官方試題](https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=011&code=113190&q=1&s=0711&t=Q) | — |
