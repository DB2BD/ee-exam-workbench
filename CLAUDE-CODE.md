# 電機工程技師 知識庫指令集與維護 Runbook (CLAUDE-CODE.md)

本文件提供知識庫維護、資料庫編譯、試題審計與模考產生的完整常用命令清單。

---

## 一、核心建置與編譯指令

### 1. 全自動編譯核心資料庫
掃描所有 Markdown 題庫與題解檔案，重新產生 `dashboard-data.js` 與 `solutions-bundle.js`：
```bash
python3 scripts/compile_dashboard_database.py
```

### 2. 審計試題與題解對齊狀態
檢查所有 66 份考卷共 303+ 道試題之題解覆蓋率與缺少檔案：
```bash
python3 scripts/audit_all_solutions_vs_exams.py
```

### 3. 全量 KaTeX 與 LaTeX 語法檢查
檢測並修復所有 Markdown 文件中的 KaTeX 語法錯誤、轉義符號與非法矩陣排版：
```bash
python3 scripts/test_katex_audit.py
```

### 4. 考點頻率雷達統計更新
重新統計 104 ~ 114 年 6 大考科考點出現頻率與命中率排行榜：
```bash
python3 scripts/analyze_topic_frequency.py
```

---

## 二、題解生成與自動化腳本

| 腳本名稱 | 功能描述 |
| :--- | :--- |
| `scripts/gen_machinery_114.py` ~ `104.py` | 批次生成電機機械各年度滿分詳細題解 |
| `scripts/gen_circuit_114.py` ~ `104.py` | 批次生成電路學各年度滿分詳細題解 |
| `scripts/gen_distribution_114.py` ~ `104.py` | 批次生成工業配電各年度滿分詳細題解 |
| `scripts/embed_diagrams_into_power_solutions.py` | 將原題電路圖檔精確關聯至電力系統題解 |
| `scripts/link_question_specific_diagrams.py` | 將原卷截圖按題號精確裁剪並內嵌至 Markdown |

---

## 三、AI 批改與解題常用對話 Prompt 模板

在 IDE 對話框中，您可以直接使用以下指令與 AI 協同：

### 1. 批改手寫解答
```markdown
@antigravity 幫我批改 EE-114-04-1 的手寫解答：
1. 請對照標準答案，逐小題進行步驟與計算數值核對。
2. 指出任何計算錯誤、符號誤用或單位遺漏。
3. 依國考 25 分給予估計得分與扣分點說明。
4. 提供加分建議與防坑技巧。
```

### 2. 白話觀念深入剖析
```markdown
@antigravity 請針對 EE-112-05-2 (電力系統牛頓-拉夫森法) 進行白話深度剖析：
1. 為什麼需要形成 Jacobian 矩陣？各子矩陣的物理意義是什麼？
2. 快速解耦法 (FDLF) 是做了哪三個關鍵物理假設進行化簡？
3. 考試時遇到這題的 3 分鐘速解破局思維是什麼？
```

### 3. 類似變形考題生成
```markdown
@antigravity 請根據 EE-110-02-1 (Buck-Boost 轉換器) 生成 1 道進階變形題：
1. 修改電路架構（如加入非理想二極體壓降或電感 ESR）。
2. 提供包含已知條件、求算目標、標準詳解與陷阱提醒。
```
