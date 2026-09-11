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
    def test_practice_stat_counts_current_round_not_historical_unique_questions(self):
        setup = "globalThis.window={}; globalThis.document={getElementById:()=>null};"
        expression = "(() => ({active:getPracticeRoundCompleted(null,{state:{activeSession:{currentIndex:2}}}),finished:getPracticeRoundCompleted({completed:3},{state:{activeSession:null}}),idle:getPracticeRoundCompleted(null,{state:{activeSession:null}})}))()"
        result = run_node(["src/components/reviewPage.js"], expression, setup)
        self.assertEqual(result, {"active": 2, "finished": 3, "idle": 0})
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

    def test_review_summary_counts_rated_and_skipped_separately(self):
        setup = r'''
globalThis.document = {getElementById:id => id === 'review-subject' ? {value:'01'} : null};
globalThis.getActiveQuestionsList = () => [
  ['q1','01',114,1,'A',[],'','',3,'verified',[],true],
  ['q2','01',114,2,'B',[],'','',3,'verified',[],true]
];
globalThis.getDueQuestionsList = () => ['q1','q2'];
globalThis.getReviewTypeLabel = () => '章節';
globalThis.openSolutionModal = () => {};
globalThis.closeSolutionModal = () => {};
globalThis.renderReviewPage = () => {};
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  startReviewSession();
  skipCurrentReviewSessionItem();
  recordReviewSessionRating('q2');
  advanceReviewSessionItem();
  return {summary:getReviewSessionSummary(),message:getReviewSessionCompletionMessage(currentReviewSessionQueue)};
})()
'''
        result = run_node(["src/components/reviewPage.js"], expression, setup)
        self.assertEqual(result["summary"], {"rated": 1, "skipped": 1, "remaining": 0, "total": 2})
        self.assertIn("完成 1 題", result["message"])
        self.assertIn("略過 1 題", result["message"])

    def test_last_due_question_has_explicit_skip_or_finish_action(self):
        source = (ROOT / "src/components/solutionModal.js").read_text(encoding="utf-8")
        self.assertIn("skipCurrentReviewSessionItem()", source)
        self.assertEqual(source.count("function advanceReviewSessionItem()"), 0)

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
  return {html, activeRecall:globalThis.__openArgs[4].recall, sourceMode:globalThis.__openArgs[4].mode};
})()
'''
        result = run_node(["src/components/reviewPage.js"], expression, setup)
        self.assertIn('aria-label="詳解已蓋牌"', result["html"])
        self.assertIn("先自行作答，再依序揭露", result["html"])
        self.assertTrue(result["activeRecall"])
        self.assertEqual(result["sourceMode"], "due-review")


class TestSolutionModalReliability(unittest.TestCase):
    def test_daily_practice_rating_does_not_write_sm2_and_requires_full_reveal(self):
        setup = r'''
