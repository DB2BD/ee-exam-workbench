# 題庫資料格式與 Metadata 規範

本文件描述目前 PE／GK 雙資料庫的識別碼、來源鏈、序列化欄位、驗證狀態與 KaTeX 規則。實際欄位契約以 `src/domain/questionRecord.js`、`scripts/question_schema.py`、兩個編譯器與測試共同決定。

## 一、QID 與資料邊界

- PE 題目：`EE-[民國年]-[科目代號]-[題號]`，例如 `EE-114-04-1`。
- GK 題目：使用 `GK-...` 識別碼；工程數學測驗題另保留其來源卷／題號識別。
- 科目代號：`01` 電路學、`02` 電子學、`03` 工程數學、`04` 電機機械、`05` 電力系統、`06` 工業配電。
- QID 必須穩定且不可因題解搬移、排序或重新編譯而改變。

## 二、實際序列化契約

### PE `dashboard-data.js`

每筆是 12 欄陣列，由 `src/domain/questionRecord.js` 轉為命名檢視。欄位順序為：

```text
[id, subjectId, year, questionNum, stem, tags, difficulty,
 solutionLink, pdfLink, vstatus, hasDedicated, topic]
```

### GK `national-exams-data.js`

每筆是 18 欄陣列，額外攜帶 GK 的年份／考試分類、來源頁、裁切圖、解答關聯與 provenance。不要直接在 UI 中以數字索引讀取；優先使用 `src/domain/questionRecord.js` 的 PE 命名轉換、GK 編譯器的欄位註解與測試契約。

生成 bundle 的來源與編譯器：

- PE：`依考科分類/`、`依年度分類/`、`📝 個人題解與錯題本/` → `scripts/compile_dashboard_database.py`。
- GK：`依考科分類/🏛️_國考同級參考題庫/`、`📝 個人題解與錯題本/🏛️_國考同級題解/` → `scripts/compile_national_exams.py`。

## 三、題解 frontmatter 與 provenance

逐題題解應能回溯到下列資訊（欄位名稱可依現有檔案慣例，但語意不可遺失）：

```yaml
qid: EE-114-04-1
subject: 電機機械
year: 114
question: 1
status: reference_book_verified
source_pdf: 依考科分類/04_電機機械/114年_電機機械.pdf
source_pages: [1]
source_crop: data/pe-question-crops.json
solution_source: 參考書頁碼或官方／人工核對說明
```

題解不能取代原題來源。圖表、頁碼、PDF 雜湊與裁切清單如已存在，應保留並在編譯時帶入；無法確認的資訊要留空或標註不確定，不得自行補造。

## 四、驗證狀態

正式稽核與題解產製使用下列語意：

- `verified`：已完成推導、獨立驗算，且證據鏈足以支持目前結論。
- `reference_book_verified`：已依參考書解答核對並通過基本一致性檢查；不宣稱參考書等於官方標準答案。
- `needs_manual_review`：題幹、圖片、參考書或不同解法存在尚未排除的差異。
- `suspected_error`：現有答案或題目疑似有錯，必須保留錯誤說明與判斷依據。
- `not_attempted`：尚未完成題解或尚未進行必要驗證。

舊資料可能出現 `pending`、`in_progress`、`ambiguous`、`unavailable` 等執行期狀態；新增內容應逐步遷移到上面的稽核語意，不得把它們誤報成已驗證。

## 五、分類與呈現

- `subjectId`、`tags`、`formulaTags`、`difficulty` 由 `data/taxonomy/` 與現有題庫分類維護。
- 篩選器使用穩定 slug／代號；顯示名稱可調整，但不得破壞 QID、URL 或 localStorage key。
- PE 與 GK 的 localStorage、題解優先順序及編譯輸出必須隔離。

## 六、KaTeX 與答案文字

- 行內公式使用 `$...$`，獨立公式使用 `$$...$$`。
- 矩陣使用 `bmatrix`／`pmatrix`，多行推導使用 `aligned`。
- 數值必須附物理單位；線電壓／相電壓、功因超前／落後、變比方向等分支要明寫。
- 詳解至少包含已知條件、核心公式、逐步推導、易錯點、驗算與結論；若題目有出題疑義，保留條件式答案與人工複核狀態。
