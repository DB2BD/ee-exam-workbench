# -*- coding: utf-8 -*-
"""
test_numeric_verifier.py
========================
Tests for fast numeric answer check and exam pitfall detection.
"""

import unittest
import subprocess
import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestNumericVerifier(unittest.TestCase):
    def test_numeric_verifier_rules(self):
        script = f"""
        const {{ verifyNumericAnswer }} = require('{os.path.join(WORKSPACE, 'src/domain/numericVerifier.js')}');
        const mockSolution = `
          計算各相阻抗與電流：
          Z = 3 + j4 \\\\Omega \\\\implies |Z| = 5 \\\\Omega
          線電流 I_L = 14.14 \\\\text{{ A}}
          三相實功 P = \\\\sqrt{{3}} V_L I_L \\\\cos\\\\theta = 8391.8 \\\\text{{ W}} = 8.39 \\\\text{{ kW}}
        `;

        // 1. Direct hit with tolerance
        const r1 = verifyNumericAnswer('14.1', mockSolution);
        if (!r1.ok || r1.matchType !== 'exact') throw new Error('14.1 should match 14.14');

        const r2 = verifyNumericAnswer('8390', mockSolution);
        if (!r2.ok || r2.matchType !== 'exact') throw new Error('8390 should match 8391.8');

        // 2. Sqrt(3) trap detection
        // 14.14 * 1.732 = 24.49
        const r3 = verifyNumericAnswer('24.5', mockSolution);
        if (r3.ok || r3.matchType !== 'sqrt3_trap') throw new Error('24.5 should trigger sqrt3_trap');

        // 3. Unit prefix 1000x trap detection
        const r4 = verifyNumericAnswer('8391800', mockSolution);
        if (r4.ok || r4.matchType !== 'unit_prefix_trap') throw new Error('1000x should trigger unit_prefix_trap');

        // 4. Sign inversion detection
        const r5 = verifyNumericAnswer('-5', mockSolution);
        if (r5.ok || r5.matchType !== 'sign_error') throw new Error('-5 should trigger sign_error against 5');

        // 5. Complete mismatch
        const r6 = verifyNumericAnswer('99999', mockSolution);
        if (r6.ok || r6.matchType !== 'mismatch') throw new Error('Random number should mismatch');

        console.log(JSON.stringify({{ success: true }}));
        """
        proc = subprocess.run(['node', '-e', script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed:\n{proc.stderr}")
        data = json.loads(proc.stdout.strip())
        self.assertTrue(data.get('success'))

if __name__ == '__main__':
    unittest.main()