globalThis.document = {body:{style:{}}, getElementById:() => null};
globalThis.window = {addEventListener(){}};
globalThis.__sm2 = 0;
globalThis.__recall = 0;
globalThis.findQuestionRecord = qid => [qid,'01',114,1,'題目',[],'','',3,'verified',[],true];
globalThis.toQuestionRecord = q => ({id:q[0],examFamily:'PE'});
globalThis.submitLearningAttempt = () => { globalThis.__recall += 1; return {ok:true,duplicate:false,nextAction:{type:'advance-daily'}}; };
globalThis.dailyPracticeApplyCompletedAttempt = () => { globalThis.__complete = (globalThis.__complete || 0) + 1; };
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  openSolutionModal(null, '', 'q1', 1, {mode:'daily-practice', recall:true});
  submitSM2Rating(5);
  const blocked = {sm2:globalThis.__sm2, recall:globalThis.__recall, complete:globalThis.__complete || 0};
  currentRecallAchievedLevel = 3;
  revealRecallFull();
  submitSM2Rating(5);
  return {blocked, after:{sm2:globalThis.__sm2, recall:globalThis.__recall, complete:globalThis.__complete || 0}};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertEqual(result["blocked"], {"sm2": 0, "recall": 0, "complete": 0})
        self.assertEqual(result["after"], {"sm2": 0, "recall": 1, "complete": 1})

    def test_daily_browse_bypass_has_no_daily_rating_or_completion(self):
        setup = r'''
globalThis.document = {body:{style:{}}, getElementById:() => null};
globalThis.window = {addEventListener(){}};
globalThis.recordSM2Review = () => { globalThis.__sm2 = (globalThis.__sm2 || 0) + 1; };
globalThis.recordRecallAttempt = () => { globalThis.__recall = (globalThis.__recall || 0) + 1; };
globalThis.dailyPracticeCompleteFromModal = () => { globalThis.__complete = (globalThis.__complete || 0) + 1; };
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  openSolutionModal(null, '', 'q1', 1, {mode:'daily-practice', recall:false});
  const state = getSolutionModalTransientState();
  submitSM2Rating(5);
  return {state, sm2:globalThis.__sm2 || 0, recall:globalThis.__recall || 0, complete:globalThis.__complete || 0};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertFalse(result["state"]["recallEntry"])
        self.assertEqual(result["sm2"], 0)
        self.assertEqual(result["recall"], 0)
        self.assertEqual(result["complete"], 0)

    def test_daily_browse_bypass_with_saved_full_reveal_still_cannot_complete(self):
        setup = r'''
globalThis.document = {body:{style:{}}, getElementById: () => null};
globalThis.window = {addEventListener(){}};
globalThis.dailyPracticeGetRecallProgress = () => 4;
globalThis.recordSM2Review = () => { globalThis.__sm2 = (globalThis.__sm2 || 0) + 1; };
globalThis.recordRecallAttempt = () => { globalThis.__recall = (globalThis.__recall || 0) + 1; };
globalThis.dailyPracticeCompleteFromModal = () => { globalThis.__complete = (globalThis.__complete || 0) + 1; };
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  openSolutionModal(null, '', 'q1', 1, {mode:'daily-practice', recall:false});
  const state = getSolutionModalTransientState();
  submitSM2Rating(5);
  return {state, sm2:globalThis.__sm2 || 0, recall:globalThis.__recall || 0, complete:globalThis.__complete || 0};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertFalse(result["state"]["recallEntry"])
        self.assertEqual(result["state"]["recallLevel"], 4)
        self.assertEqual(result["sm2"], 0)
        self.assertEqual(result["recall"], 0)
        self.assertEqual(result["complete"], 0)

    def test_daily_browse_render_has_no_daily_self_assessment_controls(self):
        setup = r'''
const rightPane = {innerHTML:''};
globalThis.window = {addEventListener(){}};
globalThis.document = {getElementById:id => id === 'modal-right-content' ? rightPane : null, querySelectorAll:() => []};
globalThis.processMarkdownWithMath = text => '<p>' + text + '</p>';
globalThis.resolveRenderedImageSources = html => html;
globalThis.renderSolutionReviewCard = () => '';
globalThis.renderScenarioMatrix = () => '';
globalThis.renderDagTracerCard = () => '';
globalThis.reviewHtmlEscape = value => String(value);
'''
        expression = r'''
(() => {
  currentModalQid='q1'; currentSolutionSourceMode='daily-practice'; currentSolutionRecallEntry=false; isActiveRecallMode=false;
  renderSubQuestionContent('完整解答', null);
  return document.getElementById('modal-right-content').innerHTML;
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertNotIn('sm2-rating-bar', result)
        self.assertNotIn('自評', result)

    def test_daily_recall_entry_toggle_at_level_zero_stays_masked(self):
        setup = r'''
const elements = new Map([
  ['recall-full-section', {style:{display:'none'}}],
  ['recall-rating-bar', {style:{display:'none'}}]
]);
globalThis.document = {
  body:{style:{}},
  getElementById:id => elements.get(id) || null,
  querySelectorAll:() => []
};
globalThis.window = {addEventListener(){}};
globalThis.resolveSolutionMarkdown = () => '';
globalThis.findQuestionRecord = () => null;
globalThis.showToast = message => { globalThis.__toast = message; };
'''
        expression = r'''
