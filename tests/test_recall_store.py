# -*- coding: utf-8 -*-
import json
import subprocess
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]


class TestRecallStore(unittest.TestCase):
    def _run(self, expression):
        source = (WORKSPACE / "src/state/recallStore.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const data = {{}};
const localStorage = {{getItem:key => data[key] || null, setItem:(key,value) => {{data[key]=String(value);}}, removeItem:key => {{delete data[key];}}}};
const context = {{ console, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(source + chr(10) + 'globalThis.__result = (' + expression + ');', ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(context.__result));
"""
        result = subprocess.run(["node", "-e", script], cwd=WORKSPACE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_two_successes_promote_one_level(self):
        self.assertEqual(
            self._run("(() => { recordRecallAttempt('Q', 1); return recordRecallAttempt('Q', 1).level; })()"),
            2,
        )

    def test_failure_demotes_only_one_level(self):
        self.assertEqual(
            self._run("(() => { recordRecallAttempt('Q', 1); recordRecallAttempt('Q', 1); recordRecallAttempt('Q', 1); return getRecallState('Q').level; })()"),
            1,
        )

    def test_invalid_level_is_clamped(self):
        self.assertEqual(
            self._run("recordRecallAttempt('Q', 99, '公式忘記').level"),
            1,
        )

    def test_each_promoted_level_requires_a_fresh_two_success_streak(self):
        result = self._run("(() => { const levels=[]; for(let i=0;i<6;i++) levels.push(recordRecallAttempt('Q',4).level); return levels; })()")
        self.assertEqual(result, [1, 2, 2, 3, 3, 4])

    def test_legacy_streak_without_level_evidence_is_reset_conservatively(self):
        result = self._run("(() => { localStorage.setItem(RECALL_STORAGE_KEY,JSON.stringify({Q:{level:3,streak:9,attempts:9,lastAchieved:4,lastErrorType:null,lastReviewed:'2026-09-01'}})); initRecallStore(); return getRecallState('Q'); })()")
        self.assertEqual(result["level"], 3)
        self.assertEqual(result["streak"], 0)


if __name__ == '__main__':
    unittest.main()
