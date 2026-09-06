# -*- coding: utf-8 -*-
"""第二階段 A 批次：複習、詳解蓋牌與模考計時的行為契約。"""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_node(source_files, expression, setup=""):
    source = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in source_files)
    script = f"""
const vm = require('vm');
const context = {{ console }};
vm.createContext(context);
vm.runInContext({json.dumps(setup, ensure_ascii=False)}, context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(result));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise AssertionError(f"Node 行為測試失敗：\n{completed.stderr}")
    return json.loads(completed.stdout)


class TestReviewReliability(unittest.TestCase):
    def test_due_scope_and_completion_message_share_subject_range(self):
        setup = r'''
globalThis.document = { getElementById: id => id === 'review-subject' ? {value: '01'} : null };
globalThis.getReviewTypeLabel = q => q[0] === 'q1' ? '章節 A' : '章節 B';
globalThis.getActiveQuestionsList = () => [
  ['q1', '01', 114, 1, 'A', [], '', '', 3, 'verified', [], true],
  ['q2', '01', 114, 2, 'B', [], '', '', 3, 'verified', [], true],
  ['q3', '02', 114, 3, 'C', [], '', '', 3, 'verified', [], true],
];
globalThis.getDueQuestionsList = () => ['q1', 'q2', 'q3'];
globalThis.renderReviewPage = () => {};
globalThis.openSolutionModal = () => {};
'''
        expression = r'''
(() => {
  globalThis.setReviewTypeFilter('章節 A');
  globalThis.startReviewSession();
  const queue = globalThis.currentReviewSessionQueue.map(q => q[0]);
  const scoped = globalThis.getReviewQuestionsForScope(
    globalThis.getActiveQuestionsList(),
    {reviewFilter: 'due', dueIds: globalThis.getDueQuestionsList(), subjectId: '01', typeFilter: 'all'}
  ).map(q => q[0]);
  return {queue, scoped, message: globalThis.getReviewSessionCompletionMessage(queue)};
})()
'''
        result = run_node(["src/components/reviewPage.js"], expression, setup)
        self.assertEqual(result["queue"], ["q1", "q2"])
        self.assertEqual(result["scoped"], ["q1", "q2"])
        self.assertIn("2 題", result["message"])

    def test_review_card_shows_cover_and_opens_progressive_recall(self):
        setup = r'''
const nodes = new Map();
const recallButton = {dataset:{reviewRecall:'q1'}, addEventListener(type, fn){this.click=fn;}};
function element(id) {
  if (!nodes.has(id)) nodes.set(id, {
    id, value:id === 'review-subject' ? 'all' : '', innerHTML:'', innerText:'', style:{},
    querySelectorAll(selector){
      if (id === 'review-container' && selector === '[data-review-recall]') return [recallButton];
      return [];
    }
  });
  return nodes.get(id);
}
globalThis.document = {getElementById:element, querySelectorAll:()=>[]};
globalThis.localStorage = {getItem:()=>null,setItem:()=>{}};
globalThis.KNOWLEDGE_DAG = {};
globalThis.progressState = {};
globalThis.starredState = {};
globalThis.sm2Schedule = {q1:{nextReviewDate:'2026-09-06'}};
globalThis.getActiveQuestionsList = () => [['q1','01',114,1,'題目',[], 'solution.md','source.pdf',3,'verified',[],true]];
globalThis.getDueQuestionsList = () => ['q1'];
globalThis.getSubjectMeta = () => ({name:'電路學',icon:'⚡'});
globalThis.getRecallState = () => ({level:1});
globalThis.renderQuestionTopic = text => text;
globalThis.openSolutionModal = (...args) => { globalThis.__openArgs = args; };
'''
        expression = r'''
(() => {
  getReviewTypeLabel = () => '章節 A';
  renderReviewPage();
  recallButton.click();
  const html = document.getElementById('review-container').innerHTML;
  return {html, activeRecall:globalThis.__openArgs[5]};
})()
'''
        result = run_node(["src/components/reviewPage.js"], expression, setup)
        self.assertIn('aria-label="詳解已蓋牌"', result["html"])
        self.assertIn("先自行作答，再依序揭露", result["html"])
        self.assertTrue(result["activeRecall"])


class TestSolutionModalReliability(unittest.TestCase):
    def test_open_sets_recall_explicitly_and_close_clears_transient_state(self):
        setup = r'''
const elements = new Map();
globalThis.document = {
  body: {style: {}},
  getElementById: id => elements.get(id) || null,
};
globalThis.window = {addEventListener() {}};
'''
        expression = r'''
(() => {
  globalThis.openSolutionModal(null, '', 'q1', 1, false, true, {sessionQueue: ['q1']});
  const recallOpen = globalThis.getSolutionModalTransientState();
  globalThis.openSolutionModal(null, '', 'q2', 2, false, false);
  const ordinaryOpen = globalThis.getSolutionModalTransientState();
  globalThis.closeModal();
  const closed = globalThis.getSolutionModalTransientState();
  return {recallOpen, ordinaryOpen, closed};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["recallOpen"]["activeRecall"])
        self.assertFalse(result["ordinaryOpen"]["activeRecall"])
        self.assertEqual(result["closed"], {
            "qid": None,
            "activeRecall": False,
            "sessionLength": 0,
            "sessionIndex": 0,
        })

    def test_active_recall_hides_solution_and_reveals_layers_in_order(self):
        setup = r'''
const elements = new Map();
const make = id => ({id, innerHTML:'', style:{display:'none'}, scrollIntoView(){}});
['modal-right-content','recall-layer-1','recall-layer-2','recall-layer-3','recall-full-section','recall-rating-bar','recall-step-box']
  .forEach(id => elements.set(id, make(id)));
globalThis.document = {
  body:{style:{}},
  getElementById:id => elements.get(id) || null,
  querySelectorAll:() => []
};
globalThis.window = {addEventListener(){}};
globalThis.getRecallHintBundle = () => ({chapter:'章節',activation:'起手式',formula:'x=1',trap:'陷阱'});
globalThis.processMarkdownWithMath = text => `<p class="rendered-solution">${text}</p>`;
globalThis.resolveRenderedImageSources = html => html;
globalThis.renderSolutionReviewCard = () => '';
globalThis.renderScenarioMatrix = () => '';
globalThis.renderDagTracerCard = () => '';
globalThis.reviewHtmlEscape = value => String(value);
'''
        expression = r'''
(() => {
  isActiveRecallMode = true;
  currentModalQid = 'q1';
  renderSubQuestionContent('答案內容', ['q1','01',114,1,'題目']);
  const initialHtml = document.getElementById('modal-right-content').innerHTML;
  revealRecallLayer(1);
  const layer1 = document.getElementById('recall-layer-1').style.display;
  const fullBefore = document.getElementById('recall-full-section').style.display;
  revealRecallFull();
  return {
    initialHtml, layer1, fullBefore,
    fullAfter: document.getElementById('recall-full-section').style.display,
    ratingAfter: document.getElementById('recall-rating-bar').style.display
  };
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertIn('id="recall-full-section" style="display: none;"', result["initialHtml"])
        self.assertIn('class="rendered-solution"', result["initialHtml"])
        self.assertEqual(result["layer1"], "block")
        self.assertEqual(result["fullBefore"], "none")
        self.assertEqual(result["fullAfter"], "block")
        self.assertEqual(result["ratingAfter"], "flex")


class TestMockExamTimerReliability(unittest.TestCase):
    SETUP = r'''
globalThis.__now = 1000000;
globalThis.__toastCount = 0;
globalThis.__toasts = [];
const timerElement = {innerText: ''};
const toggleElement = {innerText: '', className: '', onclick: null};
const storage = new Map();
globalThis.localStorage = {
  getItem: key => storage.has(key) ? storage.get(key) : null,
  setItem: (key, value) => storage.set(key, String(value)),
  removeItem: key => storage.delete(key),
};
globalThis.document = {getElementById: id => id === 'exam-timer' ? timerElement : id === 'btn-timer-toggle' ? toggleElement : null};
globalThis.setInterval = () => 1;
globalThis.clearInterval = () => {};
globalThis.showToast = message => { globalThis.__toastCount += 1; globalThis.__toasts.push(message); };
const NativeDate = Date;
globalThis.Date = class TestDate extends NativeDate {
  static now() { return globalThis.__now; }
};
'''

    def test_background_delay_uses_absolute_deadline(self):
        expression = r'''
(() => {
  globalThis.startExamTimer();
  const deadline = globalThis.getMockExamTimerState().deadline;
  globalThis.__now += 6500;
  globalThis.updateExamTimerFromClock();
  return {deadline, seconds: globalThis.getMockExamTimerState().seconds};
})()
'''
        result = run_node(["src/components/mockExamTimer.js"], expression, self.SETUP)
        # 1,000,000 ms + 120 minutes.
        self.assertEqual(result["deadline"], 8200000)
        self.assertEqual(result["seconds"], 7194)

    def test_saved_running_timer_can_be_loaded_and_expiry_notifies_once(self):
        expression = r'''
(() => {
  globalThis.startExamTimer();
  const deadline = globalThis.getMockExamTimerState().deadline;
  globalThis.loadMockExamTimerState(deadline - 1000);
  const restored = globalThis.getMockExamTimerState();
  globalThis.__now = deadline + 1;
  globalThis.updateExamTimerFromClock();
  globalThis.updateExamTimerFromClock();
  const expired = globalThis.getMockExamTimerState();
  const expiryNotices = globalThis.__toasts.filter(message => message.includes('考試時間結束')).length;
  return {restored, expired, expiryNotices};
})()
'''
        result = run_node(["src/components/mockExamTimer.js"], expression, self.SETUP)
        self.assertEqual(result["restored"]["seconds"], 1)
        self.assertEqual(result["expired"]["seconds"], 0)
        self.assertTrue(result["expired"]["completed"])
        self.assertEqual(result["expiryNotices"], 1)

    def test_pause_keeps_remaining_seconds_until_resume(self):
        expression = r'''
(() => {
  globalThis.startExamTimer();
  globalThis.__now += 5000;
  globalThis.pauseExamTimer();
  const paused = globalThis.getMockExamTimerState();
  globalThis.__now += 999999;
  globalThis.startExamTimer();
  const resumed = globalThis.getMockExamTimerState();
  return {paused, resumed};
})()
'''
        result = run_node(["src/components/mockExamTimer.js"], expression, self.SETUP)
        self.assertEqual(result["paused"]["seconds"], 7195)
        self.assertEqual(result["paused"]["running"], False)
        # Resume at 2,004,999 ms with 7,195 seconds remaining.
        self.assertEqual(result["resumed"]["deadline"], 9199999)


if __name__ == "__main__":
    unittest.main()
