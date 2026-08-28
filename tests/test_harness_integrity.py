# -*- coding: utf-8 -*-
"""
test_harness_integrity.py
=========================
Integration and unit tests for Pi x Hermes Dual Harness Architecture:
1. Validates Persistent Memory JSON schemas (.agents/memory/)
2. Validates Pi Math Verifier computation accuracy
3. Validates Skill definitions (.agents/skills/)
"""

import unittest
import os
import json
import cmath
import math

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(WORKSPACE, '.agents', 'memory')
SKILLS_DIR = os.path.join(WORKSPACE, '.agents', 'skills')
TOOLS_DIR = os.path.join(WORKSPACE, 'scripts', 'tools')

import sys
sys.path.insert(0, WORKSPACE)
from scripts.tools.math_verifier import MathVerifier, HAS_SYMPY


class TestHarnessIntegrity(unittest.TestCase):

    def test_exam_blindspots_memory_schema(self):
        """Test exam_blindspots.json exists and adheres to schema."""
        blindspots_path = os.path.join(MEMORY_DIR, 'exam_blindspots.json')
        self.assertTrue(os.path.exists(blindspots_path), "exam_blindspots.json must exist")
        
        with open(blindspots_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertIn("version", data)
        self.assertIn("subjects", data)
        required_subjects = ["circuit_theory", "power_systems", "electrical_machinery"]
        for sub in required_subjects:
            self.assertIn(sub, data["subjects"], f"Missing subject {sub} in blindspots")
            self.assertIn("blindspots", data["subjects"][sub])
            self.assertIsInstance(data["subjects"][sub]["blindspots"], list)

    def test_career_competency_memory_schema(self):
        """Test career_competency_map.json exists and adheres to EA structure."""
        competency_path = os.path.join(MEMORY_DIR, 'career_competency_map.json')
        self.assertTrue(os.path.exists(competency_path), "career_competency_map.json must exist")
        
        with open(competency_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertIn("competency_elements", data)
        self.assertIn("PE1_KNOWLEDGE_BASE", data["competency_elements"])
        self.assertIn("PE2_ENGINEERING_APPLICATION_ABILITY", data["competency_elements"])
        self.assertIn("PE3_PROFESSIONAL_AND_PERSONAL_ATTRIBUTES", data["competency_elements"])

    def test_pi_math_verifier_polar_conversions(self):
        """Test complex <-> polar conversion in math_verifier."""
        verifier = MathVerifier()
        # 3 + j4 -> 5 ∠ 53.13°
        z = complex(3, 4)
        polar = verifier.complex_to_polar(z)
        self.assertAlmostEqual(polar["magnitude"], 5.0, places=3)
        self.assertAlmostEqual(polar["angle_deg"], 53.13, delta=0.05)

        # 5 ∠ 53.1301° -> 3 + j4
        rec = verifier.polar_to_complex(5.0, 53.13010235)
        self.assertAlmostEqual(rec.real, 3.0, places=2)
        self.assertAlmostEqual(rec.imag, 4.0, places=2)

    def test_pi_math_verifier_per_unit(self):
        """Test per-unit base conversion formula."""
        verifier = MathVerifier()
        # Z_old = 0.1 pu, V_old = 11kV, V_new = 11kV, S_old = 10MVA, S_new = 100MVA -> Z_new = 1.0 pu
        z_new = verifier.per_unit_conversion(0.1, 11.0, 11.0, 10.0, 100.0)
        self.assertAlmostEqual(z_new, 1.0, places=4)

        # Z_old = 0.2 pu, V_old = 22kV, V_new = 11kV (factor 4), S_old = 50MVA, S_new = 100MVA (factor 2) -> 0.2 * 4 * 2 = 1.6 pu
        z_new2 = verifier.per_unit_conversion(0.2, 22.0, 11.0, 50.0, 100.0)
        self.assertAlmostEqual(z_new2, 1.6, places=4)

    def test_pi_math_verifier_symmetrical_components(self):
        """Test symmetrical components transformation."""
        verifier = MathVerifier()
        # Balanced 3-phase positive sequence currents: Ia = 10 ∠ 0°, Ib = 10 ∠ -120°, Ic = 10 ∠ 120°
        ia = verifier.polar_to_complex(10.0, 0.0)
        ib = verifier.polar_to_complex(10.0, -120.0)
        ic = verifier.polar_to_complex(10.0, 120.0)
        
        comps = verifier.symmetrical_components(ia, ib, ic)
        self.assertAlmostEqual(comps["zero_seq"]["magnitude"], 0.0, places=2)
        self.assertAlmostEqual(comps["pos_seq"]["magnitude"], 10.0, places=2)
        self.assertAlmostEqual(comps["neg_seq"]["magnitude"], 0.0, places=2)

    def test_skills_frontmatter(self):
        """Test skill markdown files exist and have YAML frontmatter."""
        skills_to_check = ['exam-memory-evolver', 'au-competency-tracker', 'pi-harness-circuit-verifier']
        for s in skills_to_check:
            skill_md = os.path.join(SKILLS_DIR, s, 'SKILL.md')
            self.assertTrue(os.path.exists(skill_md), f"{s}/SKILL.md must exist")
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertTrue(content.startswith('---'), f"{s} must start with YAML frontmatter")


if __name__ == '__main__':
    unittest.main()
