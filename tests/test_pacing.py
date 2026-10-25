# -*- coding: utf-8 -*-
"""v1.3 A: src/domain/pacing.js (pure) — today's plan, milestones, hours check, cuts, ahead suggestion.
Node runs via stdin; the schedule comes from the generated data file."""

import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import node_runner  # noqa: E402

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
    done = node_runner.run(script, cwd=WORKSPACE, capture_output=True, text=True)
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
        self.assertEqual(res, [5, 2, 3])  # v1.3.7: weekend budget is 5 h

    def test_schedule_and_default_budget_are_five_hour_weekends(self):
        res = js("const p = pacingPlan({schedule: {tasks: S.tasks, order: S.order, days: S.days, milestones: []}, completed: {}, today: '2026-10-10'}); return [S.budget, p.budgetHours];")
        self.assertEqual(res[0], {"weekday": 2, "weekend": 5})
        self.assertEqual(res[1], 5)  # no schedule.budget: the built-in default is also weekend 5


class TestPacingHolidays(unittest.TestCase):
    def test_schedule_lists_the_two_holidays(self):
        self.assertEqual(js("return S.holidays;"), ["2026-10-09", "2026-10-26"])

    def test_rest_day_primitive_is_holiday_aware_and_backward_compatible(self):
        res = run_node("({fri: pacingIsRestDay('2026-10-09', S), fri2: pacingIsRestDay('2026-10-09', S.holidays), plain: pacingIsRestDay('2026-10-09'), "
                       "sat: pacingIsRestDay('2026-10-10'), tue: pacingIsRestDay('2026-10-13', S), weekendOnly: pacingIsWeekend('2026-10-09'), "
                       "b1: pacingBudgetFor('2026-10-26', S.budget, S.holidays), b2: pacingBudgetFor('2026-10-26', S.budget), b3: pacingBudgetFor('2026-10-27', S.budget, S.holidays)})")
        self.assertEqual(res, {"fri": True, "fri2": True, "plain": False, "sat": True, "tue": False, "weekendOnly": False, "b1": 5, "b2": 2, "b3": 2})

    def test_holiday_plan_uses_the_five_hour_budget(self):
        r = js("const r = plan('2026-10-09', done('CORE-14')); return {codes: codes(r), budget: r.budgetHours, weekend: r.weekend, holiday: r.holiday};")
        self.assertEqual((r["budget"], r["weekend"], r["holiday"]), (5, True, True))
        self.assertEqual(r["codes"], ["CORE-14", "CORE-15", "CORE-16", "CORE-17", "CORE-18"])  # fills 5 h; the dated table's 3 CORE rounds are the on-time minimum

    def test_holiday_paper_is_a_single_sitting(self):
        r = js("const r = plan('2026-10-26', done('BLIND108-03')); return {codes: codes(r), mock: r.plan[0].hours, budget: r.budgetHours};")
        self.assertEqual(r["codes"], ["BLIND108-03", "MAIN-04"])  # paper 3 h + MAIN 1.25 h within the 5 h holiday
        self.assertEqual((r["mock"], r["budget"]), (3, 5))

    def test_without_holidays_the_same_day_is_a_weekday(self):
        r = js("const s = Object.assign({}, S, {holidays: undefined}); const r = pacingPlan({schedule: s, completed: done('BLIND108-03'), today: '2026-10-26'}); return {budget: r.budgetHours, weekend: r.weekend, part: r.plan[0].part};")
        self.assertEqual((r["budget"], r["weekend"], r["part"]), (2, False, "closed"))


