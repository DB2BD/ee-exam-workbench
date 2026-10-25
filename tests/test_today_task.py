# -*- coding: utf-8 -*-
"""K3 一鍵開始今天: generated schedule freshness, data integrity, store logic, backup."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "scripts"))
import build_daily_schedule as bds  # noqa: E402

SCHEDULE_JS = WORKSPACE / "src/data/dailySchedule.generated.js"
TODAY_JS = WORKSPACE / "src/components/todayTask.js"
PACING_JS = WORKSPACE / "src/domain/pacing.js"
SM2_JS = WORKSPACE / "src/state/sm2Store.js"


def run_node(expression, storage=None, extra_sources=()):
    sources = [(WORKSPACE / "src/components/icons.js").read_text(encoding="utf-8"), SCHEDULE_JS.read_text(encoding="utf-8"), PACING_JS.read_text(encoding="utf-8"), TODAY_JS.read_text(encoding="utf-8")]
    sources += [Path(p).read_text(encoding="utf-8") for p in extra_sources]
    script = f"""
const vm = require('vm');
const data = {json.dumps(storage or {}, ensure_ascii=False)};
const localStorage = {{
  getItem: k => Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null,
  setItem: (k, v) => {{ data[k] = String(v); }},
  removeItem: k => {{ delete data[k]; }},
}};
const context = {{ console, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(chr(10).join(sources) + chr(10) + 'globalThis.__result = (' + expression + ');', ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify({{result: context.__result, storage: data}}));
"""
    done = subprocess.run(["node", "-"], input=script, cwd=WORKSPACE, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def local_ms(y, m, d, hh=9, mm=0):
    # Mirror JS local-time Date so the test is timezone independent.
    out = subprocess.run(
        ["node", "-e", f"process.stdout.write(String(new Date({y},{m - 1},{d},{hh},{mm}).getTime()))"],
        capture_output=True, text=True, check=True)
    return int(out.stdout)


class TestGeneratedSchedule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schedule = bds.build_schedule()
        cls.dashboard = (WORKSPACE / "dashboard-data.js").read_text(encoding="utf-8")

    def test_generated_files_are_fresh(self):
        self.assertEqual(SCHEDULE_JS.read_text(encoding="utf-8"), bds.render_js(self.schedule))
        self.assertEqual(bds.OUT_JSON.read_text(encoding="utf-8"), bds.render_json(self.schedule))

    def test_every_day_code_has_a_task_or_is_non_work(self):
        for day in self.schedule["days"]:
            for code in day["codes"]:
                self.assertTrue(code in self.schedule["tasks"] or code in bds.NON_WORK, code)

    def test_task_counts_qids_and_minutes(self):
        tasks = self.schedule["tasks"]
        for prefix, count, minutes in (("CORE", 24, 60), ("FOCUS", 13, 60), ("MAIN", 5, 75), ("MOCK114", 6, 180), ("BLIND108", 6, 180),
                                       ("REINF", 9, 120), ("WRAP", 3, 120)):
            codes = [c for c in tasks if c.startswith(prefix + "-")]
            self.assertEqual(len(codes), count, prefix)
            for code in codes:
                task = tasks[code]
                self.assertEqual(sum(p["minutes"] for p in task["phases"]), minutes, code)
                self.assertEqual(task["hours"], minutes / 60, code)
                if prefix in ("CORE", "FOCUS", "MAIN", "MOCK114", "BLIND108"):
                    self.assertGreaterEqual(len(task["qids"]), 1, code)
                    for qid in task["qids"]:
                        self.assertIn(f'"{qid}"', self.dashboard, f"{code}: {qid} missing in dashboard-data.js")
                else:
                    self.assertEqual(task["qids"], [], f"{code}: practice/review tasks have no fixed qids")
                    self.assertIn(task["kind"], ("practice", "review"), code)
        self.assertEqual(tasks["BUFFER"]["hours"], 4)
        self.assertEqual(len(tasks), 67)
        self.assertEqual(len(self.schedule["order"]), 67)

    def test_retired_mix_and_ext_are_not_in_the_schedule(self):
        tasks = self.schedule["tasks"]
        self.assertFalse([c for c in tasks if c.startswith(("MIX-", "EXT-"))])
        self.assertFalse([c for c in self.schedule["order"] if c.startswith(("MIX-", "EXT-", "RECOVERY"))])
        self.assertNotIn("optionalOrder", self.schedule)
        self.assertFalse([t for t in tasks.values() if t.get("optional") or t["kind"] in ("mix", "ext")])
        self.assertNotIn("RECOVERY", bds.NON_WORK)

    def test_retired_weak_is_not_in_the_schedule(self):
        s = self.schedule
        self.assertFalse([c for c in s["tasks"] if c.startswith("WEAK")])
        self.assertFalse([c for c in s["order"] if c.startswith("WEAK")])
        self.assertNotIn("WEAK", bds.GROUP_COUNTS)
        self.assertFalse([t for t in s["tasks"].values() if t.get("launch") == "random-balanced"])
        self.assertFalse([c for d in s["days"] for c in d["codes"] if c.startswith("WEAK")])

    def test_practice_tasks_expose_launch_modes_and_gates(self):
        tasks = self.schedule["tasks"]
        self.assertEqual({tasks[f"REINF-{i:02d}"]["launch"] for i in range(1, 10)}, {"random-reinforce"})
        self.assertEqual(tasks["BUFFER"]["launch"], "random-reinforce")
        self.assertEqual(tasks["BUFFER"]["notBefore"], "2026-11-01")
        self.assertEqual(tasks["REINF-01"]["notBefore"], "2026-11-02")
        self.assertEqual(tasks["WRAP-03"]["notBefore"], "2026-11-09")
        self.assertNotIn("notBefore", tasks["FOCUS-01"])
        self.assertNotIn("notBefore", tasks["MOCK114-01"])
        self.assertTrue(tasks["CORE-07"]["variant"])
        self.assertFalse(tasks["CORE-01"]["variant"])

    def test_milestones_budget_days_and_order(self):
        s = self.schedule
        self.assertEqual(s["budget"], {"weekday": 2, "weekend": 5})
        self.assertEqual([(m["date"], m["label"], m["hard"]) for m in s["milestones"]],
                         [("2026-10-17", "核心收尾關卡", False), ("2026-10-31", "模考截止", True), ("2026-11-11", "補強完成", False)])
        hard = s["milestones"][1]
        papers = [c for c in s["order"] if c.startswith(("MOCK114-", "BLIND108-"))]
        self.assertEqual(len(papers), 12)
        self.assertTrue(set(papers) <= set(hard["codes"]))
        self.assertNotIn("BUFFER", hard["codes"])
        self.assertEqual(len(s["days"]), 41)
        self.assertEqual(s["days"][0]["date"], "2026-10-04")
        self.assertEqual(s["days"][0]["dow"], 0)  # Sunday
        self.assertEqual(s["days"][0]["budget"], 5)
        self.assertEqual(s["order"][:6], [f"CORE-0{i}" for i in range(1, 7)])
        self.assertEqual(s["order"][6], "CORE-07")
        self.assertEqual(s["due"]["CORE-01"], "2026-10-03")
        self.assertEqual(s["due"]["MOCK114-01"], "2026-10-16")  # closed 10/15, 核對 10/16
        for day in s["days"]:
            self.assertLessEqual(day["hours"], day["budget"] + 0.5)

    def test_pdf_files_exist_for_paper_tasks(self):
        for code, task in self.schedule["tasks"].items():
            if code.startswith(("MOCK114", "BLIND108")):
                self.assertTrue((WORKSPACE / "data/official_pdfs/pe" / Path(task["pdf"]).name).is_file(), code)

    def test_phase_closed_flags(self):
        tasks = self.schedule["tasks"]
        self.assertEqual([p["closed"] for p in tasks["CORE-01"]["phases"]], [True, False, False])
        self.assertEqual([p["closed"] for p in tasks["CORE-07"]["phases"]], [True, True, False, False])
        self.assertEqual(tasks["CORE-07"]["phases"][0]["qids"], [tasks["CORE-07"]["qids"][0]])
        self.assertEqual(tasks["CORE-07"]["phases"][1]["qids"], [tasks["CORE-07"]["qids"][1]])
        self.assertIn("scoringNote", tasks["MOCK114-06"])

    def test_parser_fails_loudly_on_mismatch(self):
        with self.assertRaises(bds.ParseError):
            bds.parse_days("| 2026-09-23（三） | `CORE-01` | 1 | x |")
        with self.assertRaises(bds.ParseError):
            bds.parse_milestones("no milestones here")
        with self.assertRaises(bds.ParseError):
            bds.parse_days("| 2026-10-04（日） | 4 | `CORE-07` |")  # not 41 continuous rows


class TestTodayTaskStore(unittest.TestCase):
    def test_next_task_skips_completed_not_by_date(self):
        # Only CORE-01/02 done by 10/20: the card still continues from CORE-03 (never by date) and cuts the surplus.
        now = local_ms(2026, 10, 20)
        res = run_node(
            "(() => { const s = {completed:{'CORE-01':'2026-09-23T00:00:00.000Z','CORE-02':'2026-09-24T00:00:00.000Z'}, active:null};"
            f"const vm = todayTaskViewModel(s, {now}); return {{code: vm.code, mode: vm.mode, status: vm.status, cut: vm.cutText}}; }})()")["result"]
        self.assertEqual(res["code"], "CORE-03")
        self.assertEqual(res["mode"], "task")
        self.assertEqual(res["status"], "behind")
        self.assertTrue(res["cut"].startswith("今天先跳過："), res["cut"])
        self.assertIn("（有空再做）", res["cut"])
        self.assertIn("模考卷照順序做，做不完的排到 11/01 緩衝日補考", res["cut"])  # hours still short after every allowed cut

    def test_plan_line_shows_budget_and_planned_hours(self):
        done = {f"CORE-0{i}": "x" for i in range(1, 7)}
        sunday = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 4)}).planText")["result"]
        monday = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 5)}).planText")["result"]
        self.assertEqual(sunday, "今天預算 5 小時（週末）｜還要做約 5 小時")  # CORE-07～11 (the dated row lists 07～09; spare budget pulls 2 more)
        self.assertEqual(monday, "今天預算 2 小時（平日）｜還要做約 2 小時")  # CORE-07, CORE-08 (a 2 h weekday)

    def test_plan_line_says_holiday_on_a_holiday(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("CORE-14")]}
        plan = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 9)}).planText")["result"]
        self.assertTrue(plan.startswith("今天預算 5 小時（假日）｜"), plan)
        self.assertNotIn("週末", plan)

    def test_plan_line_when_todays_share_is_done(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order}
        done["WRAP-03"] = "2026-10-05T04:00:00.000Z"
        text = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 5, 14)}).planText")["result"]
        self.assertEqual(text, "今天的份量已完成")

    def test_tasks_done_today_use_up_todays_budget(self):
        # Finishing a task must lower 「還要做」 instead of pulling a fresh 2 h of work into the same day.
        done = {f"CORE-0{i}": "x" for i in range(1, 7)}
        at = local_ms(2026, 10, 5, 10)
        now = local_ms(2026, 10, 5, 14)
        expr = ("(() => { const c = Object.assign(%s, {'CORE-07': new Date(%d).toISOString()}); const one = todayTaskViewModel({completed:c, active:null}, %d);"
                " const c2 = Object.assign({}, c, {'CORE-08': new Date(%d).toISOString()}); const two = todayTaskViewModel({completed:c2, active:null}, %d);"
                " return {one: one.planText, oneCode: one.code, two: two.planText, mode: two.mode, extra: two.code, html: todayTaskCardHtml(two)}; })()") % (json.dumps(done), at, now, at, now)
        res = run_node(expr)["result"]
        self.assertEqual(res["one"], "今天預算 2 小時（平日）｜已做約 1 小時｜還要做約 1 小時")
        self.assertEqual(res["oneCode"], "CORE-08")
        self.assertEqual(res["two"], "今天的份量已完成")
        self.assertEqual(res["mode"], "day-done")
        self.assertEqual(res["extra"], "CORE-09")  # optional extra work stays one click away
        self.assertIn("選做下一個</button>", res["html"])
        self.assertIn("分鐘，CORE-09）", res["html"])

    def test_resume_computes_remaining_time(self):
        started = local_ms(2026, 10, 3, 9, 0)
        now = started + 10 * 60000
        res = run_node(
            f"(() => {{ const s = {{completed:{{}}, active:{{code:'CORE-01', phaseIndex:0, phaseStartedAt:{started}}}}}; "
            f"const v = todayTaskViewModel(s, {now}); return {{a: v.active, p: v.primaryAction}}; }})()")["result"]
        self.assertEqual(res["a"]["remainingMs"], 25 * 60000)
        self.assertFalse(res["a"]["expired"])
        self.assertEqual(res["p"], "resume")

    def test_expired_phase_does_not_auto_advance(self):
        started = local_ms(2026, 10, 3, 9, 0)
        now = started + 3 * 3600 * 1000
        res = run_node(
            f"(() => {{ const s = {{completed:{{}}, active:{{code:'CORE-01', phaseIndex:0, phaseStartedAt:{started}}}}}; "
            f"const v = todayTaskViewModel(s, {now}); return v.active; }})()")["result"]
        self.assertTrue(res["expired"])
        self.assertEqual(res["remainingMs"], 0)
        self.assertEqual(res["phaseIndex"], 0)
        self.assertEqual(res["solutionQids"], [])

    def test_closed_phase_has_no_solution_entry_and_review_does(self):
        t0 = local_ms(2026, 10, 3, 9, 0)
        res = run_node(
            f"(() => {{ let s = todayTaskStart({{completed:{{}}, active:null}}, {t0}); "
            f"const closed = todayTaskViewModel(s, {t0}).active; "
            f"s = todayTaskAdvance(s, {t0 + 1000}); const review = todayTaskViewModel(s, {t0 + 1000}).active; "
            "return {closed, review}; })()")["result"]
        self.assertTrue(res["closed"]["closed"])
        self.assertEqual(res["closed"]["solutionQids"], [])
        self.assertEqual(res["closed"]["questionQids"], ["EE-114-01-3"])
        self.assertFalse(res["review"]["closed"])
        self.assertEqual(res["review"]["solutionQids"], ["EE-114-01-3"])

    def test_closed_phase_markup_contains_no_check_entry(self):
        t0 = local_ms(2026, 10, 3, 9, 0)
        res = run_node(
            f"(() => {{ const s = todayTaskStart({{completed:{{}}, active:null}}, {t0}); "
            f"return todayTaskOverlayHtml(todayTaskViewModel(s, {t0})); }})()")["result"]
        self.assertNotIn("data-today-check", res)
        self.assertNotIn("核對", res.replace("停筆，開始核對", ""))
        self.assertIn("停筆，開始核對", res)
        self.assertIn('class="btn-pdf today-task-abandon" data-today-act="abandon">放棄本次', res)
        self.assertLess(res.index('data-today-act="leave"'), res.index("today-task-abandon"))

    def test_stop_needs_confirm_only_with_more_than_five_minutes(self):
        res = run_node(
            "[todayTaskStopNeedsConfirm({closed:true,expired:false,remainingMs:5*60000+1}),"
            "todayTaskStopNeedsConfirm({closed:true,expired:false,remainingMs:5*60000}),"
            "todayTaskStopNeedsConfirm({closed:true,expired:true,remainingMs:0}),"
            "todayTaskStopNeedsConfirm({closed:false,expired:false,remainingMs:3600000}),"
            "todayTaskStopNeedsConfirm(null)]")["result"]
        self.assertEqual(res, [True, False, False, False, False])

    def test_overlay_source_wires_escape_focus_and_finish_focus(self):
        src = TODAY_JS.read_text(encoding="utf-8")
        self.assertIn("event.key === 'Escape'", src)
        self.assertIn("全部記錄完成，按「完成核對」結束", src)
        self.assertIn("scrollIntoView({ block: 'center' })", src)
        self.assertNotIn("window.confirm", src)

    def test_paper_task_shows_pdf_only_in_closed_phase(self):
        t0 = local_ms(2026, 10, 17, 9, 0)
        order = json.loads(bds.render_json(bds.build_schedule()))["order"]
        done = {c: "2026-10-01T00:00:00.000Z" for c in order[:order.index("MOCK114-01")]}
        res = run_node(
            f"(() => {{ let s = todayTaskStart({{completed:{json.dumps(done)}, active:null}}, {t0}); "
            f"const a = todayTaskViewModel(s, {t0}).active; s = todayTaskAdvance(s, {t0}); "
            f"return [a.pdfUrl, todayTaskViewModel(s, {t0}).active.pdfUrl]; }})()")["result"]
        self.assertTrue(res[0].startswith("data/official_pdfs/pe/114"))
        self.assertEqual(res[1], "")

    def test_last_phase_completes_task_and_clears_active(self):
        t0 = local_ms(2026, 10, 3, 9, 0)
        res = run_node(
            f"(() => {{ let s = todayTaskStart({{completed:{{}}, active:null}}, {t0}); "
            f"s = todayTaskAdvance(todayTaskAdvance(todayTaskAdvance(s, {t0}), {t0}), {t0}); "
            "return {active: s.active, done: Object.keys(s.completed), next: todayTaskCurrentCode(s)}; })()")["result"]
        self.assertIsNone(res["active"])
        self.assertEqual(res["done"], ["CORE-01"])
        self.assertEqual(res["next"], "CORE-02")

    def test_abandon_clears_active_only(self):
        res = run_node(
            "todayTaskAbandon({completed:{'CORE-01':'2026-09-23T00:00:00.000Z'}, active:{code:'CORE-02',phaseIndex:0,phaseStartedAt:1}})")["result"]
        self.assertIsNone(res["active"])
        self.assertEqual(list(res["completed"]), ["CORE-01"])

    def test_start_from_marks_earlier_codes_done_and_keeps_later_ones(self):
        # Learners who already worked on paper set their position once instead
        # of replaying CORE-01..; earlier codes become done, later ones open.
        res = run_node(
            "(() => { const s = todayTaskStartFrom({completed:{'FOCUS-01':'old'}, active:{code:'CORE-01',phaseIndex:0,phaseStartedAt:1}}, 'CORE-14', 0); "
            "return {next: todayTaskCurrentCode(s), done: Object.keys(s.completed).length, active: s.active, mix: s.completed['FOCUS-01'], "
            "back: todayTaskCurrentCode(todayTaskStartFrom(s, 'CORE-05', 0)), bogus: todayTaskStartFrom(s, 'NOPE', 0) === s}; })()")["result"]
        self.assertEqual(res["next"], "CORE-14")
        # CORE-01..13 (everything before CORE-14 in the order) plus the later FOCUS-01 that was already done and stays 'old'
        self.assertEqual(res["done"], 14)
        self.assertIsNone(res["active"])
        self.assertEqual(res["mix"], "old")
        self.assertEqual(res["back"], "CORE-05")
        self.assertTrue(res["bogus"])

    def test_exam_check_stop_and_done_modes(self):
        empty = "{completed:{}, active:null}"
        modes = run_node(
            f"[todayTaskViewModel({empty}, {local_ms(2026, 11, 12)}).mode, todayTaskViewModel({empty}, {local_ms(2026, 11, 13)}).mode, "
            f"todayTaskViewModel({empty}, {local_ms(2026, 11, 20)}).mode, "
            f"todayTaskViewModel({{completed: Object.fromEntries(DAILY_SCHEDULE.order.map(c => [c, 'x'])), active:null}}, {local_ms(2026, 10, 3)}).mode]")["result"]
        self.assertEqual(modes, ["exam-check", "stop", "stop", "done"])

    def test_rest_days_show_no_budget_or_milestone_lines(self):
        # 11/12 and 11/13 have no study hours: the card must not say 「今天預算 2 小時」, and after the
        # exam no 「已過 10/31 模考截止｜仍剩 N 份卷」 nag either.
        empty = "{completed:{}, active:null}"
        html = run_node(
            f"[{local_ms(2026, 11, 12)}, {local_ms(2026, 11, 13)}, {local_ms(2026, 11, 20)}].map(t => todayTaskCardHtml(todayTaskViewModel({empty}, t)))")["result"]
        for card in html:
            self.assertNotIn("預算", card)
            self.assertNotIn("today-pacing-milestone", card)
            self.assertNotIn("today-pacing-cut", card)
        self.assertIn("今天不開新題", html[0])
        self.assertIn("好好休息", html[2])

    def test_store_roundtrip_and_corrupt_storage(self):
        res = run_node(
            "(() => { saveTodayTaskState({completed:{'CORE-01':'2026-09-23T00:00:00.000Z', 'BOGUS':'x'}, active:{code:'CORE-02',phaseIndex:1,phaseStartedAt:5}}); "
            "return loadTodayTaskState(); })()")["result"]
        self.assertEqual(list(res["completed"]), ["CORE-01"])
        self.assertEqual(res["active"]["phaseIndex"], 1)
        bad = run_node("loadTodayTaskState()", storage={"EE_EXAM_TODAY_TASK_V1": "{not json"})["result"]
        self.assertEqual(bad, {"completed": {}, "active": None})
        nostore = run_node("(() => { try { return loadTodayTaskState({getItem(){ throw new Error('x'); }}); } catch (e) { return 'threw'; } })()")["result"]
        self.assertEqual(nostore, {"completed": {}, "active": None})

    def test_user_text_is_escaped(self):
        res = run_node("todayTaskEscape('<img onerror=\"x\">&')")["result"]
        self.assertEqual(res, "&lt;img onerror=&quot;x&quot;&gt;&amp;")


class TestTodayTaskStructure(unittest.TestCase):
    def test_build_includes_files_in_order_and_card_slot(self):
        build = (WORKSPACE / "scripts/build_workbench.py").read_text(encoding="utf-8")
        gen = build.index("'src/data/dailySchedule.generated.js'")
        dp = build.index("'src/components/dailyPractice.js'")
        tt = build.index("'src/components/todayTask.js'")
        pacing = build.index("'src/domain/pacing.js'")
        self.assertLess(gen, dp)
        self.assertLess(dp, tt)
        self.assertLess(pacing, tt)
        self.assertGreater(build.index("'src/styles/v13-pacing.css'"), build.index("'src/styles/v122-design.css'"))
        self.assertLess(build.index('id="today-task-card"'), build.index('class="home-primary-actions"'))


class TestTodayTaskBackup(unittest.TestCase):
    def test_backup_source_handles_key(self):
        text = SM2_JS.read_text(encoding="utf-8")
        self.assertIn("EE_EXAM_TODAY_TASK_V1", text)
        self.assertIn("todayTask: backupReadTodayTask(storage)", text)
        self.assertIn("BACKUP_TODAY_TASK_KEY, JSON.stringify(nextTodayTask)", text)
        # key must be in the rollback snapshot list
        self.assertRegex(text, r"BACKUP_DAILY_PRACTICE_KEY, BACKUP_TODAY_TASK_KEY")

    def test_backup_keeps_weekday_mock_hold(self):
        # A held weekday mock (「先離開，明天核對」) must survive export／import; otherwise the restored
        # state auto-opens an expired 核對 phase instead of the 接續 card.
        res = run_node(
            "(() => { const errors = []; const v = backupValidateTodayTask({completed:{}, active:{code:'MOCK114-01', phaseIndex:1, phaseStartedAt:5, "
            "mockId:'114-01-5', holdDate:'2026-10-15', heldFrom:'bad'}}, errors); return {errors, active: v.active}; })()",
            extra_sources=[SM2_JS])["result"]
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["active"]["holdDate"], "2026-10-15")
        self.assertNotIn("heldFrom", res["active"])


DONE_ONE_TO_SIX = {f"CORE-0{i}": "2026-10-03T00:00:00.000Z" for i in range(1, 7)}


class TestTodayTaskPacingCard(unittest.TestCase):
    """v1.3: today's plan, milestone line, cuts, weekday-mock continuation (view-model + card html)."""

    def vm(self, completed, now, active="null"):
        res = run_node(
            f"(() => {{ const s = {{completed:{json.dumps(completed)}, active:{active}}}; "
            f"const v = todayTaskViewModel(s, {now}); "
            "return {mode:v.mode, code:v.code, part:v.part, items:v.items.map(i => i.code), rest:v.restText, milestone:v.milestoneText, "
            "cut:v.cutText, status:v.status, held:v.held, suggestion:v.suggestion, plan:v.planText, action:v.primaryAction, "
            "html: todayTaskCardHtml(v)}; })()")
        return res["result"]

    def test_primary_task_then_rest_of_today(self):
        res = self.vm(DONE_ONE_TO_SIX, local_ms(2026, 10, 4))
        self.assertEqual(res["code"], "CORE-07")
        self.assertEqual(res["items"], ["CORE-07", "CORE-08", "CORE-09", "CORE-10", "CORE-11"])  # Sunday: 5 h budget
        self.assertTrue(res["rest"].startswith("今天還有："), res["rest"])
        self.assertIn("（CORE-08）", res["rest"])
        self.assertIn("（CORE-11）", res["rest"])
        self.assertNotIn("CORE-08｜", res["rest"])  # the title leads, the code follows
        self.assertNotIn("弱題分析", res["rest"])
        self.assertIn("今天還有：", res["html"])
        self.assertIn('<span class="today-task-eyebrow">下一個任務</span>', res["html"])
        self.assertIn('<code class="today-task-code">CORE-07</code>', res["html"])
        self.assertLess(res["html"].index('<code class="today-task-code">CORE-07</code>'), res["html"].index("今天還有："))
        self.assertIn("</svg> 開始<", res["html"])

    def test_milestone_line_counts_days_and_papers(self):
        res = self.vm(DONE_ONE_TO_SIX, local_ms(2026, 10, 5))
        # next milestone is the non-hard 10/17: hours plus the hard deadline's paper count
        self.assertTrue(res["milestone"].startswith("距 10/17 核心收尾關卡還有 12 天｜剩 "), res["milestone"])
        self.assertIn("｜10/31 模考截止剩 12 份卷", res["milestone"])
        # after 10/17 the hard milestone is next: 「距 10/31 模考截止還有 N 天｜剩 X 份卷」
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("MOCK114-03")]}
        res = self.vm(done, local_ms(2026, 10, 18))
        self.assertEqual(res["milestone"], "距 10/31 模考截止還有 13 天｜剩 10 份卷")
        self.assertIn('class="today-pacing-milestone"', res["html"])

    def test_pace_line_helper(self):
        res = run_node(
            "[todayTaskPaceLine({behindCount:3, behindHours:5.25, aheadCount:0, aheadHours:0}), "
            "todayTaskPaceLine({behindCount:0, aheadCount:0}), "
            "todayTaskPaceLine({behindCount:0, aheadCount:2, aheadHours:4}), "
            "todayTaskPaceLine(null)]")["result"]
        self.assertEqual(res, ["落後約 5.25 小時（3 項未按日程完成）", "照日程", "超前約 4 小時", ""])

    def test_pacing_exposes_behind_hours(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("CORE-16")]}
        res = run_node(
            "(() => { const p = pacingPlan({schedule: DAILY_SCHEDULE, completed:"
            f"{json.dumps(done)}, today:'2026-10-16'}}); "
            "return {n: p.behindCount, h: p.behindHours, sum: p.behindCodes.reduce((n, c) => n + pacingRemainingHours(DAILY_SCHEDULE.tasks[c], null), 0)}; })()")["result"]
        self.assertGreater(res["h"], 0)
        self.assertAlmostEqual(res["h"], res["sum"])

    def test_card_status_line_pace_line_and_no_due_count(self):
        res = self.vm(DONE_ONE_TO_SIX, local_ms(2026, 10, 5))
        card = run_node(
            f"todayTaskCardHtml(todayTaskViewModel({{completed:{json.dumps(DONE_ONE_TO_SIX)}, active:null}}, {local_ms(2026, 10, 5)}, {{dueCount: 4}}))")["result"]
        self.assertEqual(card.count("已完成 "), 1)
        self.assertNotIn("到期複習 4 題", card)  # the due count lives on the 到期複習 card only
        self.assertRegex(card, r'class="today-pacing-milestone">已完成 6／\d+｜距 10/17[^<]*</p>')
        self.assertTrue(re.search(r'class="today-pacing-pace[^"]*">(照日程|落後約|超前約)', card))
        none = run_node(
            f"todayTaskCardHtml(todayTaskViewModel({{completed:{json.dumps(DONE_ONE_TO_SIX)}, active:null}}, {local_ms(2026, 10, 5)}, {{dueCount: 0}}))")["result"]
        self.assertNotIn("到期複習", none)
        self.assertIn("</svg> 開始<", res["html"])

    def test_behind_shows_cut_line_and_keeps_papers(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("CORE-16")]}
        res = self.vm(done, local_ms(2026, 10, 16))
        self.assertEqual(res["status"], "behind")
        self.assertTrue(res["cut"].startswith("今天先跳過："), res["cut"])
        self.assertTrue(res["cut"].endswith("（有空再做）"), res["cut"])
        self.assertIn("FOCUS-", res["cut"])
        self.assertNotIn("WEAK", res["cut"])
        self.assertNotIn("MAIN", res["cut"])
        self.assertNotIn("MOCK", res["cut"])
        self.assertNotIn("BLIND", res["cut"])
        self.assertIn('class="today-pacing-cut"', res["html"])

    def test_soft_milestone_at_risk_shows_flexible_cue(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("CORE-16")]}
        res = self.vm(done, local_ms(2026, 10, 16))
        self.assertIn("10/17", res["milestone"])
        self.assertTrue(res["milestone"].endswith("｜彈性關卡：做不完就順延，不影響模考"), res["milestone"])
        ok = self.vm({c: "x" for c in order[:order.index("MAIN-01")]}, local_ms(2026, 10, 13))
        self.assertNotIn("彈性關卡", ok["milestone"])

    def test_long_cut_list_collapses_into_details(self):
        res = run_node(
            "(() => { const s = {completed:{'CORE-01':'2026-09-23T00:00:00.000Z'}, active:null};"
            f"const v = todayTaskViewModel(s, {local_ms(2026, 10, 20)}); return todayTaskCardHtml(v); }})()")["result"]
        self.assertIn("<details>", res)
        self.assertNotIn("<details open", res)
        self.assertRegex(res, r"<summary>今天先跳過 \d+ 項（有空再做）</summary>")
        self.assertIn("FOCUS-12", res)
        self.assertIn("11/01 緩衝日補考", res)
        short = run_node(
            "todayTaskCardHtml({mode:'task', pacing:{cut:['FOCUS-07','FOCUS-08','FOCUS-09'], overload:false, hardMilestone:null}, cutText:'今天先跳過：FOCUS-07～09（有空再做）', planText:'', milestoneText:'', suggestion:'', items:[], rest:[], restText:'', completedMap:{}, doneCount:0, total:1})")["result"]
        self.assertIn('<p class="today-pacing-cut">今天先跳過：FOCUS-07～09（有空再做）</p>', short)
        self.assertNotIn("<p class=\"today-pacing-cut\"><details", short)
        self.assertNotIn("<summary>今天先跳過", short)

    def test_ahead_after_all_mocks_suggests_113(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("BUFFER")]}
        res = self.vm(done, local_ms(2026, 10, 28))
        self.assertEqual(res["status"], "ahead")
        self.assertIn("113 年整卷", res["suggestion"])
        self.assertEqual(res["mode"], "task")  # every paper done: 補強 opens before its 11/01 date
        self.assertEqual(res["code"], "BUFFER")
        self.assertIn("today-pacing-suggestion", res["html"])

    def test_weekday_mock_day_one_is_closed_and_stops_the_day(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("MOCK114-04")]}
        res = self.vm(done, local_ms(2026, 10, 19))
        self.assertEqual((res["code"], res["part"]), ("MOCK114-04", "closed"))
        self.assertEqual(res["items"], ["MOCK114-04"])
        self.assertIn("今天閉卷，明天核對＋修復", res["html"])

    def test_held_mock_continues_next_day_as_first_item(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("MOCK114-04")]}
        active = "{code:'MOCK114-04', phaseIndex:1, phaseStartedAt:1000, mockId:'114-01-1000', holdDate:'2026-10-19'}"
        res = self.vm(done, local_ms(2026, 10, 20), active)
        self.assertEqual(res["code"], "MOCK114-04")
        self.assertEqual(res["action"], "resume")
        self.assertEqual(res["held"]["text"], "接續 MOCK114-04：核對＋修復")
        self.assertFalse(res["held"]["sameDay"])
        self.assertIn("接續 MOCK114-04：核對＋修復", res["html"])
        self.assertIn("</svg> 開始核對<", res["html"])
        self.assertLess(res["html"].index("接續 MOCK114-04"), res["html"].index("今天還有"))
        self.assertEqual(res["items"][0], "MOCK114-04")
        same = self.vm(done, local_ms(2026, 10, 19, 20), active)
        self.assertTrue(same["held"]["sameDay"])
        self.assertIn("今天的閉卷已完成，明天接續 MOCK114-04：核對＋修復", same["html"])
        self.assertIn("</svg> 現在就核對<", same["html"])

    def test_hold_and_resume_keep_phase_and_mock_id(self):
        res = run_node(
            "(() => { let s = todayTaskStartFrom({completed:{}, active:null}, 'MOCK114-04', 1); s = todayTaskStart(s, 1000); "
            "const id = s.active.mockId; s = todayTaskAdvance(s, 2000); "
            "const h = todayTaskHold(s, '2026-10-19'); const n = todayTaskNormalizeState(JSON.parse(JSON.stringify(h))); "
            "const r = todayTaskResumeHeld(n, 99000); "
            "return {id, held: h.active.holdDate, kept: n.active.holdDate, phase: n.active.phaseIndex, mock: n.active.mockId, "
            "resumed: r.active, noop: todayTaskResumeHeld(s, 5) === s}; })()")["result"]
        self.assertEqual(res["held"], "2026-10-19")
        self.assertEqual(res["kept"], "2026-10-19")
        self.assertEqual(res["phase"], 1)
        self.assertEqual(res["mock"], res["id"])
        self.assertNotIn("holdDate", res["resumed"])
        self.assertEqual(res["resumed"]["phaseStartedAt"], 99000)
        self.assertEqual(res["resumed"]["phaseIndex"], 1)
        self.assertTrue(res["noop"])

    def test_resumed_mock_does_not_offer_hold_again(self):
        # Day 2 (核對＋修復) after 「先離開，明天核對」 must not offer the same split again.
        now = local_ms(2026, 10, 20, 19)
        res = run_node(
            "(() => { let s = todayTaskStartFrom({completed:{}, active:null}, 'MOCK114-04', 1); s = todayTaskStart(s, 1000); "
            "s = todayTaskAdvance(s, 2000); const fresh = todayTaskOverlayHtml(todayTaskViewModel(s, " + str(now) + ")); "
            "s = todayTaskHold(s, '2026-10-19'); s = todayTaskNormalizeState(JSON.parse(JSON.stringify(todayTaskResumeHeld(s, " + str(now) + ")))); "
            "return {fresh, resumed: todayTaskOverlayHtml(todayTaskViewModel(s, " + str(now) + ")), heldFrom: s.active.heldFrom}; })()")["result"]
        self.assertIn('data-today-act="hold"', res["fresh"])
        self.assertNotIn('data-today-act="hold"', res["resumed"])
        self.assertIn('data-today-act="leave"', res["resumed"])
        self.assertEqual(res["heldFrom"], "2026-10-19")

    def test_hold_button_only_for_weekday_mock_after_closed_phase(self):
        def html(now, code, phase):
            return run_node(
                f"(() => {{ const s = {{completed:{{}}, active:{{code:'{code}', phaseIndex:{phase}, phaseStartedAt:{now}}}}}; "
                f"return todayTaskOverlayHtml(todayTaskViewModel(s, {now})); }})()")["result"]
        weekday = html(local_ms(2026, 10, 20), "MOCK114-04", 1)
        self.assertIn('data-today-act="hold"', weekday)
        self.assertIn("先離開，明天核對", weekday)
        self.assertNotIn('data-today-act="leave"', weekday)
        self.assertNotIn('data-today-act="hold"', html(local_ms(2026, 10, 20), "MOCK114-04", 0))  # still closed-book
        self.assertNotIn('data-today-act="hold"', html(local_ms(2026, 10, 24), "MOCK114-04", 1))  # Saturday: one sitting
        self.assertNotIn('data-today-act="hold"', html(local_ms(2026, 10, 20), "CORE-01", 1))
        self.assertIn('data-today-act="leave"', html(local_ms(2026, 10, 20), "CORE-01", 1))

    def test_start_any_uncompleted_code_but_not_completed_or_unknown(self):
        res = run_node(
            "(() => { const s0 = {completed:{'CORE-02':'x'}, active:null}; "
            "const a = todayTaskStart(s0, 1000, 'FOCUS-03'); const done = todayTaskStart(s0, 1000, 'CORE-02'); const bad = todayTaskStart(s0, 1000, 'MIX-01'); "
            "const plain = todayTaskStart(s0, 1000); "
            "return {a: a.active.code, done: done === s0, bad: bad === s0, plain: plain.active.code}; })()")["result"]
        self.assertEqual(res, {"a": "FOCUS-03", "done": True, "bad": True, "plain": "CORE-01"})

    def test_start_from_select_lists_current_codes_and_defaults_to_core_07(self):
        res = self.vm({}, local_ms(2026, 10, 5))
        self.assertIn('<option value="CORE-07" selected>', res["html"])
        self.assertIn('<option value="CORE-01">', res["html"])
        self.assertIn('<option value="FOCUS-13">', res["html"])
        self.assertIn('<option value="REINF-09">', res["html"])
        self.assertIn('<option value="BUFFER">', res["html"])
        for retired in ("MIX-", "EXT-", "RECOVERY", "WEAK-"):
            self.assertNotIn(retired, res["html"])
        self.assertIn("已在紙本做過前面的任務？", res["html"])
        # once CORE-01..07 are done the default follows today's task
        later = self.vm({**DONE_ONE_TO_SIX, "CORE-07": "x"}, local_ms(2026, 10, 5))
        self.assertIn('<option value="CORE-08" selected>', later["html"])

    def test_old_retired_codes_in_saved_state_are_dropped_harmlessly(self):
        res = run_node(
            "todayTaskNormalizeState({completed:{'MIX-01':'x','EXT-02':'y','RECOVERY':'z','CORE-01':'ok'}, active:{code:'MIX-03',phaseIndex:0,phaseStartedAt:5}})")["result"]
        self.assertEqual(list(res["completed"]), ["CORE-01"])
        self.assertIsNone(res["active"])

    def test_old_weak_progress_normalizes_cleanly_and_is_ignored(self):
        # v1.3.7 retired WEAK-01..11: progress saved by an older build must load without errors and simply drop them.
        res = run_node(
            "todayTaskNormalizeState({completed:{'WEAK-03':'2026-10-05T04:00:00.000Z','CORE-01':'ok','FOCUS-01':'2026-10-13T04:00:00.000Z'}, "
            "active:{code:'WEAK-04',phaseIndex:1,phaseStartedAt:5}})")["result"]
        self.assertEqual(sorted(res["completed"]), ["CORE-01", "FOCUS-01"])
        self.assertIsNone(res["active"])
        stored = json.dumps({"completed": {"WEAK-03": "x", "CORE-02": "y"}, "active": {"code": "WEAK-11", "phaseIndex": 0, "phaseStartedAt": 1}})
        loaded = run_node("loadTodayTaskState()", storage={"EE_EXAM_TODAY_TASK_V1": stored})["result"]
        self.assertEqual(loaded, {"completed": {"CORE-02": "y"}, "active": None})
        vm = run_node(f"(() => {{ const s = loadTodayTaskState(); const v = todayTaskViewModel(s, {local_ms(2026, 10, 12)}); return {{code: v.code, done: v.doneCount, mode: v.mode}}; }})()",
                      storage={"EE_EXAM_TODAY_TASK_V1": stored})["result"]
        self.assertEqual(vm["done"], 1)
        self.assertNotIn("WEAK", vm["code"])

    def test_reinforcement_day_plan(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("REINF-02")]}
        res = self.vm(done, local_ms(2026, 11, 3))
        self.assertEqual((res["code"], res["items"]), ("REINF-02", ["REINF-02"]))
        self.assertIn("距 11/11 補強完成還有 8 天", res["milestone"])

    def test_launch_phase_markup_and_no_empty_check_row(self):
        res = run_node(
            "(() => { let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); "
            "const first = todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); "
            "s = todayTaskAdvance(s, 2000); const second = todayTaskOverlayHtml(todayTaskViewModel(s, 2000)); "
            "const r = todayTaskStart({completed:{}, active:null}, 1000, 'REINF-01'); const re = todayTaskOverlayHtml(todayTaskViewModel(r, 1000)); "
            "return {first, second, re}; })()")["result"]
        self.assertNotIn("data-today-launch", res["first"])  # FOCUS phases never launch random practice
        self.assertNotIn("data-today-launch", res["second"])
        self.assertNotIn("data-today-check", res["second"])  # 蓋解重做例題 is closed-book: no solution buttons
        self.assertNotIn("today-task-result-mount", res["first"])
        self.assertIn('data-today-launch="random-reinforce"', res["re"])
        self.assertIn("開啟補強練習", res["re"])

    def test_launch_calls_the_other_entry_points_with_fallback(self):
        src = TODAY_JS.read_text(encoding="utf-8")
        body = src.split("function todayTaskLaunchPractice(launch)")[1].split("\nfunction ")[0]
        self.assertIn("dailyPracticeStartWithMode", body)
        self.assertIn("dailyPracticePrepareNewRound", body)
        self.assertIn("'random-reinforce' ? 'reinforce' : 'balanced'", body)
        res = run_node(
            "(() => { const calls = []; globalThis.dailyPracticeStartWithMode = m => calls.push('mode:' + m); "
            "globalThis.dailyPracticePrepareNewRound = () => calls.push('new'); "
            "todayTaskLaunchPractice('random-reinforce'); todayTaskLaunchPractice('random-balanced'); "
            "delete globalThis.dailyPracticeStartWithMode; todayTaskLaunchPractice('random-balanced'); return calls; })()")["result"]
        self.assertEqual(res, ["mode:reinforce", "mode:balanced", "new"])