(() => {
  currentModalQid = 'q1';
  currentSolutionSourceMode = 'daily-practice';
  currentSolutionRecallEntry = true;
  currentRecallAchievedLevel = 0;
  isActiveRecallMode = true;
  toggleActiveRecallMode();
  return {
    activeRecall: isActiveRecallMode,
    fullDisplay: document.getElementById('recall-full-section').style.display,
    ratingDisplay: document.getElementById('recall-rating-bar').style.display,
    toast: globalThis.__toast
  };
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["activeRecall"])
        self.assertEqual(result["fullDisplay"], "none")
        self.assertEqual(result["ratingDisplay"], "none")
        self.assertIn("四段蓋牌", result["toast"])

    def test_browse_can_start_a_new_recall_attempt_from_the_toggle(self):
        setup = r'''
globalThis.window = {addEventListener(){}};
globalThis.document = {getElementById:()=>null, querySelectorAll:()=>[]};
globalThis.resolveSolutionMarkdown = () => '';
globalThis.findQuestionRecord = () => null;
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  currentModalQid='EE-Q'; currentSolutionSourceMode='browse'; currentSolutionRecallEntry=false;
  currentLearningAttemptId='old-view'; isActiveRecallMode=false;
  toggleActiveRecallMode();
  return getSolutionModalTransientState();
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["activeRecall"])
        self.assertTrue(result["recallEntry"])

    def test_daily_completion_rejects_modal_qid_mismatch(self):
        setup = r'''
globalThis.document = {getElementById: id => id === 'daily-practice-container' ? {innerHTML:'', querySelector:()=>null, querySelectorAll:()=>[]} : null};
globalThis.localStorage = {data:{}, getItem(k){return this.data[k] || null;}, setItem(k,v){this.data[k]=String(v);}};
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  const session = createPracticeSession('PE','01',['q1','q2'],{now:1234});
  savePracticeSession(session);
  dailyPracticeState = loadDailyPracticeStore().state;
  const result = dailyPracticeCompleteFromModal(5, 4, 'q2');
  return {result, state:loadDailyPracticeStore().state};
})()
'''
        result = run_node(["src/state/practiceStore.js", "src/components/dailyPractice.js"], expression, setup)
        self.assertFalse(result["result"])
        self.assertEqual(result["state"]["completionByQuestion"], {})
        self.assertEqual(result["state"]["activeSession"]["currentIndex"], 0)

    def test_due_review_rating_writes_sm2(self):
        setup = r'''
globalThis.document = {body:{style:{}}, getElementById:() => null};
globalThis.window = {addEventListener(){}};
globalThis.findQuestionRecord = qid => [qid,'01',114,1,'題目',[],'','',3,'verified',[],true];
globalThis.toQuestionRecord = q => ({id:q[0],examFamily:'PE'});
globalThis.submitLearningAttempt = () => { globalThis.__sm2 = (globalThis.__sm2 || 0) + 1; return {ok:true,duplicate:false,nextReviewDate:'2026-09-07',nextAction:{type:'refresh-review'}}; };
globalThis.recordReviewSessionRating = qid => { globalThis.__rated = (globalThis.__rated || []).concat(qid); };
globalThis.showToast = () => {};
globalThis.setTimeout = fn => { globalThis.__scheduledAdvance = fn; return 1; };
globalThis.clearTimeout = () => {};
'''
        expression = r'''
