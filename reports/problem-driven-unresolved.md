# 問題驅動知識圖譜 unresolved / manual review

> 這份報告記錄 canonical graph 的完整覆蓋與仍需人工處理的來源；unknown 不會被任意 fallback 節點取代。

## 測量結果

- Legacy DAG 節點：69
- Canonical graph 節點：145
- Legacy DAG 已鏡射為 PE canonical 主題節點：69/69
- 尚未建立 approved canonical question link：0 題
- Link 來源：deterministic 442、manual 23、approved_ai 19
- 現有人工 topic labels：23 筆
- Canonical graph revision：`kg-v1-9b95af550b0b1b9e`

## 處理規則

- unknown QID 保留 unknown 狀態，等待 evidence 與人工 review。
- manual topic labels 保留在既有使用者資料，不由 canonical generator 覆寫。
- PE/GK 題目連結都必須通過 validator 與完整覆蓋 gate；新增來源若證據不足，保留 unknown 並列入人工複核。
