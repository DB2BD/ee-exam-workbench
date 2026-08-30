# -*- coding: utf-8 -*-
"""Regression locks for the source-reconstructed PE questions."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "📝 個人題解與錯題本"


class TestReconstructedPESolutions(unittest.TestCase):
    def test_109_electronics_has_four_independent_question_records(self):
        dashboard = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
        records = json.loads(re.search(r"questions:\s*(\[.*?\]),\s*\n\s*sevenLayers:", dashboard, re.S).group(1))
        qids = [row[0] for row in records if row[0].startswith("EE-109-02-")]
        self.assertEqual(qids, ["EE-109-02-1", "EE-109-02-2", "EE-109-02-3", "EE-109-02-4"])
        self.assertEqual(records[[row[0] for row in records].index("EE-109-02-1")][5], ["BJT 偏壓", "電子學"])
        self.assertIn("Boost 轉換器", records[[row[0] for row in records].index("EE-109-02-2")][5])
        self.assertIn("MOSFET 偏壓", records[[row[0] for row in records].index("EE-109-02-4")][5])

    def test_112_math_reconstruction_keeps_official_counts_and_free_parameters(self):
        q6 = (CANONICAL / "03_工程數學" / "canonical" / "EE-112-03-6.md").read_text(encoding="utf-8")
        self.assertIn("x=(1-3t-2s,\\ t,\\ 6-4s,\\ s)^T", q6)
        self.assertIn("t,s\\in\\mathbb R", q6)
        q3 = (CANONICAL / "03_工程數學" / "canonical" / "EE-112-03-3.md").read_text(encoding="utf-8")
        self.assertIn("(1-p_A)^{50}", q3)
        self.assertIn("(1-p_B)^{53}", q3)
        self.assertIn("(1-p_C)^{60}", q3)


if __name__ == "__main__":
    unittest.main()