(() => { openSolutionModal(null, '', 'q1', 1, {mode:'due-review', recall:false}); const before=(globalThis.__rated||[]).length; submitSM2Rating(3); return {writes:globalThis.__sm2||0,before,rated:globalThis.__rated||[]}; })()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertEqual(result["writes"], 1)
        self.assertEqual(result["before"], 0)
        self.assertEqual(result["rated"], ["q1"])

    def test_conflict_after_success_keeps_rating_buttons_locked(self):
        setup = r'''
const buttons=[{disabled:false},{disabled:false},{disabled:false}];
globalThis.document = {body:{style:{}},getElementById:()=>null,querySelectorAll:selector => selector.includes('.btn-sm2') ? buttons : []};
globalThis.window = {addEventListener(){}};
globalThis.findQuestionRecord = qid => [qid,'01',114,1,'題目',[],'','',3,'verified',[],true];
globalThis.toQuestionRecord = q => ({id:q[0],examFamily:'PE'});
let calls=0;
globalThis.submitLearningAttempt = () => ++calls === 1
  ? {ok:true,duplicate:false,nextReviewDate:'2026-09-09',nextAction:{type:'refresh-review'}}
  : {ok:false,duplicate:false,code:'attempt_conflict',message:'衝突'};
globalThis.showToast = () => {};
globalThis.setTimeout = fn => { globalThis.__scheduledAdvance = fn; return 1; };
globalThis.clearTimeout = () => {};
'''
        expression = r'''
(() => {
  currentModalQid='EE-Q'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt';
  submitSM2Rating(3); const afterSuccess=buttons.map(b=>b.disabled);
  submitSM2Rating(5); const afterConflict=buttons.map(b=>b.disabled);
  return {afterSuccess,afterConflict,submitted:currentLearningAttemptSubmitted};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertEqual(result["afterSuccess"], [True, True, True])
        self.assertEqual(result["afterConflict"], [True, True, True])
        self.assertTrue(result["submitted"])

    def test_open_sets_recall_explicitly_and_close_clears_transient_state(self):
        setup = r'''
const elements = new Map();
globalThis.document = {
  body: {style: {}},
  getElementById: id => elements.get(id) || null,
  activeElement: {focus(){}},
};
globalThis.window = {addEventListener() {}};
globalThis.__trigger = {isConnected:true, focus(){globalThis.__restored=(globalThis.__restored||0)+1;}};
'''
        expression = r'''