class TestTodayTaskReviewResultCard(unittest.TestCase):
    """WP5a: the 核對 phase of every task asks for a 作答結果卡 per QID (view-model level)."""

    def phases(self, code, source_expected_flag=None):
        res = run_node(
            f"(() => {{ const t = DAILY_SCHEDULE.tasks['{code}']; "
            "return t.phases.map((p, i) => { const v = todayTaskPhaseView(t, {code: t.code, phaseIndex: i, phaseStartedAt: 0}, 0); "
            "return {label: p.label, review: v.isReview, qids: v.resultQids, source: v.resultSource, closed: v.closed}; }); })()")
        return res["result"]

    def test_every_fixed_question_task_has_exactly_one_review_phase_listing_all_qids(self):
        codes = run_node("Object.keys(DAILY_SCHEDULE.tasks)")["result"]
        for code in codes:
            task = run_node(f"DAILY_SCHEDULE.tasks['{code}']")["result"]
            phases = self.phases(code)
            reviews = [p for p in phases if p["review"]]
            if not task["qids"]:
                # REINF／WRAP／BUFFER: no fixed qids, so no result card is ever requested
                for p in phases:
                    self.assertEqual(p["qids"], [], f"{code}: practice phases carry no result-card qids")
                continue
            self.assertEqual(len(reviews), 1, code)
            self.assertEqual(reviews[0]["qids"], task.get("scoredQids") or task["qids"], code)
            self.assertFalse(reviews[0]["closed"], code)
            for p in phases:
                if p["closed"]:
                    self.assertEqual(p["qids"], [], f"{code}: closed phase must not show result cards")

    def test_source_is_today_for_scheduled_tasks_and_mock_for_papers(self):
        self.assertEqual([p["source"] for p in self.phases("CORE-01") if p["review"]], ["today"])
        self.assertEqual({p["source"] for p in self.phases("FOCUS-01")}, {"today"})
        self.assertEqual([p["source"] for p in self.phases("MOCK114-01") if p["review"]], ["mock"])

    def test_overlay_markup_mounts_card_only_in_review_phase(self):
        res = run_node(
            "(() => { const t0 = 1000; let s = todayTaskStart({completed:{}, active:null}, t0); "
            "const closed = todayTaskOverlayHtml(todayTaskViewModel(s, t0)); "
            "s = todayTaskAdvance(s, t0 + 1000); "
            "const review = todayTaskOverlayHtml(todayTaskViewModel(s, t0 + 1000)); "
            "s = todayTaskAdvance(s, t0 + 2000); "
            "const last = todayTaskOverlayHtml(todayTaskViewModel(s, t0 + 2000)); "
            "return {closed, review, last}; })()")["result"]
        self.assertNotIn("today-task-result-mount", res["closed"])
        self.assertIn('id="today-task-result-mount"', res["review"])
        self.assertIn("data-today-result-next", res["review"])
        self.assertIn(">略過不記錄<", res["review"])
        self.assertNotIn(">下一題<", res["review"])
        self.assertIn(">完成核對 →<", res["review"])
        self.assertRegex(res["review"], r'id="today-task-finish"[^>]*disabled')
        self.assertIn("還有 1 題未處理", res["review"])
        self.assertNotIn("today-task-result-mount", res["last"])

    def test_overlay_header_names_the_active_task_even_when_not_the_earliest(self):
        res = run_node(
            "(() => { const s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); "
            "return todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); })()")["result"]
        self.assertIn("FOCUS-01｜", res)
        self.assertNotIn("CORE-01｜", res)


