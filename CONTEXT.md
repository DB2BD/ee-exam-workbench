# 電機工程技師歷屆試題與詳解工作台 — 專案架構與領域語境

> **版本**：`2.2.0`
> **最後更新**：2026-09-06
> **定位**：以官方原題／裁切圖為來源、以參考書與獨立驗算為核對材料的 PE／GK 靜態雙資料庫工作台。

## 1. 領域語言

| 名稱 | 定義 |
| --- | --- |
| PE／EE | 台灣電機工程技師 104–114 年、6 科、321 題。 |
| GK | 110–114 年國考同級參考題庫，共 161 筆：101 道申論題、60 道工程數學測驗題。 |
| QuestionRecord | 題庫單筆記錄；PE bundle 為 12 欄 tuple，GK bundle 為 18 欄 tuple，程式應透過命名轉換或編譯器契約理解欄位。 |
| Provenance | 題解、官方 PDF、裁切圖、頁碼、SHA-256 與參考書頁碼等來源鏈。 |
| Verification | 題解驗證狀態與專屬題解旗標；目前使用 `verified`、`reference_book_verified`、`needs_manual_review`、`suspected_error`、`not_attempted`。 |
| Workbench | `index.html` 的雙欄介面：左側原題／PDF，右側題解與驗算。 |

`reference_book_verified` 只表示已依參考書核對，並不表示參考書就是官方標準答案。PE 最新稽核快照為 256 題：`verified` 239、`reference_book_verified` 15、`needs_manual_review` 2。

## 2. 來源、編譯與執行期

```text
PE 題目／題解／裁切與稽核資料
  └─ scripts/compile_dashboard_database.py
       └─ dashboard-data.js + solutions-bundle.js

GK 題目／題解／來源與裁切資料
  └─ scripts/compile_national_exams.py
       └─ national-exams-data.js + national-solutions-bundle.js

四個 bundle + src/ + 本地 KaTeX／Marked
  └─ scripts/build_workbench.py
       └─ index.html → file:// 或 GitHub Pages
```

PE 來源主要在 `依考科分類/`、`依年度分類/`、`📝 個人題解與錯題本/`、`🧠 核心考點知識庫/` 與 `data/pe-*`；GK 來源主要在 `依考科分類/🏛️_國考同級參考題庫/`、`📝 個人題解與錯題本/🏛️_國考同級題解/` 與 `data/moex-*`。目前工作台沒有執行期後端，GitHub Pages workflow 會重建並測試靜態頁面。

## 3. 不可逾越的架構規則

1. 官方 PDF／題目裁切圖優先於既有題解；不以答案反推題幹。
2. PE 與 GK 的來源、編譯器、bundle 與前端載入路徑保持隔離。
3. 生成檔不手改；任何資料或欄位變更回到來源、schema、編譯器與測試。
4. 缺參數、圖像模糊、出題疑義與參考書衝突要在題解中明示，不用無證據的唯一答案覆蓋。
5. `src/domain/questionRecord.js`、`scripts/question_schema.py` 與測試的狀態契約必須同步；特別是 `reference_book_verified`。
6. 題解採 Solver／Verifier 分離；Verifier 必須使用獨立驗算方法。
7. localStorage 的刷題狀態與兩個資料庫的題解優先順序不得因重編譯而互相污染。

## 4. 變更後的最小驗收

```bash
python3 scripts/compile_dashboard_database.py
python3 scripts/compile_national_exams.py
python3 scripts/build_workbench.py
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
python3 scripts/verify_slicing_and_links.py
python3 scripts/health_check_codebase.py
git diff --check
```

驗收報告必須分開列出自動通過項目、人工複核佇列與尚未驗證項目；健康分數不是刪除人工判定的理由。