class TestPacingPlan(unittest.TestCase):
    def test_spent_today_shrinks_todays_plan(self):
        res = js("""
          const c = done('CORE-07');
          const r = s => pacingPlan({ schedule: S, completed: c, today: '2026-10-05', spentToday: s });
          const inFlight = pacingPlan({ schedule: S, completed: c, today: '2026-10-05', spentToday: 2, partial: {code: 'CORE-07', phaseIndex: 1} });
          return {none: codes(r(0)), half: codes(r(1)), full: codes(r(2)), spent: r(1).spentHours, planHours: r(1).planHours, inFlight: codes(inFlight)};
        """)
        self.assertEqual(res["none"], ["CORE-07", "CORE-08"])
        self.assertEqual(res["half"], ["CORE-07"])
        self.assertEqual(res["full"], [])
        self.assertEqual(res["spent"], 1)
        self.assertEqual(res["planHours"], 1)
        self.assertEqual(res["inFlight"], ["CORE-07:rest"])  # a started task is always shown

    def test_on_track_every_day_follows_the_dated_table(self):
        """A learner who does exactly the table each day always gets that day's table back (plus, on the under-filled
        early days, the next tasks pulled forward into spare budget), status on/ahead, no cuts."""
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
                self.assertEqual(day["plan"][:len(day["table"])], day["table"])  # the dated rows are the on-time minimum
                if "2026-10-13" <= day["date"] <= "2026-10-31":
                    self.assertEqual(day["plan"], day["table"])  # from 10/13 the rows are full days
                # From 11/01 every paper is done: BUFFER skips its 補考 phase and 補強 runs a day ahead of the table.
                self.assertFalse(any(p.startswith("WRAP") for p in day["plan"]) and day["date"] < "2026-11-09", day["plan"])
                self.assertEqual(day["cut"], [])
                self.assertFalse(day["overload"])
                self.assertIn(day["status"], ("on", "ahead"))

    def test_first_day_sunday_fills_five_hours_from_core_07(self):
        r = js("const r = plan('2026-10-04', done('CORE-07')); return {codes: codes(r), hours: r.planHours, budget: r.budgetHours, weekend: r.weekend, status: r.status};")
        self.assertEqual(r["codes"], ["CORE-07", "CORE-08", "CORE-09", "CORE-10", "CORE-11"])  # the dated row lists the first 3; spare budget pulls 2 more
        self.assertEqual((r["hours"], r["budget"], r["weekend"], r["status"]), (5, 5, True, "on"))

    def test_weekday_fills_two_hours_and_starts_from_earliest_uncompleted(self):
        r = js("const r = plan('2026-10-05', done('CORE-07', ['CORE-08'])); return {codes: codes(r), hours: r.planHours};")
        # CORE-07 is still open (earlier than the completed CORE-08): it comes first, then CORE-09 fills the 2 h
        self.assertEqual(r["codes"], ["CORE-07", "CORE-09"])
        self.assertEqual(r["hours"], 2)

    def test_weekday_fits_one_hour_core_after_quarter_over_main(self):
        # A 1.25 h MAIN round leaves room 0.75 of a 2 h weekday; a 1 h task still fits within the 0.25 h tolerance.
        res = js("""
          const r = plan('2026-10-16', done('MOCK114-01'), {code: 'MOCK114-01', phaseIndex: 1});
          return {codes: codes(r), used: r.planHours};
        """)
        self.assertEqual(res["codes"], ["MOCK114-01:review", "MAIN-01"])
        self.assertEqual(res["used"], 2.25)

    def test_weekday_core_days_fill_two_hours(self):
        res = js("""
          const c = done('CORE-10'); const r = plan('2026-10-07', c);
          const hours = r.plan.map(p => S.tasks[p.code].kind + ':' + p.hours);
          return {codes: codes(r), hours, used: r.planHours};
        """)
        self.assertEqual(res["codes"][0], "CORE-10")
        self.assertGreaterEqual(len(res["codes"]), 2, res)
        self.assertLessEqual(res["used"], 2.25 + 1e-9)

    def test_no_task_is_added_when_room_is_gone(self):
        res = js("""
          const c = done('CORE-07'); const r = plan('2026-10-05', c);
          return {codes: codes(r), used: r.planHours};
        """)
        self.assertEqual(res["codes"], ["CORE-07", "CORE-08"])
        self.assertEqual(res["used"], 2)

    def test_weekday_mock_is_split_across_two_days(self):
        r = js("""
          const c = done('MOCK114-04');
          const day1 = plan('2026-10-19', c);
          const day2 = plan('2026-10-20', c, {code: 'MOCK114-04', phaseIndex: 1});
          const weekend = plan('2026-10-24', done('MOCK114-06', ['MOCK114-05']), {code: 'MOCK114-06', phaseIndex: 1});
          return {day1: codes(day1), h1: day1.planHours, day2: codes(day2), h2: day2.planHours, wk: codes(weekend), hw: weekend.planHours};""")
        self.assertEqual(r["day1"], ["MOCK114-04:closed"])
        self.assertEqual(r["h1"], 2)
        self.assertEqual(r["day2"], ["MOCK114-04:review", "MAIN-02"])  # 1 h check+fix, then the 1 h of other work
        self.assertEqual(r["h2"], 2.25)
        self.assertEqual(r["wk"], ["MOCK114-06:review", "BLIND108-01", "FOCUS-07"])  # Saturday: check (1 h) + next paper in one sitting (3 h) + 1 h FOCUS
        self.assertEqual(r["hw"], 5)

    def test_weekend_paper_is_one_sitting_plus_two_hours_of_other_work(self):
        r = js("const r = plan('2026-10-18', done('MOCK114-03')); return {codes: codes(r), hours: r.planHours, mockHours: r.plan[0].hours};")
        self.assertEqual(r["codes"], ["MOCK114-03", "FOCUS-05", "FOCUS-06"])
        self.assertEqual(r["mockHours"], 3)
        self.assertEqual(r["hours"], 5)

    def test_buffer_day_makes_up_missing_papers_first(self):
        # 11/01 with two papers outstanding: makeup papers come before BUFFER (earliest uncompleted first)
        r = js("""
          const c = done('BLIND108-05');
          const r = plan('2026-11-01', c);
          return {codes: codes(r), hard: r.hardMilestone};""")
        self.assertEqual(r["codes"], ["BLIND108-05"])
        self.assertTrue(r["hard"]["missed"])
        self.assertEqual(r["hard"]["remainingPapers"], 2)
        # all papers done -> BUFFER has nothing to make up: only its 2 h 補強 phase, then FOCUS-13 and REINF-01
        b = js("const r = plan('2026-11-01', done('BUFFER')); return {codes: codes(r), hours: r.planHours, next: r.nextMilestone.label, buffer: r.plan[0]};")
        self.assertEqual(b["codes"], ["BUFFER", "FOCUS-13", "REINF-01"])  # 2 h + 1 h + 2 h = the 5 h Sunday
        self.assertEqual(b["hours"], 5)
        self.assertEqual((b["buffer"]["phaseIndex"], b["buffer"]["hours"]), (1, 2))
        self.assertEqual(b["next"], "補強完成")

    def test_late_phases_are_gated_until_their_date(self):
        # Every paper done by 10/28: 補強 (BUFFER, REINF) opens early; the 2 h weekday holds BUFFER's 補強 phase.
        r = js("const r = plan('2026-10-28', done('BUFFER')); return {codes: codes(r), status: r.status, ahead: r.aheadCount};")
        self.assertEqual(r["codes"], ["BUFFER"])
        self.assertEqual(r["status"], "ahead")
        # 收尾 keeps its date (11/09) even when everything before it is done.
        self.assertEqual(js("return codes(plan('2026-11-05', done('WRAP-01')));"), [])
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


