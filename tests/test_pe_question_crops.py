"""Regression checks for the PE question-level crop contract."""

import json
import re
import unittest
from pathlib import Path

import fitz


WORKSPACE = Path(__file__).resolve().parents[1]
MANIFEST = WORKSPACE / "data" / "pe-question-crops.json"


class PEQuestionCropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.entries = cls.manifest["entries"]

    def test_manifest_covers_all_66_pe_papers(self):
        pdfs = sorted((WORKSPACE / "依年度分類").glob("*/*.pdf"))
        self.assertEqual(len(pdfs), 66)
        listed = {
            (entry["year"], Path(entry["pdf_path"]).name)
            for entry in self.entries
        }
        expected = {
            (int(pdf.parent.name[:3]), pdf.name)
            for pdf in pdfs
        }
        self.assertEqual(listed, expected)
        self.assertEqual(self.manifest["summary"]["papers"], 66)

    def test_every_question_has_a_nonempty_crop_and_provenance(self):
        question_ids = set()
        total = 0
        for entry in self.entries:
            self.assertGreater(entry["question_count"], 0, entry["pdf_path"])
            for question in entry["questions"]:
                total += 1
                qid = question["question_id"]
                self.assertNotIn(qid, question_ids)
                question_ids.add(qid)
                crop = WORKSPACE / question["question_crop"]
                self.assertTrue(crop.is_file(), qid)
                self.assertGreater(crop.stat().st_size, 0, qid)
                self.assertIn(question["boundary_method"], {"manual_audit", "pdf_text_sequence"})
                self.assertIn(question["boundary_confidence"], {"audited", "text_sequence"})
                pages = question["source_pages"]
                self.assertGreater(len(pages), 0, qid)
                for page_info in pages:
                    self.assertGreaterEqual(page_info["page"], 1, qid)
                    x0, y0, x1, y1 = page_info["crop_rect"]
                    self.assertGreaterEqual(x0, 0, qid)
                    self.assertGreaterEqual(y0, 0, qid)
                    self.assertGreater(x1, x0, qid)
                    self.assertGreater(y1, y0, qid)
        self.assertEqual(total, self.manifest["summary"]["questions"])

    def test_boundary_methods_are_explicit(self):
        methods = {entry["questions"][0]["boundary_method"] for entry in self.entries}
        self.assertEqual(methods, {"manual_audit", "pdf_text_sequence"})
        self.assertIn("no equal-page fallback", self.manifest["boundary_policy"])

    def test_manifest_maps_every_application_question(self):
        """Every EE-* record shown in the dashboard must have its own crop."""
        dashboard = (WORKSPACE / "dashboard-data.js").read_text(encoding="utf-8")
        records = json.loads(re.search(r"questions: (\[.*?\]),\n\n  sevenLayers", dashboard, re.S).group(1))
        app_ids = {record[0] for record in records if record[0].startswith("EE-")}
        manifest_ids = {
            question["app_question_id"]
            for entry in self.entries
            for question in entry["questions"]
            if question.get("app_question_id")
        }
        self.assertEqual(len(app_ids), 321)
        self.assertTrue(app_ids <= manifest_ids)
        for entry in self.entries:
            for question in entry["questions"]:
                if question.get("app_question_id") in app_ids:
                    self.assertTrue((WORKSPACE / question["question_crop"]).is_file())

    def test_ee_109_05_4_crop_contains_the_complete_question(self):
        """The audited crop must include Q4's heading, body, and no Q5 text."""
        entry = next(
            item for item in self.entries
            if item["year"] == 109 and item["subject"] == "電力系統"
        )
        question = entry["questions"][3]
        page_info = question["source_pages"][0]
        x0, crop_top, x1, crop_bottom = page_info["crop_rect"]

        pdf = WORKSPACE / entry["pdf_path"]
        page = fitz.open(pdf)[1]
        blocks = [
            (block[1], block[3], " ".join(block[4].split()))
            for block in page.get_text("blocks")
        ]
        q4_blocks = [
            (top, bottom)
            for top, bottom, text in blocks
            if "圖二所示電力系統" in text or "試針對發生在匯流排1" in text
        ]
        q5_blocks = [
            top for top, _bottom, text in blocks
            if text.startswith("二座發電廠")
        ]
        self.assertTrue(q4_blocks)
        self.assertTrue(q5_blocks)
        q4_top = min(top for top, _bottom in q4_blocks)
        q4_bottom = max(bottom for _top, bottom in q4_blocks)
        q5_top = min(q5_blocks)

        self.assertLessEqual(crop_top, q4_top, "Q4 heading is clipped")
        self.assertGreaterEqual(crop_bottom, q4_bottom, "Q4 body is clipped")
        self.assertLess(crop_bottom, q5_top, "Q5 heading leaked into Q4 crop")


if __name__ == "__main__":
    unittest.main()
