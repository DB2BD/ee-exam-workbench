# -*- coding: utf-8 -*-
"""v1.3 A: src/domain/pacing.js (pure) — today's plan, milestones, hours check, cuts, ahead suggestion.
Node runs via stdin; the schedule comes from the generated data file."""

import json
import subprocess
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCHEDULE_JS = WORKSPACE / "src/data/dailySchedule.generated.js"
PACING_JS = WORKSPACE / "src/domain/pacing.js"


def run_node(expression):
    src = SCHEDULE_JS.read_text(encoding="utf-8") + "\n" + PACING_JS.read_text(encoding="utf-8")
    script = f"""
const vm = require('vm');
const ctx = {{ console }};
vm.createContext(ctx);
vm.runInContext({json.dumps(src, ensure_ascii=False)} + '\\nglobalThis.S = DAILY_SCHEDULE;', ctx);
const out = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, ctx);
process.stdout.write(JSON.stringify(out));
"""
    done = subprocess.run(["node", "-"], input=script, cwd=WORKSPACE, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


# Helper JS: `done(before)` marks every order code before `before`; `plan(today, completed, partial)` runs pacingPlan.
HELPERS = """
const done = (before, extra) => { const c = {}; S.order.slice(0, S.order.indexOf(before)).forEach(k => c[k] = 'x'); (extra || []).forEach(k => c[k] = 'x'); return c; };
const plan = (today, completed, partial) => pacingPlan({ schedule: S, completed, today, partial: partial || null });
const codes = r => r.plan.map(p => p.code + (p.part === 'full' ? '' : ':' + p.part));
"""


def js(body):
    return run_node("(() => {" + HELPERS + body + "})()")


class TestPacingPrimitives(unittest.TestCase):
    def test_weekend_and_date_math_are_timezone_independent(self):
        res = run_node("({sun: pacingIsWeekend('2026-10-04'), mon: pacingIsWeekend('2026-10-05'), sat: pacingIsWeekend('2026-10-10'), "
                       "days: pacingDaysBetween('2026-10-21', '2026-10-31'), add: pacingAddDays('2026-10-31', 1), bad: pacingParseIso('x')})")
        self.assertEqual(res, {"sun": True, "mon": False, "sat": True, "days": 10, "add": "2026-11-01", "bad": None})

    def test_budget_by_day(self):
        res = run_node("[pacingBudgetFor('2026-10-04', S.budget), pacingBudgetFor('2026-10-05', S.budget), pacingBudgetFor('2026-10-05', {weekday: 3, weekend: 5})]")
        self.assertEqual(res, [4, 2, 3])


class TestPacingPlan(unittest.TestCase):
    def test_on_track_every_day_follows_the_dated_table(self):
        """A learner who does exactly the table each day always gets that day's table back, status 'on', no cuts."""
        res = js("""
          const out = []; const c = {}; ['01','02','03','04','05','06'].forEach(n => c['CORE-' + n] = 'x'); let partial = null;
          S.days.forEach(day => {
            const r = plan(day.date, c, partial);
            out.push({date: day.date, plan: r.plan.map(p => p.code + ':' + p.part), table: day.items.filter(i => S.tasks[i.code]).map(i => i.code + ':' + i.part),
                      status: r.status, cut: r.cut, overload: r.overload});
            partial = null;
            day.items.forEach(it => { if (!S.tasks[it.code]) return; if (it.part === 'closed') partial = {code: it.code, phaseIndex: 1}; else c[it.code] = 'x'; });
          });
          return out;""")
        self.assertEqual(len(res), 41)
        for day in res:
            with self.subTest(day=day["date"]):
                self.assertEqual(day["plan"], day["table"])
                self.assertEqual(day["cut"], [])
                self.assertFalse(day["overload"])
                self.assertIn(day["status"], ("on", "ahead"))

    def test_first_day_sunday_fills_four_hours_from_core_07(self):
        r = js("const r = plan('2026-10-04', done('CORE-07')); return {codes: codes(r), hours: r.planHours, budget: r.budgetHours, weekend: r.weekend, status: r.status};")
        self.assertEqual(r["codes"], ["CORE-07", "CORE-08", "CORE-09", "WEAK-01"])
        self.assertEqual((r["hours"], r["budget"], r["weekend"], r["status"]), (4.25, 4, True, "on"))

    def test_weekday_fills_two_hours_and_starts_from_earliest_uncompleted(self):
        r = js("const r = plan('2026-10-05', done('CORE-07', ['CORE-08'])); return {codes: codes(r), hours: r.planHours};")
        # CORE-07 is still open (earlier than the completed CORE-08): it comes first, then CORE-09 fills the 2 h
        self.assertEqual(r["codes"], ["CORE-07", "CORE-09"])
        self.assertEqual(r["hours"], 2)

    def test_weekday_mock_is_split_across_two_days(self):
        r = js("""
          const c = done('MOCK114-04');
          const day1 = plan('2026-10-19', c);
          const day2 = plan('2026-10-20', c, {code: 'MOCK114-04', phaseIndex: 1});
          const weekend = plan('2026-10-24', done('MOCK114-06', ['MOCK114-05']), {code: 'MOCK114-06', phaseIndex: 1});
          return {day1: codes(day1), h1: day1.planHours, day2: codes(day2), h2: day2.planHours, wk: codes(weekend), hw: weekend.planHours};""")
        self.assertEqual(r["day1"], ["MOCK114-04:closed"])
        self.assertEqual(r["h1"], 2)
        self.assertEqual(r["day2"], ["MOCK114-04:review", "WEAK-11"])  # 1 h check+fix, then the 1 h of other work
        self.assertEqual(r["h2"], 2.25)
        self.assertEqual(r["wk"], ["MOCK114-06:review", "BLIND108-01"])  # Saturday: check (1 h) + next paper in one sitting (3 h)
        self.assertEqual(r["hw"], 4)

    def test_weekend_paper_is_one_sitting_plus_one_hour_of_other_work(self):
        r = js("const r = plan('2026-10-18', done('MOCK114-03')); return {codes: codes(r), hours: r.planHours, mockHours: r.plan[0].hours};")
        self.assertEqual(r["codes"], ["MOCK114-03", "WEAK-10"])
        self.assertEqual(r["mockHours"], 3)
        self.assertEqual(r["hours"], 4.25)

    def test_buffer_day_makes_up_missing_papers_first(self):
        # 11/01 with two papers outstanding: makeup papers come before BUFFER (earliest uncompleted first)
        r = js("""
          const c = done('BLIND108-05');
          const r = plan('2026-11-01', c);
          return {codes: codes(r), hard: r.hardMilestone};""")
        self.assertEqual(r["codes"], ["BLIND108-05"])
        self.assertTrue(r["hard"]["missed"])
        self.assertEqual(r["hard"]["remainingPapers"], 2)
        # all papers done -> BUFFER (4 h) opens reinforcement
        b = js("const r = plan('2026-11-01', done('BUFFER')); return {codes: codes(r), hours: r.planHours, next: r.nextMilestone.label};")
        self.assertEqual(b["codes"], ["BUFFER"])
        self.assertEqual(b["hours"], 4)
        self.assertEqual(b["next"], "補強完成")

    def test_late_phases_are_gated_until_their_date(self):
        r = js("const r = plan('2026-10-28', done('BUFFER')); return {codes: codes(r), status: r.status, ahead: r.aheadCount};")
        self.assertEqual(r["codes"], [])  # BUFFER / REINF / WRAP are not due yet
        self.assertEqual(r["status"], "ahead")
        r = js("const r = plan('2026-11-03', done('REINF-02')); return codes(r);")
        self.assertEqual(r, ["REINF-02"])
        r = js("const r = plan('2026-11-09', done('WRAP-01')); return codes(r);")
        self.assertEqual(r, ["WRAP-01"])

    def test_exam_check_and_stop_days_plan_nothing(self):
        for day in ("2026-11-12", "2026-11-13", "2026-11-20"):
            r = js(f"const r = plan('{day}', {{}}); return {{codes: codes(r), nonWork: r.nonWork, after: r.afterEnd, next: r.nextMilestone}};")
            self.assertEqual(r["codes"], [], day)
            self.assertIsNone(r["next"], day)
        self.assertTrue(js("return plan('2026-11-12', {}).nonWork;"))
        self.assertTrue(js("return plan('2026-11-14', {}).afterEnd;"))


class TestPacingMilestones(unittest.TestCase):
    def test_next_milestone_days_and_remaining(self):
        r = js("""
          const r = plan('2026-10-21', done('MOCK114-05'));
          const m = r.nextMilestone;
          return {label: m.label, hard: m.hard, days: m.daysLeft, papers: m.remainingPapers, tasks: m.remainingTasks, hours: m.remainingHours,
                  hardDays: r.hardMilestone.daysLeft, hardPapers: r.hardMilestone.remainingPapers, daysLeft: r.daysLeft};""")
        self.assertEqual((r["label"], r["hard"], r["days"], r["papers"]), ("模考截止", True, 10, 8))
        self.assertEqual((r["hardDays"], r["hardPapers"], r["daysLeft"]), (10, 8, 10))
        self.assertEqual(r["hours"], 27.75)

    def test_milestone_dates_and_hard_flag(self):
        r = js("return S.milestones.map(m => [m.date, m.hard, m.codes.length]);")
        self.assertEqual([(d, h) for d, h, _ in r], [("2026-10-17", False), ("2026-10-31", True), ("2026-11-11", False)])
        self.assertLess(r[0][2], r[1][2])
        self.assertLess(r[1][2], r[2][2])

    def test_hours_check_compares_required_with_available(self):
        r = js("const r = plan('2026-10-04', done('CORE-07')); return {req: r.requiredHours, avail: r.availableHours, days: r.daysLeft};")
        self.assertEqual((r["req"], r["avail"], r["days"]), (35.25, 36, 13))

    def test_after_the_hard_milestone_missing_papers_are_reported_and_never_cut(self):
        r = js("""
          const c = done('BLIND108-05'); const r = plan('2026-11-03', c);
          return {hard: r.hardMilestone, cut: r.cut, codes: codes(r), next: r.nextMilestone.label, status: r.status,
                  papersCut: r.cut.filter(k => /MOCK|BLIND/.test(k))};""")
        self.assertTrue(r["hard"]["passed"])
        self.assertTrue(r["hard"]["missed"])
        self.assertEqual(r["hard"]["remainingPapers"], 2)
        self.assertEqual(r["codes"][0], "BLIND108-05:closed")  # still the first thing to do (11/03 is a Tuesday: closed phase)
        self.assertEqual(r["next"], "補強完成")
        self.assertEqual(r["papersCut"], [])


class TestPacingCuts(unittest.TestCase):
    def test_behind_by_eight_cuts_weak_before_core_and_keeps_papers(self):
        r = js("""
          const c = done('CORE-16'); const r = plan('2026-10-16', c);
          return {status: r.status, cut: r.cut, detail: r.cutDetail.map(d => d.reason), codes: codes(r), behind: r.behindCount, overload: r.overload,
                  req: r.hardMilestone.requiredHours, avail: r.hardMilestone.availableHours, soft: r.nextMilestone};""")
        self.assertEqual(r["status"], "behind")
        self.assertTrue(r["cut"], "something must be cut")
        weak = [c for c in r["cut"] if c.startswith("WEAK")]
        self.assertTrue(weak)
        self.assertFalse([c for c in r["cut"] if c.startswith(("MOCK", "BLIND", "WRAP", "BUFFER"))])
        reasons = r["detail"]
        # WEAK reasons come strictly before any CORE reason
        first_core = next((i for i, x in enumerate(reasons) if x.startswith("core")), len(reasons))
        self.assertTrue(all(x == "weak" for x in reasons[:first_core]))
        self.assertTrue(all(x != "weak" for x in reasons[first_core:]))
        self.assertLessEqual(r["req"], r["avail"] + 0.5)  # after the cuts the 10/31 hours fit
        self.assertFalse(r["overload"])
        self.assertEqual(r["soft"]["label"], "弱題分析關卡")  # the earlier milestone is soft: reported, never a reason to cut
        self.assertTrue(r["codes"], "a plan still exists")
        self.assertFalse(set(c.split(":")[0] for c in r["codes"]) & set(r["cut"]), "cut tasks never appear in today's plan")

    def test_cut_order_is_weak_then_core_variants_then_core_base_latest_first(self):
        r = js("""
          const r = plan('2026-10-12', done('CORE-07'));  // 8 days from 10/17 but nothing done since CORE-07
          return {cut: r.cut, reasons: r.cutDetail.map(d => d.reason), over: r.overload};""")
        self.assertTrue(r["cut"])
        self.assertEqual(r["reasons"], sorted(r["reasons"], key=["weak", "core-variant", "core", "reinforce"].index))

    def test_each_subject_keeps_its_base_core_session(self):
        # A brand-new learner (nothing done) under heavy pressure: the six first 母題 sessions CORE-01..06 are never cut.
        r = js("""
          const r = plan('2026-10-14', {}); const x = plan('2026-10-30', {});
          return {cut: r.cut, overload: r.overload, cut2: x.cut, overload2: x.overload, short: x.shortHours};""")
        for n in range(1, 7):
            self.assertNotIn(f"CORE-{n:02d}", r["cut"])
            self.assertNotIn(f"CORE-{n:02d}", r["cut2"])
        self.assertFalse(r["overload"])  # 10/14: dropping WEAK and later CORE sessions is enough
        self.assertTrue(r["overload2"])  # 10/30: even every allowed cut cannot make 12 papers fit
        self.assertGreater(r["short"], 0)
        self.assertFalse([c for c in r["cut"] if c.startswith(("MOCK", "BLIND"))])
        self.assertFalse([c for c in r["cut2"] if c.startswith(("MOCK", "BLIND"))])

    def test_subject_with_done_base_session_can_drop_later_base_sessions_last(self):
        r = js("""
          const r = plan('2026-10-14', done('CORE-07'));
          const t = S.tasks;
          return {cut: r.cut, variantFirst: r.cutDetail.filter(d => d.reason === 'core').every(d => t[d.code] && !t[d.code].variant)};""")
        self.assertTrue(r["variantFirst"])

    def test_no_cut_when_the_hours_fit(self):
        r = js("const r = plan('2026-10-05', done('CORE-10')); return {cut: r.cut, status: r.status};")
        self.assertEqual(r["cut"], [])
        self.assertNotEqual(r["status"], "behind")

    def test_reinforcement_is_the_last_thing_cut(self):
        r = js("""
          const r = plan('2026-11-05', done('REINF-01'));  // 3 REINF days gone, reinforcement now too long for 11/11
          return {cut: r.cut, reasons: r.cutDetail.map(d => d.reason), status: r.status};""")
        self.assertEqual(r["status"], "behind")
        self.assertTrue(r["cut"])
        self.assertTrue(all(c.startswith("REINF") for c in r["cut"]))
        self.assertEqual(r["cut"][-1], "REINF-09")  # latest first, keeps the earliest reinforcement rounds


class TestPacingAhead(unittest.TestCase):
    def test_all_papers_done_before_deadline_suggests_113_paper(self):
        r = js("const r = plan('2026-10-27', done('BUFFER')); return {s: r.suggestion, st: r.status, all: r.allPapersDone};")
        self.assertIn("113 年整卷", r["s"])
        self.assertEqual((r["st"], r["all"]), ("ahead", True))

    def test_no_suggestion_when_papers_remain_or_after_the_deadline(self):
        self.assertEqual(js("return plan('2026-10-27', done('BLIND108-06')).suggestion;"), "")
        self.assertEqual(js("return plan('2026-11-02', done('BUFFER')).suggestion;"), "")

    def test_ahead_counts_and_status(self):
        r = js("const r = plan('2026-10-10', done('CORE-24')); return {st: r.status, ahead: r.aheadCount, behind: r.behindCount};")
        self.assertEqual(r["st"], "ahead")
        self.assertGreater(r["ahead"], 0)
        self.assertEqual(r["behind"], 0)


class TestPacingPurity(unittest.TestCase):
    def test_source_has_no_dom_or_storage_access(self):
        src = PACING_JS.read_text(encoding="utf-8")
        for token in ("document.", "localStorage", "window.", "Date.now", "new Date()"):
            self.assertNotIn(token, src)

    def test_input_is_not_mutated(self):
        r = js("const c = done('CORE-10'); const before = JSON.stringify(c) + JSON.stringify(S); plan('2026-10-12', c); return before === JSON.stringify(c) + JSON.stringify(S);")
        self.assertTrue(r)


if __name__ == "__main__":
    unittest.main()