class TestPacingDayByDayWalk(unittest.TestCase):
    """v1.3.8: dynamic FOCUS changes which questions are asked, never the codes or hours; pin the day-by-day plan to the dated table."""

    def test_walk_from_core_20_follows_the_dated_table_with_no_cuts(self):
        res = js("""
          const c = done('CORE-21'); let partial = null; const out = [];
          S.days.filter(d => d.date >= '2026-10-12').forEach(day => {
            const r = plan(day.date, c, partial);
            out.push({date: day.date, plan: r.plan.map(p => [p.code, p.part]), table: day.items.filter(i => S.tasks[i.code]).map(i => [i.code, i.part]),
                      codes: day.codes, cut: r.cut, overload: r.overload, status: r.status, shortHours: r.shortHours});
            partial = null;
            r.plan.forEach(p => { if (p.part === 'closed') partial = {code: p.code, phaseIndex: 1}; else c[p.code] = 'x'; });
          });
          return {out, left: S.order.filter(k => !c[k])};""")
        days = res["out"]
        self.assertEqual([d["date"] for d in days][0], "2026-10-12")
        self.assertEqual(len(days), 33)  # 10/12 .. 11/13
        for d in days:
            with self.subTest(day=d["date"]):
                work_codes = [c for c in d["codes"] if c not in ("EXAM-CHECK", "STOP")]
                if d["date"] <= "2026-10-31":
                    self.assertEqual([code for code, _ in d["plan"]], work_codes)  # the day's code sequence is the dated row
                    self.assertEqual(d["plan"], d["table"])  # incl. weekday mock day 1 = closed, day 2 = review
                else:
                    # Every paper is done: 補強 runs ahead of the dated rows (BUFFER is 2 h shorter); 收尾 keeps 11/09.
                    self.assertFalse(d["date"] < "2026-11-09" and any(code.startswith("WRAP") for code, _ in d["plan"]), d["plan"])
                self.assertEqual(d["cut"], [])
                self.assertFalse(d["overload"])
                self.assertEqual(d["shortHours"], 0)
                self.assertIn(d["status"], ("on", "ahead"))
        self.assertEqual(days[-2]["codes"], ["EXAM-CHECK"])
        self.assertEqual(days[-1]["codes"], ["STOP"])
        self.assertEqual(res["left"], [])  # every dated task got done by 11/13
        weekday_papers = [(d["date"], d["plan"]) for d in days if any(part == "closed" for _, part in d["plan"])]
        self.assertTrue(weekday_papers, "the walk must include at least one weekday paper split over two days")
        for date_iso, plan in weekday_papers:
            nxt = next(d for d in days if d["date"] > date_iso)
            closed_code = next(code for code, part in plan if part == "closed")
            self.assertIn([closed_code, "review"], nxt["plan"], date_iso)  # the 核對 half lands on the next day


