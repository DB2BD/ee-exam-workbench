# -*- coding: utf-8 -*-
"""學習狀態 follows the result card: all ○ → 已掌握, any × or △ → 需二刷; one-time reconcile of existing cards."""

import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import node_runner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "src/data/questionPoints.generated.js",
    "src/data/targetAllocation.generated.js",
    "src/domain/studyPlan.js",
    "src/state/sm2Store.js",
    "src/state/resultCardStore.js",
]
CARD_KEY = "EE_EXAM_RESULT_CARD_V1"
PROGRESS_KEY = "EE_EXAM_PROGRESS_V1"
MARKER_KEY = "EE_EXAM_PROGRESS_RECONCILED_V1"
PRELUDE = """
let currentExamCategory = 'PE';
let progressState = JSON.parse(localStorage.getItem('EE_EXAM_PROGRESS_V1') || '{}');
function saveProgress() { localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify(progressState)); }
"""


def run_node(expression, storage=None):
    sources = PRELUDE + "\n".join((ROOT / s).read_text(encoding="utf-8") for s in SOURCES)
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
vm.runInContext({json.dumps(sources + chr(10) + 'globalThis.__result = (' + expression + ');', ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify({{result: context.__result, storage: data}}));
"""
    done = node_runner.run(script, cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def card(qid, at, *marks, legacy=False):
    rec = {"id": f"r-{qid}-{at}", "qid": qid, "at": at, "source": "legacy" if legacy else "today", "tier": "main",
           "parts": [{"label": "整題", "points": 20, "mark": m} for m in marks], "errors": [], "note": "", "total": 20}
    if legacy:
        rec["legacy"] = True
    return rec


class TestRule(unittest.TestCase):
    def test_status_for_rating(self):
        out = run_node("[resultCardProgressStatus(5), resultCardProgressStatus(3), resultCardProgressStatus(1), resultCardProgressStatus(null)]")
        self.assertEqual(out["result"], [1, 2, 2, None])

    def test_new_card_with_tri_marks_review_even_if_mastered(self):
        out = run_node("""(() => {
          progressState['EE-114-01-2'] = 1;
          saveResultRecord({qid:'EE-114-01-2', source:'review', parts:[{label:'（一）', points:10, mark:'o'},{label:'（二）', points:10, mark:'tri'}]});
          saveResultRecord({qid:'EE-114-01-3', source:'today', parts:[{label:'整題', points:20, mark:'tri'}]});
          saveResultRecord({qid:'EE-114-03-5', source:'today', parts:[{label:'整題', points:20, mark:'o'}]});
          return progressState; })()""")
        self.assertEqual(out["result"], {"EE-114-01-2": 2, "EE-114-01-3": 2, "EE-114-03-5": 1})


class TestReconcile(unittest.TestCase):
    STORAGE = {
        CARD_KEY: json.dumps({"version": 1, "migrated": True, "records": [
            card("EE-114-01-1", 100, "o"), card("EE-114-01-1", 200, "tri"),    # latest △ → 需二刷 (was 已掌握)
            card("EE-114-01-2", 100, "o", legacy=True),                        # legacy ○ → 已掌握
            card("EE-114-01-3", 100, "x", legacy=True),                        # legacy × → 需二刷
            card("EE-114-01-4", 300, "x"), card("EE-114-01-4", 100, "o"),      # order by time, not by list position
        ]}),
        PROGRESS_KEY: json.dumps({"EE-114-01-1": 1, "EE-114-02-1": 1, "EE-114-02-2": 2}),
    }

    def test_reconcile_follows_latest_card_and_keeps_questions_without_cards(self):
        out = run_node("(() => ({ first: reconcileProgressWithResultCards(), mem: progressState }))()", dict(self.STORAGE))
        res = out["result"]
        self.assertEqual(res["first"]["changed"], 4)
        expected = {"EE-114-01-1": 2, "EE-114-01-2": 1, "EE-114-01-3": 2, "EE-114-01-4": 2,
                    "EE-114-02-1": 1, "EE-114-02-2": 2}
        self.assertEqual(json.loads(out["storage"][PROGRESS_KEY]), expected)
        self.assertEqual(res["mem"], expected)
        self.assertIn(MARKER_KEY, out["storage"])

    def test_reconcile_runs_once_unless_forced(self):
        storage = dict(self.STORAGE)
        storage[MARKER_KEY] = "2026-10-25T00:00:00.000Z"
        out = run_node("[reconcileProgressWithResultCards(), reconcileProgressWithResultCards({force: true})]", storage)
        self.assertTrue(out["result"][0]["already"])
        self.assertEqual(out["result"][1]["changed"], 4)

    def test_wiring(self):
        main = (ROOT / "src/main.js").read_text(encoding="utf-8")
        header = (ROOT / "src/components/header.js").read_text(encoding="utf-8")
        sm2 = (ROOT / "src/state/sm2Store.js").read_text(encoding="utf-8")
        attempt = (ROOT / "src/state/attemptStore.js").read_text(encoding="utf-8")
        self.assertIn("reconcileProgressWithResultCards()", main)
        self.assertIn("reconcileProgressWithResultCards({ force: true })", header)
        # cloud-sync merges go through applyUserDataBackup and must not re-derive (manual taps would be undone)
        self.assertNotIn("reconcileProgressWithResultCards", sm2)
        self.assertIn("else if (rating === 1 || rating === 3) nextProgressAll[qid] = 2;", attempt)


if __name__ == "__main__":
    unittest.main()
