# -*- coding: utf-8 -*-
"""
build_workbench.py
==================
Production Modular Bundling & Build Pipeline for the EE Exam Workbench.
Compiles src/ styles, state, renderers, components, and data into
a single, 100% offline, zero-backend, zero-dependency index.html.
"""

import os
import re
import datetime

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def read_file(rel_path):
    full_path = os.path.join(WORKSPACE, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()

def build_workbench():
    print("🔨 Building Workbench from modular src/ components...")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # 1. Bundle Styles
    css_files = [
        'src/styles/base.css',
        'src/styles/layout.css',
        'src/styles/components.css',
        'src/styles/modal.css',
        'src/styles/dag-graph.css'
    ]
    bundled_css = "\n\n".join([f"/* === {f} === */\n" + read_file(f) for f in css_files])

    # 2. Bundle Scripts
    js_files = [
        'src/data/knowledge-dag.js',
        'src/state/store.js',
        'src/state/filterStore.js',
        'src/state/sm2Store.js',
        'src/renderers/katexRenderer.js',
        'src/renderers/markdownRenderer.js',
        'src/components/dagTracer.js',
        'src/components/dagGraphViewer.js',
        'src/components/header.js',
        'src/components/questionList.js',
        'src/components/solutionModal.js',
        'src/components/mockExamTimer.js',
        'src/components/topTopics.js',
        'src/main.js'
    ]
    bundled_js = "\n\n".join([f"// === {f} ===\n" + read_file(f) for f in js_files])

    # 3. HTML Shell
    html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>電機工程技師 & 公務高考三級 歷屆試題全真雙欄工作台 (104-114年)</title>

<!-- Offline KaTeX & Marked.js Libraries -->
<link rel="stylesheet" href="./libs/katex.min.css">
<script src="./libs/katex.min.js"></script>
<script src="./libs/auto-render.min.js"></script>
<script src="./libs/marked.min.js"></script>

<!-- Embedded Database & Bundled Markdown Data (100% Offline & Zero-Latency) -->
<script src="./dashboard-data.js?v={timestamp}"></script>
<script src="./solutions-bundle.js?v={timestamp}"></script>
<script src="./national-exams-data.js?v={timestamp}"></script>
<script src="./national-solutions-bundle.js?v={timestamp}"></script>

<style>
{bundled_css}
</style>
</head>

<body>
<div class="container">

  <!-- Header Dashboard -->
  <header>
    <div class="header-top">
      <div class="title-area">
        <h1>⚡ 電機工程技師 & 公務高考三級 歷屆試題工作台</h1>
        <p>104 ~ 114 年 6 大考科 · 423 道試題 · 100% 步驟推導 · 5 大維度難度評級 · 離線極速載入</p>
      </div>
      <div class="header-actions">
        <button onclick="toggleTheme()" class="pill" id="theme-toggle-btn">🌙 暗色模式</button>
        <button onclick="openBackupModal()" class="pill" title="進度備份與 JSON 匯入還原">💾 備份/還原</button>
        <a href="./australia-job-radar.html" target="_blank" class="pill" style="background: var(--accent-light); color: var(--accent-dark); text-decoration: none; font-weight: 700;">
          🇦🇺 澳洲求職戰情室 ➔
        </a>
      </div>
    </div>

    <!-- Category Switcher Tabs (PE 技師 vs GK 高考三級) -->
    <div class="category-switcher">
      <button class="cat-tab on" id="cat-tab-PE" onclick="switchExamCategory('PE')">
        <span>🏆 專技高考：電機工程技師</span>
        <span class="cat-badge">318 題 · 66 卷</span>
      </button>
      <button class="cat-tab" id="cat-tab-GK" onclick="switchExamCategory('GK')">
        <span>🏛️ 公務高考：三級電力/電子</span>
        <span class="cat-badge">105 題 · 25 卷</span>
      </button>
    </div>

    <!-- Statistics Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="label">📚 收錄試題總數</span>
        <span class="val" id="stat-total">423</span>
      </div>
      <div class="stat-card">
        <span class="label">🟢 已掌握題數</span>
        <span class="val" id="stat-mastered" style="color: var(--success);">0</span>
      </div>
      <div class="stat-card">
        <span class="label">🔴 需二刷 (錯題本)</span>
        <span class="val" id="stat-review" style="color: var(--review);">0</span>
      </div>
      <div class="stat-card">
        <span class="label">⚪ 未開始題數</span>
        <span class="val" id="stat-unstarted" style="color: var(--muted);">0</span>
      </div>
      <div class="stat-card">
        <span class="label">⭐ 重點收藏題數</span>
        <span class="val" id="stat-starred" style="color: var(--star);">0</span>
      </div>
      <div class="stat-card">
        <span class="label">📑 考卷總卷數</span>
        <span class="val" id="stat-exams">66</span>
      </div>
    </div>

    <!-- Progress Bar -->
    <div style="margin-top: 18px;">
      <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--muted); font-weight: 600; margin-bottom: 6px;">
        <span>📊 刷題整體掌握度</span>
        <span id="stat-pct" style="color: var(--accent-dark); font-weight: 700;">0%</span>
      </div>
      <div style="height: 10px; background: var(--bg-secondary); border-radius: 9999px; overflow: hidden; display: flex;">
        <div id="bar-mastered" style="width: 0%; background: var(--success); height: 100%; transition: width 0.3s;"></div>
        <div id="bar-review" style="width: 0%; background: var(--review); height: 100%; transition: width 0.3s;"></div>
        <div id="bar-unstarted" style="width: 100%; background: var(--line); height: 100%; transition: width 0.3s;"></div>
      </div>
    </div>
  </header>

  <!-- Main Navigation Tabs -->
  <div class="main-tabs">
    <button class="main-tab-btn active" id="tab-btn-questions" onclick="switchTab('questions')">
      <span>📚 歷屆真題雙欄刷題庫</span>
    </button>
    <button class="main-tab-btn" id="tab-btn-dag" onclick="switchTab('dag')">
      <span>🕸️ 全科知識相依圖譜 (DAG)</span>
    </button>
    <button class="main-tab-btn" id="tab-btn-mock" onclick="switchTab('mock')">
      <span>⏱️ 120 分鐘計時全真模考</span>
    </button>
    <button class="main-tab-btn" id="tab-btn-layers" onclick="switchTab('layers')">
      <span>🧠 7 層認知考點架構</span>
    </button>
    <button class="main-tab-btn" id="tab-btn-stats" onclick="switchTab('stats')">
      <span>🔥 高頻必考命題分析</span>
    </button>
  </div>

  <!-- TAB 1: Questions Explorer -->
  <div class="tab-pane" id="tab-pane-questions" style="display: block;">
    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="search-input" placeholder="搜尋考題關鍵字、公式標籤、觀念、題號..." oninput="renderQuestions()">
      </div>

      <select id="filter-subject" onchange="renderQuestions()">
        <option value="all">所有考科 (6 大考科)</option>
        <option value="01">⚡ 01. 電路學</option>
        <option value="02">🔌 02. 電子學（含電力電子）</option>
        <option value="03">📐 03. 工程數學</option>
        <option value="04">⚙️ 04. 電機機械</option>
        <option value="05">🏢 05. 電力系統</option>
        <option value="06">🏭 06. 工業配電</option>
      </select>

      <select id="filter-year" onchange="renderQuestions()">
        <option value="all">所有年度 (104 ~ 114 年)</option>
        <option value="114">114 年 (最新)</option>
        <option value="113">113 年</option>
        <option value="112">112 年</option>
        <option value="111">111 年</option>
        <option value="110">110 年</option>
        <option value="109">109 年</option>
        <option value="108">108 年</option>
        <option value="107">107 年</option>
        <option value="106">106 年</option>
        <option value="105">105 年</option>
        <option value="104">104 年</option>
      </select>

      <select id="filter-status" onchange="renderQuestions()">
        <option value="all">所有做題狀態</option>
        <option value="1">🟢 已掌握</option>
        <option value="2">🔴 需二刷 (錯題本)</option>
        <option value="0">⚪ 未開始</option>
        <option value="starred">⭐ 僅看收藏</option>
      </select>

      <select id="filter-diff" onchange="renderQuestions()">
        <option value="all">所有難度</option>
        <option value="5">⭐⭐⭐⭐⭐ 5星 地獄壓軸</option>
        <option value="4">⭐⭐⭐⭐ 4星 高難挑戰</option>
        <option value="3">⭐⭐⭐ 3星 中等進階</option>
        <option value="2">⭐⭐ 2星 常規核心</option>
        <option value="1">⭐ 1星 入門基礎</option>
      </select>
    </div>

    <!-- Quick Filter Pills -->
    <div class="pills-bar">
      <span style="font-size: 0.82rem; color: var(--muted); font-weight: 600;">⚡ 快速篩選：</span>
      <button class="pill active" onclick="setQuickFilter('all', this)">全部試題</button>
      <button class="pill" onclick="setQuickFilter('due', this)" title="SM-2 今日待複習或逾期試題">⏳ 今日待複習</button>
      <button class="pill" onclick="setQuickFilter('review', this)">🔴 我的錯題本</button>
      <button class="pill" onclick="setQuickFilter('starred', this)">⭐ 我的收藏</button>
      <button class="pill" onclick="setQuickFilter('top10', this)">🔥 高頻核心考點</button>
      <button class="pill" onclick="setQuickFilter('dedicated', this)">📝 有完整步驟推導</button>
      <span id="filtered-count" style="margin-left: auto; font-size: 0.82rem; color: var(--muted); font-weight: 600;"></span>
    </div>

    <!-- Questions Container -->
    <div id="questions-container" class="qlist"></div>
  </div>

  <!-- TAB 2: Knowledge DAG Graph Visualizer -->
  <div class="tab-pane" id="tab-pane-dag" style="display: none;">
    <div class="dag-visualizer-container">
      <h2 style="color: var(--accent-dark); font-size: 1.3rem; margin-bottom: 6px;">
        🕸️ 6 大考科知識相依有向無環圖 (Knowledge Dependency DAG)
      </h2>
      <p style="font-size: 0.86rem; color: var(--muted); margin-bottom: 20px;">
        全方位梳理電機工程考科的前置觀念流向。每道進階試題皆可沿著拓撲關係逆向溯源，精準擊破前置盲點！
      </p>
      <div id="dag-graph-viewer-content"></div>
    </div>
  </div>

  <!-- TAB 3: Mock Exam System -->
  <div class="tab-pane" id="tab-pane-mock" style="display: none;">
    <div class="mock-exam-box">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 18px;">
        <div>
          <h2 style="color: var(--accent-dark); font-weight: 700; font-size: 1.3rem;">⏱️ 國考全真 120 分鐘計時模考系統</h2>
          <p style="font-size: 0.85rem; color: var(--muted); margin-top: 2px;">白紙蓋牌獨立推導，訓練考場時間分配與作答節奏</p>
        </div>
        
        <!-- Exam Year & Subject Selector -->
        <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
          <select id="exam-select-subj" style="font-weight: 600;">
            <option value="01">⚡ 01. 電路學</option>
            <option value="02">🔌 02. 電子學（含電力電子）</option>
            <option value="03">📐 03. 工程數學</option>
            <option value="04">⚙️ 04. 電機機械</option>
            <option value="05">🏢 05. 電力系統</option>
            <option value="06">🏭 06. 工業配電</option>
          </select>
          <select id="exam-select-yr" style="font-weight: 600;">
            <option value="114">114 年全卷</option>
            <option value="113">113 年全卷</option>
            <option value="112">112 年全卷</option>
            <option value="111">111 年全卷</option>
            <option value="110">110 年全卷</option>
            <option value="109">109 年全卷</option>
            <option value="108">108 年全卷</option>
            <option value="107">107 年全卷</option>
            <option value="106">106 年全卷</option>
            <option value="105">105 年全卷</option>
            <option value="104">104 年全卷</option>
            <option value="random">🎲 隨機抽 4 題模考</option>
          </select>
          <button onclick="loadMockExam()" class="btn-sol">📄 載入試卷</button>
        </div>
      </div>

      <!-- Timer Center -->
      <div class="timer-display" id="exam-timer">120:00</div>
      
      <div class="timer-controls">
        <button onclick="startExamTimer()" class="btn-timer start" id="btn-timer-toggle">▶️ 開始計時</button>
        <button onclick="resetExamTimer()" class="btn-timer reset">🔄 重設時間</button>
      </div>

      <div id="mock-exam-questions" style="margin-top: 24px;"></div>
    </div>
  </div>

  <!-- TAB 4: Seven Layers -->
  <div class="tab-pane" id="tab-pane-layers" style="display: none;">
    <div style="background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow);">
      <h2 style="color: var(--accent-dark); font-size: 1.3rem; margin-bottom: 6px;">🧠 7 層階梯式認知考點架構</h2>
      <p style="font-size: 0.86rem; color: var(--muted); margin-bottom: 20px;">從基礎元件、核心定理到綜合電網保護，系統化掌握 11 年試題骨架：</p>
      <div id="layers-container"></div>
    </div>
  </div>

  <!-- TAB 5: Top Topics -->
  <div class="tab-pane" id="tab-pane-stats" style="display: none;">
    <div style="background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow);">
      <h2 style="color: var(--accent-dark); font-size: 1.3rem; margin-bottom: 6px;">🔥 歷屆高頻命題考點命中分析</h2>
      <p style="font-size: 0.86rem; color: var(--muted); margin-bottom: 20px;">統計 104~114 年 423 道大題中出現頻率最高的核心命題題型：</p>
      <div id="top-topics-container"></div>
    </div>
  </div>

