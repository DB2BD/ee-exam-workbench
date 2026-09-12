# 清理、工作樹與瀏覽器驗證

修改執行期、裁剪程式或處理每日練習 bug 時，使用本流程。測試數量下降不是效能改善證據；先確認刪除項目的呼叫者、動態事件入口、CLI 入口與替代驗證。

## 建立可回復工作樹

先執行 `git status --short`、`git worktree list` 與 `git rev-parse HEAD`，記錄基線。已有修改時保留原工作目錄，在獨立分支工作；需要包含未提交修改時逐檔檢查後轉移，不使用強制清理。

```bash
git worktree add -b cleanup/example ../ee-cleanup-example HEAD
cd ../ee-cleanup-example
```

新工作樹不包含原工作目錄的未追蹤檔案及 node_modules。相依套件使用鎖檔重建；不要在不同分支共享可寫 node_modules。交接需列出工作樹絕對路徑、基線 SHA、修改清單、指令結果及是否已合併。已發布 Tag 維持原指向。

## 安裝與單一驗證入口

需要 Python 3、Node.js 20 以上、npm 和 Chromium。Python 題解相關套件見根目錄 requirements.txt，可在獨立虛擬環境安裝。

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci --ignore-scripts
npx --no-install playwright install chromium
npm run qa
git diff --check
```

`npm run check` 建置後執行完整單元／整合測試、真正的 Node 語法解析、482 題離線切片與連結檢核、兩庫圖片稽核及 staging。檢核外部連結格式不代表遠端 URL 可連線。

`npm run qa:browser` 只測已建立的 `_site/`：使用臨時本機埠、獨立瀏覽器 storage、固定抽題亂數，測 PE/GK × 1440/390px。每個組合以實際點擊完成 3 題、四段蓋牌、自評、下一題、重新整理復原及本輪摘要；檢查原圖實際載入、KaTeX 錯誤與 HTTP 錯誤。每次保留 result.json、截圖與 trace.zip 到獨立 `.qa-artifacts/browser-*` 目錄，失敗回傳非零退出碼。固定題組不是全部 482 題的瀏覽器覆蓋，須搭配資料／公式全庫閘門。

## 除錯存取與證據

```bash
QA_HEADED=1 npm run qa:browser
npx --no-install playwright show-trace .qa-artifacts/browser-實際批次/trace-PE-390.zip
```

伺服器只綁定 127.0.0.1 並在結束時關閉，不需要正式站管理員權限、個人瀏覽器資料或全磁碟存取。若 sandbox 阻擋本機埠或 Chromium，僅申請執行 `npm run qa:browser` 的權限；若缺套件或瀏覽器，回報安裝問題，不把跳過當成功。需要人工觀察時使用 headed 模式，不變更系統除錯設定。

## 效能前後比較

```bash
npm run benchmark:lookup -- 7cbf5d9
```

此工具比對指定 Git ref 與目前的每日練習題目查找，確認全部 482 筆結果完全一致、計算物件轉換次數，並報告七批次耗時中位數。這是局部查找微基準，不能宣稱等同整站載入改善。更新清理範圍時先保留新基線 SHA，再改碼；時間數值應連同硬體／執行環境一起解讀。

## 本次裁剪依據

- `scripts/test_page_render.py` 使用過時 DOM ID 與大括號計數，失敗仍 exit 0；正式 build pipeline 測試及 Node 語法閘門已接手。
- `scripts/test_katex_audit.py` 用字元計數猜測公式且不讓失敗阻擋流程；正式 `test_formula_format.py` 已實際解析完整有效題解。
- `dailyPracticeQuestionCrop` 只有單一呼叫者且僅取欄位，已內聯。
- `dailyPracticeAdvance` 為已標明的舊書籤相容防護，保留；不能只因正式 UI 無呼叫便認定可刪。
- CI 改為直接採用語法檢查的非零退出碼，去掉重複的文字 grep 判定。

上述舊腳本可由 Git 基線取回。提交與發布依 AGENT-CODE.md 的發版流程另行處理。
