# 📖 電機工程技師歷屆試題與詳解工作台 — 專案架構與領域語境 (CONTEXT.md)

> **版本**：`2.0.0`  
> **最後更新**：2026-08-24  
> **核心定位**：極致純前端、零後端依賴、100% 離線可用之「電機工程技師（104~114年 318題）與公務高考三級（110~114年 105題）全真雙欄刷題與知識庫儀表板」＋「🇦🇺 澳洲重電工程師求職戰情室」。

---

## 🏛️ 1. 領域通用語言字典 (Ubiquitous Domain Language)

為確保人類工程師與 AI 在協同開發時具備 100% 精準的共同語言，嚴格定義以下核心專有名詞：

| 專有名詞 | 縮寫/標識 | 定義與約束 |
| :--- | :---: | :--- |
| **電機工程技師** | `PE` / `EE` | 台灣專門職業及技術人員高等考試電機工程技師，共 6 大考科（電路、電子、工數、機械、電力、配電），104~114 年共 318 題。 |
| **公務高考三級** | `GK` | 考選部公務人員高等考試三級（電力/電子工程），共 5 大考科，110~114 年共 105 題。 |
| **旗艦雙欄工作台** | `Workbench` | `index.html` 之核心 UI 模式，左欄對照「官方原題圖表 / PDF」，右欄同步渲染「KaTeX 教科書級步驟推導」。 |
| **黃金標準題解** | `Golden Standard` | 題解必須且僅能包含四大區塊：`📌 題目與已知條件`、`💡 核心考點與破題關鍵`、`✏️ 步驟式詳細數學推導`、`🎯 滿分結論與作答要點`。 |
| **5 大維度客觀難度** | `5D Difficulty` | 依據數學複雜度 (25%)、概念抽象度 (25%)、推導步驟相依 (20%)、邊界陷阱 (15%)、分值權重 (15%) 科學量化之 1★~5★ 難度。 |
| **零覆蓋雙軌資料庫** | `Dual-DB` | 技師題庫使用 `dashboard-data.js` + `solutions-bundle.js`；國考題庫使用獨立的 `national-exams-data.js` + `national-solutions-bundle.js`，互不污染。 |

---

## 🏗️ 2. 系統架構與資料流向 (System Architecture & Data Flow)

```
[原始 Markdown / 圖檔 / PDF / 求解器]
   ├── 依考科分類/*.md
   ├── 依年度分類/*.md
   ├── 📝 個人題解與錯題本/*.md
   └── scripts/solvers/gk_*.py
               │
               ▼ (編譯腳本)
   ├── scripts/compile_dashboard_database.py ───► dashboard-data.js + solutions-bundle.js (PE 技師)
   └── scripts/compile_national_exams.py     ───► national-exams-data.js + national-solutions-bundle.js (GK 高考)
               │
               ▼ (純前端單檔預載入)
   ┌─────────────────────────────────────────────────────────────┐
   │ index.html (雙欄工作台 / 搜尋過濾 / KaTeX 即時渲染 / 離線快取) │
   └─────────────────────────────────────────────────────────────┘
               │
               ▼ (GitHub Actions CI/CD)
   [GitHub Pages: https://db2bd.github.io/ee-exam-workbench/]
```

---

## ⚖️ 3. 不可逾越之架構鐵律 (Invariants & Rules)

1. **零後端純靜態原則**：
   - 嚴禁引入任何伺服器端 Node/Python 後端服務執行期依賴。
   - 所有資料必須編譯為靜態 JSON/JS 封裝，開頁即用、0ms 載入、100% 支援本機 `file://` 與 GitHub Pages。
2. **零佔位符原則（No Placeholders）**：
   - 題解中絕對禁止出現「待補」、「待解」、「本題尚未提供詳解」等虛假佔位文字。
   - 每一題必須針對真實題幹進行第一原理步驟推導並計算出具體數值。
3. **資料庫獨立隔離原則**：
   - 編譯國考資料庫（`national-*`）時，嚴禁覆蓋或破壞 PE 技師原始資料庫（`dashboard-data.js`）。
4. **前端優先權原則**：
   - 瀏覽器開啟 `GK-` 題號時，強制優先自 `NATIONAL_BUNDLED_MD` 提取最新題解，避免快取衝突。
