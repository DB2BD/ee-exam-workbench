# 工作台效能與發布基線（2026-09-08）

## 靜態傳輸基線

| 檔案 | 原始大小 | gzip 約略大小 |
| --- | ---: | ---: |
| `index.html` | 431,093 B | 110,318 B |
| `dashboard-data.js` | 408,540 B | 80,324 B |
| `solutions-bundle.js` | 3,324,496 B | 699,510 B |
| `national-exams-data.js` | 227,980 B | 40,862 B |
| `national-solutions-bundle.js` | 1,420,963 B | 197,026 B |

五個啟動檔合計約 5.54 MB（未壓縮）、1.13 MB（gzip、`mtime=0` 推估）。`stage_pages_artifact.py` 目前產出 1,074 個執行期檔案、約 190.6 MiB；內容只保留工作台、四個 bundle、KaTeX／Marked 執行期檔案、字型、官方 PDF 與實際圖片資產，不含 `.git`、測試、來源程式與個人工作文件。

## 尚待真實瀏覽器量測

本次環境的瀏覽器安全政策禁止開啟本機 `file://`，因此未宣稱以下數值已量到：冷／暖快取可開始練習時間、首次開題、切題、長任務及 360／390／768／1280 視窗表現。發布候選版應以隔離資料的本地 HTTP 預覽量測，並另用可支援 `file://` 的瀏覽器人工確認完整離線資料夾。

只有量測證實約 1.13 MB 啟動傳輸或主執行緒解析造成可感延遲時，才評估拆分 bundle；不得以犧牲完整離線能力為代價預先導入網路依賴。

## 可重現命令

```bash
BUILD_VERSION=review-candidate python3 scripts/build_workbench.py
python3 scripts/stage_pages_artifact.py
du -sh _site
```
