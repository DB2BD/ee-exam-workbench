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
        daily_ui = (ROOT / "src/components/dailyPractice.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const nodes = new Map();
function node(id) {{
  if (!nodes.has(id)) nodes.set(id, {{id, value:'', innerHTML:'', querySelector:()=>null}});
  return nodes.get(id);
}}
globalThis.document = {{ getElementById: node, querySelector:()=>null }};
globalThis.localStorage = {{
  data: {{}},
  getItem(key) {{ return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; }},
  setItem(key, value) {{ this.data[key] = String(value); }}
}};
globalThis.showToast = () => {{}};
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

    def test_production_bundle_contains_daily_practice_entry(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("// === src/state/practiceStore.js ===", html)
        self.assertIn("// === src/components/dailyPractice.js ===", html)
        self.assertIn('id="tab-btn-practice"', html)
        self.assertIn('id="daily-practice-container"', html)

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
            "dailyPracticeStart(); dailyPracticeAdvance(true); dailyPracticeAdvance(true); dailyPracticeAdvance(true); "
            "process.stdout.write(JSON.stringify({html:node('daily-practice-container').innerHTML}));"
        )
        self.assertIn("本輪完成摘要", result["html"])
        self.assertIn("再練 3 題", result["html"])


if __name__ == "__main__":
    unittest.main()
