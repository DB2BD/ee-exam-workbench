# 破題訓練（選用功能）

看題目 2 分鐘內選出題型、寫下第一步，翻答案後對照該題的解題路線（詳解的步驟標題）並自評。這個功能的所有程式、資料與樣式都在這個資料夾，核心程式不直接引用它。

| 檔案 | 用途 |
| --- | --- |
| `feature.json` | 告訴 `scripts/build_workbench.py` 要載入哪些檔案、順序為何 |
| `build.py` | 從 canonical 題解產生 `data.generated.js`（`npm run check` 透過 `scripts/build_features.py` 執行） |
| `data.generated.js` | 323 題的章節、題型與解題路線 |
| `store.js` | 作答紀錄、間隔複習、抽題；向備份註冊 `breakdownDrill` 欄位 |
| `component.js` | 畫面；自行在首頁加入入口按鈕，並向狀態視窗註冊經驗值 |
| `style.css` | 樣式 |

它透過核心的三個通用掛勾接入：

- `registerBackupExtension`（`src/state/sm2Store.js`）：讓破題紀錄能備份與雲端同步。
- `registerHomeStatusExpSource`（`src/components/homeStatus.js`）：讓破題紀錄計入經驗值。
- `ee:data-merged` 事件（`src/state/cloudSync.js`）：雲端同步合併後重繪畫面。

測試在 `tests/test_feature_breakdown_drill.py`；資料夾不存在時整個檔案自動略過。

## 移除

1. 刪除 `src/features/breakdownDrill/` 整個資料夾。
2. 執行 `npm run check` 重新建置（測試檔會自動略過，可一併刪除）。

已存的破題紀錄仍留在瀏覽器的 `EE_EXAM_BREAKDOWN_DRILL_V1`，不影響其他功能。移除後匯出的備份不再含 `breakdownDrill` 欄位；之後若匯入含此欄位的舊備份，該欄位會被忽略。經驗值會少掉破題訓練的部分，其他經驗值不受影響。
