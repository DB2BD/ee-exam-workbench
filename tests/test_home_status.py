# -*- coding: utf-8 -*-
"""v1.4.0 首頁像素風狀態視窗: pure stat model (homeStatusModel), HTML and shell wiring."""

import json
import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "src" / "data" / "questionPoints.generated.js",
    ROOT / "src" / "data" / "targetAllocation.generated.js",
    ROOT / "src" / "domain" / "studyPlan.js",
    ROOT / "src" / "components" / "scoreboard.js",
    ROOT / "src" / "components" / "homeStatus.js",
]
HOME_JS = (ROOT / "src" / "components" / "homeStatus.js").read_text(encoding="utf-8")
CSS = (ROOT / "src" / "styles" / "v14-home-status.css").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts" / "build_workbench.py").read_text(encoding="utf-8")
HEADER_JS = (ROOT / "src" / "components" / "header.js").read_text(encoding="utf-8")
MAIN_JS = (ROOT / "src" / "main.js").read_text(encoding="utf-8")

PRELUDE = """
const DAY = 86400000;
// 2026-10-14 20:00 in the machine's local time zone
const NOW = new Date(2026, 9, 14, 20, 0, 0).getTime();
const at = (y, m, d, h) => new Date(y, m - 1, d, h === undefined ? 12 : h, 0, 0).getTime();
const iso = (y, m, d, h) => new Date(y, m - 1, d, h === undefined ? 12 : h, 0, 0).toISOString();
function qidsOf(year, subj) { return Object.keys(QUESTION_POINTS).filter(q => q.startsWith('EE-' + year + '-' + subj + '-')); }
function rec(qid, o) {
  o = o || {};
  const total = QUESTION_POINTS[qid].total;
  const f = o.ratio === undefined ? 1 : o.ratio;
  return { id: 'r-' + qid + '-' + (o.at || 0) + (o.mockId || ''), qid, at: o.at || NOW - DAY, source: o.source || 'today',
    mockId: o.mockId, tier: studyTierFor(qid), parts: [{label: '整題', points: total, mark: 'o'}], errors: [],
    total, estimate: total * f, legacy: o.legacy };
}
function mockRecs(mockId, year, subj, when, ratio) {
  return qidsOf(year, subj).map(q => rec(q, {source: 'mock', mockId, at: when, ratio}));
}
"""


def run_node(expression, tz=None):
    script = (
        "const vm = require('vm');\nconst context = {};\ncontext.globalThis = context;\nvm.createContext(context);\n"
        + "".join(f"vm.runInContext({json.dumps(p.read_text(encoding='utf-8'))}, context);\n" for p in SOURCES)
        + f"vm.runInContext({json.dumps(PRELUDE)}, context);\n"
        + f"process.stdout.write(JSON.stringify(vm.runInContext({json.dumps(expression)}, context)));\n"
    )
    env = dict(os.environ)
    if tz:
        env["TZ"] = tz
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True, env=env)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