class TestPacingMilestones(unittest.TestCase):
    def test_next_milestone_days_and_remaining(self):
        r = js("""
          const r = plan('2026-10-21', done('MOCK114-05'));
          const m = r.nextMilestone;
          return {label: m.label, hard: m.hard, days: m.daysLeft, papers: m.remainingPapers, tasks: m.remainingTasks, hours: m.remainingHours,
                  hardDays: r.hardMilestone.daysLeft, hardPapers: r.hardMilestone.remainingPapers, daysLeft: r.daysLeft};""")
        self.assertEqual((r["label"], r["hard"], r["days"], r["papers"]), ("模考截止", True, 10, 8))
        self.assertEqual((r["hardDays"], r["hardPapers"], r["daysLeft"]), (10, 8, 10))
        self.assertEqual(r["hours"], 33.75)  # MOCK05 + MAIN-03 + MOCK06 + 6 BLIND + MAIN-04/05 + FOCUS-07..12

    def test_milestone_dates_and_hard_flag(self):
        r = js("return S.milestones.map(m => [m.date, m.hard, m.codes.length]);")
        self.assertEqual([(d, h) for d, h, _ in r], [("2026-10-17", False), ("2026-10-31", True), ("2026-11-11", False)])
        self.assertLess(r[0][2], r[1][2])
        self.assertLess(r[1][2], r[2][2])

    def test_hours_check_compares_required_with_available(self):
        r = js("const r = plan('2026-10-04', done('CORE-07')); return {req: r.requiredHours, avail: r.availableHours, days: r.daysLeft};")
        self.assertEqual((r["req"], r["avail"], r["days"]), (29.25, 43, 13))  # 10/09 (補假) counts as a 5 h day: 43 h = 20 weekend + 5 holiday + 18 weekday
        self.assertFalse(js("return plan('2026-10-04', done('CORE-07')).nextMilestone.atRisk;"))

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
    def test_behind_cuts_variants_then_focus_and_keeps_papers_and_main(self):
        r = js("""
          const c = done('CORE-16'); const r = plan('2026-10-16', c);
          return {status: r.status, cut: r.cut, detail: r.cutDetail.map(d => d.reason), codes: codes(r), behind: r.behindCount, overload: r.overload,
                  req: r.hardMilestone.requiredHours, avail: r.hardMilestone.availableHours, soft: r.nextMilestone};""")
        self.assertEqual(r["status"], "behind")
        self.assertTrue(r["cut"], "something must be cut")
        self.assertTrue([c for c in r["cut"] if c.startswith("FOCUS")])
        self.assertTrue([c for c in r["cut"] if c.startswith("CORE")])
        self.assertFalse([c for c in r["cut"] if c.startswith(("MOCK", "BLIND", "WRAP", "BUFFER", "MAIN"))])
        self.assertNotIn("weak", r["detail"])
        self.assertLessEqual(r["req"], r["avail"] + 0.5)  # after the cuts the 10/31 hours fit
        self.assertFalse(r["overload"])
        self.assertEqual(r["soft"]["label"], "核心收尾關卡")  # the earlier milestone is soft: reported, never a reason to cut
        self.assertTrue(r["codes"], "a plan still exists")
        self.assertFalse(set(c.split(":")[0] for c in r["codes"]) & set(r["cut"]), "cut tasks never appear in today's plan")

    def test_cut_order_is_core_variants_then_focus_then_core_base_then_reinforce(self):
        order = ["core-variant", "focus", "core", "reinforce"]
        # Mild pressure: variants first, then FOCUS latest first; the 母題 sessions are untouched.
        r = js("""
          const r = plan('2026-10-16', done('CORE-16'));
          return {cut: r.cut, reasons: r.cutDetail.map(d => d.reason), codes: r.cutDetail.map(d => d.code)};""")
        self.assertEqual(r["reasons"], sorted(r["reasons"], key=order.index))
        self.assertEqual(set(r["reasons"]), {"core-variant", "focus"})
        focus = [c for c, why in zip(r["codes"], r["reasons"]) if why == "focus"]
        self.assertEqual(focus, sorted(focus, reverse=True), "FOCUS is cut latest first")
        self.assertEqual(focus[0], "FOCUS-12")
        # Heavy pressure: every stage is used, always in this order.
        r = js("""
          const r = plan('2026-10-20', done('CORE-07'));
          const first = r.cutDetail.filter(d => d.milestone === '2026-10-31');  // stages are ordered within each milestone's candidate list
          return {reasons: r.cutDetail.map(d => d.reason), codes: r.cutDetail.map(d => d.code), first: first.map(d => d.reason)};""")
        self.assertEqual(r["first"], sorted(r["first"], key=order.index))
        self.assertEqual(set(r["first"]), {"core-variant", "focus", "core"})
        self.assertIn("reinforce", r["reasons"])
        self.assertNotIn("weak", r["reasons"])
        self.assertFalse([c for c in r["codes"] if c.startswith(("MOCK", "BLIND", "WRAP", "BUFFER", "MAIN"))])

    def test_cut_candidates_put_variants_before_focus_before_base_core(self):
        r = js("""
          const cands = pacingCutCandidates(S.order.filter(c => /^(CORE|FOCUS|REINF|MAIN)/.test(c)), S, done('CORE-07'), null, new Set());
          return cands.map(c => c.code + ':' + c.reason);""")
        reasons = [x.split(":")[1] for x in r]
        self.assertEqual(reasons, sorted(reasons, key=["core-variant", "focus", "core", "reinforce"].index))
        self.assertFalse([x for x in r if x.startswith("MAIN")], "MAIN is never a cut candidate")
        self.assertEqual([x for x in r if x.endswith(":focus")][0], "FOCUS-13:focus")  # latest first

    def test_each_subject_keeps_its_base_core_session(self):
        # A brand-new learner (nothing done) under heavy pressure: the six first 母題 sessions CORE-01..06 are never cut.
        r = js("""
          const r = plan('2026-10-14', {}); const x = plan('2026-10-30', {});
          return {cut: r.cut, overload: r.overload, cut2: x.cut, overload2: x.overload, short: x.shortHours};""")
        for n in range(1, 7):
            self.assertNotIn(f"CORE-{n:02d}", r["cut"])
            self.assertNotIn(f"CORE-{n:02d}", r["cut2"])
        self.assertFalse(r["overload"])  # 10/14: dropping variants, FOCUS and later CORE sessions is enough
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
