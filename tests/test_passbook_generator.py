# -*- coding: utf-8 -*-
"""
test_passbook_generator.py
==========================
Tests for the 15-Day Personal Exam Passbook Generator.
"""

import unittest
import subprocess
import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPassbookGenerator(unittest.TestCase):
    def test_passbook_generation(self):
        script = f"""
        const {{ generatePassbookData }} = require('{os.path.join(WORKSPACE, 'src/components/passbookGenerator.js')}');
        
        const mockQuestions = [];
        for (let i = 1; i <= 25; i++) {{
            mockQuestions.push([`EE-114-01-${{i}}`, '01', 114, i, `題目題幹${{i}}`, ['考點'], '', '', 3]);
        }}

        // Mark 3 questions as wrong (progressState = 2)
        const progress = {{
            'EE-114-01-3': 2,
            'EE-114-01-7': 2,
            'EE-114-01-12': 2
        }};

        const result = generatePassbookData(mockQuestions, progress, {{}}, {{}});
        if (!result.topAnchorQuestions || result.topAnchorQuestions.length > 15) {{
            throw new Error('topAnchorQuestions should be at most 15 items');
        }}

        // Check that wrong questions have higher priority
        const topQids = result.topAnchorQuestions.map(item => item.qid);
        if (!topQids.includes('EE-114-01-3') || !topQids.includes('EE-114-01-7')) {{
            throw new Error('Wrong questions must be ranked high in anchor questions');
        }}

        console.log(JSON.stringify({{ success: true, count: result.topAnchorQuestions.length }}));
        """
        proc = subprocess.run(['node', '-e', script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed:\n{proc.stderr}")
        data = json.loads(proc.stdout.strip())
        self.assertTrue(data.get('success'))

if __name__ == '__main__':
    unittest.main()
