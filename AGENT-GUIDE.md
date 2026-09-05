# 電機工程技師歷屆試題 AI 解析知識庫 — 協作指引

本文件供 Sol、Luna、Gemini、Codex 與其他 Agent 冷啟動使用。現行產品是「PE 技師題庫」與「GK 國考同級參考題庫」兩套隔離的靜態資料庫，前端由同一個 `index.html` 工作台呈現。

## 一、現況摘要

- PE／EE：104–114 年、6 科、321 題。
- GK：161 筆，包含 101 道申論題與 60 道工程數學測驗題。
- 合計：482 筆題目／題目記錄。
- PE 最新稽核快照：256 題中 `verified` 239、`reference_book_verified` 15、`needs_manual_review` 2。
- `reference_book_verified` 是參考書核對狀態，不宣稱等同官方標準答案。
- 目前沒有執行期後端；資料先由 Python 編譯，再由瀏覽器載入靜態 bundle。

## 二、六大 PE 考科

1. 電路學：交流穩態、暫態、三相、雙埠與拉氏轉換。
2. 電子學（含電力電子）：BJT／MOSFET、小訊號、運算放大器與轉換器。
3. 工程數學：線性代數、ODE、拉氏／傅立葉與複變。
4. 電機機械：變壓器、感應機、同步機、直流機與磁路。
5. 電力系統：故障、對稱成分、潮流、暫態穩定與輸電線。
6. 工業配電：短路容量、功因、諧波、壓降、需量與保護協調。

## 三、文件導覽

| 文件 | 用途 |
| --- | --- |
| `AGENTS.md` | 所有 Agent 共用的工程紀律、資料邊界與發布安全門檻。 |
| `CONTEXT.md` | 領域語言、雙資料庫資料流與不可變量。 |
| `AGENT-SOLVE.md` | 題解撰寫、參考書核對與 Solver／Verifier SOP。 |
| `AGENT-SPEC.md` | QID、QuestionRecord、frontmatter、provenance、狀態與 KaTeX 契約。 |
| `AGENT-CODE.md` | 編譯、建置、測試、稽核與發布 Runbook。 |
| `docs/adr/` | 已採用的架構決策與其理由。 |
| `README.md`、`檔案架構索引表.md` | 對使用者的入口、功能介紹與檔案索引。 |

## 四、雙資料庫資料流

```text
PE sources + crop/audit/taxonomy manifests
        └─ scripts/compile_dashboard_database.py
             └─ dashboard-data.js + solutions-bundle.js

GK sources + national/crop manifests
        └─ scripts/compile_national_exams.py
             └─ national-exams-data.js + national-solutions-bundle.js

四個 bundle + src/ + 本地 KaTeX/Marked
        └─ scripts/build_workbench.py
             └─ index.html → file:// 或 GitHub Pages
```

PE 來源位於 `依考科分類/`、`依年度分類/`、`📝 個人題解與錯題本/`、`🧠 核心考點知識庫/`；GK 來源位於 `依考科分類/🏛️_國考同級參考題庫/` 與 `📝 個人題解與錯題本/🏛️_國考同級題解/`。生成檔不作為手動編輯入口。

## 五、協作規則

1. 原題 PDF／裁切圖與 provenance 優先於既有題解；參考書只能作為核對來源，若與題意或物理檢查衝突，保留兩種解釋並標記疑義。
2. Solver 先獨立推導，Verifier 再用另一種方法驗算；不要由同一段推導自行宣告通過。
3. 題解應有已知條件、公式、逐步計算、單位、陷阱、驗算與結論；需要分支時明確寫出假設。
4. 狀態至少區分 `verified`、`reference_book_verified`、`needs_manual_review`、`suspected_error`、`not_attempted`；不得把人工佇列藏起來。
5. 修改欄位契約先補測試，再更新 `src/domain/questionRecord.js`、schema 與編譯器，最後重建 bundle。
6. 以繁體中文撰寫與回報。

## 六、快速啟動

```bash
python3 scripts/compile_dashboard_database.py
python3 scripts/compile_national_exams.py
python3 scripts/build_workbench.py
python3 scripts/run_all_tests.py
python3 scripts/verify_slicing_and_links.py
```

GitHub Pages 由 `.github/workflows/deploy-pages.yml` 建置；任何 `push` 前都要讓使用者確認明確的 remote、分支與提交內容。
