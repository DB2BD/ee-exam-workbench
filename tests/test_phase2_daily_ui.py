# -*- coding: utf-8 -*-
"""第二階段 C 批次：每日練習入口與 session UI 行為契約。"""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDailyPracticeUI(unittest.TestCase):
    def run_node(self, expression):
        practice_store = (ROOT / "src/state/practiceStore.js").read_text(encoding="utf-8")
        question_record = (ROOT / "src/domain/questionRecord.js").read_text(encoding="utf-8")
        daily_ui = (ROOT / "src/components/dailyPractice.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const nodes = new Map();
function node(id) {{
  if (!nodes.has(id)) nodes.set(id, {{id, value:'', innerHTML:'', querySelector:()=>null,
    querySelectorAll(selector) {{
      return typeof globalThis.__dailyQuerySelectorAll === 'function'
        ? globalThis.__dailyQuerySelectorAll(this, selector) : [];
    }}
  }});
  return nodes.get(id);
}}
globalThis.document = {{ getElementById: node, querySelector:()=>null }};
globalThis.localStorage = {{
  data: {{}},
  getItem(key) {{ return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; }},
  setItem(key, value) {{ this.data[key] = String(value); }}
}};
globalThis.showToast = () => {{}};
globalThis.openSolutionModal = (...args) => {{ globalThis.openSolutionArgs = args; }};
globalThis.QUESTION_CROP_MAP = {{'EE-a':'crop-a.png'}};
globalThis.resolveImageMapUrl = crop => '/assets/' + crop;
globalThis.currentExamCategory = 'PE';
globalThis.DB_DATA = {{
  subjects: [{{id:'01', name:'電路學', icon:'⚡'}}],
  questions: [
    ['EE-a','01',114,1,'題目 A',['A'],'solution-a','source-a',3,'verified',['A'],true],
    ['EE-b','01',114,2,'題目 B',['B'],'solution-b','source-b',3,'verified',['B'],true],
    ['EE-c','01',114,3,'題目 C',['C'],'solution-c','source-c',3,'verified',['C'],true]
  ]
}};
globalThis.NATIONAL_EXAMS_DATA = {{subjects:[], questions:[]}};
vm.runInThisContext({json.dumps(practice_store, ensure_ascii=False)});
vm.runInThisContext({json.dumps(question_record, ensure_ascii=False)});
vm.runInThisContext({json.dumps(daily_ui, ensure_ascii=False)});
globalThis.initDailyPracticeHome();
{expression}
"""
        completed = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_first_use_renders_start_form_and_category_scope(self):
        result = self.run_node(
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML}));"
        )
        self.assertIn("開始 3 題練習", result["html"])
        self.assertIn("daily-practice-category", result["html"])
        self.assertIn("daily-practice-subject", result["html"])

    def test_start_and_reload_keep_same_session_order(self):
        result = self.run_node(
            "dailyPracticeStart(); const first=node('daily-practice-container').innerHTML; "
            "const saved=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "dailyPracticeState=null; initDailyPracticeHome(); "
            "process.stdout.write(JSON.stringify({first, second:node('daily-practice-container').innerHTML, ids:saved.activeSession.questionIds}));"
        )
        self.assertEqual(len(result["ids"]), 3)
        self.assertIn("1 / 3", result["first"])
        self.assertIn("1 / 3", result["second"])

    def test_reload_restores_solution_view_and_dual_scroll_positions(self):
        result = self.run_node(
            "dailyPracticeStart(); dailyPracticeSetView('solution'); "
            "dailyPracticeScroll({currentTarget:{scrollTop:88}}); "
            "const saved=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "dailyPracticeState=null; initDailyPracticeHome(); "
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML, saved}));"
        )
        self.assertIn('daily-practice-tab active', result["html"])
        self.assertEqual(result["saved"]["activeSession"]["viewByQuestion"][result["saved"]["activeSession"]["questionIds"][0]], "solution")
        qid = result["saved"]["activeSession"]["questionIds"][0]
        self.assertEqual(result["saved"]["activeSession"]["scrollByQuestion"][qid]["solution"], 88)

    def test_production_bundle_contains_daily_practice_entry(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("// === src/state/practiceStore.js ===", html)
        self.assertIn("// === src/components/dailyPractice.js ===", html)
        self.assertIn('id="tab-btn-practice"', html)
        self.assertIn('id="daily-practice-container"', html)
        source = (ROOT / "src/components/dailyPractice.js").read_text(encoding="utf-8")
        self.assertIn("原題截圖載入失敗", source)
        self.assertIn("開啟官方原題 PDF", source)

    def test_question_topic_uses_the_production_math_renderer(self):
        """The real daily-practice call chain must not expose raw LaTeX."""
        script = r'''
const fs = require('fs'), vm = require('vm');
const nodes = new Map();
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {id, value:'', innerHTML:'', scrollTop:0, focus(){}, querySelector:()=>null});
  return nodes.get(id);
}
node('daily-practice-category').value = 'PE';
node('daily-practice-subject').value = 'all';
globalThis.window = {addEventListener(){}};
globalThis.document = {getElementById: node, querySelector:()=>null};
globalThis.localStorage = {
  data:{}, getItem(key){return this.data[key] ?? null;},
  setItem(key,value){this.data[key]=String(value);}
};
globalThis.showToast = () => {};
globalThis.currentExamCategory = 'PE';
globalThis.DB_DATA = {subjects:[{id:'02',name:'電子學',icon:'🔌'}], questions:[
  ['EE-111-02-3','02',111,3,'汲極電流 $3.17\\text{ mA}$，且 $R_S=30\\Omega$。',[], '', '',3,'verified',[],true]
]};
globalThis.NATIONAL_EXAMS_DATA = {subjects:[],questions:[]};
globalThis.katex = require('./libs/katex.min.js');
globalThis.marked = require('./libs/marked.min.js');
vm.runInThisContext(fs.readFileSync('src/renderers/katexRenderer.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/renderers/markdownRenderer.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/domain/questionRecord.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/state/practiceStore.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/components/dailyPractice.js','utf8'));
dailyPracticeStart();
const html = node('daily-practice-container').innerHTML;
const visible = html.replace(/<annotation[\s\S]*?<\/annotation>/g,'').replace(/<[^>]+>/g,'');
process.stdout.write(JSON.stringify({html,visible}));
'''
        completed = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertIn('class="katex"', result["html"])
        self.assertNotIn(r"\text", result["visible"])
        self.assertNotIn(r"\Omega", result["visible"])

    def test_completed_round_shows_summary_and_practice_again(self):
        result = self.run_node(
            "dailyPracticeStart(); dailyPracticeAdvance(true); const before=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "dailyPracticeCompleteFromModal(5,4,before.activeSession.questionIds[0]); "
            "let step=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); dailyPracticeCompleteFromModal(5,4,step.activeSession.questionIds[step.activeSession.currentIndex]); "
            "step=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); dailyPracticeCompleteFromModal(5,4,step.activeSession.questionIds[step.activeSession.currentIndex]); "
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML, before}));"
        )
        self.assertIn("本輪完成摘要", result["html"])
        self.assertIn("再練 3 題", result["html"])

    def test_daily_practice_shows_original_crop_and_shared_recall_entry(self):
        result = self.run_node(
            "savePracticeSession(createPracticeSession('PE', 'all', ['EE-a'], {now: Date.now()})); "
            "initDailyPracticeHome(); const original=node('daily-practice-container').innerHTML; "
            "dailyPracticeSetView('solution'); "
            "process.stdout.write(JSON.stringify({original, solution:node('daily-practice-container').innerHTML}));"
        )
        self.assertIn('/assets/crop-a.png', result["original"])
        self.assertIn("原題截圖", result["original"])
        self.assertIn("開始四段蓋牌", result["original"])
        self.assertIn('data-daily-open-solution="recall"', result["original"])
        self.assertIn("開始四段蓋牌揭露", result["solution"])
        self.assertIn("直接看完整詳解", result["solution"])
        self.assertIn('data-daily-open-solution="recall"', result["solution"])
        self.assertIn('data-daily-open-solution="browse"', result["solution"])

    def test_daily_practice_exposes_explicit_completion_action_without_bypassing_recall(self):
        result = self.run_node(
            "dailyPracticeStart(); const before=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML, before}));"
        )
        self.assertIn("完成本題並進入下一題", result["html"])
        self.assertIn("暫存本題進度", result["html"])
        self.assertIn('data-daily-open-solution="recall"', result["html"])
        self.assertEqual(result["before"]["activeSession"]["currentIndex"], 0)
        self.assertEqual(result["before"]["completionByQuestion"], {})

    def test_daily_practice_last_question_uses_round_summary_action_label(self):
        result = self.run_node(
            "savePracticeSession(createPracticeSession('PE', 'all', ['EE-a','EE-b','EE-c'], {now: Date.now()})); "
            "const loaded=loadDailyPracticeStore(); loaded.state.activeSession.currentIndex=2; "
            "savePracticeSession(loaded.state.activeSession); initDailyPracticeHome(); "
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML}));"
        )
        self.assertIn("完成本題並查看本輪摘要", result["html"])

    def test_completion_action_only_opens_recall_and_does_not_commit(self):
        result = self.run_node(
            "globalThis.__buttons=[]; globalThis.__dailyQuerySelectorAll=(element, selector) => { "
            "if (element.id !== 'daily-practice-container' || selector !== '[data-daily-open-solution]' "
            "|| !element.innerHTML.includes('data-daily-completion-action=\\\"true\\\"')) return []; "
            "const button={dataset:{dailyOpenSolution:'recall', dailyCompletionAction:'true'}, addEventListener(type, handler){this.handler=handler; __buttons.push(this);}}; "
            "return [button]; }; "
            "dailyPracticeStart(); const before=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "__buttons[0].handler({}); const after=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML, args:openSolutionArgs, before, after}));"
        )
        self.assertIn('data-daily-completion-action="true"', result["html"])
        self.assertIn(
            'data-daily-completion-action="true" data-daily-open-solution="recall"',
            result["html"],
        )
        self.assertEqual(result["args"][4], {"mode": "daily-practice", "recall": True})
        self.assertEqual(result["before"]["activeSession"]["currentIndex"], result["after"]["activeSession"]["currentIndex"])
        self.assertEqual(result["after"]["completionByQuestion"], {})

    def test_summary_exposes_assessment_and_explicit_follow_up_action(self):
        source = (ROOT / "src/components/dailyPractice.js").read_text(encoding="utf-8")
        self.assertIn("dailyPracticeSummaryRows", source)
        self.assertIn("加入到期複習", source)
        self.assertIn("scheduleDailyPracticeFollowUp", source)

    def test_defer_does_not_move_or_complete_current_question(self):
        result = self.run_node(
            "dailyPracticeStart(); const before=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "dailyPracticeAdvance(true); const after=JSON.parse(localStorage.data.EE_EXAM_DAILY_PRACTICE_V1); "
            "process.stdout.write(JSON.stringify({before,after}));"
        )
        self.assertEqual(result["before"]["activeSession"]["currentIndex"], result["after"]["activeSession"]["currentIndex"])
        self.assertEqual(result["after"]["completionByQuestion"], {})

    def test_production_facet_wiring_keeps_chapter_and_type_independent(self):
        result = self.run_node(
            "globalThis.getQuestionFacetIds=()=>['el-bjt']; "
            "globalThis.getQuestionFacetLabel=()=> 'BJT 章節'; "
            "const q=DB_DATA.questions[0].slice(); q[10]=['S = VI*']; "
            "process.stdout.write(JSON.stringify({chapter:dailyPracticeFacet(q,'chapter'),type:dailyPracticeFacet(q,'type')}));"
        )
        self.assertEqual(result["chapter"], "el-bjt")
        self.assertEqual(result["type"], "complex-power")
        self.assertNotEqual(result["chapter"], result["type"])

    def test_unmapped_formula_string_does_not_create_fake_type_diversity(self):
        result = self.run_node(
            "const q=DB_DATA.questions[0].slice(); q[10]=['任意未驗證公式']; "
            "process.stdout.write(JSON.stringify(dailyPracticeFacet(q,'type')));"
        )
        self.assertEqual(result, "unknown")

    def test_production_path_interleaves_two_known_types_in_one_chapter(self):
        result = self.run_node(
            "globalThis.getQuestionFacetIds=()=>['em-machines']; "
            "const base=DB_DATA.questions[0]; "
            "const qs=['a','b','c','d'].map((id,i)=>{const q=base.slice();q[0]='EE-'+id;q[10]=i<2?['S = VI*']:['s = (Ns - N)/Ns'];return q;}); "
            "const ids=createDailyPracticeQueue(qs,{count:3,random:()=>0,chapterOf:q=>dailyPracticeFacet(q,'chapter'),typeOf:q=>dailyPracticeFacet(q,'type')}); "
            "process.stdout.write(JSON.stringify(ids.map(id=>dailyPracticeFacet(qs.find(q=>q[0]===id),'type'))));"
        )
        self.assertIn("complex-power", result)
        self.assertIn("induction-slip", result)


if __name__ == "__main__":
    unittest.main()
