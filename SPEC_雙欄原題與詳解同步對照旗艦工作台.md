# 📐 技術規格架構書：雙欄原題與詳解同步對照旗艦工作台 (Split-Screen Solution Workspace)

**檔案識別**：`SPEC-UI-001`  
**建立時間**：2026-08-21  
**遵循規範**：[`CLAUDE.md`](file:///Users/a/技師考試/歷屆試題_104-114年/CLAUDE.md) · [`CLAUDE-SPEC.md`](file:///Users/a/技師考試/歷屆試題_104-114年/CLAUDE-SPEC.md) · [`to-spec`](file:///Users/a/技師考試/歷屆試題_104-114年/.agents/skills/to-spec/SKILL.md)

---

## 🎯 一、問題陳述與核心目標 (Problem Statement & Goals)

### 1.1 現狀痛點
- **分頁跳轉打斷思維**：考生在閱讀 Markdown 詳解時，若需核對考選部官方原題或電路圖，需點擊按鈕跳轉至新分頁，在「試卷 PDF」與「解題推導」之間頻繁切換分頁，嚴重影響刷題流暢度與專注力。
- **圖表與步驟割裂**：題解中的電路單線圖位於內文上方，當步驟推導較長向下滾動時，圖表移出視窗，考生無法對照電路節點編號進行即時計算。

### 1.2 核心目標 (Goals)
1. **雙欄同步對照 (Split-Screen Experience)**：在詳解彈窗內實作左右雙欄架構——**左欄展示官方試卷與原題電路圖，右欄展示步驟式詳細推導**，同屏對照無縫流暢。
2. **自由拖曳調整比例 (Draggable Resizer)**：中間具備滑鼠拖曳分割線，考生可自由調整左右欄寬度（預設 45% : 55%），並持久化記錄於 `localStorage`。
3. **三種視圖一鍵切換 (Layout Modes)**：
   - ◫ **雙欄對照模式 (Split View)**：標準桌面刷題模式。
   - 🗖 **純詳解全寬模式 (Full Solution)**：專注閱讀長篇推導。
   - 🗕 **原題優先模式 (Exam Focused)**：專注審題與手算。
4. **工具卡片頂部常駐 (Sticky Tooling Hub)**：右欄頂部整合折疊式「🧮 fx-127 國考神機秒殺 SOP」與「🤖 AI 批改/觀念剖析 Prompt」一鍵複製功能。
5. **小螢幕自動自適應 (Mobile Responsive)**：寬度小於 900px 時自動降級為頂部 Tab 切換或垂直堆疊。

### 1.3 非目標 (Non-Goals)
- 本次升級不重構底層題目資料庫格式（`dashboard-data.js` 與 `solutions-bundle.js` 格式維持 100% 相容）。

---

## 🏗️ 二、系統架構與組件邊界 (Component Architecture)

```mermaid
graph TD
    A[Modal Overlay #modal-overlay] --> B[Modal Content #modal-content]
    B --> C[頂部全域控制列 .modal-nav-bar]
    C --> C1[上一題 / 下一題按鈕 .modal-nav-btns]
    C --> C2[三態視圖切換器 .view-layout-toggle]
    C --> C3[題目掌握度狀態列 .modal-status-actions]
    C --> C4[關閉視窗 .close-modal]
    
    B --> D[雙欄主工作區 .modal-split-container]
    D --> E[左欄：原題與試卷 .pane-left]
    E --> E1[左欄子分頁：🖼️ 題目與電路圖 / 📄 官方試卷 PDF]
    E --> E2[左欄內容容器 #pane-left-content]
    
    D --> F[拖曳分隔線 .pane-resizer #modal-resizer]
    
    D --> G[右欄：詳細步驟推導 .pane-right]
    G --> G1[頂部輔助工具列：🧮 fx-127 SOP | 🤖 AI Prompt]
    G --> G2[Markdown & KaTeX 推導主體 #pane-right-body]
```

---

## 📐 三、介面規格與狀態管理 (Interface & State Management)

### 3.1 視圖模式狀態機 (Layout State Machine)

```typescript
type ModalLayoutMode = 'split' | 'solution-only' | 'exam-only';

interface ModalState {
  currentQid: string | null;
  layoutMode: ModalLayoutMode;
  splitRatio: number; // 範圍 0.25 ~ 0.75，預設 0.45
  leftTab: 'diagram' | 'pdf';
}
```

### 3.2 核心 DOM 結構規格

```html
<div id="modal-content" class="layout-split">
  <!-- 頂部控制列 -->
  <div class="modal-nav-bar">
    <div class="modal-nav-btns">
      <button class="btn-nav" onclick="navModalQuestion(-1)">← 上一題</button>
      <button class="btn-nav" onclick="navModalQuestion(1)">下一題 →</button>
    </div>

    <!-- 視圖切換控制鈕 -->
    <div class="view-layout-toggle" id="layout-toggle-group">
      <button class="btn-layout on" onclick="setModalLayout('split')" title="雙欄對照 (◫)">◫ 雙欄對照</button>
      <button class="btn-layout" onclick="setModalLayout('solution-only')" title="純詳解 (🗖)">🗖 純詳解</button>
      <button class="btn-layout" onclick="setModalLayout('exam-only')" title="原題優先 (🗕)">🗕 原題優先</button>
    </div>

    <div id="modal-status-actions"></div>
    <button class="close-modal" onclick="closeModalDirect()">✕</button>
  </div>

  <!-- 雙欄工作區 -->
  <div class="modal-split-container" id="modal-split-container">
    <!-- 左欄：原題與圖檔 -->
    <div class="pane-left" id="modal-pane-left">
      <div class="pane-tab-bar">
        <button class="pane-tab on" id="tab-left-diagram" onclick="switchLeftTab('diagram')">🖼️ 題目與電路圖</button>
        <button class="pane-tab" id="tab-left-pdf" onclick="switchLeftTab('pdf')">📄 官方試卷 PDF</button>
      </div>
      <div class="pane-scroll-body" id="left-pane-body"></div>
    </div>

    <!-- 分割調整線 -->
    <div class="pane-resizer" id="modal-resizer" title="左右拖曳調整寬度"></div>

    <!-- 右欄：步驟式詳解 -->
    <div class="pane-right" id="modal-pane-right">
      <div class="quick-tools-bar" id="right-quick-tools">
        <!-- 🧮 fx-127 SOP 提示與 AI 批改一鍵啟動 -->
      </div>
      <div class="pane-scroll-body md-content" id="modal-body"></div>
    </div>
  </div>
</div>
```

---

## ⚡ 四、邊界條件與失敗降級處理 (Edge Cases & Failure Modes)

| 情境 / 異常 | 系統處理機制 |
| :--- | :--- |
| **開啟非考題 Markdown**（如考點頻率分析報告） | 系統偵測 `qid === ''`，自動切換至 `solution-only` 模式，隱藏左欄、拖曳線、上一題／下一題與星號狀態列，展現乾淨全寬閱讀器。 |
| **瀏覽器螢幕寬度 < 900px（平板/手機）** | CSS Media Query 自動強制覆蓋為單欄 Tab 切換模式，隱藏 Resizer，確保小螢幕不破版。 |
| **官方 PDF 載入受瀏覽器阻擋** | 左欄自動切換至備援模式，呈現題目圖片並提供「📄 於新分頁開啟官方 PDF」外部超連結。 |
| **使用者自訂拖曳比例超出合理範圍** | 在滑鼠移動事件中限制拖曳比例在 `25%` 至 `75%` 之間，防止單側被完全擠壓消失。 |

---

## 🧪 五、驗收標準 (Acceptance Criteria)

- [ ] **AC-1**：點選任一考題（如 114年電力系統第2題），彈窗預設以 45%:55% 雙欄呈現，左側顯示原題圖表/PDF，右側顯示詳細步驟推導。
- [ ] **AC-2**：按住中間分割線可流暢左右拖曳調整寬度，釋放後寬度記憶至 `localStorage`。
- [ ] **AC-3**：點擊「◫ 雙欄對照」、「🗖 純詳解」、「🗕 原題優先」能瞬間平滑切換視圖。
- [ ] **AC-4**：左側「🖼️ 題目與電路圖」與「📄 官方試卷 PDF」分頁切換正常。
- [ ] **AC-5**：右側頂部具備「🧮 fx-127 按鍵提示」與「🤖 AI 批改/追問」一鍵複製卡片。
- [ ] **AC-6**：鍵盤快速鍵 `j`（下一題）、`k`（上一題）、`s`（收藏）、`Esc`（關閉）在雙欄模式下維持 100% 靈敏可用。
- [ ] **AC-7**：開啟「📈 考點頻率分析」等非題型文件時，自動呈現全寬純文件模式，無殘留導航鈕。
