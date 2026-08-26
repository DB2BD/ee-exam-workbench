# 🤖 Repository Agent Instructions & Collaboration Contract (AGENTS.md)

> 本文件依據 **Codex × Antigravity 協作架構** 制定，為本 Repository 中所有 AI Agent（包括 Antigravity、Codex、GitHub Copilot、本地模型等）的通用遵循規範。

---

## 1. 核心原則與四大工程紀律 (Core Principles & 4-Pillar Disciplines)

本專案之所有 Agent 行動**強制遵循四大現代工程紀律**：

1. **`grill-with-docs` (領域語境與架構決策優先)**:
   - 任何行動前必須先閱讀 [CONTEXT.md](CONTEXT.md) 與 [docs/adr/](docs/adr/)，遵守專案的領域語言與架構鐵律，杜絕無脈絡之重複發問或偏離架構之實作。
2. **`tdd` (測試驅動與質量關卡)**:
   - 遵循紅-綠-重構循環，實作前必須先寫好或更新 `tests/` 中的單元/整合測試，執行 `python3 scripts/run_all_tests.py` 全綠燈前嚴禁提交代碼。
3. **`diagnose` (5 步科學除錯迴圈)**:
   - 遇到任何 bug 或使用者回饋異常時，嚴禁盲目瞎猜。必須嚴格按照：**1. 觀察極簡復現 ➔ 2. 提出假說 ➔ 3. 最小探針度量 ➔ 4. 原子根因修復 ➔ 5. 迴歸驗證**。
4. **`improve-codebase-architecture` (持續對抗軟體熵增)**:
   - 定期運行 `python3 scripts/health_check_codebase.py` 進行架構體檢，確保全庫維持在 100/100 Pristine 零架構負債狀態。
5. **`solver-verifier-separation` (解題推導與對抗驗證職責嚴格分離)**:
   - 嚴禁「自己解題自己驗證」產生的認知盲區。
   - **Solver Agent（解題推導）**：專注題意建模、公式推導與數值求解。
   - **Verifier Agent（對抗驗證）**：必須以完全獨立視角，採用第二種解法（如逆向代入、能量守恆、極限分析）進行對抗式交叉驗算與格式嚴審。
6. **`pi-hermes-harness` (極簡驗算外骨骼與持久記憶進化)** 🆕:
   - 數值與矩陣計算優先調用 `scripts/tools/math_verifier.py` 本地工具，保證數值計算零幻覺。
   - 解題盲點與澳洲 EA 能力進度持久化於 `.agents/memory/`，嚴禁將記憶寫入前端 bundle 檔案。

---

## 2. 專案雙核心架構 (Repository Dual Core)

本倉庫包含兩大核心子系統，任何 Agent 修改時均不得破壞既有架構：

### 核心 A: 電機技師歷屆試題雙欄對照工作台
- **主頁面**: `index.html`
- **資料庫**: `dashboard-data.js`, `solutions-bundle.js`
- **架構規格書**: `SPEC_雙欄原題與詳解同步對照旗艦工作台.md`
- **編譯腳本**: `scripts/compile_dashboard_database.py`

### 核心 B: 澳洲重電求職情報戰情室 (Australia Job Radar)
- **主頁面**: `australia-job-radar.html`
- **資料庫**: `au-job-radar-data.js` (⚠️ 由 Python 自動產生，禁止手動修改)
- **爬蟲/資料產生器**: `scripts/au_job_radar_crawler.py` (6 大模組)
- **架構規格書**: `SPEC_澳洲重電求職戰情室架構規格書.md`
- **CI/CD 自動排程**: `.github/workflows/job-radar-update.yml` (每日 08:00 AM 台北時間自動爬取)

### 核心 C: 國考同級參考題庫擴充系統 (National Exam Cross-Reference Bank) 🆕
- **擴充資料庫**: `national-exams-data.js`, `national-solutions-bundle.js` (⚠️ 獨立於 Core A，由獨立編譯器產生)
- **獨立編譯器**: `scripts/compile_national_exams.py` (含 SHA-256 零覆蓋安全檢查)
- **試題索引**: `依考科分類/🏛️_國考同級參考題庫/` (獨立目錄，不動既有技師資料)
- **題解筆記**: `📝 個人題解與錯題本/🏛️_國考同級題解/` (獨立目錄)
- **架構規格書**: `SPEC_國考同級參考題庫擴充架構規格書.md`
- **⚠️ 隔離契約**: 任何對 Core C 的操作嚴禁修改 Core A 的 `dashboard-data.js` 或 `solutions-bundle.js`

---

## 3. 內容規範與安全不變量 (Content Invariants)

1. **中立性原則**:
   - 澳洲戰情室及題庫內容面向公開 GitHub Pages，嚴禁出現特定前雇主或現職企業字眼（如「中鼎」、「CTCI」等），統一使用客觀工程/產業用語（如「EPC 重工業」、「LNG 天然氣工程」）。
2. **URL 建構規範**:
   - 澳洲戰情室的所有職缺連結必須透過 `scripts/au_job_radar_crawler.py` 中的 `build_links()` 產生，嚴禁手動寫死失效路徑。
   - LinkedIn GeoID: Perth 必須使用 `101902409`，Brisbane 使用 `101471505`。
   - Indeed AU 必須使用 `au.indeed.com`。
   - Google Jobs 必須攜帶 `&ibp=htl;jobs`。

---

## 4. 跨平台交接格式 (Task / Result Packet Protocol)

當不同 AI Runtime 之間透過 GitHub Issue、PR 或 Markdown 交換任務時，請遵循標準封包格式：

- 任務交辦範本：`.agents/templates/TASK_PACKET.md`
- 成果回報範本：`.agents/templates/RESULT_PACKET.md`
