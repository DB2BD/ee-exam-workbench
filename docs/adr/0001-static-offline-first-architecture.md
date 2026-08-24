# ADR-0001: 靜態純前端與 100% 離線優先架構 (Static Offline-First Architecture)

* **狀態**：`已接受 (Accepted)`
* **日期**：2026-08-20
* **決策者**：系統架構團隊
* **範圍**：全專案運行時與部署策略

---

## 1. 背景與脈絡 (Context)

考生在圖書館、考場自習室、飛機上或無網路環境時需要高頻刷題與查閱詳解。傳統採用 Node.js/Python 後端伺服器搭配資料庫（如 PostgreSQL/MongoDB）的架構存在以下痛點：
1. **依賴網路**：斷網或伺服器宕機即無法使用。
2. **部署與維護成本**：需租用雲端伺服器與維護 API 存取權限。
3. **載入延遲**：每次點擊題目需進行 API Round-trip 請求。

---

## 2. 決策方案 (Decision)

決定採用 **「極致純前端、零後端（Zero-Backend）、100% 離線優先」** 架構：
1. 將所有考題元資料、Markdown 題解與圖片映射，透過 Python 編譯腳本預先打包成靜態 `.js` 資料庫（`dashboard-data.js`、`solutions-bundle.js`、`national-exams-data.js`、`national-solutions-bundle.js`）。
2. 本機內建離線 KaTeX 與 Marked.js 引擎，開頁 0ms 即時渲染數學公式。
3. 支援直接以本機檔案協議（`file:///`）或 GitHub Pages 靜態託管開啟。

---

## 3. 影響與結果 (Consequences)

### 正面效益：
- **極致速度**：開頁與切換題目延遲均為 0ms（純記憶體操作）。
- **零託管成本**：完全運行於 GitHub Pages 免費靜態託管。
- **高強韌性**：只要下載 repo，斷網環境下全功能依然正常運作。

### 限制與約束：
- 資料庫更新需透過編譯腳本重新產生 `.js` 檔並推播。
- 前端需設計良好的防快取戳記（`?v=...`）避免瀏覽器讀取過期靜態快取。