class TestFocusTasks(unittest.TestCase):
    """v1.3.7 弱章專攻: FOCUS-01..13 replace the retired WEAK random-practice slots."""

    @classmethod
    def setUpClass(cls):
        cls.schedule = bds.build_schedule()
        cls.tasks = {c: t for c, t in cls.schedule["tasks"].items() if c.startswith("FOCUS-")}

    def row(self, n):
        text = (WORKSPACE / "docs/01_備考計畫/弱章專攻_13輪.md").read_text(encoding="utf-8")
        line = next(l for l in text.splitlines() if l.startswith(f"| FOCUS-{n:02d} |"))
        cells = [c.strip() for c in line.strip("|").split("|")]
        return cells[1], re.findall(r"EE-\d{3}-\d{2}-\d+", cells[2]), re.findall(r"EE-\d{3}-\d{2}-\d+", cells[3])

    def test_thirteen_rounds_match_the_doc_table(self):
        self.assertEqual(list(self.tasks), [f"FOCUS-{i:02d}" for i in range(1, 14)])
        for n in range(1, 14):
            topic, ex, new = self.row(n)
            t = self.tasks[f"FOCUS-{n:02d}"]
            self.assertEqual((t["title"], t["subject"]), ("弱章專攻｜" + topic, topic.split("／")[0]))
            self.assertEqual(t["qids"], ex + new)
            self.assertEqual(t["scoredQids"], new)
        self.assertEqual(self.row(1)[1:], (["EE-112-06-3"], ["EE-109-06-3"]))
        self.assertEqual(self.row(13)[1:], (["EE-104-05-3"], ["EE-106-05-2"]))

    def test_task_shape_and_phases(self):
        for code, t in self.tasks.items():
            ex, new = t["qids"]
            self.assertEqual(t["kind"], "focus", code)
            self.assertEqual(t["hours"], 1, code)
            self.assertEqual(t["scoredQids"], [new], code)
            labels = [p["label"] for p in t["phases"]]
            self.assertEqual(labels, ["看懂例題詳解", "蓋解重做例題", "同章新題", "核對＋一句話錯因整理"], code)
            self.assertEqual([p["minutes"] for p in t["phases"]], [10, 15, 25, 10], code)
            self.assertEqual([p["closed"] for p in t["phases"]], [False, True, True, False], code)
            self.assertEqual(t["phases"][0]["qids"], [ex], code)
            self.assertEqual(t["phases"][0]["solutionQids"], [ex], code)
            self.assertEqual(t["phases"][1]["qids"], [ex], code)
            self.assertEqual(t["phases"][2]["qids"], [new], code)
            self.assertNotIn("qids", t["phases"][3], code)
            self.assertIn("弄懂每一步為什麼這樣做", t["phases"][0]["note"], code)
            self.assertIn("一句", t["phases"][3]["note"], code)
            # only the last phase may read as the review phase
            self.assertFalse(re.search("核對|對照", labels[0]), code)
            self.assertTrue(re.search("核對", labels[3]), code)
            self.assertFalse(t.get("launch"), code)

    def test_qid_rules_hold(self):
        core = {q for c, t in self.schedule["tasks"].items() if c.startswith("CORE-") for q in t["qids"]}
        main = {q for c, t in self.schedule["tasks"].items() if c.startswith("MAIN-") for q in t["qids"]}
        news = [t["scoredQids"][0] for t in self.tasks.values()]
        allq = [q for t in self.tasks.values() for q in t["qids"]]
        self.assertEqual(len(set(news)), 13)
        self.assertEqual(len(set(allq)), 26)
        self.assertFalse(set(news) & (core | main))
        self.assertFalse([q for q in allq if q.startswith(("EE-114-", "EE-108-"))])
        self.assertIn("EE-111-05-2", self.schedule["tasks"]["MAIN-01"]["qids"])
        self.assertNotIn("EE-109-01-1", [q for t in self.schedule["tasks"].values() for q in t["qids"]])

    def test_parse_focus_validations(self):
        good = (WORKSPACE / "docs/01_備考計畫/弱章專攻_13輪.md").read_text(encoding="utf-8")
        core = [t for t in self.schedule["tasks"].values() if t["code"].startswith("CORE-")]
        main = [t for t in self.schedule["tasks"].values() if t["code"].startswith("MAIN-")]
        self.assertEqual(len(bds.parse_focus(good, core, main)), 13)
        core_qid = next(q for t in core for q in t["qids"] if not q.startswith(("EE-114-", "EE-108-")))
        bad_new_core = good.replace("`EE-109-06-3` |", f"`{core_qid}` |", 1)
        bad_114 = good.replace("`EE-109-06-3` |", "`EE-114-06-3` |", 1)
        bad_108_example = good.replace("`EE-112-06-3` |", "`EE-108-06-3` |", 1)
        dup_new = good.replace("`EE-110-05-2` |", "`EE-109-06-3` |", 1)
        new_repeats_example = good.replace("`EE-110-05-2` |", "`EE-112-06-3` |", 1)
        same_pair = good.replace("`EE-109-06-3` |", "`EE-112-06-3` |", 1)
        missing_row = "\n".join(l for l in good.splitlines() if not l.startswith("| FOCUS-07 |"))
        for name, text in (("new in CORE", bad_new_core), ("114 qid", bad_114), ("108 example", bad_108_example), ("duplicate new", dup_new),
                           ("repeats another FOCUS qid", new_repeats_example), ("example == new", same_pair), ("missing row", missing_row)):
            with self.subTest(name):
                with self.assertRaises(bds.ParseError):
                    bds.parse_focus(text, core, main)
        # an example may itself be a CORE qid
        core_example = good.replace("`EE-112-06-3` |", f"`{core_qid}` |", 1)
        self.assertEqual(bds.parse_focus(core_example, core, main)[0]["qids"][0], core_qid)

    def phase_views(self, code):
        return run_node(
            f"(() => {{ const t = DAILY_SCHEDULE.tasks['{code}']; return t.phases.map((p, i) => todayTaskPhaseView(t, {{code: t.code, phaseIndex: i, phaseStartedAt: 0}}, 0)); }})()")["result"]

    def test_review_phase_result_cards_cover_only_the_new_question(self):
        views = self.phase_views("FOCUS-01")
        self.assertEqual([v["isReview"] for v in views], [False, False, False, True])
        self.assertEqual([v["resultQids"] for v in views], [[], [], [], ["EE-109-06-3"]])
        self.assertEqual(run_node("todayTaskScoredQids(DAILY_SCHEDULE.tasks['FOCUS-02'])")["result"], ["EE-110-05-2"])
        # tasks without scoredQids keep scoring every question
        self.assertEqual(run_node("todayTaskScoredQids(DAILY_SCHEDULE.tasks['CORE-01'])")["result"], run_node("DAILY_SCHEDULE.tasks['CORE-01'].qids")["result"])
        self.assertEqual(run_node("todayTaskScoredQids(DAILY_SCHEDULE.tasks['MAIN-01'])")["result"], run_node("DAILY_SCHEDULE.tasks['MAIN-01'].qids")["result"])

    def test_phase_one_opens_only_the_example_solution(self):
        views = self.phase_views("FOCUS-03")
        self.assertEqual(views[0]["solutionQids"], ["EE-112-02-3"])
        self.assertEqual(views[0]["questionQids"], ["EE-112-02-3"])
        self.assertEqual(views[1]["solutionQids"], [])  # closed-book redo: no solutions
        self.assertEqual(views[2]["solutionQids"], [])
        self.assertEqual(views[2]["questionQids"], ["EE-113-02-3"])
        self.assertEqual(views[3]["solutionQids"], ["EE-112-02-3", "EE-113-02-3"])  # checking may open either solution
        self.assertEqual(views[0]["instruction"], "打開例題題解，弄懂每一步為什麼這樣做（特別是第一步怎麼起手）；不抄寫。")

    def test_overlay_phase_one_has_one_check_button_and_last_phase_has_result_slot(self):
        res = run_node(
            "(() => { let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); "
            "const p1 = todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); "
            "s = todayTaskAdvance(s, 2000); s = todayTaskAdvance(s, 3000); const p3 = todayTaskOverlayHtml(todayTaskViewModel(s, 3000)); "
            "s = todayTaskAdvance(s, 4000); const p4 = todayTaskOverlayHtml(todayTaskViewModel(s, 4000)); return {p1, p3, p4}; })()")["result"]
        self.assertEqual(res["p1"].count("data-today-check="), 1)
        self.assertIn('data-today-check="EE-112-06-3"', res["p1"])
        self.assertNotIn("data-today-check", res["p3"])
        self.assertIn("同章新題（閉卷）", res["p3"])
        self.assertIn('id="today-task-result-mount"', res["p4"])
        self.assertIn("還有 1 題未處理（EE-109-06-3）", res["p4"])

    def test_focus_task_can_be_completed_end_to_end(self):
        res = run_node(
            "(() => { let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-05'); for (let i = 1; i <= 4; i++) s = todayTaskAdvance(s, 1000 + i * 1000); "
            "return {done: Object.keys(s.completed), active: s.active}; })()")["result"]
        self.assertEqual(res, {"done": ["FOCUS-05"], "active": None})

    def test_focus_hours_count_as_one_hour_in_the_plan(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("FOCUS-01")]}
        plan = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 13)}).items.map(i => [i.code, i.minutes])")["result"]
        self.assertEqual(plan, [["FOCUS-01", 60], ["FOCUS-02", 60]])


