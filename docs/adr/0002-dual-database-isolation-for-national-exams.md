# ADR-0002: 技師 (PE) 與國考 (GK) 獨立資料庫雙軌隔離架構 (Dual Database Isolation)

* **狀態**：`已接受 (Accepted)`
* **日期**：2026-08-21
* **決策者**：系統架構團隊
* **範圍**：資料庫編譯管線與前端載入策略

---

## 1. 背景與脈絡 (Context)

系統最初僅收錄「電機工程技師（104~114 年共 318 題）」。當需要擴充「公務高考三級（110~114 年共 105 題）」時，若直接修改合併進原有的 `dashboard-data.js` 與 `solutions-bundle.js`，將帶來高度風險：
1. **污染原始核心資料庫**：可能導致 318 題已驗證的技師資料損壞或格式不相容。
2. **耦合度過高**：任一考科擴充或重新編譯都將迫使全量重構。

---

## 2. 決策方案 (Decision)

決定採用 **「零覆蓋、零污染之雙軌獨立資料庫架構（Dual Database Isolation）」**：
1. **技師資料庫（PE）**：保留 `dashboard-data.js` 與 `solutions-bundle.js`，由 `compile_dashboard_database.py` 維護。
2. **國考資料庫（GK）**：建立專屬 `national-exams-data.js` 與 `national-solutions-bundle.js`，由 `compile_national_exams.py` 維護。
3. **前端載入與優先權路由**：在 `index.html` 中預載入兩者，當開啟 `GK-` 題號時，強制優先從 `NATIONAL_BUNDLED_MD` 提取題解，徹底杜絕同名路徑衝突。

---

## 3. 影響與結果 (Consequences)

### 正面效益：
- **零風險擴充**：國考題庫的任何變更 100% 不會影響技師題庫的校驗碼與完整性。
- **清晰模組化**：未來擴充鐵路特考（RW）、地方特考（LOC）或國營事業（SOE）時，可沿用此模式持續橫向擴充。
