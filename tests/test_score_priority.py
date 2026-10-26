"""依上榜效益選題：src/domain/scorePriority.js 的排序規則，以及 REINF／練習頁接上 priority 模式。"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import node_runner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = (ROOT / "src/domain/scorePriority.js").read_text(encoding="utf-8")
STORE = (ROOT / "src/state/practiceStore.js").read_text(encoding="utf-8")
DAY = 86400000
NOW = "new Date(2026, 9, 27, 9).getTime()"

# Two subjects.  01: chapter a (6 questions) and b (2).  02: chapter c (4) and d (4).
BANK = ([{"id": f"EE-114-01-{i}", "subjectId": "01", "chapter": "a"} for i in range(1, 7)]
        + [{"id": f"EE-113-01-{i}", "subjectId": "01", "chapter": "b"} for i in range(1, 3)]
        + [{"id": f"EE-114-02-{i}", "subjectId": "02", "chapter": "c"} for i in range(1, 5)]
        + [{"id": f"EE-113-02-{i}", "subjectId": "02", "chapter": "d"} for i in range(1, 5)])


def rank(records, candidates=None, due=(), now=NOW, count=3):
    script = f"""
const vm = require('vm'); const ctx = {{}}; vm.createContext(ctx);
vm.runInContext({json.dumps(DOMAIN)}, ctx);
ctx.__in = {json.dumps({"bank": BANK, "records": records, "cands": candidates, "due": list(due)})};
const r = vm.runInContext(`(() => {{ const now = {now}; const recs = __in.records.map(r => Object.assign({{}}, r, {{ at: now + r.at }}));
  return priorityRankCandidates(__in.cands || __in.bank, {{ questions: __in.bank, records: recs, dueIds: __in.due, now, count: {count} }}); }})()`, ctx);
process.stdout.write(JSON.stringify(r));
"""
    done = node_runner.run(script, check=True)
    return json.loads(done.stdout)


def card(qid, ratio, days_ago=1):
    return {"qid": qid, "at": -days_ago * DAY, "estimate": 20 * ratio, "total": 20, "parts": []}


class TestScorePriority(unittest.TestCase):
    def test_big_weak_chapter_comes_first_and_one_per_chapter(self):
        # Chapter a is 75% of subject 01 but answered at 10%; chapter c answered at 90%.
        recs = [card("EE-114-01-1", 0.1), card("EE-114-01-2", 0.1), card("EE-114-02-1", 0.9),
                card("EE-114-02-2", 0.9), card("EE-113-02-1", 0.9), card("EE-113-01-1", 0.9)]
        out = rank(recs)
        self.assertEqual(out[0]["chapter"], "a")
        self.assertEqual(out[0]["kind"], "redo")  # a missed question beats a new one in the same chapter
        chapters = [x["chapter"] for x in out]
        self.assertEqual(len(chapters), len(set(chapters)))

    def test_rate_uses_first_attempts_not_redone_scores(self):
        # Redone up to 100% later: the chapter still counts as weak on NEW questions.
        recs = [card("EE-114-01-1", 0.0, 5), card("EE-114-01-1", 1.0, 1), card("EE-114-02-1", 0.9),
                card("EE-113-02-1", 0.9), card("EE-113-01-1", 0.9)]
        out = rank(recs)
        self.assertEqual(out[0]["chapter"], "a")
        self.assertEqual(out[0]["kind"], "new")
        self.assertLess(out[0]["rate"], 0.5)

    def test_well_answered_question_returns_only_when_due_and_at_half_value(self):
        recs = [card("EE-114-02-1", 0.8)]
        cands = [b for b in BANK if b["id"] in ("EE-114-02-1", "EE-114-02-2")]
        self.assertEqual([x["id"] for x in rank(recs, cands, count=2)], ["EE-114-02-2"])
        out = rank(recs, [cands[0]], due=["EE-114-02-1"], count=1)
        self.assertEqual(out[0]["kind"], "review")

    def test_no_new_questions_in_the_last_week(self):
        late = "new Date(2026, 10, 8, 9).getTime()"
        recs = [card("EE-114-01-1", 0.2)]
        out = rank(recs, now=late)
        self.assertEqual([x["kind"] for x in out], ["redo"])
        self.assertTrue(any(x["kind"] == "new" for x in rank(recs)))

    def test_subject_untouched_for_three_days_gets_the_last_slot(self):
        # Subject 01 is far more valuable, but subject 02 has no card for 5 days.
        recs = [card("EE-114-01-1", 0.0, 1), card("EE-114-01-2", 0.0, 1), card("EE-113-01-1", 0.0, 1),
                card("EE-114-02-1", 0.95, 5), card("EE-113-02-1", 0.95, 5)]
        out = rank(recs)
        self.assertEqual(out[-1]["subjectId"], "02")
        self.assertLessEqual(sum(1 for x in out if x["subjectId"] == "01"), 2)

    def test_expected_scores_follow_chapter_share(self):
        script = f"""
const vm = require('vm'); const ctx = {{}}; vm.createContext(ctx);
vm.runInContext({json.dumps(DOMAIN)}, ctx);
ctx.__bank = {json.dumps(BANK)};
process.stdout.write(JSON.stringify(vm.runInContext('priorityExpectedScores(priorityModel(__bank, []))', ctx)));
"""
        out = json.loads(node_runner.run(script, check=True).stdout)
        self.assertAlmostEqual(out["01"], 45.0)
        self.assertAlmostEqual(out["02"], 45.0)


class TestPriorityQueueWiring(unittest.TestCase):
    def test_store_queue_respects_the_pool_and_tops_up(self):
        script = f"""
const vm = require('vm'); const ctx = {{ console }}; vm.createContext(ctx);
vm.runInContext({json.dumps(DOMAIN)}, ctx);
vm.runInContext({json.dumps(STORE)}, ctx);
ctx.__bank = {json.dumps(BANK)};
const r = vm.runInContext(`(() => {{ const now = {NOW};
  const qs = __bank.map(b => ({{ id: b.id, subjectId: b.subjectId, chapter: b.chapter }}));
  const recent = {{ 'EE-114-01-2': new Date(now - 86400000).toISOString() }};
  return createPriorityPracticeQueue(qs, {{ count: 3, now, records: [], dueQids: [], lockedQids: ['EE-114-01-1'],
    completionByQuestion: recent, chapterOf: q => q.chapter, typeOf: () => 'unknown', random: () => 0.5, tierOf: () => 'main' }}); }})()`, ctx);
process.stdout.write(JSON.stringify(r));
"""
        out = json.loads(node_runner.run(script, check=True).stdout)
        self.assertEqual(len(out), 3)
        self.assertNotIn("EE-114-01-1", out)  # locked mock paper
        self.assertNotIn("EE-114-01-2", out)  # practised yesterday

    def test_ui_and_reinf_use_priority_mode(self):
        ui = (ROOT / "src/components/dailyPractice.js").read_text(encoding="utf-8")
        self.assertIn("['priority', '依上榜效益']", ui)
        self.assertIn("createPriorityPracticeQueue(questions, base)", ui)
        today = (ROOT / "src/components/todayTask.js").read_text(encoding="utf-8")
        self.assertIn("'random-reinforce' ? 'priority' : 'balanced'", today)
        build = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
        self.assertLess(build.index("src/domain/scorePriority.js"), build.index("src/state/practiceStore.js"))


if __name__ == "__main__":
    unittest.main()
