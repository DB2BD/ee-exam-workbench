"""動態解鎖：12 份模考卷做完後，補強任務（BUFFER、REINF-*）不必等到 11/01、11/02；收尾（WRAP-*）仍照日期。"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import node_runner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["src/components/icons.js", "src/data/dailySchedule.generated.js", "src/domain/pacing.js", "src/components/todayTask.js"]


def node(expression):
    code = "\n".join((ROOT / s).read_text(encoding="utf-8") for s in SOURCES)
    script = ("const vm = require('vm'); const data = {};"
              "const localStorage = { getItem: k => data[k] ?? null, setItem: (k, v) => { data[k] = String(v); }, removeItem: k => { delete data[k]; } };"
              "const ctx = { console, localStorage }; vm.createContext(ctx);"
              f"vm.runInContext({json.dumps(code + chr(10) + 'globalThis.__r = (' + expression + ');')}, ctx);"
              "process.stdout.write(JSON.stringify(ctx.__r));")
    # Through stdin, not `node -e`: the inlined sources exceed Linux's 128 KB single-argument limit.
    return json.loads(node_runner.run(script, check=True).stdout)


# Everything before BUFFER done (all 12 papers included), dated a few days ago so nothing counts as done today.
DONE_BEFORE_BUFFER = """(() => { const o = DAILY_SCHEDULE.order, c = {};
  for (const k of o) { if (k === 'BUFFER') break; c[k] = '2026-10-20T10:00:00.000Z'; } return c; })()"""
# Same, but one paper still open.
ONE_PAPER_OPEN = """(() => { const c = %s; delete c['BLIND108-06']; return c; })()""" % DONE_BEFORE_BUFFER


def plan(completed, today, spent=0):
    return node(f"pacingPlan({{ schedule: DAILY_SCHEDULE, completed: {completed}, today: '{today}', spentToday: {spent} }})")


class TestDynamicUnlock(unittest.TestCase):
    def test_reinforce_opens_once_all_papers_are_done(self):
        p = plan(DONE_BEFORE_BUFFER, "2026-10-25")  # Sunday, before BUFFER (11/01) and REINF (11/02)
        self.assertTrue(p["allPapersDone"])
        codes = [i["code"] for i in p["plan"]]
        self.assertEqual(codes[0], "BUFFER")
        self.assertIn("REINF-01", codes)
        self.assertFalse(any(c.startswith("WRAP") for c in codes), codes)
        buffer = p["plan"][0]
        self.assertEqual(buffer["phaseIndex"], 1)  # nothing to make up: starts at 補強
        self.assertAlmostEqual(buffer["hours"], 2.0)
        self.assertEqual(buffer["part"], "full")

    def test_reinforce_waits_for_its_date_while_a_paper_is_open(self):
        p = plan(ONE_PAPER_OPEN, "2026-10-25")
        self.assertFalse(p["allPapersDone"])
        codes = [i["code"] for i in p["plan"]]
        self.assertNotIn("BUFFER", codes)
        self.assertFalse(any(c.startswith("REINF") for c in codes), codes)

    def test_wrap_keeps_its_date(self):
        done_through_reinf = """(() => { const o = DAILY_SCHEDULE.order, c = {};
          for (const k of o) { if (k.startsWith('WRAP')) break; c[k] = '2026-10-20T10:00:00.000Z'; } return c; })()"""
        p = plan(done_through_reinf, "2026-10-25")
        self.assertEqual(p["plan"], [])

    def test_day_done_offers_buffer_as_next_and_start_skips_make_up_phase(self):
        r = node(f"""(() => {{
          const state = {{ completed: {DONE_BEFORE_BUFFER}, active: null }};
          const now = new Date(2026, 9, 25, 20, 0).getTime();
          const vm = todayTaskViewModel(state, now, {{ dueCount: 0 }});
          const started = todayTaskStart(state, now, 'BUFFER');
          return {{ mode: vm.mode, code: vm.code, minutes: vm.totalMinutes, phase: started.active.phaseIndex }};
        }})()""")
        self.assertEqual(r["code"], "BUFFER")
        self.assertEqual(r["minutes"], 120)
        self.assertEqual(r["phase"], 1)

    def test_buffer_starts_at_make_up_phase_while_a_paper_is_open(self):
        r = node(f"todayTaskStart({{ completed: {ONE_PAPER_OPEN}, active: null }}, Date.now(), 'BUFFER').active.phaseIndex")
        self.assertEqual(r, 0)


if __name__ == "__main__":
    unittest.main()