class TestLevelAndTitle(unittest.TestCase):
    def test_level_curve(self):
        r = run_node("[0, 149, 150, 329, 330, 539, 540].map(homeStatusLevelFor)")
        levels = [(x["level"], x["into"], x["need"]) for x in r]
        self.assertEqual(levels, [(1, 0, 150), (1, 149, 150), (2, 0, 180), (2, 179, 180), (3, 0, 210), (3, 209, 210), (4, 0, 240)])
        self.assertEqual(r[1]["pct"], 99)
        self.assertEqual(r[0]["pct"], 0)

    def test_exp_to_reach_matches_need_sum(self):
        r = run_node("""(() => { let sum = 0; const out = [];
          for (let n = 1; n <= 30; n++) { out.push(homeStatusExpToReach(n) === sum); sum += homeStatusExpNeed(n); }
          return out; })()""")
        self.assertTrue(all(r))

    def test_negative_and_garbage_exp(self):
        r = run_node("[-5, NaN, undefined, 'x'].map(v => homeStatusLevelFor(v).level)")
        self.assertEqual(r, [1, 1, 1, 1])

    def test_titles_by_level(self):
        r = run_node("[1, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21, 24, 25, 60].map(homeStatusTitleFor)")
        self.assertEqual(r, ["見習巡線員", "見習巡線員", "配電學徒", "配電學徒", "變電值班員", "變電值班員",
                             "保護電驛師", "保護電驛師", "系統調度員", "系統調度員", "電網守護者", "電網守護者",
                             "榜上技師", "榜上技師"])

    def test_card_exp(self):
        r = run_node("""[
          homeStatusCardExp({ total: 20, estimate: 20 }),
          homeStatusCardExp({ total: 20, estimate: 10 }),
          homeStatusCardExp({ total: 20, estimate: 0 }),
          homeStatusCardExp({ total: 20, estimate: 99 }),
          homeStatusCardExp({ total: 0, estimate: 5 }),
          homeStatusCardExp({ total: 20, estimate: 20, legacy: true }),
          homeStatusCardExp(null)]""")
        self.assertEqual(r, [20, 15, 10, 20, 10, 5, 0])


