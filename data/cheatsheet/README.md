# 失分點速查卡（K6）資料格式

流程：`scripts/build_cheatsheet_sources.py` 產出 `sources.json`（323 份 canonical 的「失分點」、「條件與疑義」，加 30 張條件題作答卡與 15 筆命題疑點）。策展者讀 `sources.json`，每科寫一份 `0X.json`（X = 01..06）。`scripts/build_cheatsheet.py` 驗證後產出 `docs/02_考場策略/失分點速查卡_六科.md` 與 `src/data/cheatsheet.generated.js`。

## 0X.json 格式

```json
{
  "subject": "01",
  "items": [
    {"category": "method_trap", "text": "不超過 80 字的一句話", "qids": ["EE-104-01-1"], "example": true}
  ],
  "assumption_templates": [
    {"situation": "題幹缺什麼（≤60 字）", "how_to_write": "考場怎麼寫假設（≤120 字）", "qids": ["EE-105-01-3"]}
  ]
}
```

| 欄位 | 規則 |
| --- | --- |
| `subject` | `"01"`..`"06"`，須與檔名一致 |
| `items` | 每科最多 22 條（不含 `example`），為了一科一頁 A4 |
| `items[].category` | 下表固定 id 之一 |
| `items[].text` | 不超過 80 字；LaTeX 原樣保留 |
| `items[].qids` | 至少 1 個，每個都必須存在於 `dashboard-data.js` |
| `items[].example` | 選填；`true` 的條目只作格式示範，不進入輸出，也不計入上限 |
| `assumption_templates` | 每科最多 6 條，六科合併成最後一節「缺條件時怎麼寫假設」 |
| `assumption_templates[].qids` | 至少 1 個，同樣須存在 |

## 類別（固定）

| id | 標籤 |
| --- | --- |
| `polarity_direction` | 極性／方向／參考方向 |
| `per_unit_base` | 標么基準換算 |
| `reading_figures_tables` | 讀圖讀表與題幹條件 |
| `approximation_convention` | 近似口徑與教科書慣例 |
| `units_rms_peak` | 單位、有效值／峰值 |
| `method_trap` | 方法選擇陷阱 |
| `calc_check` | 計算與驗算習慣 |

驗證失敗時 `build_cheatsheet.py` 以非零狀態結束。不要手改 `docs/02_考場策略/失分點速查卡_六科.md` 或 `cheatsheet.generated.js`。
