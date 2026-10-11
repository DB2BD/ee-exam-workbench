# -*- coding: utf-8 -*-
"""v1.3.7 作答時間帽: stage thresholds, overlay block text and starter buttons."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_today_task import run_node, local_ms, TODAY_JS  # noqa: E402

MIN = 60000
T0 = local_ms(2026, 10, 3, 9, 0)


def view_expr(code, phase, elapsed_ms):
    return (f"todayTaskViewModel({{completed:{{}}, active:{{code:'{code}', phaseIndex:{phase}, phaseStartedAt:{T0}}}}}, {T0 + elapsed_ms}).active")


def overlay_expr(code, phase, elapsed_ms):
    return (f"(() => {{ const vm = todayTaskViewModel({{completed:{{}}, active:{{code:'{code}', phaseIndex:{phase}, phaseStartedAt:{T0}}}}}, {T0 + elapsed_ms}); "
            "return todayTaskOverlayHtml(vm); })()")


class TestTimeCapStage(unittest.TestCase):
    def stage(self, code, phase, elapsed_ms):
        return run_node(f"todayTaskTimeCapStage({view_expr(code, phase, elapsed_ms)})")["result"]

    def test_thresholds(self):
        self.assertEqual(self.stage("CORE-01", 0, 5 * MIN - 1000)["stage"], 0)  # 4:59
        self.assertEqual(self.stage("CORE-01", 0, 5 * MIN)["stage"], 1)  # 5:00
        self.assertEqual(self.stage("CORE-01", 0, 15 * MIN - 1000)["stage"], 1)  # 14:59
        self.assertEqual(self.stage("CORE-01", 0, 15 * MIN)["stage"], 2)  # 15:00

    def test_constants(self):
        res = run_node("[TODAY_TASK_CAP_HINT_MS, TODAY_TASK_CAP_STOP_MS]")["result"]
        self.assertEqual(res, [5 * MIN, 15 * MIN])

    def test_non_closed_phase_is_stage_zero(self):
        self.assertEqual(self.stage("CORE-01", 1, 20 * MIN)["stage"], 0)

    def test_expired_phase_is_stage_zero(self):
        self.assertEqual(self.stage("CORE-01", 0, 3 * 3600 * 1000)["stage"], 0)

    def test_paper_task_closed_phase_is_stage_zero(self):
        for code in ("MOCK114-01", "BLIND108-01"):
            self.assertEqual(self.stage(code, 0, 30 * MIN)["stage"], 0, code)

    def test_multi_flag(self):
        self.assertFalse(self.stage("CORE-01", 0, 6 * MIN)["multi"])
        self.assertTrue(self.stage("MAIN-01", 0, 6 * MIN)["multi"])
        self.assertEqual(self.stage("MAIN-01", 0, 16 * MIN), {"stage": 2, "multi": True})

    def test_null_view(self):
        self.assertEqual(run_node("todayTaskTimeCapStage(null)")["result"], {"stage": 0, "multi": False})


class TestTimeCapOverlay(unittest.TestCase):
    def test_no_block_before_five_minutes(self):
        html = run_node(overlay_expr("CORE-01", 0, 5 * MIN - 1000))["result"]
        self.assertNotIn("today-task-timecap", html)
        self.assertNotIn("data-today-starter", html)

    def test_stage_one_block_and_starter_button(self):
        html = run_node(overlay_expr("CORE-01", 0, 6 * MIN))["result"]
        self.assertIn('<div class="today-task-timecap" id="today-task-timecap" role="status"', html)
        self.assertIn("已經 5 分鐘還沒下第一筆？可以只看起手式（不看完整詳解），寫出第一步後繼續。", html)
        self.assertIn('data-today-starter="EE-114-01-3"', html)
        self.assertIn("看 EE-114-01-3 起手式", html)
        self.assertNotIn("today-task-timecap--stop", html)
        self.assertLess(html.index("today-task-timecap"), html.index("today-task-figure"))
        self.assertNotIn("data-today-starter-panel", html)  # panel closed until clicked
        self.assertNotIn("data-today-check", html)  # closed book: still no solution entry

    def test_stage_two_single_question(self):
        html = run_node(overlay_expr("CORE-01", 0, 16 * MIN))["result"]
        self.assertIn("today-task-timecap--stop", html)
        self.assertIn("卡超過 15 分鐘了：按「停筆，開始核對」看詳解、標 ×，明天再重做這題。卡住的時間不會變成分數。", html)
        self.assertIn('data-today-starter="EE-114-01-3"', html)

    def test_stage_two_multi_question(self):
        res = run_node("(() => { const v = " + view_expr("MAIN-01", 0, 16 * MIN) + "; return {html: todayTaskTimeCapHtml(v, []), qids: v.questionQids}; })()")["result"]
        self.assertGreater(len(res["qids"]), 1)
        self.assertIn("有一題卡超過 15 分鐘就先跳下一題，把會的先拿穩；核對時再看詳解、標 ×。", res["html"])
        self.assertNotIn("卡超過 15 分鐘了", res["html"])
        for qid in res["qids"]:
            self.assertIn(f'data-today-starter="{qid}"', res["html"])

    def test_paper_overlay_has_no_block(self):
        html = run_node(overlay_expr("MOCK114-01", 0, 30 * MIN))["result"]
        self.assertNotIn("today-task-timecap", html)

    def test_review_phase_has_no_block(self):
        html = run_node(overlay_expr("CORE-01", 1, 20 * MIN))["result"]
        self.assertNotIn("today-task-timecap", html)

    def test_starter_panel_shows_only_the_starter(self):
        prelude = ("globalThis.findQuestionRecord = q => ['EE-114-01-3', 1]; "
                   "globalThis.getRecallHintBundle = (q, r) => ({ activation: 'plain', activationMd: 'FIRST-STEP', formula: 'FORMULA-SECRET', trap: 'TRAP-SECRET', trapsMd: 'TRAPS-SECRET' }); "
                   "globalThis.processMarkdownWithMath = md => '<p>' + md + '</p>';")
        expr = ("(() => { " + prelude + " const v = " + view_expr("CORE-01", 0, 6 * MIN) + "; return todayTaskTimeCapHtml(v, new Set(['EE-114-01-3'])); })()")
        html = run_node(expr)["result"]
        self.assertIn('data-today-starter-panel="EE-114-01-3"', html)
        self.assertIn("<p>FIRST-STEP</p>", html)
        self.assertIn('aria-expanded="true"', html)
        for secret in ("FORMULA-SECRET", "TRAP-SECRET", "TRAPS-SECRET"):
            self.assertNotIn(secret, html)

    def test_starter_plain_fallback_is_escaped(self):
        prelude = "globalThis.getRecallHintBundle = () => ({ activation: '<b>先列出已知量</b>' });"
        expr = "(() => { " + prelude + " return todayTaskStarterHtml('EE-114-01-3'); })()"
        self.assertEqual(run_node(expr)["result"], "&lt;b&gt;先列出已知量&lt;/b&gt;")

    def test_revealed_state_resets_when_phase_changes(self):
        expr = ("(() => { const a = " + view_expr("CORE-07", 0, 6 * MIN) + "; const b = " + view_expr("CORE-07", 1, 6 * MIN) + "; "
                "todayTaskCapSync(a); todayTaskCapRevealed.add('EE-x'); const added = todayTaskCapRevealed.size; "
                "todayTaskCapSync(a); const kept = todayTaskCapRevealed.size; todayTaskCapSync(b); const cleared = todayTaskCapRevealed.size; "
                "todayTaskCapRevealed.add('EE-y'); todayTaskCapReset(); return [added, kept, cleared, todayTaskCapRevealed.size]; })()")
        self.assertEqual(run_node(expr)["result"], [1, 1, 0, 0])

    def test_source_wiring(self):
        src = TODAY_JS.read_text(encoding="utf-8")
        self.assertIn("todayTaskUpdateTimeCap(vm.active)", src)
        self.assertIn("todayTaskToggleStarter(starter)", src)
        self.assertIn("todayTaskCapReset();", src)


if __name__ == "__main__":
    unittest.main()