(() => {
  globalThis.openSolutionModal({preventDefault(){},currentTarget:globalThis.__trigger}, '', 'q1', 1, {mode:'due-review', recall:true, sessionQueue: ['q1']});
  const recallOpen = globalThis.getSolutionModalTransientState();
  globalThis.openSolutionModal(null, '', 'q2', 2, {mode:'browse'});
  const ordinaryOpen = globalThis.getSolutionModalTransientState();
  globalThis.closeModal();
  const closed = globalThis.getSolutionModalTransientState();
  return {recallOpen, ordinaryOpen, closed, restored:globalThis.__restored||0};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["recallOpen"]["activeRecall"])
        self.assertEqual(result["recallOpen"]["sourceMode"], "due-review")
        self.assertFalse(result["ordinaryOpen"]["activeRecall"])
        self.assertEqual(result["ordinaryOpen"]["sourceMode"], "browse")
        self.assertEqual(result["closed"], {
            "qid": None,
            "activeRecall": False,
            "recallEntry": False,
            "sourceMode": "browse",
            "recallLevel": 0,
            "sessionLength": 0,
            "sessionIndex": 0,
        })
        self.assertEqual(result["restored"], 1)

    def test_tab_from_outside_modal_is_forced_back_inside(self):
        setup = r'''
const first={offsetParent:{},focus(){globalThis.__focused='first';}};
const last={offsetParent:{},focus(){globalThis.__focused='last';}};
const modal={classList:{contains:()=>true},querySelectorAll:()=>[first,last],contains:()=>false};
globalThis.document={activeElement:{},getElementById:id=>id==='solution-modal'?modal:null};
globalThis.window={addEventListener(type,fn){if(type==='keydown')globalThis.__keydown=fn;}};
'''
        expression = r'''
(() => { let prevented=false; __keydown({key:'Tab',shiftKey:false,target:{matches:()=>false},preventDefault(){prevented=true;}}); return {prevented,focused:globalThis.__focused}; })()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["prevented"])
        self.assertEqual(result["focused"], "first")

    def test_crop_fallback_escapes_pdf_and_supports_keyboard_entry(self):
        setup = r'''
const image = {src:'crop.png', alt:'題圖', handlers:{}, addEventListener(type, fn){this.handlers[type]=fn;}, closest(){return {set outerHTML(value){globalThis.__fallback=value;}};}};
globalThis.window = {addEventListener(){}};
globalThis.document = {querySelector:() => image};
'''
        expression = r'''
(() => {
  bindQuestionCropPreview('q1', 'https://example.test/a?x="bad"&y=1');
  image.handlers.keydown({key:'Enter', preventDefault(){}});
  image.handlers.keydown({key:' ', preventDefault(){}});
  image.handlers.error();
  return {fallback:globalThis.__fallback, hasKeys:Object.keys(image.handlers).sort()};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertIn('x=&quot;bad&quot;&amp;y=1', result["fallback"])
        self.assertEqual(result["hasKeys"], ["click", "error", "keydown"])

    def test_image_lightbox_escape_only_closes_lightbox_and_restores_trigger_focus(self):
        setup = r'''
const trigger = {focus(){globalThis.__focus = 'trigger';}};
const nodes = {};
const makeChild = () => ({addEventListener(type, fn){this.handlers = this.handlers || {}; this.handlers[type] = fn;}, focus(){globalThis.__focus = 'stage';}});
globalThis.window = {addEventListener(type, fn){if (type === 'keydown') globalThis.__windowKeydown = fn;}};
globalThis.document = {
  activeElement: trigger,
  body: {appendChild(node){nodes.lightbox = node;}},
  createElement(){
    const children = {
      '[data-image-close]': makeChild(),
      '[data-image-zoom-in]': makeChild(),
      '[data-image-zoom-out]': makeChild(),
      '.question-image-lightbox-stage': makeChild()
    };
    return {
      handlers:{},
      setAttribute(){},
      querySelector(selector){return children[selector];},
      addEventListener(type, fn){this.handlers[type] = fn;},
      remove(){nodes.lightbox = null;},
      set innerHTML(value){this.__html = value;}
    };
  },
  getElementById(id){return id === 'question-image-lightbox' ? nodes.lightbox : {classList:{contains:()=>true}};},
  querySelector(){return null;}
};
globalThis.closeModal = () => { globalThis.__modalClosed = (globalThis.__modalClosed || 0) + 1; };
'''
        expression = r'''
(() => {
  openImageLightbox('crop.png', '題圖', trigger);
  const event = {key:'Escape', preventDefault(){this.prevented = true;}, stopPropagation(){this.stopped = true;}};
  nodes.lightbox.handlers.keydown(event);
  if (!event.stopped && globalThis.__windowKeydown) globalThis.__windowKeydown(event);
  return {stopped:event.stopped || false, prevented:event.prevented || false, lightboxOpen:Boolean(nodes.lightbox), modalClosed:globalThis.__modalClosed || 0, focus:globalThis.__focus};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["stopped"])
        self.assertTrue(result["prevented"])
        self.assertFalse(result["lightboxOpen"])
        self.assertEqual(result["modalClosed"], 0)
        self.assertEqual(result["focus"], "trigger")

    def test_solution_image_click_and_enter_restore_actual_image_when_other_element_is_active(self):
        setup = r'''
const other = {focus(){globalThis.__focus = 'other';}};
const image = {
  src:'crop.png', alt:'題圖', handlers:{}, isConnected:true,
  addEventListener(type, fn){this.handlers[type]=fn;},
  focus(){globalThis.__focus = 'image';},
  closest(){return {set outerHTML(value){globalThis.__fallback=value;}};}
};
const nodes = {};
const makeChild = () => ({addEventListener(type, fn){this.handlers = this.handlers || {}; this.handlers[type] = fn;}, focus(){}});
globalThis.window = {addEventListener(){}};
globalThis.document = {
  activeElement: other,
  body: {appendChild(node){nodes.lightbox = node;}},
  contains(node){return node === image || node === other;},
  createElement(){
    const children = {
      '[data-image-close]': makeChild(),
      '[data-image-zoom-in]': makeChild(),
      '[data-image-zoom-out]': makeChild(),
      '.question-image-lightbox-stage': makeChild()
    };
    return {
      handlers:{}, setAttribute(){}, querySelector(selector){return children[selector];},
      addEventListener(type, fn){this.handlers[type]=fn;},
      remove(){nodes.lightbox=null;},
      set innerHTML(value){this.__html=value;}
    };
  },
  getElementById(id){return id === 'question-image-lightbox' ? nodes.lightbox : null;},
  querySelector(){return image;}
};
'''
        expression = r'''
(() => {
  bindQuestionCropPreview('q1', 'source.pdf');
  image.handlers.click({type:'click'});
  const clickLightbox = nodes.lightbox;
  clickLightbox.handlers.keydown({key:'Escape', preventDefault(){}, stopPropagation(){}});
  image.handlers.keydown({key:'Enter', preventDefault(){}});
  const enterLightbox = nodes.lightbox;
  enterLightbox.handlers.keydown({key:'Escape', preventDefault(){}, stopPropagation(){}});
  return {clickRestored: globalThis.__focus, openedByClick:Boolean(clickLightbox), openedByEnter:Boolean(enterLightbox)};
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertTrue(result["openedByClick"])
        self.assertTrue(result["openedByEnter"])
        self.assertEqual(result["clickRestored"], "image")

    def test_daily_image_click_and_enter_pass_the_actual_image_trigger(self):
        setup = r'''
const image = {
  src:'daily-crop.png', alt:'每日題圖', handlers:{},
  addEventListener(type, fn){this.handlers[type]=fn;},
  closest(){return {set outerHTML(value){}};}
};
const deferButton = {addEventListener(){}};
const scroll = {scrollTop:0};
const container = {
  _html:'',
  set innerHTML(value){this._html=value;},
  get innerHTML(){return this._html;},
  querySelector(selector){
    if (selector === '.daily-practice-scroll') return scroll;
    if (selector === '[data-daily-defer]') return deferButton;
    if (selector === '[data-daily-zoom-image]') return image;
    return null;
  },
  querySelectorAll(){return [];}
};
globalThis.document = {getElementById:() => null};
globalThis.DB_DATA = {subjects:[], questions:[['q1','01',114,1,'題目',[], 'solution.md','source.pdf',3,'verified',[],true]]};
globalThis.NATIONAL_EXAMS_DATA = {subjects:[], questions:[]};
globalThis.QUESTION_CROP_MAP = {q1:'daily-crop.png'};
globalThis.resolveImageMapUrl = crop => crop;
globalThis.openImageLightbox = (...args) => { globalThis.__openArgs = args; };
globalThis.showToast = () => {};
'''
        expression = r'''
(() => {
  dailyPracticeCategory = 'PE';
  dailyPracticeHomeMode = 'continue';
  dailyPracticeState = {activeSession:createPracticeSession('PE','01',['q1'],{now:1234})};
  renderDailyPractice(container);
  image.handlers.click({type:'click'});
  const clickTrigger = globalThis.__openArgs[2] === image;
  image.handlers.keydown({key:'Enter', preventDefault(){}});
  const enterTrigger = globalThis.__openArgs[2] === image;
  return {clickTrigger, enterTrigger};
})()
'''
        result = run_node(["src/state/practiceStore.js", "src/domain/questionRecord.js", "src/components/dailyPractice.js"], expression, setup)
        self.assertTrue(result["clickTrigger"])
        self.assertTrue(result["enterTrigger"])

    def test_active_recall_hides_solution_and_reveals_layers_in_order(self):
        setup = r'''
const elements = new Map();
const stepButtons = [0,1,2,3].map(() => ({disabled:false,title:''}));
const make = id => ({id, innerHTML:'', style:{display:'none'}, scrollIntoView(){}, querySelectorAll:() => id === 'recall-step-box' ? stepButtons : []});
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
  revealRecallLayer(2);
  revealRecallLayer(3);
  const layer1 = document.getElementById('recall-layer-1').style.display;
  const fullBefore = document.getElementById('recall-full-section').style.display;
  revealRecallFull();
  currentRecallAchievedLevel = 4;
  renderSubQuestionContent('答案內容', ['q1','01',114,1,'題目']);
  return {
    initialHtml, layer1, fullBefore,
    fullAfter: document.getElementById('recall-full-section').style.display,
    ratingAfter: document.getElementById('recall-rating-bar').style.display,
    restoredLayer3: document.getElementById('recall-layer-3').style.display,
    restoredFull: document.getElementById('recall-full-section').style.display,
    restoredBox: document.getElementById('recall-step-box').style.display
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
        self.assertEqual(result["restoredLayer3"], "block")
        self.assertEqual(result["restoredFull"], "block")
        self.assertEqual(result["restoredBox"], "none")

    def test_active_recall_keeps_answer_bearing_matrix_inside_fourth_reveal(self):
        setup = r'''
const rightPane = {innerHTML:''};
globalThis.document = {
  getElementById:id => id === 'modal-right-content' ? rightPane : null,
  querySelectorAll:() => []
};
globalThis.window = {addEventListener(){}};
globalThis.getRecallHintBundle = () => ({chapter:'章節',activation:'起手式',formula:'x=1',trap:'陷阱'});
globalThis.processMarkdownWithMath = text => `<p class="rendered-solution">${text}</p>`;
globalThis.resolveRenderedImageSources = html => html;
globalThis.renderSolutionReviewCard = () => '<aside class="solution-review-card">來源摘要</aside>';
globalThis.renderDagTracerCard = () => '';
globalThis.reviewHtmlEscape = value => String(value);
globalThis.SCENARIO_MATRIX_DATA = {
  'EE-111-02-3': {
    coreConflict:'條件不同',
    scenarioA:{name:'A',condition:'條件A',keyValues:[{param:'P',val:'42'}],examAdvice:'作法A'},
    scenarioB:{name:'B',condition:'條件B',keyValues:[{param:'P',val:'24'}],examAdvice:'作法B'}
  }
};
'''
        expression = r'''
(() => {
  isActiveRecallMode = true;
  currentModalQid = 'EE-111-02-3';
  renderSubQuestionContent('完整答案', ['EE-111-02-3','02',111,3,'題目']);
  const html = document.getElementById('modal-right-content').innerHTML;
  const fullStart = html.indexOf('id="recall-full-section"');
  const fullEnd = html.indexOf('recall-full-section-end');
  return {
    matrixIndex: html.indexOf('scenario-matrix-card'),
    reviewIndex: html.indexOf('solution-review-card'),
    fullStart, fullEnd
  };
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertGreater(result["matrixIndex"], result["fullStart"])
        self.assertEqual(result["reviewIndex"], -1)
        self.assertLess(result["matrixIndex"], result["fullEnd"])

    def test_direct_browse_does_not_offer_self_assessment_that_cannot_succeed(self):
        setup = r'''
const rightPane = {innerHTML:''};
globalThis.window = {addEventListener(){}};
globalThis.document = {getElementById:id => id === 'modal-right-content' ? rightPane : null, querySelectorAll:() => []};
globalThis.processMarkdownWithMath = text => '<p>' + text + '</p>';
globalThis.resolveRenderedImageSources = html => html;
globalThis.renderSolutionReviewCard = () => '<aside class="solution-review-card">維護資訊</aside>';
globalThis.renderScenarioMatrix = () => '';
globalThis.renderDagTracerCard = () => '';
'''
        expression = r'''
(() => {
  currentModalQid='EE-Q'; currentSolutionSourceMode='browse'; currentSolutionRecallEntry=false; isActiveRecallMode=false;
  renderSubQuestionContent('完整詳解', null);
  return document.getElementById('modal-right-content').innerHTML;
})()
'''
        result = run_node(["src/components/solutionModal.js"], expression, setup)
        self.assertNotIn('sm2-rating-bar', result)
        self.assertNotIn('solution-review-card', result)


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
