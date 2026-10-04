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
    print("Building Workbench from modular src/ components...")

    # Reproducible builds: CI supplies BUILD_VERSION (usually the commit
    # SHA); SOURCE_DATE_EPOCH is supported for deterministic local builds.
    build_version = os.environ.get('BUILD_VERSION')
    if not build_version:
        source_epoch = os.environ.get('SOURCE_DATE_EPOCH')
        if source_epoch:
            try:
                build_version = datetime.datetime.fromtimestamp(
                    int(source_epoch), tz=datetime.timezone.utc
                ).strftime('%Y%m%d_%H%M')
            except (TypeError, ValueError, OverflowError):
                build_version = 'dev'
        else:
            build_version = 'dev'
    
    # 1. Bundle Styles
    css_files = [
        'src/styles/base.css',
        'src/styles/layout.css',
        'src/styles/components.css',
        'src/styles/modal.css',
        'src/styles/dag-graph.css',
        'src/styles/v12-g1.css',
        'src/styles/v12-g2a.css',
        'src/styles/v12-g2b.css',
        'src/styles/v122-design.css',
        'src/styles/v13-practice.css',
        'src/styles/v13-pacing.css',
        'src/styles/v13-icons.css'
    ]
    bundled_css = "\n\n".join([f"/* === {f} === */\n" + read_file(f) for f in css_files])

    # 2. Bundle Scripts
    js_files = [
        'src/components/icons.js',
        'src/domain/questionRecord.js',
        'src/domain/knowledgeDiagnosis.js',
        'src/domain/weaknessProjection.js',
        'src/domain/passingProbability.js',
        'src/data/taxonomyAliases.js',
        'src/data/knowledge-dag.js',
        'src/data/knowledge-dag.generated.js',
        'src/data/dailySchedule.generated.js',
        'src/data/questionPoints.generated.js',
        'src/data/targetAllocation.generated.js',
        'src/domain/studyPlan.js',
        'src/data/answerCorrections.generated.js',
        'src/state/store.js',
        'src/state/filterStore.js',
        'src/state/sm2Store.js',
        'src/state/resultCardStore.js',
        'src/state/practiceStore.js',
        'src/data/recallHints.generated.js',
        'src/state/recallStore.js',
        'src/state/attemptStore.js',
        'src/state/knowledgeIssueStore.js',
        'src/state/knowledgeReviewStore.js',
        'src/components/weaknessView.js',
        'src/data/manualTopicLabels.js',
        'src/data/scenarioMatrixData.js',
        'src/components/answerCorrectionNotice.js',
        'src/components/reviewPage.js',
        'src/components/quickReviewSheet.js',
        'src/renderers/katexRenderer.js',
        'src/renderers/markdownRenderer.js',
        'src/components/dagTracer.js',
        'src/components/dagGraphViewer.js',
        'src/components/header.js',
        'src/components/questionList.js',
        'src/components/calculatorGuide.js',
        'src/data/cheatsheet.generated.js',
        'src/components/passbookGenerator.js',
        'src/components/resultCard.js',
        'src/components/solutionModal.js',
        'src/components/mockExam.js',
        'src/components/scoreboard.js',
        'src/components/dailyPractice.js',
        'src/domain/pacing.js',
        'src/components/todayTask.js',
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
<title>電機工程技師 歷屆試題全真雙欄工作台 (104-114年)</title>
<link rel="manifest" href="./manifest.json">
<meta name="theme-color" content="#4a7c8f">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">

<!-- Offline KaTeX & Marked.js Libraries -->
<link rel="stylesheet" href="./libs/katex.min.css">
<script src="./libs/katex.min.js"></script>
<script src="./libs/auto-render.min.js"></script>
<script src="./libs/marked.min.js"></script>

<!-- Embedded PE Database & Bundled Markdown Data (100% Offline & Zero-Latency).
     GK data files stay in the repo and are loaded lazily by ensureGkData() only if a GK path is triggered. -->
<script src="./dashboard-data.js?v={build_version}"></script>
<script src="./solutions-bundle.js?v={build_version}"></script>

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
        <h1><span class="title-full">電機工程技師 歷屆試題工作台</span><span class="title-short">電機技師工作台</span></h1>
        <p>專技高考電機工程技師 · 104 ~ 114 年 6 大考科 · <span id="hero-total-count">323 題</span> · 逐題來源可追溯 · 離線使用</p>
      </div>
      <div class="header-actions">
        <button onclick="toggleTheme()" class="pill" id="theme-toggle-btn" aria-label="切換暗色／亮色模式"><span class="theme-ico" aria-hidden="true"><span class="ui-ico" data-ui-icon="moon"></span></span><span class="theme-label"> 暗色模式</span></button>
      </div>
    </div>

    <!-- One-line summary: 今天 / 到期 / 成績 -->
    <p class="header-summary" id="header-summary-line" role="status" aria-live="polite">今天：—｜到期 0 題｜估計總分：尚無資料</p>
  </header>

  <!-- Main Navigation: three entries plus a collapsed 更多 -->
  <div class="main-tabs">
    <button class="main-tab-btn active" id="tab-btn-practice" onclick="switchTab('practice')">
      <span><span class="ui-ico" data-ui-icon="calendar"></span> 今天</span>
    </button>
    <button class="main-tab-btn" id="tab-btn-mock" onclick="switchTab('mock')">
      <span><span class="ui-ico" data-ui-icon="file-text"></span> 模考</span>
    </button>
    <button class="main-tab-btn" id="tab-btn-scoreboard" onclick="switchTab('scoreboard')">
      <span><span class="ui-ico" data-ui-icon="bar-chart"></span> 成績</span>
    </button>
    <details class="more-tools-menu" id="more-tools-menu">
      <summary><span class="ui-ico" data-ui-icon="more-horizontal"></span> 更多</summary>
      <div class="more-tools-panel">
        <button class="main-tab-btn" id="tab-btn-questions" onclick="switchTab('questions')"><span><span class="ui-ico" data-ui-icon="book"></span> 題庫瀏覽</span></button>
        <button class="main-tab-btn" id="tab-btn-passbook" onclick="openPassbookModal()"><span><span class="ui-ico" data-ui-icon="printer"></span> 考前速查手冊（列印）</span></button>
        <button class="main-tab-btn" id="tab-btn-backup" onclick="openBackupModal()"><span><span class="ui-ico" data-ui-icon="download"></span> 備份／還原</span></button>
      </div>
    </details>
  </div>

  <!-- TAB 0: Daily Practice -->
  <div class="tab-pane" id="tab-pane-practice" style="display: block;">
    <div id="today-task-card"></div>
    <div id="review-corrections"></div>
    <section class="home-primary-actions" aria-label="首頁主要入口">
      <button id="home-action-start" class="home-random-button" type="button" onclick="dailyPracticePrepareNewRound()"><span class="ui-ico" data-ui-icon="shuffle"></span><strong>隨機練習 3 題</strong><small>依目標分配抽題，按一次就開始</small></button>
      <button id="home-action-due" class="home-due-button" type="button" onclick="homeStartDueReview()" disabled><span class="ui-ico" data-ui-icon="rotate-ccw"></span><strong>到期複習</strong><small>今天沒有到期題</small></button>
    </section>
    <div class="practice-home-secondary">
      <button id="home-action-continue" type="button" onclick="switchTab('practice'); dailyPracticeContinue()" disabled>↩ 繼續上次</button>
    </div>
    <div id="daily-practice-container"></div>
  </div>

  <!-- TAB 1: Questions Explorer -->
  <div class="tab-pane" id="tab-pane-questions" style="display: none;">
    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon" data-ui-icon="search"></span>
        <input type="text" id="search-input" placeholder="搜尋考題關鍵字、公式標籤、觀念、題號..." oninput="renderQuestions()">
      </div>

      <select id="filter-subject" onchange="handleQuestionSubjectFilterChange(this.value)">
        <option value="all">所有考科 (6 大考科)</option>
        <option value="01">01. 電路學</option>
        <option value="02">02. 電子學（含電力電子）</option>
        <option value="03">03. 工程數學</option>
        <option value="04">04. 電機機械</option>
        <option value="05">05. 電力系統</option>
        <option value="06">06. 工業配電</option>
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
        <option value="1">已掌握</option>
        <option value="2">需二刷 (錯題本)</option>
        <option value="0">未開始</option>
        <option value="starred">僅看收藏</option>
      </select>

      <select id="filter-diff" onchange="renderQuestions()">
        <option value="all">所有難度</option>
        <option value="5">5星 地獄壓軸</option>
        <option value="4">4星 高難挑戰</option>
        <option value="3">3星 中等進階</option>
        <option value="2">2星 常規核心</option>
        <option value="1">1星 入門基礎</option>
      </select>
    </div>

    <!-- Quick Filter Pills -->
    <div class="pills-bar">
      <span style="font-size: 0.82rem; color: var(--muted); font-weight: 600;">快速篩選：</span>
      <button class="pill active" onclick="setQuickFilter('all', this)">全部試題</button>
      <button class="pill" onclick="setQuickFilter('due', this)" title="SM-2 今日待複習或逾期試題">⏳ 今日待複習</button>
      <button class="pill" onclick="setQuickFilter('review', this)">我的錯題本</button>
      <button class="pill" onclick="setQuickFilter('starred', this)">我的收藏</button>
      <button class="pill" onclick="setQuickFilter('top10', this)">高頻核心考點</button>
      <button class="pill" onclick="setQuickFilter('dedicated', this)">有完整步驟推導</button>
      <span id="filtered-count" style="margin-left: auto; font-size: 0.82rem; color: var(--muted); font-weight: 600;"></span>
    </div>

    <!-- Facet Filter Bar -->
    <div id="facet-filter-bar" class="facet-filter-bar" style="display: none;"></div>

    <!-- Questions Container -->
    <div id="questions-container" class="qlist"></div>
  </div>

  <!-- TAB 2: Mock exam (rendered by src/components/mockExam.js) -->
  <div class="tab-pane" id="tab-pane-mock" style="display: none;"></div>

  <!-- TAB 3: Scoreboard (rendered by renderScoreboard on switch) -->
  <div class="tab-pane" id="tab-pane-scoreboard" style="display: none;">
    <div id="scoreboard-container"></div>
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
        <button id="btn-modal-active-recall" onclick="toggleActiveRecallMode()" class="btn-sol" style="background: var(--warn); border-color: var(--warn); color: #fff; font-weight: 700; padding: 5px 12px; font-size: 0.82rem;" title="切換主動回想白紙蓋牌模式">
          主動回想蓋牌
        </button>
        <button id="modal-status-btn" class="status-badge s-0">未開始</button>
        <button id="modal-star-btn" class="btn-star"><span class="sm-ico" aria-hidden="true"><span class="ui-ico" data-ui-icon="star"></span></span><span class="sm-lbl"> 收藏本題</span></button>
        <button onclick="closeModal()" class="btn-pdf" style="font-size: 0.9rem; font-weight: 700;"><span class="sm-ico" aria-hidden="true"><span class="ui-ico" data-ui-icon="x"></span></span><span class="sm-lbl"> 關閉</span></button>
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
          主動回想
        </button>
      </div>

      <div class="modal-nav-group">
        <div class="view-layout-toggle">
          <button class="btn-layout active" id="btn-layout-split" onclick="setModalLayout('split')" title="雙欄對照檢視 (預設)">
            雙欄對照
          </button>
          <button class="btn-layout" id="btn-layout-solution" onclick="setModalLayout('solution-only')" title="純詳解全寬檢視">
            純詳解
          </button>
          <button class="btn-layout" id="btn-layout-exam" onclick="setModalLayout('exam-only')" title="原題優先全寬檢視">
            原題考卷
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
</div>

<!-- Manual Review Topic Annotation Modal -->
<div id="manual-label-modal" role="dialog" aria-modal="true" aria-labelledby="manual-label-title" onclick="if (event.target === this) closeManualLabelModal()">
  <div class="manual-label-dialog" onclick="event.stopPropagation()">
    <div class="manual-label-header">
      <div>
        <h3 id="manual-label-title">人工覆核題型標注</h3>
        <span id="manual-label-progress" class="manual-label-progress">0 / 0</span>
      </div>
      <button type="button" class="btn-pdf" onclick="closeManualLabelModal()"><span class="ui-ico" data-ui-icon="x"></span> 關閉</button>
    </div>
    <div id="manual-label-body" class="manual-label-body"></div>
    <div class="manual-label-footer">
      <button type="button" class="btn-modal-nav" id="manual-label-prev" onclick="moveManualLabel(-1)">← 上一題</button>
      <button type="button" class="btn-pdf" onclick="moveManualLabel(1, false)">略過（不儲存）→</button>
      <div class="manual-label-footer-spacer"></div>
      <button type="button" class="btn-sol" onclick="saveManualLabel()">儲存標注</button>
      <button type="button" class="btn-sol" id="manual-label-next" onclick="saveManualLabelAndNext()">儲存並下一題 →</button>
    </div>
  </div>
</div>

<!-- Backup & Restore Modal -->
<div id="backup-modal" onclick="closeBackupModal()">
  <div class="backup-modal-box" onclick="event.stopPropagation()">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--line); padding-bottom: 10px;">
      <h3 style="color: var(--accent-dark); font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
        備考進度與 SM-2 排程備份/還原
      </h3>
      <button onclick="closeBackupModal()" class="btn-pdf" style="padding: 2px 8px;" aria-label="關閉"><span class="ui-ico" data-ui-icon="x"></span></button>
    </div>
    <p style="font-size: 0.86rem; color: var(--muted);">
      備份儲存在此瀏覽器的本機資料，包含 PE／GK 全庫做題狀態、收藏、SM-2 排程、主動回想與人工章節標籤。載入或貼上後請先驗證，再選擇合併或取代還原：
    </p>
    <textarea id="backup-json-textarea" class="backup-textarea" placeholder="在此貼上備份 JSON 代碼..."></textarea>
    <div id="backup-preview" class="backup-preview" role="status">尚未驗證備份內容。</div>
    <div id="backup-history" class="backup-history"></div>
    <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
      <div style="display: flex; gap: 8px;">
        <button onclick="copyBackupToClipboard()" class="btn-sol"><span class="ui-ico" data-ui-icon="copy"></span> 複製代碼</button>
        <button onclick="exportProgressJSON()" class="btn-pdf"><span class="ui-ico" data-ui-icon="download"></span> 下載 .json</button>
      </div>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button onclick="previewImportedBackupJSON()" class="btn-pdf"><span class="ui-ico" data-ui-icon="search"></span> 先驗證／預覽</button>
        <button onclick="applyImportedBackupJSON('merge')" class="btn-sol">合併還原</button>
        <button onclick="applyImportedBackupJSON('replace')" class="btn-sol" style="background: var(--success); border-color: var(--success);"><span class="ui-ico" data-ui-icon="check"></span> 取代還原</button>
      </div>
    </div>
  </div>
</div>

<script>
{bundled_js}
</script>
<script>
// 不再註冊 service worker（K12）。解除既有註冊，避免舊快取釘住舊版本。
try {{
  if ('serviceWorker' in navigator && navigator.serviceWorker.getRegistrations) {{
    navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister())).catch(() => {{}});
  }}
}} catch (_) {{}}
</script>
</body>
</html>
"""

    out_path = os.path.join(WORKSPACE, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"OK Successfully compiled production index.html ({len(html_template)} bytes, build version: {build_version})")
    return True

if __name__ == '__main__':
    build_workbench()