</div>

<!-- Split Solution Viewer Modal -->
<div id="solution-modal">
  <div class="modal-container">
    <!-- Modal Header -->
    <div class="modal-header">
      <div class="modal-title" id="modal-title">
        <span>試題推導詳解</span>
      </div>
      <div class="modal-actions">
        <button id="modal-status-btn" class="status-badge s-0">⚪ 未開始</button>
        <button id="modal-star-btn" class="btn-star">☆ 收藏本題</button>
        <button onclick="closeModal()" class="btn-pdf" style="font-size: 0.9rem; font-weight: 700;">✕ 關閉</button>
      </div>
    </div>

    <!-- Modal Navigation Toolbar (上一題 / 下一題 / 該年度選題 / 視圖切換 / 主動回想) -->
    <div class="modal-nav-bar">
      <div class="modal-nav-group">
        <button class="btn-modal-nav" id="btn-modal-prev" onclick="navModalQuestion(-1)" title="快捷鍵：鍵盤向左鍵 ←">
          ← 上一題
        </button>
        <select class="modal-same-exam-select" id="modal-same-exam-select" onchange="onSameExamSelectChange(this)" title="同年度同考科試題快速切換">
        </select>
        <button class="btn-modal-nav" id="btn-modal-next" onclick="navModalQuestion(1)" title="快捷鍵：鍵盤向右鍵 →">
          下一題 →
        </button>
        <button class="btn-modal-nav" id="btn-active-recall" onclick="toggleActiveRecallMode()" title="主動回想蓋牌模式：先白紙列式，再揭曉破題提示與步驟">
          🎴 主動回想
        </button>
      </div>

      <div class="modal-nav-group">
        <div class="view-layout-toggle">
          <button class="btn-layout active" id="btn-layout-split" onclick="setModalLayout('split')" title="雙欄對照檢視 (預設)">
            ⚖️ 雙欄對照
          </button>
          <button class="btn-layout" id="btn-layout-solution" onclick="setModalLayout('solution-only')" title="純詳解全寬檢視">
            📝 純詳解
          </button>
          <button class="btn-layout" id="btn-layout-exam" onclick="setModalLayout('exam-only')" title="原題優先全寬檢視">
            📄 原題考卷
          </button>
        </div>
      </div>
    </div>

    <!-- Sub-Question Navigation Pills Bar -->
    <div class="sub-q-pills-bar" id="modal-sub-q-pills" style="display: none;"></div>

    <!-- Modal Split Body -->
    <div class="modal-split-body">
      <!-- Left Pane: Raw Question + PDF -->
      <div class="modal-pane-left" id="modal-pane-left">
        <div id="modal-left-content"></div>
      </div>

      <!-- Resizer Bar -->
      <div class="modal-resizer" id="modal-resizer"></div>

      <!-- Right Pane: Golden Standard KaTeX Solution + DAG Weakness Tracer -->
      <div class="modal-pane-right" id="modal-pane-right">
        <div id="modal-right-content"></div>
      </div>
    </div>
  </div>
