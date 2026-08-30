# 其他考科詳解稽核（2026-08-30）

本輪已將同一套稽核管線套用至電路學、電子學（含電力電子）、電機機械、電力系統與工業配電，共 254 題；工程數學另有 64 題獨立 manifest。

- 官方逐題裁切圖仍是題目來源；年度 Markdown 只作為待稽核詳解來源。
- 新增 `scripts/audit_pe_solutions.py` 與 `data/pe-solution-audit.json`。
- 編譯器會依 manifest 顯示 `verified`、`suspected_error`、`needs_manual_review`、`not_attempted`，避免年度模板被誤標為 verified。
- 本輪先將年度題目拆成題號級 canonical 記錄，並以保守狀態阻擋誤導。現有稽核 manifest 統計為 `verified=52`、`needs_manual_review=202`、`not_attempted=0`、`suspected_error=0`。全部 254 題均已具備官方逐題裁切與題號級記錄；其中 202 題仍待 Sol/Luna 獨立重算，未宣稱已校驗。

所有已校驗題目均綁定官方逐題裁切圖、章節分類與標準 LaTeX 推導；本輪由 Luna 追加 24 題獨立重算（電路/電子 9 題、電機機械 5 題、電力系統 5 題、111–113 年電機與電力 5 題）。工程數學目前為 `verified=59`、`needs_manual_review=5`；112 年五題因官方 PDF 與索引整年錯版已全部降級，避免把另一套題目的正確計算套到錯題。初步交叉檢查另發現 104 年電路學第 1 題的年度答案與獨立 KCL 計算不一致（30 V 對 270/7 V），因此維持 `needs_manual_review`；這正是本輪不直接批次標 verified 的原因。工業配電題若缺少可辨識網路參數，也會維持人工複核。

## 來源覆蓋阻擋項

官方裁切 manifest 另列出 3 個目前主索引未呈現的來源槽位：`EE-109-02-3`、`EE-109-02-4`、`EE-112-03-6`。這些槽位已保留題圖與 canonical 暫存檔（或待轉錄），但在題意、章節與詳解完成對照前不直接加入可作答清單，避免把錯位題意或合併裁切誤導成正式題號。此差異已列為下一輪校訂的阻擋項。
