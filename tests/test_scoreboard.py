# -*- coding: utf-8 -*-
"""Scoreboard (成績 tab) pure functions and rendering (WP6)."""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "src" / "data" / "questionPoints.generated.js",
    ROOT / "src" / "data" / "targetAllocation.generated.js",
    ROOT / "src" / "domain" / "studyPlan.js",
    ROOT / "src" / "components" / "scoreboard.js",
]

PRELUDE = """
const NOW = Date.UTC(2026, 9, 4, 4, 0, 0);
const DAY = 86400000;
function qidsOf(year, subj) { return Object.keys(QUESTION_POINTS).filter(q => q.startsWith('EE-' + year + '-' + subj + '-')); }
function rec(qid, o) {
  o = o || {};
  const total = QUESTION_POINTS[qid].total;
  const tier = studyTierFor(qid);
  const f = o.ratio === undefined ? 1 : o.ratio;
  return { id: 'r-' + qid + '-' + (o.at || 0) + (o.mockId || ''), qid, at: o.at || NOW - DAY, source: o.source || 'today',
    mockId: o.mockId, tier, parts: [{label: '整題', points: total, mark: 'o'}], errors: o.errors || [],
    total, estimate: total * f, legacy: o.legacy };
}
function mockRecs(mockId, year, subj, at, ratio, skip) {
  return qidsOf(year, subj).slice(skip ? 1 : 0).map(q => rec(q, {source: 'mock', mockId, at, ratio}));
}
"""


def run_node(expression, mock=False):
    sources = SOURCES[:-1] + [ROOT / "src" / "components" / "mockExam.js"] + SOURCES[-1:] if mock else SOURCES
    script = (
        "const vm = require('vm');\nconst context = {};\ncontext.globalThis = context;\nvm.createContext(context);\n"
        + "".join(
            f"vm.runInContext({json.dumps(p.read_text(encoding='utf-8'))}, context);\n" for p in sources
        )
        + f"vm.runInContext({json.dumps(PRELUDE)}, context);\n"
        + f"process.stdout.write(JSON.stringify(vm.runInContext({json.dumps(expression)}, context)));\n"
    )
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


