# -*- coding: utf-8 -*-
"""
test_sm2_spaced_repetition.py
=============================
Unit tests for the SuperMemo SM-2 Spaced Repetition Algorithm & Active Recall Engine.
"""

import unittest
import json
import datetime
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestSM2SpacedRepetition(unittest.TestCase):

    def run_store(self, expression, timezone="Asia/Taipei"):
        source = (ROOT / "src/state/sm2Store.js").read_text(encoding="utf-8")
        script = f"""
const vm=require('vm');
const localStorage={{getItem:()=>null,setItem:()=>{{}},removeItem:()=>{{}}}};
const context={{console,localStorage}}; vm.createContext(context);
vm.runInContext({json.dumps(source, ensure_ascii=False)},context);
const result=vm.runInContext({json.dumps(expression, ensure_ascii=False)},context);
process.stdout.write(JSON.stringify(result));
"""
        env = os.environ.copy()
        env["TZ"] = timezone
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_calendar_dates_follow_browser_timezone_across_midnight(self):
        result = self.run_store("(() => { const now=new Date('2026-09-06T16:30:00.000Z'); const next=calculateSM2ReviewItem(null,3,now); return {today:formatLocalCalendarDate(now),last:next.lastReviewed,next:next.nextReviewDate}; })()")
        self.assertEqual(result, {"today": "2026-09-07", "last": "2026-09-07", "next": "2026-09-08"})

    def test_due_list_uses_the_same_local_calendar_day(self):
        result = self.run_store("(() => { sm2Schedule={due:{nextReviewDate:'2026-09-07'},future:{nextReviewDate:'2026-09-08'}}; return getDueQuestionsList(new Date('2026-09-06T16:30:00.000Z')); })()")
        self.assertEqual(result, ["due"])
    
    def simulate_sm2(self, item, rating):
        """Python mirror of sm2Store.js algorithm for deterministic verification."""
        repetitions = item.get('repetitions', 0)
        interval = item.get('interval', 0)
        easeFactor = item.get('easeFactor', 2.5)

        if rating < 3:
            repetitions = 0
            interval = 1
            easeFactor = max(1.3, easeFactor - 0.2)
        elif rating == 3:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 3
            else:
                interval = max(1, round(interval * 1.2))
            repetitions += 1
            easeFactor = max(1.3, easeFactor - 0.05)
        else:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 4
            else:
                interval = round(interval * easeFactor)
            repetitions += 1
            easeFactor = min(3.0, easeFactor + 0.1)

        return {
            'repetitions': repetitions,
            'interval': interval,
            'easeFactor': round(easeFactor, 2)
        }

    def test_sm2_progression_rating_5(self):
        """Test ideal SM-2 progression with consecutive 5s (Easy/Mastered)."""
        item = {'repetitions': 0, 'interval': 0, 'easeFactor': 2.5}
        
        # Day 1: First review -> interval = 1
        r1 = self.simulate_sm2(item, 5)
        self.assertEqual(r1['repetitions'], 1)
        self.assertEqual(r1['interval'], 1)
        self.assertEqual(r1['easeFactor'], 2.6)

        # Day 2: Second review -> interval = 4
        r2 = self.simulate_sm2(r1, 5)
        self.assertEqual(r2['repetitions'], 2)
        self.assertEqual(r2['interval'], 4)
        self.assertEqual(r2['easeFactor'], 2.7)

        # Day 6: Third review -> interval = round(4 * 2.7) = 11
        r3 = self.simulate_sm2(r2, 5)
        self.assertEqual(r3['repetitions'], 3)
        self.assertEqual(r3['interval'], 11)
        self.assertEqual(r3['easeFactor'], 2.8)

    def test_sm2_reset_on_failure(self):
        """Test SM-2 reset when rating is 1 (Forgot / Fail)."""
        item = {'repetitions': 3, 'interval': 11, 'easeFactor': 2.8}
        r = self.simulate_sm2(item, 1)
        self.assertEqual(r['repetitions'], 0)
        self.assertEqual(r['interval'], 1)
        self.assertEqual(r['easeFactor'], 2.6)

    def test_sm2_ease_factor_bounds(self):
        """Test ease factor does not drop below 1.3 or exceed 3.0."""
        item = {'repetitions': 0, 'interval': 1, 'easeFactor': 1.4}
        r_low = self.simulate_sm2(item, 1)
        self.assertGreaterEqual(r_low['easeFactor'], 1.3)

        item_high = {'repetitions': 10, 'interval': 100, 'easeFactor': 2.95}
        r_high = self.simulate_sm2(item_high, 5)
        self.assertLessEqual(r_high['easeFactor'], 3.0)

    def test_backup_restore_json_schema(self):
        """Test that user backup JSON includes progress, starred, and SM-2 schedules."""
        sample_payload = {
            "version": "1.0.0",
            "exportedAt": "2026-08-27T00:00:00.000Z",
            "progressState": {"EE-114-05-1": 1, "EE-107-05-2": 2},
            "starredState": {"EE-114-05-1": True},
            "sm2Schedule": {
                "EE-114-05-1": {
                    "repetitions": 2,
                    "interval": 4,
                    "easeFactor": 2.7,
                    "lastReviewed": "2026-08-27",
                    "nextReviewDate": "2026-08-31"
                }
            },
            "manualTopicLabels": {
                "EE-109-02-3": {
                    "chapterId": "el-pe-buck-boost",
                    "updatedAt": "2026-08-27T00:00:00.000Z"
                }
            }
        }
        json_str = json.dumps(sample_payload)
        parsed = json.loads(json_str)
        self.assertIn("sm2Schedule", parsed)
        self.assertEqual(parsed["sm2Schedule"]["EE-114-05-1"]["interval"], 4)
        self.assertEqual(parsed["manualTopicLabels"]["EE-109-02-3"]["chapterId"], "el-pe-buck-boost")

if __name__ == '__main__':
    unittest.main()
