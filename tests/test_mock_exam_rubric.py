# -*- coding: utf-8 -*-
"""
test_mock_exam_rubric.py
========================
Tests for the Mock Exam 2.0 pacing advisor and step-marking rubric.
"""

import unittest
import subprocess
import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestMockExamRubric(unittest.TestCase):
    def test_pacing_and_rubric_logic(self):
        script = f"""
        const {{ getMockExamPacingInfo, DEFAULT_RUBRIC_STEPS, saveMockExamResult, getMockExamHistory, MOCK_EXAM_TIMER_DURATION_SECONDS }} = require('{os.path.join(WORKSPACE, 'src/components/mockExamTimer.js')}');
        
        // 1. Test pacing stage 1 (at start: 7200s remaining)
        const p1 = getMockExamPacingInfo(7200);
        if (p1.stage !== 1) throw new Error('Stage at start should be 1');

        // 2. Test pacing stage 3 (at 60 mins remaining: 3600s)
        const p3 = getMockExamPacingInfo(3600);
        if (p3.stage !== 3) throw new Error('Stage at 60 mins should be 3');

        // 3. Test final 10 mins (600s remaining)
        const p5 = getMockExamPacingInfo(600);
        if (p5.stage !== 5) throw new Error('Stage in last 10 mins should be 5 (audit period)');

        // 4. Test rubric steps total points
        const totalRubricPts = DEFAULT_RUBRIC_STEPS.reduce((sum, s) => sum + s.maxPts, 0);
        if (totalRubricPts !== 25) throw new Error('Default rubric steps must total exactly 25 points, got ' + totalRubricPts);

        // 5. Test mock storage mock
        globalThis.localStorage = {{
            _data: {{}},
            getItem(k) {{ return this._data[k] || null; }},
            setItem(k, v) {{ this._data[k] = String(v); }}
        }};
        saveMockExamResult({{ id: 'TEST1', score: 85, passed: true }});
        const history = getMockExamHistory();
        if (history.length !== 1 || history[0].score !== 85) {{
            throw new Error('History save failed');
        }}

        console.log(JSON.stringify({{ success: true }}));
        """
        proc = subprocess.run(['node', '-e', script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed:\n{proc.stderr}")
        data = json.loads(proc.stdout.strip())
        self.assertTrue(data.get('success'))

if __name__ == '__main__':
    unittest.main()
