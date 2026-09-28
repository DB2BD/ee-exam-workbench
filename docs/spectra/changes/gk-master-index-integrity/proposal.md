## Why

五科 GK 考科彙編把舊版手寫題目當成官方試題呈現；抽查發現年度、試題代號、題數與題幹均和 repo 內官方來源頁及 PDF 不符。官方 manifest 顯示工程數學 113、114 年在本次選定類科沒有官方題目連結，但同名 ReportLab 替代 PDF 卻放在 `official_pdfs`，未驗證轉錄頁也連到它們；目前國考 bundle 亦會打包 `_unverified_pre_moex` 內容，舊生成器還可能覆寫正式年度原題頁。

## What Changes

* 將五份 GK 考科彙編改成以官方 manifest 與可追溯年度原題頁為依據的索引；可連到現有 repo 題解，但不能在 metadata 不支持時把它宣稱為官方答案或已驗證答案。
* 彙編不得複製舊版硬編碼題幹、代號、題數或配分。工程數學 113、114 年在所選類科的 manifest 狀態是 `not_available_in_selected_exam_class`，只能標示官方原題連結不可用並連回考選部查詢頁；不得把舊轉錄或 ReportLab 替代 PDF 當成官方試題。
* 將兩份無官方 manifest 項目的替代 PDF 從 `data/official_pdfs/gk/` 移到工程數學 `_unverified_pre_moex` 資料夾，保留位元組並修正既有符號連結，讓其不再出現在官方來源目錄。
* 國考 bundle 不再包含 `_unverified_pre_moex` 內的 Markdown、圖片或經符號連結指向隔離區的別名；用 manifest 與 `data/official_pdfs/gk/` 的雙向比對，發現多餘、缺少或雜湊不符的官方 PDF 時必須失敗。
* 彙編產生器不得再依賴舊版 `EXAM_DATA` 模組；若應有的官方來源或連結目標缺失，必須明確報錯。
* 舊題目／題解生成入口（包含旗艦圖表與解答產生器）須可安全匯入，且不得覆寫目前的官方年度來源頁。
* 新增回歸測試，涵蓋五科索引、來源覆蓋、缺少來源的標示、PDF 清單與雜湊、bundle 排除未驗證內容、連結目標與防覆寫保證；確認重建後 23 份正式來源及原題頁均未改變。

## Non-Goals

- 不修改試題、QID、題解計算、驗證狀態或 PE 備考路徑；未驗證題目與 PDF 僅重新分類，不刪除。
- 不宣稱已獨立覆核所有 GK 題解，也不發布官方答案。
- 不修改工作台執行期、GK 資料庫 schema、前端行為或發版流程。

## Impact

- Affected specs: none
- Affected code:
  - Modified: `scripts/build_master_national_subject_files.py`、`scripts/compile_national_exams.py`、會寫入年度原題／題解／PDF 的舊 GK 生成腳本（包括 `scripts/generate_flagship_gk_diagrams_and_solutions.py`）、五份 GK 考科彙編 Markdown、`national-solutions-bundle.js`、兩份未驗證替代 PDF 的位置與專用回歸測試。
  - 來源邊界：目前官方來源 Markdown、`data/moex-national-exams.json` 與 manifest 收錄的本機官方 PDF 僅作唯讀輸入；只重新分類兩份已證實為替代件的 PDF，並保留雜湊與降級理由。
  - 不新增相依套件。
- Compatibility: 不改變工作台功能層級的執行期行為；GK 考科彙編改為正確的導覽索引，舊生成入口則會安全停止，不再覆寫目前資料。
