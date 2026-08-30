# ADR-0006：QuestionRecord 命名資料契約與可重現品質閘門

* **狀態**：`已接受 (Accepted)`
* **日期**：2026-08-30
* **範圍**：PE/GK 題目資料、分類、來源溯源與靜態發布管線

## 背景

PE 題目目前以 12 欄位置陣列序列化，GK 題目以 18 欄位置陣列序列化。前端各元件直接使用 `q[0]`、`q[4]`、`q[10]` 等索引，新增欄位或跨考別擴充時容易產生靜默錯位。分類規則、官方來源、裁切資產與 Solver／Verifier 狀態也需要能被獨立追溯。

## 決策

1. 題目以不可變 QID 作為唯一主鍵，採 `examFamily-year-subjectId-questionNumber` 命名。
2. 生成 bundle 維持 PE 12 欄、GK 18 欄的舊序列化格式；前端與新工具透過 `QuestionRecord` 命名檢視與 accessor 讀取。
3. `QuestionRecord` 將識別、內容、taxonomy、solution、provenance 與 verification 語意分層；狀態允許 `verified`、`in_progress`、`pending`、`ambiguous`、`unavailable`。
4. 教科書章節節點使用穩定 slug；題目保留一個主章節與多個次要考點，低信心分類不得靜默歸類。
5. build 版本由 `BUILD_VERSION` 或 `SOURCE_DATE_EPOCH` 決定，不使用本機 wall-clock；GitHub Pages 部署前必須通過 schema、測試與 inline JavaScript 語法閘門。
6. 官方題目裁切與原圖是電氣語意的唯一來源；向量重繪為輔助資產，必須保留溯源與狀態。
7. 複習提取狀態獨立儲存於 `recallState`：L1～L4 連續兩次達標才升級，失敗只退一級；分類器使用 alias 正規化、0.65 信心與 0.15 margin 門檻，低信心題進入人工複核。

## 影響

### 正面效益

- 新增欄位不會要求所有 UI 重新理解位置索引。
- PE/GK 可維持資料庫隔離，同時共享一致的驗證與分類概念。
- 相同 source 在相同 build 版本下可產生相同產物，部署前錯誤會被阻擋。

### 代價與限制

- 短期內必須維護 tuple 序列化與 named view 兩層相容介面。
- 分類與驗證 metadata 需要額外 manifest 與人工覆核流程。
- `pending` 或 `ambiguous` 題目可存在於題庫，但不得宣告為完整驗證題解。

## 驗證命令

```text
BUILD_VERSION=local python3 scripts/build_workbench.py
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
```