class TestModel(unittest.TestCase):
    def test_empty_inputs(self):
        r = run_node("homeStatusModel()")
        self.assertEqual(r["level"], 1)
        self.assertEqual(r["title"], "見習巡線員")
        self.assertEqual(r["exp"]["total"], 0)
        self.assertEqual(r["streak"], {"days": 0, "activeToday": False})
        self.assertEqual(r["tasks"], {"done": 0, "total": 0})
        self.assertEqual(r["cards"], {"count": 0})
        self.assertFalse(r["score"]["hasData"])
        self.assertEqual(r["attrs"], [])

    def test_exp_formula_from_tasks_and_cards(self):
        r = run_node("""(() => {
          const completed = { 'CORE-01': iso(2026, 10, 13), 'CORE-02': iso(2026, 10, 14), 'CORE-03': iso(2026, 10, 14) };
          const records = [
            { at: at(2026, 10, 14), total: 20, estimate: 20 },              // 20
            { at: at(2026, 10, 14), total: 20, estimate: 10 },              // 15
            { at: at(2026, 10, 12), total: 20, estimate: 0 },               // 10
            { at: at(2026, 10, 12), total: 20, estimate: 20, legacy: true } // 5
          ];
          return homeStatusModel({ now: NOW, completed, totalTasks: 67, records }); })()""")
        self.assertEqual(r["exp"]["fromTasks"], 300)
        self.assertEqual(r["exp"]["fromCards"], 50)
        self.assertEqual(r["exp"]["total"], 350)
        self.assertEqual(r["level"], 3)  # 330 <= 350 < 540
        self.assertEqual(r["exp"]["into"], 20)
        self.assertEqual(r["exp"]["need"], 210)
        self.assertEqual(r["tasks"], {"done": 3, "total": 67})
        self.assertEqual(r["cards"]["count"], 4)

    def test_total_tasks_never_below_done(self):
        r = run_node("homeStatusModel({ now: NOW, completed: { A: iso(2026,10,14), B: iso(2026,10,14) }, totalTasks: 0 }).tasks")
        self.assertEqual(r, {"done": 2, "total": 2})

    def test_streak_runs(self):
        for tz in (None, "Asia/Taipei", "America/Los_Angeles", "UTC"):
            with self.subTest(tz=tz):
                r = run_node("""(() => {
                  const key = (y, m, day) => y + '-' + String(m).padStart(2, '0') + '-' + String(day).padStart(2, '0');
                  const run = (days) => homeStatusStreak(days, NOW);
                  return {
                    today3: run([key(2026,10,14), key(2026,10,13), key(2026,10,12)]),
                    yesterdayOnly: run([key(2026,10,13), key(2026,10,12)]),
                    brokenYesterday: run([key(2026,10,12), key(2026,10,11)]),
                    gap: run([key(2026,10,14), key(2026,10,12)]),
                    none: run([]),
                    monthEdge: homeStatusStreak([key(2026,10,1), key(2026,9,30), key(2026,9,29)], new Date(2026, 9, 1, 1).getTime()),
                    dstWeek: homeStatusStreak(['2026-03-08','2026-03-09','2026-03-10'], new Date(2026, 2, 10, 23, 30).getTime())
                  }; })()""", tz)
                self.assertEqual(r["today3"], {"days": 3, "activeToday": True})
                self.assertEqual(r["yesterdayOnly"], {"days": 2, "activeToday": False})
                self.assertEqual(r["brokenYesterday"], {"days": 0, "activeToday": False})
                self.assertEqual(r["gap"], {"days": 1, "activeToday": True})
                self.assertEqual(r["none"], {"days": 0, "activeToday": False})
                self.assertEqual(r["monthEdge"], {"days": 3, "activeToday": True})
                self.assertEqual(r["dstWeek"], {"days": 3, "activeToday": True})

    def test_streak_counts_tasks_cards_and_reviews_and_ignores_future(self):
        r = run_node("""(() => {
          const m = homeStatusModel({ now: NOW,
            completed: { 'CORE-01': iso(2026, 10, 14, 9) },
            records: [{ at: at(2026, 10, 13, 22), total: 10, estimate: 10 }],
            reviewDates: ['2026-10-12', '2026-10-20', 'bad'] });
          return m.streak; })()""")
        self.assertEqual(r, {"days": 3, "activeToday": True})

    def test_days_until_exam(self):
        for tz in (None, "Asia/Taipei", "America/Los_Angeles"):
            with self.subTest(tz=tz):
                r = run_node("""({
                  today: homeStatusDaysUntil('2026-11-14', NOW),
                  lateNight: homeStatusDaysUntil('2026-11-14', new Date(2026, 9, 14, 23, 59).getTime()),
                  eve: homeStatusDaysUntil('2026-11-14', new Date(2026, 10, 13, 8).getTime()),
                  day: homeStatusDaysUntil('2026-11-14', new Date(2026, 10, 14, 0, 1).getTime()),
                  after: homeStatusDaysUntil('2026-11-14', new Date(2026, 10, 15, 8).getTime()),
                  dst: homeStatusDaysUntil('2026-11-14', new Date(2026, 10, 1, 12).getTime()),
                  bad: homeStatusDaysUntil('nope', NOW),
                  model: homeStatusModel({ now: NOW }).exam
                })""", tz)
                self.assertEqual(r["today"]["days"], 31)
                self.assertEqual(r["lateNight"]["days"], 31)
                self.assertEqual(r["eve"]["days"], 1)
                self.assertEqual((r["day"]["days"], r["day"]["today"], r["day"]["passed"]), (0, True, False))
                self.assertEqual((r["after"]["days"], r["after"]["passed"]), (0, True))
                self.assertEqual(r["dst"]["days"], 13)
                self.assertEqual(r["bad"]["days"], 0)
                self.assertEqual(r["model"]["date"], "2026-11-14")
                self.assertEqual(r["model"]["days"], 31)

    def test_attributes_and_score_from_scoreboard(self):
        r = run_node("""(() => {
          const stub = { hasData: true, estimateTotal: 274.4, estimateTargetTotal: 320, estimateCount: 5, subjectCount: 6, goal: 380, passLine: 360,
            subjects: [
              { id: '01', name: '電路學', estimate: 80, target: 75 },
              { id: '02', name: '電子學', estimate: 62.4, target: 70 },
              { id: '03', name: '工程數學', estimate: null, target: 60 },
              { id: '04', name: '電機機械', estimate: 41, target: 70 },
              { id: '05', name: '電力系統', estimate: 130, target: 55 },
              { id: '06', name: '工業配電', estimate: 60, target: null }
            ] };
          return homeStatusModel({ now: NOW, scoreboard: stub }); })()""")
        self.assertEqual(r["score"], {"hasData": True, "total": 274, "target": 320, "count": 5, "subjectCount": 6, "passLine": 360})
        attrs = {a["id"]: a for a in r["attrs"]}
        self.assertEqual([a["name"] for a in r["attrs"]], ["電路", "電子", "工數", "電機", "電力", "配電"])
        self.assertEqual(attrs["01"]["state"], "goal")
        self.assertEqual(attrs["02"]["state"], "pass")
        self.assertEqual(attrs["03"]["state"], "none")
        self.assertIsNone(attrs["03"]["estimate"])
        self.assertEqual(attrs["03"]["pct"], 0)
        self.assertEqual(attrs["04"]["state"], "low")
        self.assertEqual(attrs["05"]["pct"], 100)  # clamped
        self.assertEqual(attrs["06"]["state"], "pass")
        self.assertIsNone(attrs["06"]["target"])
        self.assertEqual(attrs["01"]["targetPct"], 75)

    def test_score_target_falls_back_to_goal(self):
        r = run_node("""homeStatusModel({ now: NOW, scoreboard: { hasData: true, estimateTotal: 100, estimateTargetTotal: null,
          estimateCount: 1, subjectCount: 6, goal: 380, subjects: [] } }).score""")
        self.assertEqual(r["target"], 380)
        self.assertEqual(r["total"], 100)

    def test_matches_real_scoreboardcompute(self):
        r = run_node("""(() => {
          const recs = ['01', '02'].reduce((a, s) => a.concat(mockRecs('m' + s, '114', s, NOW - DAY, 0.8)), []);
          const sb = scoreboardCompute(recs, NOW);
          const m = homeStatusModel({ now: NOW, records: recs, scoreboard: sb, totalTasks: 67 });
          return { sbTotal: sb.estimateTotal, sbTarget: sb.estimateTargetTotal, sbCount: sb.estimateCount,
                   sbSubjects: sb.subjects.map(s => [s.id, s.estimate === null ? null : Math.round(s.estimate), s.target]),
                   m: { total: m.score.total, target: m.score.target, count: m.score.count,
                        attrs: m.attrs.map(a => [a.id, a.estimate, a.target]) },
                   line: scoreboardSummaryLine({ records: recs, now: NOW }) }; })()""")
        self.assertEqual(r["m"]["total"], round(r["sbTotal"]))
        self.assertEqual(r["m"]["target"], round(r["sbTarget"]))
        self.assertEqual(r["m"]["count"], r["sbCount"])
        self.assertEqual(r["m"]["attrs"], r["sbSubjects"])
        # the header one-liner and the window agree on the numbers
        self.assertIn(f"{r['m']['total']}／{r['m']['target']}（{r['m']['count']}／6 科）", r["line"])


