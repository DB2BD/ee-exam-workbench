---
name: au-competency-tracker
description: Persistent career competency mapping skill for aligning engineering project achievements with Engineers Australia (EA) Stage 1/Stage 2 standards.
---

# AU Career Competency Tracker (Hermes Architecture)

本 Skill 負責將使用者的工程經驗、專案實績與歷屆試題解題能力，持續映射並累積至 **Engineers Australia (EA) 16 項能力指標 (PE1.1 ~ PE3.6)**。

## 觸發時機
1. **分析澳洲職缺**：在執行 `au-radar-pipeline` 或評估澳洲重電/電網職缺時。
2. **沉澱工程經歷**：當使用者輸入新的專案成果、變電所設計經驗或系統分析案例時。
3. **撰寫 CDR 報告**：需要產出 Career Episode 或 Summary Statement 時。

## 執行工作流

### 步驟 1：載入目前 EA 能力狀態
讀取記憶庫：
`file:///.agents/memory/career_competency_map.json`

### 步驟 2：能力對齊與證據提取 (Competency Mapping)
根據使用者提供的實例，對齊至以下三大維度：
- **PE1 專業知識基礎 (Knowledge Base)**: PE1.1 理論基礎, PE1.2 數理與電腦工具, PE1.3 領域專業知識。
- **PE2 工程應用能力 (Engineering Application)**: PE2.1 複雜問題求解, PE2.2 工具與規範應用, PE2.3 系統化設計。
- **PE3 專業素養與領導力 (Professional Attributes)**: PE3.1 倫理規範, PE3.2 技術溝通, PE3.6 團隊協作與領導。

### 步驟 3：更新記憶與草稿輸出
- 將新的能力證據紀錄追加至 `career_competency_map.json`。
- 輸出符合 STAR 原則 (Situation, Task, Action, Result) 的 CDR 建議草稿段落。

## 安全與隱私守則
- 遵循 `AGENTS.md` 中立性原則，嚴禁出現特定前雇主或現職企業名稱，統一使用客觀工程術語。
