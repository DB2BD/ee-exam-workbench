# -*- coding: utf-8 -*-
"""Post-submit diagnosis card and navigation gating tests."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDiagnosisUI(unittest.TestCase):
    def _run(self, expression, setup="", include_issue_store=False):
        sources = []
        if include_issue_store:
            sources.append((ROOT / "src/state/knowledgeIssueStore.js").read_text(encoding="utf-8"))
        sources.append((ROOT / "src/components/solutionModal.js").read_text(encoding="utf-8"))
        source = "\n".join(sources)
        script = f"""
const vm = require('vm');
const storageData = {{}};
const localStorage = {{
  getItem:key=>Object.prototype.hasOwnProperty.call(storageData,key) ? storageData[key] : null,
  setItem:(key,value)=>{{storageData[key]=String(value);}},
}};
const context = {{console,localStorage}};
vm.createContext(context);
vm.runInContext({json.dumps(setup, ensure_ascii=False)}, context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def _setup(self, diagnosis="candidate"):
        diagnosis_value = {
            "diagnosisVersion": "knowledge-diagnosis.v1",
            "attemptId": "attempt-1",
            "graphRevision": "kg-v1-test",
            "status": "mapped" if diagnosis == "candidate" else "clear",
            "likelyQuestions": [{"nodeId": "pe-node", "title": "前置機制", "nodeType": "mechanism", "why": "證據指出概念邊界。", "confidence": 0.9, "evidence": ["test"]}] if diagnosis == "candidate" else [],
            "firstPrerequisiteGap": {"nodeId": "pe-prereq", "title": "更早前提", "why": "先具備這個前提。", "confidence": 0.8, "evidence": ["test"]} if diagnosis == "candidate" else None,
            "reason": "請確認最符合的問題點。" if diagnosis == "candidate" else "沒有診斷訊號。",
            "reasonCode": "evidence-backed-candidates" if diagnosis == "candidate" else "no-error-signal",
            "confidence": 0.9 if diagnosis == "candidate" else 1,
            "needsConfirmation": diagnosis == "candidate",
        }
        return f"""
const elements = new Map();
function element(id) {{
  if (!elements.has(id)) elements.set(id, {{id, innerHTML:'', style:{{}}, classList:{{add(){{}},remove(){{}}}}, querySelectorAll:()=>[], insertAdjacentHTML(_position, html){{this.innerHTML += html; globalThis.__diagnosisHtml = this.innerHTML;}}}});
  return elements.get(id);
}}
globalThis.document = {{body:{{style:{{}}}}, getElementById:element, querySelectorAll:()=>[], activeElement:null}};
globalThis.window = {{addEventListener(){{}}}};
globalThis.findQuestionRecord = () => ['EE-114-01-2','01',114,2,'題目',[],'','',3,'verified',[],true];
globalThis.toQuestionRecord = q => ({{id:q[0],examFamily:'PE',subjectId:'01',stem:'題目'}});
globalThis.submitLearningAttempt = () => ({{ok:true,duplicate:false,nextReviewDate:'2026-09-14',nextAction:{{type:'refresh-review'}}}});
globalThis.diagnose = () => ({json.dumps(diagnosis_value, ensure_ascii=False)});
globalThis.setTimeout = fn => {{ globalThis.__scheduled = fn; return 1; }};
globalThis.clearTimeout = () => {{}};
globalThis.showToast = message => {{ globalThis.__toast = message; }};
globalThis.updateModalStatusButtons = () => {{}};
globalThis.renderQuestions = () => {{}};
globalThis.renderReviewPage = () => {{}};
globalThis.getRecallState = () => ({{level:1,lastAchieved:1}});
globalThis.CANONICAL_KNOWLEDGE_GRAPH = {{graphRevision:'kg-v1-test'}};
globalThis.progressState = {{}};
globalThis.starredState = {{}};
"""

    def test_committed_candidate_stops_auto_advance_and_exposes_four_outcomes(self):
        setup = self._setup("candidate")
        result = self._run(r"""
(() => {
  currentModalQid='EE-114-01-2'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt-1';
  submitSM2Rating(3);
  return {html:globalThis.__diagnosisHtml || '',scheduled:Boolean(globalThis.__scheduled)};
})()
""", setup)
        self.assertIn("確認主要問題並保存", result["html"])
        self.assertIn("都不是", result["html"])
        self.assertIn("保存診斷並到下一題", result["html"])
        self.assertIn("查看診斷說明", result["html"])
        self.assertIn("先補哪個前提", result["html"])
        self.assertIn("回到主線", result["html"])
        self.assertIn("改選問題點並保存", result["html"])
        self.assertIn("保存『都不是』並繼續", result["html"])
        self.assertIn("保存診斷並到下一題", result["html"])
        self.assertIn("請按下方含「保存」的按鈕", result["html"])
        self.assertFalse(result["scheduled"])

    def test_skip_records_explicit_outcome_then_allows_advance(self):
        setup = self._setup("candidate") + "\nglobalThis.appendKnowledgeIssueEvent = event => { globalThis.__event = event; return {ok:true}; };\n"
        result = self._run(r"""
(() => {
  currentModalQid='EE-114-01-2'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt-1';
  submitSM2Rating(3);
  const saved = resolveKnowledgeDiagnosis('skip');
  return {saved, event:globalThis.__event, scheduled:Boolean(globalThis.__scheduled)};
})()
""", setup)
        self.assertTrue(result["saved"])
        self.assertEqual(result["event"]["eventType"], "skip")
        self.assertEqual(result["event"]["primaryKnowledgeNodeId"], None)
        self.assertTrue(result["scheduled"])

    def test_typed_reason_is_saved_through_real_issue_store(self):
        setup = self._setup("candidate") + r"""
globalThis.CANONICAL_KNOWLEDGE_GRAPH.nodes={
  'pe-node':{nodeId:'pe-node',examFamily:'PE',lifecycle:'active'},
  'pe-prereq':{nodeId:'pe-prereq',examFamily:'PE',lifecycle:'active'}
};
localStorage.setItem('EE_EXAM_ATTEMPT_ENVELOPES_V1',JSON.stringify({schemaVersion:'learning-attempts.v1',attempts:{'attempt-1':{sessionId:'attempt-1',status:'committed',qid:'EE-114-01-2',examFamily:'PE'}}}));
globalThis.ack = () => ({ok:true});
"""
        result = self._run(r"""
(() => {
  currentModalQid='EE-114-01-2'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt-1';
  submitSM2Rating(3);
  document.getElementById('diagnosis-custom-text').value='我卡在邊界條件';
  const saved = resolveKnowledgeDiagnosis('confirm');
  const log = JSON.parse(localStorage.getItem('EE_KNOWLEDGE_ISSUES_PE_V1'));
  return {saved, event:log.events[0], toast:globalThis.__toast};
})()
""", setup, include_issue_store=True)
        self.assertTrue(result["saved"])
        self.assertEqual(result["event"]["customText"], "我卡在邊界條件")
        self.assertIn("診斷與補充說明已保存", result["toast"])

    def test_missing_issue_store_keeps_diagnosis_open_without_claiming_save(self):
        setup = self._setup("candidate")
        result = self._run(r"""
(() => {
  currentModalQid='EE-114-01-2'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt-1';
  submitSM2Rating(3);
  document.getElementById('diagnosis-custom-text').value='我卡在邊界條件';
  const saved = resolveKnowledgeDiagnosis('confirm');
  return {saved, scheduled:Boolean(globalThis.__scheduled), toast:globalThis.__toast};
})()
""", setup)
        self.assertFalse(result["saved"])
        self.assertFalse(result["scheduled"])
        self.assertIn("診斷保存功能尚未載入", result["toast"])

    def test_commit_failure_never_renders_diagnosis_card(self):
        setup = self._setup("candidate").replace(
            "globalThis.submitLearningAttempt = () => ({ok:true,duplicate:false,nextReviewDate:'2026-09-14',nextAction:{type:'refresh-review'}});",
            "globalThis.submitLearningAttempt = () => ({ok:false,duplicate:false,message:'未提交'});",
        )
        result = self._run(r"""
(() => {
  currentModalQid='EE-114-01-2'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt-1';
  submitSM2Rating(3);
  return {html:globalThis.__diagnosisHtml || '',scheduled:Boolean(globalThis.__scheduled)};
})()
""", setup)
        self.assertEqual(result, {"html": "", "scheduled": False})

    def test_clear_happy_path_keeps_fast_advance(self):
        setup = self._setup("clear")
        result = self._run(r"""
(() => {
  currentModalQid='EE-114-01-2'; currentSolutionSourceMode='due-review'; currentSolutionRecallEntry=true;
  currentRecallAchievedLevel=4; currentLearningAttemptId='attempt-1';
  submitSM2Rating(5);
  return {html:globalThis.__diagnosisHtml || '',scheduled:Boolean(globalThis.__scheduled)};
})()
""", setup)
        self.assertEqual(result["html"], "")
        self.assertTrue(result["scheduled"])

    def test_diagnosis_card_focuses_reason_input_for_immediate_typing(self):
        setup = r"""
const elements = new Map();
const reasonInput = {id:'diagnosis-custom-text', focus(){ globalThis.__focusedId = this.id; }};
const rightPane = {
  innerHTML:'',
  insertAdjacentHTML(_position, html) {
    this.innerHTML += html;
    elements.set('diagnosis-custom-text', reasonInput);
  }
};
globalThis.document = {
  getElementById(id) { return id === 'modal-right-content' ? rightPane : elements.get(id) || null; },
  querySelector() { return null; }
};
globalThis.window = {addEventListener(){}};
"""
        result = self._run(r"""
(() => {
  renderKnowledgeDiagnosisCard({
    reason:'請補充卡住的步驟。', confidence:.9,
    likelyQuestions:[], firstPrerequisiteGap:null,
  });
  return globalThis.__focusedId || null;
})()
""", setup)
        self.assertEqual(result, "diagnosis-custom-text")

    def test_diagnosis_helper_buttons_show_guidance_inside_card(self):
        setup = r"""
const elements = new Map();
const guidance = {id:'diagnosis-guidance', hidden:true, innerHTML:''};
const reasonInput = {id:'diagnosis-custom-text', focus(){}};
const rightPane = {
  innerHTML:'',
  insertAdjacentHTML(_position, html) {
    this.innerHTML += html;
    elements.set('diagnosis-custom-text', reasonInput);
    elements.set('diagnosis-guidance', guidance);
  }
};
globalThis.document = {
  getElementById(id) { return id === 'modal-right-content' ? rightPane : elements.get(id) || null; },
  querySelector() { return null; }
};
globalThis.window = {addEventListener(){}};
globalThis.showToast = message => { globalThis.__toast = message; };
globalThis.switchTab = tab => { globalThis.__tab = tab; };
"""
        result = self._run(r"""
(() => {
  currentKnowledgeDiagnosis={
    reason:'系統根據作答證據判斷你可能卡在核心機制。',
    likelyQuestions:[{nodeId:'pe-node',title:'核心機制',evidence:['題目條件']}],
    firstPrerequisiteGap:{nodeId:'pe-prereq',title:'前置觀念',why:'先補這個觀念。'}
  };
  renderKnowledgeDiagnosisCard(currentKnowledgeDiagnosis);
  const actions=[openDiagnosisWhyStuck,openDiagnosisPrerequisite,openDiagnosisMainline];
  const outputs=actions.map(action => {
    guidance.hidden=true; guidance.innerHTML='';
    const returned=action();
    return {returned,hidden:guidance.hidden,html:guidance.innerHTML};
  });
  return {outputs,tab:globalThis.__tab};
})()
""", setup)
        self.assertTrue(all(item["returned"] for item in result["outputs"]))
        self.assertTrue(all(not item["hidden"] for item in result["outputs"]))
        self.assertTrue(all(item["html"] for item in result["outputs"]))
        self.assertEqual(result["tab"], "dag")

    def test_unknown_mapping_explains_a_learning_next_step(self):
        setup = self._setup("candidate") + r"""
globalThis.QUESTION_TAXONOMY_MAP = {
  'EE-110-04-5': {
    primaryChapter: 'emach-induction-motor-torque',
    canonicalChapter: '感應電動機啟動電抗器與啟動轉矩'
  }
};
globalThis.KNOWLEDGE_DAG = {
  'emach-induction-motor-torque': {name:'感應電動機轉矩與轉差率'}
};
"""
        result = self._run(r"""
(() => {
  currentModalQid='EE-110-04-5';
  currentRecallErrorType='觀念混淆';
  currentKnowledgeDiagnosis={
    status:'unknown',
    reasonCode:'no-approved-question-link',
    reason:'目前沒有足夠證據把這題連到 canonical knowledge node。',
    likelyQuestions:[], firstPrerequisiteGap:null
  };
  renderKnowledgeDiagnosisCard(currentKnowledgeDiagnosis);
  const initial = globalThis.__diagnosisHtml || '';
  openDiagnosisWhyStuck();
  return {initial, guidance:elements.get('diagnosis-guidance').innerHTML};
})()
""", setup)
        self.assertIn("尚未完成圖譜對應", result["initial"])
        self.assertIn("感應電動機啟動電抗器與啟動轉矩", result["initial"])
        self.assertNotIn("canonical knowledge node", result["initial"])
        self.assertIn("待分類", result["initial"])
        self.assertIn("不會替你貼上錯誤標籤", result["guidance"])
        self.assertIn("觀念混淆", result["guidance"])
        self.assertIn("兩個概念", result["guidance"])
        self.assertIn("保存『都不是』並繼續", result["guidance"])


if __name__ == "__main__":
    unittest.main()
