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
    sources = [SCHEDULE_JS.read_text(encoding="utf-8"), PACING_JS.read_text(encoding="utf-8"), TODAY_JS.read_text(encoding="utf-8")]
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
        for prefix, count, minutes in (("CORE", 24, 60), ("WEAK", 14, 75), ("MOCK114", 6, 180), ("BLIND108", 6, 180),
                                       ("REINF", 9, 120), ("WRAP", 3, 120)):
            codes = [c for c in tasks if c.startswith(prefix + "-")]
            self.assertEqual(len(codes), count, prefix)
            for code in codes:
                task = tasks[code]
                self.assertEqual(sum(p["minutes"] for p in task["phases"]), minutes, code)
                self.assertEqual(task["hours"], minutes / 60, code)
                if prefix in ("CORE", "MOCK114", "BLIND108"):
                    self.assertGreaterEqual(len(task["qids"]), 1, code)
                    for qid in task["qids"]:
                        self.assertIn(f'"{qid}"', self.dashboard, f"{code}: {qid} missing in dashboard-data.js")
                else:
                    self.assertEqual(task["qids"], [], f"{code}: practice/review tasks have no fixed qids")
                    self.assertIn(task["kind"], ("practice", "review"), code)
        self.assertEqual(tasks["BUFFER"]["hours"], 4)
        self.assertEqual(len(tasks), 63)
        self.assertEqual(len(self.schedule["order"]), 63)

    def test_retired_mix_and_ext_are_not_in_the_schedule(self):
        tasks = self.schedule["tasks"]
        self.assertFalse([c for c in tasks if c.startswith(("MIX-", "EXT-"))])
        self.assertFalse([c for c in self.schedule["order"] if c.startswith(("MIX-", "EXT-", "RECOVERY"))])
        self.assertNotIn("optionalOrder", self.schedule)
        self.assertFalse([t for t in tasks.values() if t.get("optional") or t["kind"] in ("mix", "ext")])
        self.assertNotIn("RECOVERY", bds.NON_WORK)

    def test_practice_tasks_expose_launch_modes_and_gates(self):
        tasks = self.schedule["tasks"]
        self.assertEqual({tasks[f"WEAK-{i:02d}"]["launch"] for i in range(1, 15)}, {"random-balanced"})
        self.assertEqual({tasks[f"REINF-{i:02d}"]["launch"] for i in range(1, 10)}, {"random-reinforce"})
        self.assertEqual(tasks["BUFFER"]["launch"], "random-reinforce")
        self.assertEqual(tasks["BUFFER"]["notBefore"], "2026-11-01")
        self.assertEqual(tasks["REINF-01"]["notBefore"], "2026-11-02")
        self.assertEqual(tasks["WRAP-03"]["notBefore"], "2026-11-09")
        self.assertNotIn("notBefore", tasks["WEAK-01"])
        self.assertNotIn("notBefore", tasks["MOCK114-01"])
        self.assertEqual(tasks["WEAK-01"]["phases"][0]["launch"], "random-balanced")
        self.assertTrue(tasks["CORE-07"]["variant"])
        self.assertFalse(tasks["CORE-01"]["variant"])

    def test_milestones_budget_days_and_order(self):
        s = self.schedule
        self.assertEqual(s["budget"], {"weekday": 2, "weekend": 4})
        self.assertEqual([(m["date"], m["label"], m["hard"]) for m in s["milestones"]],
                         [("2026-10-17", "弱題分析關卡", False), ("2026-10-31", "模考截止", True), ("2026-11-11", "補強完成", False)])
        hard = s["milestones"][1]
        papers = [c for c in s["order"] if c.startswith(("MOCK114-", "BLIND108-"))]
        self.assertEqual(len(papers), 12)
        self.assertTrue(set(papers) <= set(hard["codes"]))
        self.assertNotIn("BUFFER", hard["codes"])
        self.assertEqual(len(s["days"]), 41)
        self.assertEqual(s["days"][0]["date"], "2026-10-04")
        self.assertEqual(s["days"][0]["dow"], 0)  # Sunday
        self.assertEqual(s["days"][0]["budget"], 4)
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
        self.assertTrue(res["cut"].startswith("已自動刪減："), res["cut"])
        self.assertIn("（有空再做）", res["cut"])
        self.assertIn("模考卷與 10/31 期限不刪", res["cut"])  # hours still short after every allowed cut

    def test_plan_line_shows_budget_and_planned_hours(self):
        done = {f"CORE-0{i}": "x" for i in range(1, 7)}
        sunday = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 4)}).planText")["result"]
        monday = run_node(f"todayTaskViewModel({{completed:{json.dumps(done)}, active:null}}, {local_ms(2026, 10, 5)}).planText")["result"]
        self.assertEqual(sunday, "今天預算 4 小時（週末）｜排入 4.25 小時")  # CORE-07～09 + WEAK-01
        self.assertEqual(monday, "今天預算 2 小時（平日）｜排入 2 小時")  # CORE-07, CORE-08 (a 2 h weekday)

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
        self.assertNotIn("核對", res)
        self.assertIn("停筆", res)

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
            "(() => { const s = todayTaskStartFrom({completed:{'WEAK-01':'old'}, active:{code:'CORE-01',phaseIndex:0,phaseStartedAt:1}}, 'CORE-14', 0); "
            "return {next: todayTaskCurrentCode(s), done: Object.keys(s.completed).length, active: s.active, mix: s.completed['WEAK-01'], "
            "back: todayTaskCurrentCode(todayTaskStartFrom(s, 'CORE-05', 0)), bogus: todayTaskStartFrom(s, 'NOPE', 0) === s}; })()")["result"]
        self.assertEqual(res["next"], "CORE-14")
        # CORE-01..13 plus the interleaved WEAK-01..05 that precede CORE-14 in the order (WEAK-01 was already done and stays 'old')
        self.assertEqual(res["done"], 18)
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
        self.assertEqual(res["items"], ["CORE-07", "CORE-08", "CORE-09", "WEAK-01"])
        self.assertTrue(res["rest"].startswith("今天還有：CORE-08｜"), res["rest"])
        self.assertIn("WEAK-01｜弱題分析｜隨機練習 第 1 輪（各科輪流）", res["rest"])
        self.assertIn("今天還有：", res["html"])
        self.assertLess(res["html"].index("下一個任務：CORE-07"), res["html"].index("今天還有："))
        self.assertIn(">開始<", res["html"])

    def test_milestone_line_counts_days_and_papers(self):
        res = self.vm(DONE_ONE_TO_SIX, local_ms(2026, 10, 5))
        # next milestone is the non-hard 10/17: hours plus the hard deadline's paper count
        self.assertTrue(res["milestone"].startswith("距 10/17 弱題分析關卡還有 12 天｜剩 "), res["milestone"])
        self.assertTrue(res["milestone"].endswith("｜10/31 模考截止剩 12 份卷"), res["milestone"])
        # after 10/17 the hard milestone is next: 「距 10/31 模考截止還有 N 天｜剩 X 份卷」
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("MOCK114-03")]}
        res = self.vm(done, local_ms(2026, 10, 18))
        self.assertEqual(res["milestone"], "距 10/31 模考截止還有 13 天｜剩 10 份卷")
        self.assertIn('class="today-pacing-milestone"', res["html"])

    def test_behind_shows_cut_line_and_keeps_papers(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("CORE-16")]}
        res = self.vm(done, local_ms(2026, 10, 16))
        self.assertEqual(res["status"], "behind")
        self.assertTrue(res["cut"].startswith("已自動刪減："), res["cut"])
        self.assertTrue(res["cut"].endswith("（有空再做）"), res["cut"])
        self.assertIn("WEAK-", res["cut"])
        self.assertNotIn("MOCK", res["cut"])
        self.assertNotIn("BLIND", res["cut"])
        self.assertIn('class="today-pacing-cut"', res["html"])

    def test_ahead_after_all_mocks_suggests_113(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("BUFFER")]}
        res = self.vm(done, local_ms(2026, 10, 28))
        self.assertEqual(res["status"], "ahead")
        self.assertIn("113 年整卷", res["suggestion"])
        self.assertEqual(res["mode"], "idle")  # BUFFER/REINF are not due yet
        self.assertIn("今天沒有待做的必做任務", res["html"])
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
        self.assertIn(">開始核對<", res["html"])
        self.assertLess(res["html"].index("接續 MOCK114-04"), res["html"].index("今天還有"))
        self.assertEqual(res["items"][0], "MOCK114-04")
        same = self.vm(done, local_ms(2026, 10, 19, 20), active)
        self.assertTrue(same["held"]["sameDay"])
        self.assertIn("今天的閉卷已完成，明天接續 MOCK114-04：核對＋修復", same["html"])
        self.assertIn(">現在就核對<", same["html"])

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
            "const a = todayTaskStart(s0, 1000, 'WEAK-03'); const done = todayTaskStart(s0, 1000, 'CORE-02'); const bad = todayTaskStart(s0, 1000, 'MIX-01'); "
            "const plain = todayTaskStart(s0, 1000); "
            "return {a: a.active.code, done: done === s0, bad: bad === s0, plain: plain.active.code}; })()")["result"]
        self.assertEqual(res, {"a": "WEAK-03", "done": True, "bad": True, "plain": "CORE-01"})

    def test_start_from_select_lists_current_codes_and_defaults_to_core_07(self):
        res = self.vm({}, local_ms(2026, 10, 5))
        self.assertIn('<option value="CORE-07" selected>', res["html"])
        self.assertIn('<option value="CORE-01">', res["html"])
        self.assertIn('<option value="WEAK-14">', res["html"])
        self.assertIn('<option value="REINF-09">', res["html"])
        self.assertIn('<option value="BUFFER">', res["html"])
        for retired in ("MIX-", "EXT-", "RECOVERY"):
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

    def test_reinforcement_day_plan(self):
        order = run_node("DAILY_SCHEDULE.order")["result"]
        done = {c: "x" for c in order[:order.index("REINF-02")]}
        res = self.vm(done, local_ms(2026, 11, 3))
        self.assertEqual((res["code"], res["items"]), ("REINF-02", ["REINF-02"]))
        self.assertIn("距 11/11 補強完成還有 8 天", res["milestone"])

    def test_launch_phase_markup_and_no_empty_check_row(self):
        res = run_node(
            "(() => { let s = todayTaskStart({completed:{}, active:null}, 1000, 'WEAK-01'); "
            "const first = todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); "
            "s = todayTaskAdvance(s, 2000); const second = todayTaskOverlayHtml(todayTaskViewModel(s, 2000)); "
            "const r = todayTaskStart({completed:{}, active:null}, 1000, 'REINF-01'); const re = todayTaskOverlayHtml(todayTaskViewModel(r, 1000)); "
            "return {first, second, re}; })()")["result"]
        self.assertIn('data-today-launch="random-balanced"', res["first"])
        self.assertIn("開啟隨機練習（各科輪流）", res["first"])
        self.assertNotIn("data-today-check", res["first"])
        self.assertNotIn("核對題解", res["first"])
        self.assertNotIn("today-task-result-mount", res["first"])
        self.assertNotIn("data-today-launch", res["second"])
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
                # WEAK／REINF／WRAP／BUFFER: no fixed qids, so no result card is ever requested
                for p in phases:
                    self.assertEqual(p["qids"], [], f"{code}: practice phases carry no result-card qids")
                continue
            self.assertEqual(len(reviews), 1, code)
            self.assertEqual(reviews[0]["qids"], task["qids"], code)
            self.assertFalse(reviews[0]["closed"], code)
            for p in phases:
                if p["closed"]:
                    self.assertEqual(p["qids"], [], f"{code}: closed phase must not show result cards")

    def test_source_is_today_for_scheduled_tasks_and_mock_for_papers(self):
        self.assertEqual([p["source"] for p in self.phases("CORE-01") if p["review"]], ["today"])
        self.assertEqual({p["source"] for p in self.phases("WEAK-01")}, {"today"})
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
            "(() => { const s = todayTaskStart({completed:{}, active:null}, 1000, 'WEAK-01'); "
            "return todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); })()")["result"]
        self.assertIn("WEAK-01｜", res)
        self.assertNotIn("CORE-01｜", res)


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


if __name__ == "__main__":
    unittest.main()
