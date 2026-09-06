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


if __name__ == "__main__":
    unittest.main()
