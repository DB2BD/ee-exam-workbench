<!-- SPECTRA:START v1.3.0 -->

# Spectra Instructions

This project uses Spectra for Spec-Driven Development(SDD). Specs live in `docs/spectra/specs/`, change proposals in `docs/spectra/changes/`.

## Use `$spectra-*` skills when:

- An explicitly requested Spectra decision needs structure → `$spectra-discuss`
- User explicitly requests a Spectra change proposal → `$spectra-propose`
- Continue tasks for an identified change → `$spectra-apply`
- Update requirements or plans for an identified change → `$spectra-ingest`
- Check implementation matches artifacts → `$spectra-verify`
- Review implementation quality and logic issues → `$spectra-review`
- Analyze artifact consistency before coding → `$spectra-analyze`
- Audit security sharp edges → `$spectra-audit`
- Check stale changes before resuming → `$spectra-drift`
- Debug a concrete bug systematically → `$spectra-debug`
- Implementation is done → `$spectra-archive`
- Commit only files related to a specific change → `$spectra-commit`

Explicit skill invocation takes precedence. Apply existing authorization within its unchanged scope.

## Workflow

discuss? → propose → apply ⇄ ingest → verify / review → archive

- `discuss` is optional — skip if requirements are clear
- Requirements change mid-work? Plan mode (`/plan`) → `ingest` → resume `apply`

## Parked Changes

Changes can be parked（暫存）— temporarily moved out of `docs/spectra/changes/`. Parked changes won't appear in `spectra list` but can be found with `spectra list --parked`. To restore: `spectra unpark <name>`. The `$spectra-apply` and `$spectra-ingest` skills disclose parking and restore when the named operation is already explicitly requested; respect a known refusal, otherwise ask for missing authorization.

<!-- SPECTRA:END -->

# Repository Agent Instructions & Collaboration Contract

本文件是本 Repository 的通用協作規範；內容以目前可執行的程式、資料編譯器與測試為準。若本文件與程式碼或 `CONTEXT.md` 不一致，先修正文件或提出差異，不得把過時描述當成現況。

## 1. 先讀文件，再修改

開始任何跨檔案工作前，依序閱讀：

1. `CONTEXT.md`：領域語言、資料庫邊界與不可變量。
2. `docs/adr/`：已採用的架構決策；只讀與本次修改有關的 ADR。
3. 對應的 `AGENT-SOLVE.md`、`AGENT-SPEC.md`、`AGENT-CODE.md`。
4. 目標程式、資料來源與現有測試。

## 2. 目前 Repository 架構

### A. 電機工程技師（PE／EE）題庫

- 原始題目：`依考科分類/`、`依年度分類/`。
- 題解與考點：`📝 個人題解與錯題本/`、`🧠 核心考點知識庫/`。
- 來源與稽核資料：`data/pe-question-crops.json`、`data/pe-solution-audit.json`、`data/taxonomy/`。
- 編譯器：`scripts/compile_dashboard_database.py`。
- 生成物：`dashboard-data.js`、`solutions-bundle.js`。
- 現況：321 題；目前稽核快照 256 題，其中 `verified` 239、`reference_book_verified` 15、`needs_manual_review` 2。

### B. 國考同級參考題庫（GK）

- 原始題目：`依考科分類/🏛️_國考同級參考題庫/`。
- 題解：`📝 個人題解與錯題本/🏛️_國考同級題解/`。
- 來源清單：`data/moex-national-exams.json`、`data/moex-question-crops.json`。
- 編譯器：`scripts/compile_national_exams.py`。
- 生成物：`national-exams-data.js`、`national-solutions-bundle.js`。
- 現況：161 筆（101 道申論題、60 道工程數學測驗題）。GK 生成物與 PE 生成物互相隔離。

### C. 執行期、建置與發布

- `src/` 是前端原始模組；`scripts/build_workbench.py` 將模組、資料與本地函式庫編入 `index.html`。
- `index.html` 以靜態檔案執行，支援本機 `file://` 與 GitHub Pages；目前沒有執行期後端。
- `.github/workflows/deploy-pages.yml` 負責建置、測試與 GitHub Pages 發布。
- `dashboard-data.js`、`solutions-bundle.js`、`national-exams-data.js`、`national-solutions-bundle.js` 都是生成檔，應修改來源與編譯器，不應手改生成內容。

目前主工作台不包含澳洲求職雷達。倉庫中的相關舊檔或 workflow 不屬於本題庫現行核心，除非使用者另行指定，不得把它們列為目前產品功能，也不要為了本次文件同步刪除歷史檔案。

## 3. 內容與資料不變量

1. 題目必須保留穩定 QID、官方來源、原題裁切圖／PDF 頁碼與 provenance；不以題解反推原題。
2. PE 與 GK 的資料庫、編譯器、題解 bundle 必須維持隔離。
3. `reference_book_verified` 表示「已依參考書核對」，不等於官方標準答案；有出題疑義或證據不足時保留 `needs_manual_review`，並在詳解說明條件與疑點。
4. 題解需保留可追溯的公式、單位、分支條件、驗算與題源；不得用空泛佔位文字冒充完成。
5. `src/domain/questionRecord.js`、`scripts/question_schema.py` 與各編譯器的欄位契約須同步更新；狀態、欄位順序或 bundle 格式變更必須有測試。
6. 使用者偏好使用繁體中文；文件、介面文案與回報不得改用簡體中文。

## 4. 解題、驗證與診斷紀律

- Solver 負責建模、推導與數值計算；Verifier 以獨立方法進行逆向代入、KCL/KVL、功率守恆、極限或單位檢查。
- 發現 bug 時遵循：最小復現 → 假說 → 最小探針 → 原子修復 → 回歸測試。
- 新增或修正程式契約時遵循 red → green → refactor；至少補一個對外行為測試。
- `python3 scripts/health_check_codebase.py` 的分數應如實回報，不得為了達成 100/100 而隱藏人工複核佇列或刪除證據。

## 5. 變更、檢核與發布流程

內容或程式修改後，依需要執行：

```bash
python3 scripts/audit_pe_solutions.py --write
python3 scripts/compile_dashboard_database.py
python3 scripts/compile_national_exams.py
python3 scripts/build_workbench.py
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
python3 scripts/verify_slicing_and_links.py
python3 scripts/health_check_codebase.py
git diff --check
```

報告中要區分「已通過自動檢核」、「仍需人工判定」與「尚未驗證」。提交前檢查生成檔、README、發布紀錄與文件索引是否一致。向 GitHub `push`、發布頁面或發送外部訊息前，必須取得使用者對明確目的地與內容的確認。

使用者明確要求「進版／發布」時，依 `AGENT-CODE.md` 的「版本與發版 Tag」規則同步處理版次、發版紀錄、README、Tag 與遠端驗證；單純修正或推送未獲發布指令時，不自行建立新 Tag。

## 6. 跨 Agent 交接

裁剪程式、效能比較、建立工作樹或瀏覽器除錯時，先讀 `docs/QA_WORKFLOW.md`，依其命令建立基線與可重跑的 QA 證據。

交接時提供：變更檔案、資料來源、編譯／測試命令、測試結果、未解決人工佇列與下一個安全步驟。任務模板位於 `.agents/templates/`；不要把暫時推測寫成已確認事實。
