# -*- coding: utf-8 -*-
"""
test_passing_probability.py
===========================
Tests for the Passing Probability Index (PPI) and readiness prediction engine.
"""

import unittest
import subprocess
import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPassingProbability(unittest.TestCase):
    def test_passing_probability_evaluation_node(self):
        script = f"""
        const {{ calculateExamReadiness, calculateSubjectReadiness, evaluateQuestionReadiness }} = require('{os.path.join(WORKSPACE, 'src/domain/passingProbability.js')}');
        
        // 1. Test question readiness calculation
        const r1 = evaluateQuestionReadiness('EE-114-01-1', 1, null, {{ achievedLevel: 4 }});
        if (r1 < 0.9) throw new Error('Mastered level 4 question should have readiness >= 0.9');

        const r2 = evaluateQuestionReadiness('EE-114-01-2', 0, null, null);
        if (r2 > 0.15) throw new Error('Unstarted question should have readiness <= 0.15');

        // 2. Test subject readiness
        const mockQuestions = [
            ['EE-114-01-1', '01', 114, 1, '戴維寧等效', [], '', '', 3],
            ['EE-114-01-2', '01', 114, 2, '交流暫態', [], '', '', 4],
            ['EE-114-01-3', '01', 114, 3, '二階電路', [], '', '', 4],
            ['EE-114-01-4', '01', 114, 4, '雙埠網路', [], '', '', 3],
        ];
        const progress = {{
            'EE-114-01-1': 1,
            'EE-114-01-2': 1,
            'EE-114-01-3': 0,
            'EE-114-01-4': 2
        }};
        const subjRes = calculateSubjectReadiness('01', mockQuestions, progress, {{}}, {{}});
        if (subjRes.estimatedScore < 30 || subjRes.estimatedScore > 90) {{
            throw new Error('Estimated score out of expected range: ' + subjRes.estimatedScore);
        }}

        // 3. Test full exam readiness across 6 subjects
        const fullMockQuestions = [];
        const subjects = ['01', '02', '03', '04', '05', '06'];
        subjects.forEach(sid => {{
            for (let i = 1; i <= 5; i++) {{
                fullMockQuestions.push([`EE-114-${{sid}}-${{i}}`, sid, 114, i, `章節${{i}}`, [], '', '', 3]);
            }}
        }});
        
        // Baseline: all unstarted
        const unstartedRes = calculateExamReadiness(fullMockQuestions, {{}}, {{}}, {{}});
        if (unstartedRes.passingProbability >= 20) {{
            throw new Error('Unstarted learner should have low passing probability: ' + unstartedRes.passingProbability);
        }}
        if (unstartedRes.tier !== 'danger') {{
            throw new Error('Unstarted learner should be in danger tier');
        }}

        // Well-prepared candidate: 80% mastered
        const preparedProgress = {{}};
        fullMockQuestions.forEach((q, idx) => {{
            if (idx % 5 !== 0) preparedProgress[q[0]] = 1; // 4 out of 5 mastered
        }});
        const preparedRes = calculateExamReadiness(fullMockQuestions, preparedProgress, {{}}, {{}});
        if (preparedRes.passingProbability < 70) {{
            throw new Error('Prepared learner should have passing probability >= 70%: ' + preparedRes.passingProbability);
        }}
        if (preparedRes.projectedAverage < 60) {{
            throw new Error('Prepared learner projected average should be >= 60');
        }}

        console.log(JSON.stringify({{ success: true, prob: preparedRes.passingProbability, avg: preparedRes.projectedAverage }}));
        """
        proc = subprocess.run(['node', '-'], input=script, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed:\n{proc.stderr}")
        data = json.loads(proc.stdout.strip())
        self.assertTrue(data.get('success'))

if __name__ == '__main__':
    unittest.main()
