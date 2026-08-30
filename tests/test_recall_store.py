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
const context = {{ console }};
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


if __name__ == '__main__':
    unittest.main()
