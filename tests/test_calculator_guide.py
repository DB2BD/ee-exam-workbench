# -*- coding: utf-8 -*-
"""
test_calculator_guide.py
========================
Tests for the fx-82 calculator guide and phasor conversion logic.
"""

import unittest
import subprocess
import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestCalculatorGuide(unittest.TestCase):
    def test_phasor_conversions(self):
        script = f"""
        const {{ convertRectToPolar, convertPolarToRect, shouldShowCalculatorTip, FX82_RECIPES }} = require('{os.path.join(WORKSPACE, 'src/components/calculatorGuide.js')}');
        
        // 1. Test 3-4-5 triangle
        const p1 = convertRectToPolar(3, 4);
        if (Math.abs(p1.magnitude - 5.0) > 0.001) throw new Error('Magnitude should be 5');
        if (Math.abs(p1.angleDeg - 53.13) > 0.05) throw new Error('Angle should be ~53.13');

        // 2. Test polar to rect
        const r1 = convertPolarToRect(100, 30);
        if (Math.abs(r1.real - 86.602) > 0.01) throw new Error('Real should be ~86.60');
        if (Math.abs(r1.imag - 50.0) > 0.01) throw new Error('Imag should be ~50.0');

        // 3. Test negative imaginary (capacitive impedance)
        const p2 = convertRectToPolar(10, -10);
        if (Math.abs(p2.magnitude - 14.142) > 0.01) throw new Error('Magnitude should be ~14.14');
        if (Math.abs(p2.angleDeg - (-45.0)) > 0.01) throw new Error('Angle should be -45');

        // 4. Test shouldShowCalculatorTip keyword detector
        if (!shouldShowCalculatorTip('試求該三相負載之視在功率', ['電力系統'], '三相電路')) {{
            throw new Error('Should show calculator tip for 3-phase power question');
        }}
        if (shouldShowCalculatorTip('試說明微處理機中斷機制', ['嵌入式'], '計組')) {{
            throw new Error('Should not show calculator tip for pure digital logic question');
        }}

        // 5. Test recipes presence
        if (FX82_RECIPES.length < 4) throw new Error('Should have at least 4 recipes');

        console.log(JSON.stringify({{ success: true }}));
        """
        proc = subprocess.run(['node', '-e', script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed:\n{proc.stderr}")
        data = json.loads(proc.stdout.strip())
        self.assertTrue(data.get('success'))

if __name__ == '__main__':
    unittest.main()