class TestHtml(unittest.TestCase):
    def render(self, extra=""):
        return run_node("""(() => {
          const stub = { hasData: true, estimateTotal: 274, estimateTargetTotal: 320, estimateCount: 5, subjectCount: 6, goal: 380,
            subjects: [['01', 80, 75], ['02', 62, 70], ['03', null, 60], ['04', 41, 70], ['05', 55, 55], ['06', 60, 50]]
              .map(r => ({ id: r[0], name: 'x' + r[0], estimate: r[1], target: r[2] })) };
          const m = homeStatusModel({ now: NOW, completed: { 'CORE-01': iso(2026, 10, 14) }, totalTasks: 67,
            records: [{ at: NOW, total: 10, estimate: 10 }], scoreboard: stub });
          return homeStatusHtml(m); })()""" + extra)

    def test_html_has_every_stat(self):
        html = self.render()
        for label in ("連續學習", "距考試", "任務", "結果卡", "預估總分", "收合", "Lv", "EXP "):
            self.assertIn(label, html, label)
        for name in ("電路", "電子", "工數", "電機", "電力", "配電"):
            self.assertIn(">" + name + "<", html, name)
        self.assertEqual(html.count('data-hs-attr="'), 6)
        self.assertIn('aria-label="1／67"', html)
        self.assertIn('aria-label="274／320"', html)
        self.assertIn('data-hs="exam"', html)
        self.assertIn("5／6 科", html)
        self.assertIn('aria-expanded="true"', html)
        self.assertIn('onclick="homeStatusToggle()"', html)
        self.assertNotIn("NaN", html)
        self.assertNotIn("undefined", html)
        self.assertNotIn("null", html)

    def test_no_data_state_renders_dashes(self):
        html = run_node("homeStatusHtml(homeStatusModel({ now: NOW }))")
        self.assertIn('data-hs="score"', html)
        self.assertNotIn("NaN", html)
        self.assertNotIn("undefined", html)

    def test_pixel_text_escapes_and_labels(self):
        r = run_node("""[homeStatusPixelText('21／67', 3), homeStatusPixelText('<b>"', 2)]""")
        self.assertIn('aria-label="21／67"', r[0])
        self.assertNotIn("<b>", r[1])
        self.assertIn("&lt;b&gt;", r[1])
        self.assertIn('role="img"', r[0])