class TestScoreboard(unittest.TestCase):
    def test_incomplete_mock_not_counted(self):
        r = run_node("scoreboardMockForSubject(mockRecs('m1','114','01',NOW-DAY,1,true),'01')")
        self.assertIsNone(r)

    def test_complete_mock_and_latest_chosen(self):
        r = run_node("""(() => {
          const recs = mockRecs('old','113','01',NOW-9*DAY,0.5).concat(mockRecs('new','114','01',NOW-2*DAY,0.8))
            .concat(mockRecs('newest','112','01',NOW-1*DAY,1,true));
          return scoreboardMockForSubject(recs,'01'); })()""")
        self.assertEqual(r["mockId"], "new")
        self.assertAlmostEqual(r["estimate"], 80.0, places=1)

    def test_tier_shares_sum_to_one(self):
        r = run_node("scoreboardTierShares('01')")
        self.assertAlmostEqual(r["main"] + r["basic"], 1.0, places=6)
        self.assertGreater(r["main"], 0)

    def test_practice_needs_three_questions(self):
        r = run_node("""(() => { const q = qidsOf('114','01').slice(0,2).map(x => rec(x));
          return scoreboardPracticeForSubject(q,'01'); })()""")
        self.assertIsNone(r["projection"])
        self.assertEqual(r["questions"], 2)

    def test_practice_projection_uses_tier_shares(self):
        r = run_node("""(() => {
          const sh = scoreboardTierShares('01');
          const main = []; const basic = [];
          Object.keys(QUESTION_POINTS).filter(q => q.indexOf('-01-') > 0).forEach(q =>
            (studyTierFor(q) === 'main' ? main : basic).push(q));
          const recs = main.slice(0,3).map(q => rec(q, {ratio: 1})).concat(basic.slice(0,3).map(q => rec(q, {ratio: 0.5})));
          const p = scoreboardPracticeForSubject(recs, '01').projection;
          return { p, expected: 100 * (sh.main * 1 + sh.basic * 0.5) }; })()""")
        self.assertAlmostEqual(r["p"], r["expected"], delta=0.06)

    def test_practice_ignores_mock_legacy_and_old(self):
        r = run_node("""(() => {
          const qs = qidsOf('114','01').concat(qidsOf('113','01')).slice(0,4);
          const recs = [
            rec(qs[0], {at: NOW - 30*DAY}),                 // outside 21 days
            rec(qs[1], {legacy: true, source: 'legacy'}),
            rec(qs[2], {source: 'mock', mockId: 'm'}),
            rec(qs[3])];
          return scoreboardCompute(recs, NOW).subjects[0]; })()""")
        self.assertIsNone(r["practice"])
        self.assertEqual(r["practiceQuestions"], 1)

    def test_totals_and_distance_text(self):
        r = run_node("""(() => {
          const recs = mockRecs('m','114','01',NOW-DAY,0.8);
          const m = scoreboardCompute(recs, NOW);
          return { mockTotal: m.mockTotal, est: m.estimateTotal, d: m.estimateDistance, md: m.mockDistance,
                   un: m.subjects[1].mock, line: scoreboardSummaryLine({records: recs, now: NOW}) }; })()""")
        self.assertAlmostEqual(r["mockTotal"], 80.0, places=1)
        self.assertIsNone(r["d"])  # distance only when all six subjects have data
        self.assertIsNone(r["md"])
        self.assertIsNone(r["un"])
        self.assertRegex(r["line"], r"^估計總分 80／\d+（1／6 科）$")
        self.assertNotIn("／380", r["line"])

    def test_all_six_subjects_show_distance(self):
        r = run_node("""(() => {
          const recs = ['01','02','03','04','05','06'].reduce((a, s) => a.concat(mockRecs('m'+s,'114',s,NOW-DAY,0.8)), []);
          const m = scoreboardCompute(recs, NOW);
          return { n: m.estimateCount, d: m.estimateDistance, line: scoreboardSummaryLine({records: recs, now: NOW}) }; })()""")
        self.assertEqual(r["n"], 6)
        self.assertIsNotNone(r["d"])
        self.assertIn("（6／6 科）", r["line"])

    def test_scored_subset_mock_counts_and_scales(self):
        # 114 配電 only scores Q1 and Q5 (40 points); latestMockScoreBySubject scales it to 0–100.
        r = run_node("""(() => {
          const rows = Object.keys(QUESTION_POINTS).map(q => { const m = /^EE-(\\d+)-(\\d+)-(\\d+)$/.exec(q);
            return [q, m[2], m[1], Number(m[3]), 'T', [], 's/' + q, 'p/' + m[1]]; });
          globalThis.DB_DATA = { questions: rows };
          const mk = q => Object.assign(rec(q, {source: 'mock', mockId: '114-06-4000', at: NOW - DAY}),
            {parts: [{label: 'p', points: QUESTION_POINTS[q].total, mark: 'o'}]});
          const full = ['EE-114-06-1', 'EE-114-06-5'].map(mk);
          const partial = scoreboardMockForSubject([full[0]], '06');
          const done = scoreboardMockForSubject(full, '06');
          return { partial, done, line: scoreboardSummaryLine({records: full, now: NOW}) }; })()""", mock=True)
        self.assertIsNone(r["partial"])
        self.assertEqual(r["done"]["estimate"], 100)
        self.assertEqual(r["done"]["rawTotal"], 40)
        self.assertIn("（1／6 科）", r["line"])

    def test_distance_exceeded(self):
        r = run_node("scoreboardCompute([], NOW) && [scoreboardDistanceText(370, 360), scoreboardDistanceText(370, 380)]")
        self.assertEqual(r, ["已超過 10 分", "還差 10 分"])

    def test_dominant_error_next_step(self):
        r = run_node("""[scoreboardNextStep({R:0,S:3,F:1,C:0,K:0,U:0,T:0}),
          scoreboardNextStep({R:0,S:1,F:0,C:2,K:0,U:0,T:0}),
          scoreboardNextStep({R:0,S:0,F:2,C:0,K:1,U:0,T:0}),
          scoreboardNextStep({R:0,S:0,F:0,C:0,K:0,U:0,T:3}),
          scoreboardNextStep({R:0,S:0,F:0,C:0,K:0,U:3,T:0}),
          scoreboardNextStep({R:3,S:0,F:0,C:0,K:0,U:0,T:0}),
          scoreboardNextStep({R:0,S:1,F:1,C:0,K:0,U:0,T:0}),
          scoreboardNextStep({R:0,S:2,F:0,C:0,K:0,U:0,T:0})]""")
        self.assertIn("起手式急救卡", r[0])
        self.assertIn("回代驗算", r[1])
        self.assertIn("核心公式", r[2])
        self.assertIn("配分時間帽", r[3])
        self.assertIn("單位", r[4])
        self.assertIn("已知、所求", r[5])
        self.assertIsNone(r[6])
        self.assertIn("起手式急救卡", r[7])  # two errors of the same code are enough

    def test_errors_exclude_legacy_and_old(self):
        r = run_node("""(() => { const q = qidsOf('114','01');
          const recs = [rec(q[0], {errors:['S','C']}), rec(q[1], {errors:['S'], legacy: true, source:'legacy'}),
                        rec(q[2], {errors:['T'], at: NOW - 40*DAY})];
          return scoreboardCompute(recs, NOW).subjects[0].errors; })()""")
        self.assertEqual((r["S"], r["C"], r["T"]), (1, 1, 0))

    def test_tier_rates(self):
        r = run_node("""(() => { const q = qidsOf('114','01');
          const m = scoreboardCompute([rec(q[0], {ratio: 0.5})], NOW).subjects[0].rates;
          return { tier: studyTierFor(q[0]), m }; })()""")
        self.assertEqual(r["m"][r["tier"]], 50)

    def test_empty_state(self):
        r = run_node("""(() => { const c = {innerHTML: ''}; renderScoreboard(c, {records: [], now: NOW});
          return { html: c.innerHTML, line: scoreboardSummaryLine({records: [], now: NOW}) }; })()""")
        self.assertIn("作答結果卡", r["html"])
        self.assertIn("sb-empty", r["html"])
        self.assertNotIn("sb-subject", r["html"])
        self.assertEqual(r["line"], "估計總分：尚無資料")
        self.assertIn("16%", r["html"])

    def test_render_with_data_and_escaping(self):
        r = run_node("""(() => { const q = qidsOf('114','01');
          const bad = Object.assign(rec(q[0], {errors:['S']}), {note: '<img onerror=x>'});
          const c = {innerHTML: ''};
          renderScoreboard(c, {records: [bad], now: NOW});
          return { html: c.innerHTML, esc: scoreboardEscape_('<a href="x">&\\'') }; })()""")
        self.assertIn("電路學", r["html"])
        self.assertIn("衝高分", r["html"])
        self.assertIn("再練 2 題就會顯示（需近 21 天 3 題）", r["html"])
        self.assertIn("尚有 6 科無資料", r["html"])
        self.assertIn("未考", r["html"])
        self.assertNotIn("<img", r["html"])
        self.assertEqual(r["esc"], "&lt;a href=&quot;x&quot;&gt;&amp;&#39;")

    def test_risk_flag(self):
        r = run_node("[scoreboardRisk(75), scoreboardRisk(60), scoreboardRisk(55), scoreboardRisk(39.5), scoreboardRisk(null)]")
        self.assertIsNone(r[0])
        self.assertIsNone(r[1])
        self.assertEqual(r[2], {"level": "low", "gap": 5})
        self.assertEqual(r[3], {"level": "zero", "gap": 20.5})
        self.assertIsNone(r[4])

    def test_risk_rendered(self):
        r = run_node("""(() => { const c = {innerHTML: ''};
          renderScoreboard(c, {records: mockRecs('m','114','01',NOW-DAY,0.3), now: NOW}); return c.innerHTML; })()""")
        self.assertIn("&lt;60", r)
        self.assertIn("零分風險", r)
        self.assertIn("差 30 分到 60", r)

    def test_drag_subject(self):
        r = run_node("""[scoreboardDragSubject([{id:'01',name:'A',target:70,estimate:60},{id:'02',name:'B',target:65,estimate:50},{id:'03',name:'C',target:60,estimate:null}]),
          scoreboardDragSubject([{id:'01',name:'A',target:70,estimate:80}]), scoreboardDragSubject([]),
          scoreboardDragText(null)]""")
        self.assertEqual(r[0], {"id": "02", "name": "B", "shortfall": 15})
        self.assertIsNone(r[1])
        self.assertIsNone(r[2])
        self.assertEqual(r[3], "各科都在目標之上")

    def test_trend(self):
        r = run_node("""[scoreboardTrend([{at:1,scaled:50}]), scoreboardTrend([]),
          scoreboardTrend([{at:3,scaled:70},{at:1,scaled:40},{at:2,scaled:55}]),
          scoreboardTrendText(scoreboardTrend([{at:1,scaled:70},{at:2,scaled:60}])), scoreboardTrendText(null)]""")
        self.assertIsNone(r[0])
        self.assertIsNone(r[1])
        self.assertEqual(r[2], {"prev": 55, "cur": 70, "delta": 15})
        self.assertEqual(r[3], "前次 70 → 本次 60（−10）")
        self.assertEqual(r[4], "")

    def test_mock_phase_hides_practice(self):
        r = run_node("""[scoreboardShowPractice(true, new Date(2026, 9, 14, 23).getTime()),
          scoreboardShowPractice(true, new Date(2026, 9, 15, 0, 1).getTime()),
          scoreboardShowPractice(false, new Date(2026, 9, 20).getTime()),
          (() => { const c = {innerHTML: ''}; const t = new Date(2026, 9, 16).getTime();
            renderScoreboard(c, {records: mockRecs('m','114','01',t-DAY,0.8), now: t}); return c.innerHTML.split('data-subject="02"')[0].indexOf('sb-val--practice'); })()]""")
        self.assertEqual(r[:3], [True, False, True])
        self.assertEqual(r[3], -1)


if __name__ == "__main__":
    unittest.main()
