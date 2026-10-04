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

        // 2-3. Stages follow docs/上榜考場120分鐘得分節奏.md: 5 scan + 90 first
        // pass + 17 score-recovery + 8 wrap-up.
        const expectStage = (remaining, stage, word) => {{
            const p = getMockExamPacingInfo(remaining);
            if (p.stage !== stage || p.label.indexOf(word) < 0) throw new Error('remaining ' + remaining + 's: ' + JSON.stringify(p));
        }};
        expectStage(7200 - 4 * 60, 1, '掃卷');
        expectStage(7200 - 5 * 60, 2, '第一輪');
        expectStage(3600, 2, '第一輪');
        expectStage(7200 - 95 * 60, 3, '搶分');
        expectStage(600, 3, '搶分');
        expectStage(8 * 60, 4, '收尾');
        expectStage(0, 4, '收尾');

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