class TestSceneAndShell(unittest.TestCase):
    def test_scene_is_original_inline_art(self):
        html = run_node("homeStatusSceneHtml()")
        for cls in ("hs-sky", "hs-far", "hs-mid", "hs-ground", "hs-near", "hs-hero", "hs-beacon", "hs-lamp"):
            self.assertIn(cls, html, cls)
        self.assertNotIn("<image", html)
        self.assertNotIn("url(", html)
        self.assertNotRegex(html, r"https?://(?!www\.w3\.org/2000/svg)")

    def test_no_storage_keys_added(self):
        self.assertNotRegex(HOME_JS, r"\b(localStorage|sessionStorage)\s*\.\s*(setItem|getItem|removeItem)")
        self.assertNotRegex(HOME_JS, r"EE_EXAM_[A-Z_]+_V\d")
        self.assertNotRegex(HOME_JS, r"indexedDB")

    def test_build_wires_module_css_and_markup(self):
        self.assertIn("'src/components/homeStatus.js'", BUILD)
        self.assertIn("'src/styles/v14-home-status.css'", BUILD)
        self.assertIn('id="home-status"', BUILD)
        self.assertIn('id="hs-scene"', BUILD)
        self.assertIn('id="header-summary-line"', BUILD)
        self.assertIn("homeStatusRefresh()", HEADER_JS)
        self.assertIn("homeStatusInit()", MAIN_JS)
        # module order: after todayTask.js / scoreboard.js (it reads their globals lazily) and before main.js
        order = [m.start() for m in (re.search(re.escape(f"'{n}'"), BUILD) for n in (
            "src/components/scoreboard.js", "src/components/todayTask.js", "src/components/homeStatus.js", "src/main.js"))]
        self.assertEqual(order, sorted(order))

    def test_css_respects_reduced_motion_and_phone_layout(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", CSS)
        reduced = CSS[CSS.index("@media (prefers-reduced-motion: reduce)"):]
        self.assertIn("animation: none !important", reduced)
        self.assertIn("@media (max-width: 640px)", CSS)
        self.assertIn('[data-theme="dark"] header.hs-header', CSS)
        self.assertNotRegex(CSS, r"url\(")
        self.assertNotIn("@import", CSS)
        self.assertNotIn("@font-face", CSS)

    def test_rows_are_collapsible_without_hiding_main_entries(self):
        self.assertIn(".hs--collapsed .hs-body", CSS)
        self.assertIn("function homeStatusToggle", HOME_JS)
        # the window lives inside <header>; the main entries (today task card, tabs) stay outside it
        build_header = BUILD[BUILD.index('<header class="hs-header">'):BUILD.index("</header>")]
        self.assertIn('id="home-status"', build_header)
        self.assertNotIn("today-task-card", build_header)
        self.assertNotIn("main-tabs", build_header)

    def test_built_index_contains_window(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        if "homeStatusModel" not in index:
            self.skipTest("index.html not rebuilt yet")
        self.assertIn('id="home-status"', index)
        self.assertIn("function homeStatusModel", index)


if __name__ == "__main__":
    unittest.main()