<!-- Backup & Restore Modal -->
<div id="backup-modal" onclick="closeBackupModal()">
  <div class="backup-modal-box" onclick="event.stopPropagation()">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--line); padding-bottom: 10px;">
      <h3 style="color: var(--accent-dark); font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
        💾 備考進度與 SM-2 排程備份/還原
      </h3>
      <button onclick="closeBackupModal()" class="btn-pdf" style="padding: 2px 8px;">✕</button>
    </div>
    <p style="font-size: 0.86rem; color: var(--muted);">
      此代碼包含全庫 423 題做題狀態、重點收藏與 SM-2 智能遺忘曲線週期。複製此 JSON 或在換裝置時貼上即可無縫銜接：
    </p>
    <textarea id="backup-json-textarea" class="backup-textarea" placeholder="在此貼上備份 JSON 代碼..."></textarea>
    <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
      <div style="display: flex; gap: 8px;">
        <button onclick="copyBackupToClipboard()" class="btn-sol">📋 複製代碼</button>
        <button onclick="exportProgressJSON()" class="btn-pdf">📥 下載 .json</button>
      </div>
      <button onclick="applyImportedBackupJSON()" class="btn-sol" style="background: var(--success); border-color: var(--success);">
        ✅ 貼上並套用還原
      </button>
    </div>
  </div>
</div>

<script>
{bundled_js}
</script>
</body>
</html>
"""

    out_path = os.path.join(WORKSPACE, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Successfully compiled production index.html ({len(html_template)} bytes, version timestamp: {timestamp})")
    return True

if __name__ == '__main__':
    build_workbench()