class TestDynamicFocus(unittest.TestCase):
    """v1.3.8: FOCUS 例題／新題 are picked when the task starts (src/domain/anchorSelection.js); the fixed table is the fallback.
    anchorSelection.js is not loaded here: a stub anchorFocusPick is injected as a global."""

    DAG = WORKSPACE / "src/data/knowledge-dag.js"
    PICK = {"chapter": "dist-short-circuit-capacity", "qids": ["EE-110-06-2", "EE-112-06-2"], "scoredQids": ["EE-112-06-2"]}

    @classmethod
    def setUpClass(cls):
        cls.schedule = bds.build_schedule()

    def run_js(self, body, stub="(() => null)"):
        """Evaluate `body` (statements ending in return) with globalThis.anchorFocusPick = `stub` (a JS expression; 'none' leaves it undefined)."""
        define = "" if stub == "none" else f"globalThis.anchorFocusPick = {stub}; "
        return run_node(f"(() => {{ {define}{body} }})()", extra_sources=[self.DAG])["result"]

    def stub_returning(self, pick=None):
        return ("(({ task, state, ctx }) => { globalThis.__args = { code: task.code, hasState: !!state.completed, ctx: typeof ctx }; return "
                + json.dumps(pick or self.PICK) + "; })")

    def test_schedule_marks_only_focus_tasks_dynamic_with_roles(self):
        for code, t in self.schedule["tasks"].items():
            if code.startswith("FOCUS-"):
                self.assertEqual(t["dynamic"], "anchor-focus", code)
                self.assertEqual([p.get("role") for p in t["phases"]], ["example", "example", "fresh", None], code)
                # fixed qids stay as the fallback
                self.assertEqual(len(t["qids"]), 2, code)
                self.assertEqual(t["scoredQids"], [t["qids"][1]], code)
            else:
                self.assertNotIn("dynamic", t, code)
                self.assertTrue(all("role" not in p for p in t["phases"]), code)

    def test_start_stores_the_pick_and_phases_follow_the_roles(self):
        res = self.run_js(
            "let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); const a = s.active; const t = DAILY_SCHEDULE.tasks['FOCUS-01']; "
            "const views = t.phases.map((p, i) => todayTaskPhaseView(t, Object.assign({}, a, {phaseIndex: i}), 1000)); "
            "return {a, args: globalThis.__args, views: views.map(v => ({q: v.questionQids, sol: v.solutionQids, res: v.resultQids, review: v.isReview})), "
            "title: todayTaskViewModel(s, 1000).activeTitle, scored: todayTaskScoredQids(todayTaskResolvedTask(t, a))}; ",
            self.stub_returning())
        ex, fresh = self.PICK["qids"]
        self.assertEqual(res["a"]["qids"], [ex, fresh])
        self.assertEqual(res["a"]["scoredQids"], [fresh])
        self.assertEqual(res["a"]["chapter"], "dist-short-circuit-capacity")
        self.assertEqual(res["args"], {"code": "FOCUS-01", "hasState": True, "ctx": "undefined"})
        v = res["views"]
        self.assertEqual([x["q"] for x in v[:3]], [[ex], [ex], [fresh]])
        self.assertEqual(v[0]["sol"], [ex])          # phase 0 opens only the example's solution
        self.assertEqual(v[1]["sol"], [])            # closed phases never expose solutions
        self.assertEqual(v[2]["sol"], [])
        self.assertEqual([x["res"] for x in v], [[], [], [], [fresh]])  # result card lists only the fresh question
        self.assertTrue(v[3]["review"])
        self.assertEqual(res["scored"], [fresh])
        self.assertEqual(res["title"], "弱章專攻｜工業配電／短路容量計算 (MVA 法)")

    def test_ctx_comes_from_anchor_context_when_available(self):
        res = self.run_js(
            "globalThis.anchorContext = o => ({ now: o.now, marker: 'ctx' }); "
            "const s = todayTaskStart({completed:{}, active:null}, 4321, 'FOCUS-02'); return {args: globalThis.__args, a: s.active}; ",
            "(({ task, ctx }) => { globalThis.__args = { code: task.code, ctx }; return { chapter: 'power-3ph-short', qids: ['EE-107-05-2', 'EE-113-05-2'], scoredQids: ['EE-113-05-2'] }; })")
        self.assertEqual(res["args"], {"code": "FOCUS-02", "ctx": {"now": 4321, "marker": "ctx"}})
        self.assertEqual(res["a"]["qids"], ["EE-107-05-2", "EE-113-05-2"])

    def test_null_throwing_malformed_or_missing_pick_falls_back_to_the_fixed_task(self):
        fixed = self.schedule["tasks"]["FOCUS-03"]
        bad_picks = {
            "null": "(() => null)",
            "throws": "(() => { throw new Error('boom'); })",
            "same": "(() => ({ chapter: 'c', qids: ['EE-110-06-2', 'EE-110-06-2'], scoredQids: ['EE-110-06-2'] }))",
            "format": "(() => ({ chapter: 'c', qids: ['EE-110-06-2', 'bad'], scoredQids: ['bad'] }))",
            "scored-not-fresh": "(() => ({ chapter: 'c', qids: ['EE-110-06-2', 'EE-112-06-2'], scoredQids: ['EE-110-06-2'] }))",
            "length": "(() => ({ chapter: 'c', qids: ['EE-110-06-2'], scoredQids: [] }))",
            "no-function": "none",
        }
        for name, stub in bad_picks.items():
            res = self.run_js(
                "let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-03'); const a = s.active; const t = DAILY_SCHEDULE.tasks['FOCUS-03']; "
                "const v = todayTaskPhaseView(t, Object.assign({}, a, {phaseIndex: 3}), 1000); "
                "return {a, resultQids: v.resultQids, q0: todayTaskPhaseView(t, a, 1000).questionQids, title: todayTaskViewModel(s, 1000).activeTitle}; ", stub)
            self.assertEqual(res["a"], {"code": "FOCUS-03", "phaseIndex": 0, "phaseStartedAt": 1000}, name)
            self.assertEqual(res["resultQids"], fixed["scoredQids"], name)
            self.assertEqual(res["q0"], [fixed["qids"][0]], name)
            self.assertEqual(res["title"], fixed["title"], name)

    def test_only_focus_tasks_ask_for_a_pick(self):
        res = self.run_js(
            "const s = todayTaskStart({completed:{}, active:null}, 1000, 'CORE-07'); return {a: s.active, called: globalThis.__args !== undefined}; ",
            self.stub_returning())
        self.assertEqual(res["a"], {"code": "CORE-07", "phaseIndex": 0, "phaseStartedAt": 1000})
        self.assertFalse(res["called"])

    def test_pick_survives_advancing_every_phase_and_completion_clears_it(self):
        res = self.run_js(
            "let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); const seen = []; "
            "for (let i = 1; i <= 3; i++) { s = todayTaskAdvance(s, 1000 + i * 1000); seen.push({idx: s.active.phaseIndex, qids: s.active.qids, scored: s.active.scoredQids, chapter: s.active.chapter}); } "
            "s = todayTaskAdvance(s, 9000); return {seen, active: s.active, done: Object.keys(s.completed)}; ",
            self.stub_returning())
        self.assertEqual([i["idx"] for i in res["seen"]], [1, 2, 3])
        for item in res["seen"]:
            self.assertEqual(item["qids"], self.PICK["qids"])
            self.assertEqual(item["scored"], ["EE-112-06-2"])
            self.assertEqual(item["chapter"], "dist-short-circuit-capacity")
        self.assertEqual(res["done"], ["FOCUS-01"])
        self.assertIsNone(res["active"])

    def test_pick_survives_a_storage_roundtrip(self):
        res = self.run_js(
            "let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); "
            "const store = {}; const st = { getItem: k => store[k] || null, setItem: (k, v) => { store[k] = v; } }; "
            "saveTodayTaskState(s, st); return loadTodayTaskState(st).active; ",
            self.stub_returning())
        self.assertEqual(res["qids"], self.PICK["qids"])
        self.assertEqual(res["scoredQids"], ["EE-112-06-2"])
        self.assertEqual(res["chapter"], "dist-short-circuit-capacity")

    def test_normalize_keeps_a_valid_pick_and_validates_skipped_against_it(self):
        raw = {"completed": {}, "active": {"code": "FOCUS-01", "phaseIndex": 3, "phaseStartedAt": 5, "chapter": "dist-short-circuit-capacity",
                                           "qids": ["EE-110-06-2", "EE-112-06-2"], "scoredQids": ["EE-112-06-2"],
                                           "skipped": ["EE-112-06-2", "EE-109-06-3", "EE-112-06-3"]}}
        a = run_node(f"todayTaskNormalizeState({json.dumps(raw)})")["result"]["active"]
        self.assertEqual(a["qids"], ["EE-110-06-2", "EE-112-06-2"])
        self.assertEqual(a["scoredQids"], ["EE-112-06-2"])
        self.assertEqual(a["chapter"], "dist-short-circuit-capacity")
        self.assertEqual(a["skipped"], ["EE-112-06-2"])  # fixed table qids no longer count
        # scoredQids may be omitted: it is derived from the 新題
        del raw["active"]["scoredQids"]
        a = run_node(f"todayTaskNormalizeState({json.dumps(raw)})")["result"]["active"]
        self.assertEqual(a["scoredQids"], ["EE-112-06-2"])

    def test_normalize_drops_malformed_picks_so_the_fixed_task_is_used(self):
        base = {"code": "FOCUS-01", "phaseIndex": 1, "phaseStartedAt": 5, "skipped": ["EE-112-06-3", "EE-110-06-2"]}
        fixed_ex = self.schedule["tasks"]["FOCUS-01"]["qids"][0]
        bad = [
            {"qids": ["EE-110-06-2"]},
            {"qids": ["EE-110-06-2", "EE-112-06-2", "EE-113-06-2"]},
            {"qids": ["EE-110-06-2", "EE-110-06-2"]},
            {"qids": ["EE-110-06-2", "GK-112-06-2"]},
            {"qids": ["EE-110-06-2", 5]},
            {"qids": "EE-110-06-2,EE-112-06-2"},
            {"qids": ["EE-110-06-2", "EE-112-06-2"], "scoredQids": ["EE-110-06-2"]},
            {"qids": ["EE-110-06-2", "EE-112-06-2"], "scoredQids": ["EE-112-06-2", "EE-110-06-2"]},
            {"scoredQids": ["EE-112-06-2"], "chapter": "x"},
        ]
        for extra in bad:
            raw = {"completed": {}, "active": dict(base, **extra)}
            a = run_node(f"todayTaskNormalizeState({json.dumps(raw)})")["result"]["active"]
            self.assertIsNotNone(a, extra)
            for key in ("qids", "scoredQids", "chapter"):
                self.assertNotIn(key, a, f"{key} should be dropped for {extra}")
            self.assertEqual(a["skipped"], [fixed_ex], extra)  # validated against the fixed table
        # a bad chapter alone only costs the chapter
        raw = {"completed": {}, "active": dict(base, qids=["EE-110-06-2", "EE-112-06-2"], chapter="x" * 65)}
        a = run_node(f"todayTaskNormalizeState({json.dumps(raw)})")["result"]["active"]
        self.assertEqual(a["qids"], ["EE-110-06-2", "EE-112-06-2"])
        self.assertNotIn("chapter", a)

    def test_normalize_ignores_picks_on_non_dynamic_tasks(self):
        raw = {"completed": {}, "active": {"code": "CORE-07", "phaseIndex": 0, "phaseStartedAt": 5,
                                           "qids": ["EE-110-06-2", "EE-112-06-2"], "scoredQids": ["EE-112-06-2"], "chapter": "c"}}
        a = run_node(f"todayTaskNormalizeState({json.dumps(raw)})")["result"]["active"]
        self.assertEqual(a, {"code": "CORE-07", "phaseIndex": 0, "phaseStartedAt": 5})
        same = run_node("(() => { const t = DAILY_SCHEDULE.tasks['CORE-07']; return todayTaskResolvedTask(t, " + json.dumps(raw["active"]) + ") === t; })()")["result"]
        self.assertTrue(same)

    def test_resolved_task_without_a_pick_is_the_same_object(self):
        res = run_node("(() => { const t = DAILY_SCHEDULE.tasks['FOCUS-01']; return [todayTaskResolvedTask(t, null) === t, "
                       "todayTaskResolvedTask(t, {code:'FOCUS-01', phaseIndex:0, phaseStartedAt:1}) === t]; })()")["result"]
        self.assertEqual(res, [True, True])

    def test_unknown_chapter_keeps_the_fixed_title(self):
        res = self.run_js(
            "const s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); return todayTaskViewModel(s, 1000).activeTitle; ",
            self.stub_returning(dict(self.PICK, chapter="no-such-chapter")))
        self.assertEqual(res, self.schedule["tasks"]["FOCUS-01"]["title"])

    def test_overlay_markup_shows_dynamic_title_and_qids(self):
        res = self.run_js(
            "let s = todayTaskStart({completed:{}, active:null}, 1000, 'FOCUS-01'); const p1 = todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); "
            "s = todayTaskAdvance(s, 2000); s = todayTaskAdvance(s, 3000); s = todayTaskAdvance(s, 4000); const p4 = todayTaskOverlayHtml(todayTaskViewModel(s, 4000)); return {p1, p4}; ",
            self.stub_returning())
        self.assertIn("FOCUS-01｜弱章專攻｜工業配電／短路容量計算 (MVA 法)", res["p1"])
        self.assertEqual(res["p1"].count("data-today-check="), 1)
        self.assertIn('data-today-check="EE-110-06-2"', res["p1"])
        self.assertIn("還有 1 題未處理（EE-112-06-2）", res["p4"])

    def test_pick_does_not_change_pacing(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("FOCUS-01")]}
        now = local_ms(2026, 10, 13)
        expr = f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {now}).items.map(i => [i.code, i.minutes])"
        before = run_node(expr)["result"]
        started = self.run_js(
            f"const s = todayTaskStart({{completed:{json.dumps(done)}, active:null}}, {now}, 'FOCUS-01'); "
            f"return todayTaskViewModel(s, {now}).items.map(i => [i.code, i.minutes]); ",
            self.stub_returning())
        self.assertEqual(before, [["FOCUS-01", 60], ["FOCUS-02", 60]])
        self.assertEqual(started[0], ["FOCUS-01", 60])


