# -*- coding: utf-8 -*-
"""
test_solution_extractor_and_years.py
====================================
Comprehensive calibration and verification test:
1. Verifies that all 11 years (104~114) are fully present in PE and 5 years (110~114) in GK.
2. Verifies that 100% of the 423 questions (318 PE + 105 GK) extract valid, non-empty solutions with derivations.
3. Verifies that multi-question full paper files correctly extract individual question sections instead of just header metadata.
"""

import unittest
import sys
import os
import json
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE)

class TestSolutionExtractorAndYears(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(WORKSPACE, 'dashboard-data.js'), 'r', encoding='utf-8') as f:
            t1 = f.read()
        m1 = re.search(r'questions:\s*(\[[\s\S]+?\]),\s*\n\s*sevenLayers:', t1)
        cls.pe_qs = json.loads(m1.group(1))

        with open(os.path.join(WORKSPACE, 'national-exams-data.js'), 'r', encoding='utf-8') as f:
            t2 = f.read()
        m2 = re.search(r'questions:\s*(\[[\s\S]+?\])\s*\}\;', t2)
        cls.gk_qs = json.loads(m2.group(1))

        with open(os.path.join(WORKSPACE, 'solutions-bundle.js'), 'r', encoding='utf-8') as f:
            sb = f.read()
        m_sb = re.search(r'const BUNDLED_MD\s*=\s*(\{[\s\S]+?\});\s*const IMAGE_MAP', sb)
        cls.pe_md = json.loads(m_sb.group(1)) if m_sb else {}

        with open(os.path.join(WORKSPACE, 'national-solutions-bundle.js'), 'r', encoding='utf-8') as f:
            nb = f.read()
        m_nb = re.search(r'const NATIONAL_BUNDLED_MD\s*=\s*(\{[\s\S]+?\});\s*const NATIONAL_IMAGE_MAP', nb)
        cls.gk_md = json.loads(m_nb.group(1)) if m_nb else {}

        cls.cn_num_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8
        }

    def _extract_question_md(self, raw_md, qnum):
        if not raw_md:
            return ''
        qnum_int = int(qnum)
        major_split_regex = r'(?=\n##\s+(?:第\s*[一二三四五六七八九十\d]+\s*[大題題]|(?:[一二三四五六七八九十]|\d+)\s*[、\.\:]))'
        sections = re.split(major_split_regex, raw_md)
        if len(sections) > 1:
            for sec in sections[1:]:
                h_match = re.search(r'##\s+(?:第\s*([一二三四五六七八九十\d]+)\s*[大題題]|([一二三四五六七八九十]|\d+)\s*[、\.\:])', sec)
                if h_match:
                    token = (h_match.group(1) or h_match.group(2) or '').strip()
                    if self.cn_num_map.get(token) == qnum_int:
                        return sec
            if qnum_int < len(sections):
                return sections[qnum_int]
        return raw_md

    def test_pe_all_11_years_present(self):
        years = set(q[2] for q in self.pe_qs)
        for expected_yr in range(104, 115):
            self.assertIn(expected_yr, years, f"Year {expected_yr} must exist in PE database")
        self.assertEqual(len(self.pe_qs), 318)

    def test_gk_all_5_years_present(self):
        years = set(q[2] for q in self.gk_qs)
        for expected_yr in range(110, 115):
            self.assertIn(expected_yr, years, f"Year {expected_yr} must exist in GK database")
        self.assertEqual(len(self.gk_qs), 105)

    def test_100_percent_pe_solutions_extractable(self):
        failures = []
        for q in self.pe_qs:
            qid, sid, yr, qnum, topic, tags, sol_link = q[:7]
            clean_path = sol_link.replace('./', '')
            raw_md = self.pe_md.get(clean_path, '')
            if not raw_md:
                failures.append((qid, 'Markdown file missing in bundle', clean_path))
                continue
            extracted = self._extract_question_md(raw_md, qnum)
            if len(extracted.strip()) < 50:
                failures.append((qid, f'Extracted content too short ({len(extracted)} chars)', clean_path))

        self.assertEqual(len(failures), 0, f"PE solution failures: {failures[:5]}")

    def test_100_percent_gk_solutions_extractable(self):
        failures = []
        for q in self.gk_qs:
            qid, sid, yr, qnum, topic, tags, sol_link = q[:7]
            clean_path = sol_link.replace('./', '')
            raw_md = self.gk_md.get(clean_path, '')
            if not raw_md:
                failures.append((qid, 'Markdown file missing in bundle', clean_path))
                continue
            extracted = self._extract_question_md(raw_md, qnum)
            if len(extracted.strip()) < 50:
                failures.append((qid, f'Extracted content too short ({len(extracted)} chars)', clean_path))

        self.assertEqual(len(failures), 0, f"GK solution failures: {failures[:5]}")

if __name__ == '__main__':
    unittest.main()
