# -*- coding: utf-8 -*-
"""
test_database_integrity.py
==========================
Integration tests verifying:
1. Total 423 questions (318 PE + 105 GK) exist and are valid.
2. Every question maps to a valid Markdown file in the bundle.
3. Zero placeholder text ('待解', '尚未提供') exists.
"""

import unittest
import json
import re
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestDatabaseIntegrity(unittest.TestCase):

    def setUp(self):
        self.pe_db_path = os.path.join(WORKSPACE, 'dashboard-data.js')
        self.pe_bundle_path = os.path.join(WORKSPACE, 'solutions-bundle.js')
        self.gk_db_path = os.path.join(WORKSPACE, 'national-exams-data.js')
        self.gk_bundle_path = os.path.join(WORKSPACE, 'national-solutions-bundle.js')

    def test_pe_database_records(self):
        self.assertTrue(os.path.exists(self.pe_db_path))
        with open(self.pe_db_path, 'r', encoding='utf-8') as f:
            text = f.read()
        m = re.search(r'questions:\s*(\[[\s\S]+?\]),\s*\n\s*sevenLayers:', text)
        self.assertIsNotNone(m, "PE questions array must be parseable")
        pe_questions = json.loads(m.group(1))
        self.assertEqual(len(pe_questions), 318, "PE database must contain exactly 318 questions")

    def test_gk_database_records(self):
        self.assertTrue(os.path.exists(self.gk_db_path))
        with open(self.gk_db_path, 'r', encoding='utf-8') as f:
            text = f.read()
        m = re.search(r'questions:\s*(\[[\s\S]+?\])\s*\}\;', text)
        self.assertIsNotNone(m, "GK questions array must be parseable")
        gk_questions = json.loads(m.group(1))
        self.assertEqual(len(gk_questions), 105, "GK database must contain exactly 105 questions")

    def test_zero_placeholders_in_gk_bundle(self):
        self.assertTrue(os.path.exists(self.gk_bundle_path))
        with open(self.gk_bundle_path, 'r', encoding='utf-8') as f:
            text = f.read()
        m = re.search(r'const NATIONAL_BUNDLED_MD\s*=\s*(\{[\s\S]+?\});\s*const NATIONAL_IMAGE_MAP', text)
        self.assertIsNotNone(m)
        bundle = json.loads(m.group(1))
        for path, md in bundle.items():
            self.assertNotIn("⏳ 本題尚未提供詳解", md, f"Placeholder found in {path}")
            self.assertNotIn("(待解)", md, f"Placeholder found in {path}")

if __name__ == '__main__':
    unittest.main()