class TestPaperClosedPhaseNote(unittest.TestCase):
    NOTE = "5 分鐘沒頭緒就先跳下一題；最後回來寫已知、圖、適用公式，拿步驟分。"

    def test_every_paper_closed_phase_carries_the_note(self):
        tasks = bds.build_schedule()["tasks"]
        for code, t in tasks.items():
            if code.startswith(("MOCK114", "BLIND108")):
                self.assertEqual(t["phases"][0]["label"], "閉卷模考", code)
                self.assertEqual(t["phases"][0]["note"], self.NOTE, code)
                self.assertNotIn("note", t["phases"][1], code)

    def test_overlay_shows_the_note_as_the_instruction(self):
        res = run_node(
            "(() => { const s = todayTaskStart({completed:{}, active:null}, 1000, 'MOCK114-01'); const vm = todayTaskViewModel(s, 1000); "
            "return {ins: vm.active.instruction, html: todayTaskOverlayHtml(vm)}; })()")["result"]
        self.assertEqual(res["ins"], self.NOTE)
        self.assertIn('<p class="today-task-instruction" role="note">' + self.NOTE + "</p>", res["html"])


class TestG2aFixes(unittest.TestCase):
    def test_code_range_text(self):
        self.assertEqual(run_node("todayTaskCodeRange(['CORE-16','CORE-17'])")["result"], "CORE-16～17")
        self.assertEqual(run_node("todayTaskCodeRange(['CORE-16'])")["result"], "CORE-16")

    def test_next_action_phase_has_instruction_and_can_finish(self):
        res = run_node(
            "(() => { let s = todayTaskStart({completed:{}, active:null}, 1000); "
            "s = todayTaskAdvance(s, 2000); s = todayTaskAdvance(s, 3000); "
            "const vm = todayTaskViewModel(s, 3000); const html = todayTaskOverlayHtml(vm); "
            "return {label: vm.active.label, ins: vm.active.instruction, html}; })()")["result"]
        self.assertEqual(res["label"], "下次動作")
        self.assertIn("寫下一句：下次最先要改的動作（不必回填）", res["ins"])
        self.assertIn("寫下一句：下次最先要改的動作", res["html"])
        self.assertIn(">完成<", res["html"])
        self.assertNotIn("disabled", res["html"])

    def test_review_progress_gates_finish(self):
        res = run_node(
            "(() => { const f = {saved:[], skipped:[]}; const a = todayTaskReviewProgress(['A','B'], f, 0); "
            "f.saved.push('A'); const b = todayTaskReviewProgress(['A','B'], f, 0); "
            "f.skipped.push('B'); const c = todayTaskReviewProgress(['A','B'], f, 0); "
            "return {a: a.canFinish, b: b.canFinish, bp: b.pending, c: c.canFinish, reason: a.reason}; })()")["result"]
        self.assertFalse(res["a"]); self.assertFalse(res["b"]); self.assertEqual(res["bp"], ["B"])
        self.assertTrue(res["c"])
        self.assertIn("略過不記錄", res["reason"])

    def test_closed_phase_image_is_zoomable(self):
        src = TODAY_JS.read_text(encoding="utf-8")
        self.assertIn("data-today-zoom", src)
        self.assertIn("openImageLightbox", src)

    def test_review_html_has_check_buttons(self):
        res = run_node(
            "(() => { let s = todayTaskStart({completed:{}, active:null}, 1000); s = todayTaskAdvance(s, 2000); "
            "return todayTaskOverlayHtml(todayTaskViewModel(s, 2000)); })()")["result"]
        self.assertIn("data-today-check=", res)

    def test_source_docks_card_in_solution_modal(self):
        src = TODAY_JS.read_text(encoding="utf-8")
        body = src.split("function todayTaskOpenSolution(qid)")[1].split("function todayTaskZoomImage")[0]
        self.assertIn("openSolutionModal(", body)
        self.assertIn("openResultCard({", body)
        self.assertNotIn("mount", body.split("openResultCard({")[1].split("});")[0].split("onSaved")[0])

    def test_variant_comparison_phase_shows_anchor_same_type_and_variant(self):
        schedule = json.loads(bds.render_json(bds.build_schedule()))
        for n in list(range(7, 13)) + list(range(19, 25)):
            task = schedule["tasks"][f"CORE-{n:02d}"]
            phase = next(p for p in task["phases"] if p["label"] == "三題對照")
            anchor = schedule["tasks"][f"CORE-{n - 6:02d}"]["qids"][0]
            self.assertEqual(phase["qids"], [anchor] + task["qids"])
            self.assertEqual(phase["qidLabels"], ["母題", "同型", "變式"])
        t0 = local_ms(2026, 10, 4, 9, 0)
        html = run_node(
            f"(() => {{ let s = todayTaskStart({{completed:{{}}, active:null}}, {t0}, 'CORE-07'); "
            f"s = todayTaskAdvance(s, {t0}); s = todayTaskAdvance(s, {t0}); "
            f"return todayTaskOverlayHtml(todayTaskViewModel(s, {t0})); }})()")["result"]
        self.assertEqual(html.count("today-task-figure"), 3)
        for label in ("母題", "同型", "變式"):
            self.assertIn(label, html)
        self.assertIn("EE-114-01-3", html)

    def test_rest_days_do_not_auto_open_and_note_dropped_task(self):
        src = TODAY_JS.read_text(encoding="utf-8")
        init = src.split("function initTodayTask()")[1]
        self.assertIn("restDay", init)
        self.assertIn("&& !restDay", init)
        for d in (12, 13):
            t = local_ms(2026, 11, d, 9, 0)
            res = run_node(
                f"(() => {{ const s = todayTaskStart({{completed:{{}}, active:null}}, {t}, 'CORE-07'); "
                f"const vm = todayTaskViewModel(s, {t}); return [vm.mode, todayTaskCardHtml(vm)]; }})()")["result"]
            self.assertIn(res[0], ("exam-check", "stop"))
            self.assertIn("不開新題" if d == 12 else "不再開新題", res[1])
            self.assertIn("不再繼續", res[1])
            self.assertNotIn("today-task-start", res[1])

    def test_fresh_user_sees_prompt_not_cut_line(self):
        t = local_ms(2026, 10, 4, 9, 0)
        fresh = run_node(f"todayTaskCardHtml(todayTaskViewModel({{completed:{{}}, active:null}}, {t}))")["result"]
        self.assertNotIn("今天先跳過", fresh)
        self.assertIn("先設定已在紙本做過的任務，再排今天", fresh)
        self.assertIn("today-task-from is-prompt", fresh)
        set_up = run_node(
            f"(() => {{ const s = todayTaskStartFrom({{completed:{{}}, active:null}}, 'CORE-07', {t}); "
            f"return todayTaskCardHtml(todayTaskViewModel(s, {t})); }})()")["result"]
        self.assertNotIn("先設定已在紙本做過的任務", set_up)

    def test_start_from_does_not_count_as_todays_hours(self):
        t = local_ms(2026, 10, 5, 9, 0)
        res = run_node(
            f"(() => {{ const s = todayTaskStartFrom({{completed:{{}}, active:null}}, 'CORE-10', {t}); const v = todayTaskViewModel(s, {t}); "
            f"return {{plan: v.planText, code: v.code, mode: v.mode}}; }})()")["result"]
        self.assertEqual(res, {"plan": "今天預算 2 小時（平日）｜還要做約 2 小時", "code": "CORE-10", "mode": "task"})


class TestDayChangeRerender(unittest.TestCase):
    def test_rerenders_only_when_local_date_moves_on(self):
        oct5 = local_ms(2026, 10, 5, 23, 59)
        oct6 = local_ms(2026, 10, 6, 0, 1)
        expr = f"""(() => {{
          const host = {{ innerHTML: '' }};
          globalThis.document = {{ getElementById: id => id === 'today-task-card' ? host : null }};
          let stats = 0;
          globalThis.updateStatsAndBar = () => {{ stats += 1; }};
          const before = todayTaskCheckDayChange({oct5});
          todayTaskRenderedDate = '2026-10-05';
          const same = todayTaskCheckDayChange({oct5});
          const next = todayTaskCheckDayChange({oct6});
          return {{ before, same, next, stats, rendered: host.innerHTML.length > 0, date: todayTaskRenderedDate }};
        }})()"""
        r = run_node(expr)["result"]
        self.assertFalse(r["before"])
        self.assertFalse(r["same"])
        self.assertTrue(r["next"])
        self.assertEqual(r["stats"], 1)
        self.assertTrue(r["rendered"])
        self.assertRegex(r["date"], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
