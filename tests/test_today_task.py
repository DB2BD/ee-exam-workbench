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
SM2_JS = WORKSPACE / "src/state/sm2Store.js"


def run_node(expression, storage=None, extra_sources=()):
    sources = [SCHEDULE_JS.read_text(encoding="utf-8"), TODAY_JS.read_text(encoding="utf-8")]
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
        for prefix, count, minutes in (("CORE", 24, 60), ("MIX", 6, 90), ("MOCK114", 6, 180), ("BLIND108", 6, 180), ("EXT", 9, 90)):
            codes = [c for c in tasks if c.startswith(prefix + "-")]
            self.assertEqual(len(codes), count, prefix)
            for code in codes:
                task = tasks[code]
                self.assertGreaterEqual(len(task["qids"]), 1, code)
                self.assertEqual(sum(p["minutes"] for p in task["phases"]), minutes, code)
                for qid in task["qids"]:
                    self.assertIn(f'"{qid}"', self.dashboard, f"{code}: {qid} missing in dashboard-data.js")
        self.assertEqual(len(self.schedule["order"]), 42)
        self.assertEqual(len(tasks), 51)

    def test_ext_tasks_are_optional_and_outside_mandatory_order(self):
        tasks = self.schedule["tasks"]
        codes = [f"EXT-{i:02d}" for i in range(1, 10)]
        self.assertEqual([c for c in tasks if c.startswith("EXT-")], codes)
        self.assertEqual(self.schedule["optionalOrder"], codes)
        self.assertFalse(set(codes) & set(self.schedule["order"]))
        seen = set()
        for code in codes:
            task = tasks[code]
            self.assertTrue(task["optional"], code)
            self.assertEqual(len(task["qids"]), 2, code)
            self.assertEqual([p["minutes"] for p in task["phases"]], [50, 20, 20], code)
            self.assertEqual([p["closed"] for p in task["phases"]], [True, False, False], code)
            self.assertEqual(task["phases"][0]["qids"], task["qids"], code)
            for qid in task["qids"]:
                self.assertIn(f'"{qid}"', self.dashboard, f"{code}: {qid}")
        for code, task in tasks.items():
            if code.startswith("EXT-"):
                continue
            self.assertFalse(task.get("optional"), code)
            seen.update(task["qids"])
        all_ext = [q for c in codes for q in tasks[c]["qids"]]
        self.assertEqual(len(set(all_ext)), 18)
        self.assertFalse(set(all_ext) & seen, "EXT qids overlap CORE/MIX/MOCK114/BLIND108")

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
            bds.parse_mix("no table here")


class TestTodayTaskStore(unittest.TestCase):
    def test_next_task_skips_completed_not_by_date(self):
        now = local_ms(2026, 11, 1)
        res = run_node(
            "(() => { const s = {completed:{'CORE-01':'2026-09-23T00:00:00.000Z','CORE-02':'2026-09-24T00:00:00.000Z'}, active:null};"
            f"const vm = todayTaskViewModel(s, {now}); return {{code: vm.code, mode: vm.mode, pace: vm.plan.pace, text: vm.planText}}; }})()")["result"]
        self.assertEqual(res["code"], "CORE-03")
        self.assertEqual(res["mode"], "task")
        self.assertEqual(res["pace"], "behind")
        self.assertIn("依日程今天應做到", res["text"])
        self.assertIn("你目前在 CORE-03", res["text"])
        self.assertIn("點下方設定進度", res["text"])

    def test_plan_suggestion_and_ahead(self):
        now = local_ms(2026, 10, 3)
        res = run_node(f"(() => {{ const vm = todayTaskViewModel({{completed:{{}}, active:null}}, {now}); return vm.planText; }})()")["result"]
        self.assertIn("依日程今天應做到 CORE-14～15；你目前在 CORE-01（若紙本已做過，點下方設定進度）", res)

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
            "(() => { const s = todayTaskStartFrom({completed:{'MIX-01':'old'}, active:{code:'CORE-01',phaseIndex:0,phaseStartedAt:1}}, 'CORE-14', 0); "
            "return {next: todayTaskCurrentCode(s), done: Object.keys(s.completed).length, active: s.active, mix: s.completed['MIX-01'], "
            "back: todayTaskCurrentCode(todayTaskStartFrom(s, 'CORE-05', 0)), bogus: todayTaskStartFrom(s, 'NOPE', 0) === s}; })()")["result"]
        self.assertEqual(res["next"], "CORE-14")
        self.assertEqual(res["done"], 14)  # CORE-01..13 plus the untouched later MIX-01
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
        self.assertLess(gen, dp)
        self.assertLess(dp, tt)
        self.assertLess(build.index('id="today-task-card"'), build.index('class="home-primary-actions"'))


class TestTodayTaskBackup(unittest.TestCase):
    def test_backup_source_handles_key(self):
        text = SM2_JS.read_text(encoding="utf-8")
        self.assertIn("EE_EXAM_TODAY_TASK_V1", text)
        self.assertIn("todayTask: backupReadTodayTask(storage)", text)
        self.assertIn("BACKUP_TODAY_TASK_KEY, JSON.stringify(nextTodayTask)", text)
        # key must be in the rollback snapshot list
        self.assertRegex(text, r"BACKUP_DAILY_PRACTICE_KEY, BACKUP_TODAY_TASK_KEY")


def mandatory_before(date_iso):
    """Mandatory (non-EXT, non-non-work) codes scheduled strictly before date_iso."""
    schedule = bds.build_schedule()
    out = []
    for day in schedule["days"]:
        if day["date"] < date_iso:
            out += [c for c in day["codes"] if c in schedule["order"]]
    return out


