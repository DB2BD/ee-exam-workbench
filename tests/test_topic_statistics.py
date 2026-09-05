# -*- coding: utf-8 -*-
"""Behavioral tests for statistics and study-entry data seams."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestTopicStatistics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = r'''
const fs = require('fs'), vm = require('vm');
const elements = new Map([
  ['filter-subject', { value: 'all' }],
  ['filter-year', { value: 'all' }],
  ['filter-status', { value: 'all' }],
  ['filter-diff', { value: 'all' }],
  ['search-input', { value: '' }],
  ['filtered-count', { innerText: '' }],
  ['facet-filter-bar', { style: {}, innerHTML: '' }],
  ['questions-container', { innerHTML: '' }],
  ['top-topics-container', { innerHTML: '' }],
  ['layers-container', { innerHTML: '' }],
]);
const ctx = {
  console,
  document: { getElementById: id => elements.get(id) || null },
  localStorage: { setItem() {} },
  currentExamCategory: 'PE',
  progressState: {},
  starredState: {},
  activeQuickFilter: 'all',
};
vm.createContext(ctx);
for (const file of [
  'dashboard-data.js',
  'national-exams-data.js',
  'src/data/knowledge-dag.js',
  'src/components/questionList.js',
  'src/components/topTopics.js',
]) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
const result = vm.runInContext(process.argv[1], ctx);
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

    def test_small_dataset_has_hand_calculable_question_and_year_percentages(self):
        result = self.run_js(
            "(() => { const q = DB_DATA.questions.find(q => q[0] === 'EE-112-02-1'); "
            "const model = buildTopicStatistics([q], {examFamily:'PE', subject:'02', year:'all', "
            "difficulty:'all', status:'all', searchText:'', quickFilter:'all', progressState:{}, "
            "starredState:{}, dueQuestionIds:[], selectedYears:[112, 113, 114]}); "
            "return {denominator:model.denominator, years:model.selectedYears, item:model.items[0]}; })()"
        )
        self.assertEqual(result["denominator"], 1)
        self.assertEqual(result["years"], [112, 113, 114])
        self.assertEqual(result["item"]["id"], "el-bjt-bias-small-signal")
        self.assertEqual(result["item"]["count"], 1)
        self.assertEqual(result["item"]["questionPct"], 100)
        self.assertEqual(result["item"]["yearCoveragePct"], 33)

    def test_search_does_not_shrink_year_coverage_denominator(self):
        result = self.run_js(
            "(() => { const q112 = DB_DATA.questions.find(q => q[0] === 'EE-112-02-1'); "
            "const q113 = DB_DATA.questions.find(q => q[0] === 'EE-113-02-2'); "
            "const q114 = ['EE-test-114', '02', 114, 1, 'needle topic', ['needle'], '', '', 1, 'verified', [], false]; "
            "Object.assign(QUESTION_TAXONOMY_MAP, {'EE-test-114': {primaryChapter:'el-bjt-bias-small-signal'}}); "
            "const records = [q112, q113, q114]; "
            "const common = {examFamily:'PE', subject:'02', difficulty:'all', status:'all', quickFilter:'all', progressState:{}, starredState:{}, dueQuestionIds:[]}; "
            "const searched = buildTopicStatistics(records, {...common, year:'all', searchText:'needle'}); "
            "const singleYear = buildTopicStatistics(records, {...common, year:'112', searchText:''}); "
            "const empty = buildTopicStatistics(records, {...common, year:'all', searchText:'not-found'}); "
            "return {searched:{years:searched.selectedYears, denominator:searched.denominator, item:searched.items.find(i => i.id === 'el-bjt-bias-small-signal')}, singleYear:singleYear.selectedYears, empty:{years:empty.selectedYears, denominator:empty.denominator, items:empty.items}}; })()"
        )
        self.assertEqual(result["searched"]["years"], [112, 113, 114])
        self.assertEqual(result["searched"]["denominator"], 1)
        self.assertEqual(result["searched"]["item"]["yearCoveragePct"], 33)
        self.assertEqual(result["singleYear"], [112])
        self.assertEqual(result["empty"], {"years": [112, 113, 114], "denominator": 0, "items": []})

    def test_real_pe_bjt_stat_and_click_share_exact_qids(self):
        result = self.run_js(
            "(() => { const opts = {examFamily:'PE', subject:'all', year:'all', difficulty:'all', "
            "status:'all', searchText:'', quickFilter:'all', progressState:{}, starredState:{}, dueQuestionIds:[]}; "
            "const stat = buildTopicStatistics(DB_DATA.questions, opts).items.find(i => i.id === 'el-bjt-bias-small-signal'); "
            "const clicked = getFilteredQuestionRecords(DB_DATA.questions, {...opts, facetTag:stat.id, includeSecondary:false}).map(q => q[0]); "
            "return {stat:stat.qids, clicked}; })()"
        )
        self.assertIn("EE-112-02-1", result["stat"])
        self.assertEqual(result["stat"], result["clicked"])

    def test_gk_with_similar_text_is_explicitly_empty_statistics(self):
        result = self.run_js(
            "(() => { const q = ['GK-114-02-1', '02', 114, 1, 'MOSFET 放大器', ['MOSFET'], '', '', 3, 'pending', [], false]; "
            "return buildTopicStatistics([q], {examFamily:'GK', subject:'02', year:'all', difficulty:'all', "
            "status:'all', searchText:'', quickFilter:'all', progressState:{}, starredState:{}, dueQuestionIds:[]}); })()"
        )
        self.assertEqual(result["items"], [])
        self.assertTrue(result["empty"])
        self.assertEqual(result["message"], "no-formal-taxonomy")

    def test_empty_range_has_zero_denominator_and_no_items(self):
        result = self.run_js(
            "buildTopicStatistics([], {examFamily:'PE', subject:'all', year:'all', difficulty:'all', "
            "status:'all', searchText:'', quickFilter:'all', progressState:{}, starredState:{}, dueQuestionIds:[]})"
        )
        self.assertEqual(result["denominator"], 0)
        self.assertEqual(result["items"], [])
        self.assertTrue(result["empty"])

    def test_study_actions_resolve_expected_unique_qids(self):
        records = [
            ["EE-a", "01", 114, 1, "A", ["a", "b", "c", "d"], "", "", 5, "verified", ["formula"], True],
            ["EE-a", "01", 114, 1, "A duplicate", ["a"], "", "", 5, "verified", [], True],
            ["EE-b", "01", 113, 2, "B", ["b"], "", "", 2, "verified", [], False],
            ["EE-c", "01", 112, 3, "C", ["c", "d"], "", "", 1, "verified", [], False],
        ]
        expression = (
            "(() => { const records = " + json.dumps(records, ensure_ascii=False) + "; "
            "const opts={examFamily:'PE', subject:'all', year:'all', difficulty:'all', status:'all', searchText:'', progressState:{'EE-b':2}, starredState:{}, dueQuestionIds:['EE-c']}; "
            "return ['all','formula','dedicated','review','top10','due'].reduce((out, action) => { out[action]=resolveStudyAction(action, records, opts).map(q=>q[0]); return out; }, {}); })()"
        )
        self.assertEqual(self.run_js(expression), {
            "all": ["EE-a", "EE-b", "EE-c"],
            "formula": ["EE-a", "EE-c"],
            "dedicated": ["EE-a"],
            "review": ["EE-b"],
            "top10": ["EE-a"],
            "due": ["EE-b", "EE-c"],
        })

    def test_render_questions_refreshes_derived_views_for_empty_and_nonempty_results(self):
        result = self.run_js(
            "(() => { let records = []; let refreshes = 0; "
            "getActiveQuestionsList = () => records; "
            "refreshAnalysisViews = () => { refreshes += 1; }; "
            "renderQuestionTopic = topic => topic; "
            "renderQuestions(); records = [['EE-test', '01', 114, 1, '測試', [], '', '', 1, 'verified', [], false]]; "
            "document.getElementById('filter-year').value = '114'; renderQuestions(); "
            "return refreshes; })()"
        )
        self.assertEqual(result, 2)

    def test_focus_stats_topic_applies_the_same_chapter_qid_filter(self):
        result = self.run_js(
            "(() => { const opts = {examFamily:'PE', subject:'all', year:'112', difficulty:'all', "
            "status:'all', searchText:'EE-112', quickFilter:'all', progressState:{}, starredState:{}, dueQuestionIds:[]}; "
            "const stat = buildTopicStatistics(DB_DATA.questions, opts).items.find(i => i.id === 'el-bjt-bias-small-signal'); "
            "renderQuestions = () => {}; switchTab = () => {}; focusStatsTopic(stat.id); "
            "const active = getQuestionFacetState().activeFacetTag; "
            "const clicked = getFilteredQuestionRecords(DB_DATA.questions, {...opts, facetTag:active, includeSecondary:false}).map(q => q[0]); "
            "return {active, stat:stat.qids, clicked}; })()"
        )
        self.assertEqual(result["active"], "el-bjt-bias-small-signal")
        self.assertEqual(result["stat"], result["clicked"])


if __name__ == "__main__":
    unittest.main()
