---
name: exam-memory-evolver
description: Hermes-style persistent memory evolver for tracking exam blindspots and extracting recurring solution patterns into customized skills.
---

# Exam Memory Evolver (Hermes Architecture)

本 Skill 負責維護考生在 6 大考科（電路學、電力系統、電機機械、工數、電子學、工業配電）的**長期思維盲點與解題經驗進化**。

## 觸發時機
1. **解題遇到陷阱**：在推導或驗算歷屆試題時，發現有易錯觀念（例如變壓器接法、拉氏轉換初值條件、轉差率正負號等）。
2. **提煉通用 SOP**：在攻克某一類高頻考點後，需要將解題流程固化為規範或防呆清單。

## 執行工作流

### 步驟 1：檢索既有盲點
在解題或分析前，優先讀取：
`file:///.agents/memory/exam_blindspots.json`

### 步驟 2：記錄新盲點 (Persistent Memory Update)
若在互動中發現新的易錯點，將其追加或更新至對應科目的 `blindspots` 陣列中，格式如下：
```json
{
  "topic": "考點名稱",
  "note": "精確的錯誤原因與防呆提醒",
  "severity": "high | medium | low"
}
```

### 步驟 3：自我進化 (Self-Evolving Skill Extraction)
若某考點在 104-114 年歷屆試題中出現超過 3 次且具有高複雜度（例如：三相不對稱短路計算、凸極同步機功率角推導），應主動提煉解題 SOP 並在 `.agents/skills/` 內建立或更新專屬解題 Skill。

## 安全守則
- 嚴禁直接修改題庫資料庫檔案 (`dashboard-data.js`, `solutions-bundle.js`)。
- 記憶檔案更新必須保持合法 JSON 格式，並經 `test_harness_integrity.py` 測試通過。