class TestTodayTaskExt(unittest.TestCase):
    """WP5a: EXT is optional; it is secondary while behind and primary once caught up."""

    def vm(self, completed, now, active="null"):
        res = run_node(
            f"(() => {{ const s = {{completed:{json.dumps(completed)}, active:{active}}}; "
            f"const v = todayTaskViewModel(s, {now}); "
            "return {mode:v.mode, code:v.code, mandatoryCode:v.mandatoryCode, primaryIsOptional:v.primaryIsOptional, "
            "optional:v.optional, text:v.planText, pace:v.plan.pace, diff:v.plan.diff, done:v.doneCount}; })()")
        return res["result"]

    def test_behind_on_ext_day_keeps_mandatory_primary_and_ext_secondary(self):
        res = self.vm({}, local_ms(2026, 10, 16))
        self.assertEqual(res["pace"], "behind")
        self.assertEqual(res["code"], "CORE-01")
        self.assertFalse(res["primaryIsOptional"])
        self.assertEqual(res["optional"]["code"], "EXT-01")
        self.assertTrue(res["optional"]["text"].startswith("選做：EXT-01｜"))
        self.assertTrue(res["optional"]["text"].endswith("（有餘力再做）"))
        self.assertNotIn("EXT", res["text"])

    def test_caught_up_on_ext_day_makes_ext_primary(self):
        done = {c: "2026-10-01T00:00:00.000Z" for c in mandatory_before("2026-10-16")}
        res = self.vm(done, local_ms(2026, 10, 16))
        self.assertEqual(res["pace"], "on")
        self.assertEqual(res["code"], "EXT-01")
        self.assertTrue(res["primaryIsOptional"])
        self.assertIsNone(res["optional"])
        self.assertEqual(res["mandatoryCode"] in done, False)
        self.assertNotIn("EXT", res["text"])
        self.assertIn("選做", res["text"])

    def test_ext_completion_never_blocks_order_or_counts_for_pace(self):
        res = self.vm({"EXT-01": "2026-10-16T00:00:00.000Z"}, local_ms(2026, 10, 16))
        self.assertEqual(res["mandatoryCode"], "CORE-01")
        self.assertEqual(res["done"], 0)
        self.assertEqual(res["pace"], "behind")
        self.assertIsNone(res["optional"])  # already done -> not offered again

    def test_pace_counts_only_mandatory_codes(self):
        done = {c: "2026-10-01T00:00:00.000Z" for c in mandatory_before("2026-10-17")}
        # 10-16 is an EXT-only day: finishing every earlier mandatory code is exactly on pace.
        res = self.vm(done, local_ms(2026, 10, 17))
        self.assertEqual(res["pace"], "on")
        self.assertEqual(res["diff"], 0)

    def test_start_optional_requires_optional_code_and_keeps_order(self):
        res = run_node(
            "(() => { const s0 = {completed:{}, active:null}; "
            "const bad = todayTaskStart(s0, 1000, 'CORE-02'); "
            "const ext = todayTaskStart(s0, 1000, 'EXT-01'); "
            "const plain = todayTaskStart(s0, 1000); "
            "let s = ext; for (let i = 0; i < 3; i++) s = todayTaskAdvance(s, 2000 + i); "
            "return {badCode: bad.active && bad.active.code, ext: ext.active.code, plain: plain.active.code, "
            "done: Object.keys(s.completed), current: todayTaskCurrentCode(s)}; })()")["result"]
        self.assertEqual(res["ext"], "EXT-01")
        self.assertEqual(res["plain"], "CORE-01")
        self.assertIsNone(res["badCode"])  # a mandatory code is not accepted as the optional argument
        self.assertEqual(res["done"], ["EXT-01"])
        self.assertEqual(res["current"], "CORE-01")


class TestTodayTaskReviewResultCard(unittest.TestCase):
    """WP5a: the 核對 phase of every task asks for a 作答結果卡 per QID (view-model level)."""

    def phases(self, code, source_expected_flag=None):
        res = run_node(
            f"(() => {{ const t = DAILY_SCHEDULE.tasks['{code}']; "
            "return t.phases.map((p, i) => { const v = todayTaskPhaseView(t, {code: t.code, phaseIndex: i, phaseStartedAt: 0}, 0); "
            "return {label: p.label, review: v.isReview, qids: v.resultQids, source: v.resultSource, closed: v.closed}; }); })()")
        return res["result"]

    def test_every_task_has_exactly_one_review_phase_listing_all_qids(self):
        codes = run_node("Object.keys(DAILY_SCHEDULE.tasks)")["result"]
        for code in codes:
            task = run_node(f"DAILY_SCHEDULE.tasks['{code}']")["result"]
            phases = self.phases(code)
            reviews = [p for p in phases if p["review"]]
            self.assertEqual(len(reviews), 1, code)
            self.assertEqual(reviews[0]["qids"], task["qids"], code)
            self.assertFalse(reviews[0]["closed"], code)
            for p in phases:
                if p["closed"]:
                    self.assertEqual(p["qids"], [], f"{code}: closed phase must not show result cards")

    def test_source_is_today_for_mandatory_and_ext_for_optional(self):
        self.assertEqual([p["source"] for p in self.phases("CORE-01") if p["review"]], ["today"])
        self.assertEqual([p["source"] for p in self.phases("EXT-01") if p["review"]], ["ext"])

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

    def test_overlay_header_names_the_active_task_even_when_it_is_ext(self):
        res = run_node(
            "(() => { const s = todayTaskStart({completed:{}, active:null}, 1000, 'EXT-01'); "
            "return todayTaskOverlayHtml(todayTaskViewModel(s, 1000)); })()")["result"]
        self.assertIn("EXT-01｜", res)
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
