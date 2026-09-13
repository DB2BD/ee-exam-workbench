# -*- coding: utf-8 -*-
"""Weakness view filter and drill-down rendering tests."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestWeaknessView(unittest.TestCase):
    def _run(self, expression, setup):
        source = (ROOT / "src/components/weaknessView.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const context = {{console}};
vm.createContext(context);
vm.runInContext({json.dumps(setup, ensure_ascii=False)}, context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def setup(self):
        return r"""
const element={id:'weakness-view',innerHTML:''};
globalThis.document={getElementById:id=>id==='weakness-view'?element:null};
globalThis.currentExamCategory='PE';
globalThis.knowledgeIssueReadLog=family=>({ok:true,log:{examFamily:family,events:[],graphRevisions:[]}});
globalThis.CANONICAL_KNOWLEDGE_GRAPH={graphRevision:'kg-v1-test'};
globalThis.buildWeaknessProjection=(log,options)=>{ globalThis.lastWeaknessOptions=options; return {nodes:[{nodeId:'pe-node',title:'PE 問題',role:'primary',rawCount:2,distinctQids:1,lastSeen:'2026-09-12',confirmationRate:1,reviewState:'corrected',historicalNodeIds:['old-node'],nextAction:{label:'進入知識回想'},events:[{eventId:'e2',qid:'EE-114-01-2',recordedAt:'2026-09-12',errorType:'觀念混淆',customText:'我卡在邊界條件',evidence:['題目條件']}],supersessionChain:[{eventId:'e1',eventType:'confirm',recordedAt:'2026-09-11',effective:false,nodeIds:['old-node']},{eventId:'e2',eventType:'correct',recordedAt:'2026-09-12',effective:true,nodeIds:['pe-node']}],traceStatus:'complete'}],pendingClassification:{count:1,events:[{eventId:'e3',qid:'EE-114-01-3',eventType:'skip',recordedAt:'2026-09-12',customText:'這題目前完全沒有頭緒',evidence:[]}]},totals:{effectiveEventCount:3}}; };
"""

    def test_renders_filters_pending_and_drilldown(self):
        result = self._run("(() => { const projection=renderWeaknessView({now:'2026-09-13'}); return {projection,html:document.getElementById('weakness-view').innerHTML}; })()", self.setup())
        self.assertIn("data-weakness-range=\"7d\"", result["html"])
        self.assertIn("data-weakness-range=\"30d\"", result["html"])
        self.assertIn("data-weakness-range=\"all\"", result["html"])
        self.assertIn("EE-114-01-2", result["html"])
        self.assertIn("題目條件", result["html"])
        self.assertIn("我卡在邊界條件", result["html"])
        self.assertIn("這題目前完全沒有頭緒", result["html"])
        self.assertIn("待分類事件（1）", result["html"])
        self.assertIn("診斷狀態：corrected", result["html"])
        self.assertIn("weakness-supersession-trace", result["html"])
        self.assertIn("歷史事件（1）", result["html"])
        self.assertIn("e1", result["html"])

    def test_family_and_range_controls_update_state(self):
        result = self._run("(() => { renderWeaknessView(); setWeaknessFamily('GK'); setWeaknessRange('all'); return document.getElementById('weakness-view').innerHTML; })()", self.setup())
        self.assertIn("data-weakness-family=\"GK\"", result)
        self.assertIn("data-weakness-range=\"all\"", result)

    def test_user_render_passes_a_live_iso_time_anchor(self):
        result = self._run("(() => { renderWeaknessView(); return globalThis.lastWeaknessOptions; })()", self.setup())
        self.assertRegex(result.get("now", ""), r"^\d{4}-\d{2}-\d{2}T")


if __name__ == "__main__":
    unittest.main()
