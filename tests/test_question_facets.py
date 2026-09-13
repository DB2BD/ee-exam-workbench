# -*- coding: utf-8 -*-
"""Behavioral tests for the question-list taxonomy facet seam."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestQuestionFacets(unittest.TestCase):
    """Exercise facet behavior without coupling to DOM markup."""

    @classmethod
    def setUpClass(cls):
        cls.script = r'''
const fs = require('fs'), vm = require('vm');
const ctx = { console };
vm.createContext(ctx);
for (const file of [
  'dashboard-data.js',
  'national-exams-data.js',
  'src/data/knowledge-dag.js',
  'src/data/knowledge-dag.generated.js',
  'src/components/questionList.js',
]) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
const expression = process.argv[1];
const result = vm.runInContext(expression, ctx);
process.stdout.write(JSON.stringify(result));
'''

    def run_js(self, expression):
        completed = subprocess.run(
            ["node", "-e", self.script, expression],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout.splitlines()[-1])

    def test_primary_taxonomy_facet_finds_bjt_question(self):
        result = self.run_js(
            "buildQuestionFacetModel(DB_DATA.questions, {"
            "examFamily:'PE', subject:'02', year:'all', difficulty:'all', "
            "status:'all', searchText:'', quickFilter:'all', progressState:{}, "
            "starredState:{}, facetTag:'el-bjt-bias-small-signal', includeSecondary:false"
            "}).questions.map(q => q[0])"
        )
        self.assertIn("EE-112-02-1", result)

    def test_secondary_facet_inclusion_is_unique_by_qid(self):
        result = self.run_js(
            "(() => { const q = DB_DATA.questions.find(q => q[0] === 'EE-112-02-1'); "
            "const model = buildQuestionFacetModel([q, q], {examFamily:'PE', subject:'02', "
            "year:'all', difficulty:'all', status:'all', searchText:'', quickFilter:'all', "
            "progressState:{}, starredState:{}, facetTag:'el-active-filter', includeSecondary:true}); "
            "return {qids:model.questions.map(q => q[0]), count:model.facets.find(f => f.id === 'el-active-filter').count}; })()"
        )
        self.assertEqual(result, {"qids": ["EE-112-02-1"], "count": 1})

    def test_facet_counts_match_click_result_under_same_nonfacet_filters(self):
        result = self.run_js(
            "(() => { const opts = {examFamily:'PE', subject:'02', year:'112', difficulty:'all', "
            "status:'all', searchText:'電晶體', quickFilter:'all', progressState:{}, starredState:{}, "
            "facetTag:null, includeSecondary:true}; const model = buildQuestionFacetModel(DB_DATA.questions, opts); "
            "return model.facets.map(f => { const qids=buildQuestionFacetModel(DB_DATA.questions, {...opts, facetTag:f.id}).questions.map(q => q[0]); "
            "return {id:f.id, count:f.count, resultCount:qids.length, uniqueResultCount:new Set(qids).size}; }); })()"
        )
        self.assertTrue(result)
        self.assertTrue(all(
            row["count"] == row["resultCount"] == row["uniqueResultCount"]
            for row in result
        ))

    def test_switching_subject_clears_facet_and_secondary_state(self):
        result = self.run_js(
            "(() => { setQuestionFacetState('el-mosfet-bias-small-signal', true); "
            "updateQuestionFacetContext('PE', '02'); updateQuestionFacetContext('PE', '04'); "
            "return getQuestionFacetState(); })()"
        )
        self.assertEqual(result, {"activeFacetTag": None, "includeSecondary": False})

    def test_gk_uses_its_own_canonical_facet_even_when_text_differs(self):
        result = self.run_js(
            "(() => { const q = ['GK-114-02-1', '02', 114, 1, 'MOSFET 放大器題目', ['MOSFET'], '', '', 3, 'pending', [], false]; "
            "const model = buildQuestionFacetModel([q], {examFamily:'GK', subject:'02', year:'all', difficulty:'all', status:'all', searchText:'', quickFilter:'all', progressState:{}, starredState:{}, facetTag:null, includeSecondary:true}); "
            "return {ids:getQuestionFacetIds(q, true, 'GK'), facets:model.facets, unclassified:model.unclassifiedCount}; })()"
        )
        self.assertEqual(result["ids"], ["gk-el-opamp-ideal"])
        self.assertEqual(result["facets"][0]["id"], "gk-el-opamp-ideal")
        self.assertEqual(result["unclassified"], 0)


if __name__ == "__main__":
    unittest.main()
