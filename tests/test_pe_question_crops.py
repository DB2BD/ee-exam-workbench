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
                self.assertIn(question["boundary_method"], {"manual_audit", "pdf_text_sequence", "pdf_ink_heading"})
                self.assertIn(question["boundary_confidence"], {"audited", "text_sequence", "ink_heading"})
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
        self.assertEqual(methods, {"manual_audit", "pdf_text_sequence", "pdf_ink_heading"})
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
        self.assertEqual(len(app_ids), 323)
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
        # Line-level positions: PDF blocks merge the 代號 header into Q4's first line.
        q4_blocks = [
            (rect.y0, rect.y1)
            for needle in ("圖二所示電力系統", "試針對發生在匯流排")
            for rect in page.search_for(needle)
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


    def _question(self, year, subject, number):
        entry = next(
            item for item in self.entries
            if item["year"] == year and item["subject"] == subject
        )
        return entry, entry["questions"][number - 1]

    def test_page_chrome_is_masked_in_every_crop(self):
        """Exam headers, page numbers and 「請接背面」 never appear in a crop."""
        strong = re.compile(r"代號：|頁次：|請接背面|請接第|全一張|專門職業及技術人員")
        for entry in self.entries:
            doc = fitz.open(WORKSPACE / entry["pdf_path"])
            for question in entry["questions"]:
                for page_info in question["source_pages"]:
                    page = doc[page_info["page"] - 1]
                    crop = fitz.Rect(page_info["crop_rect"])
                    masks = [fitz.Rect(rect) for rect in page_info.get("masked_rects", [])]
                    for block in page.get_text("dict")["blocks"]:
                        for line in block.get("lines", []):
                            text = "".join(span["text"] for span in line["spans"])
                            bbox = fitz.Rect(line["bbox"])
                            if not strong.search(text) or not bbox.intersects(crop):
                                continue
                            visible = bbox & crop
                            self.assertTrue(
                                any(mask.contains(visible) for mask in masks),
                                f"{question['app_question_id']} p{page_info['page']}: {text.strip()[:20]}",
                            )
            doc.close()

    def test_every_ink_band_is_in_exactly_one_crop(self):
        """No question content is cut off (C1) or shared with a neighbour (C2).

        Rendered ink is used instead of text lines because captions, matrix
        brackets and diagrams are mostly vector graphics.
        """
        import sys

        sys.path.insert(0, str(WORKSPACE / "scripts"))
        import crop_pe_questions as crops

        problems = []
        for entry in self.entries:
            doc = fitz.open(WORKSPACE / entry["pdf_path"])
            first = min(q["source_pages"][0]["page"] for q in entry["questions"])
            first_top = min(
                q["source_pages"][0]["crop_rect"][1]
                for q in entry["questions"] if q["source_pages"][0]["page"] == first
            )
            for page_number in range(first, doc.page_count + 1):
                page = doc[page_number - 1]
                spans = [
                    (question["app_question_id"], info["crop_rect"][1], info["crop_rect"][3])
                    for question in entry["questions"]
                    for info in question["source_pages"]
                    if info["page"] == page_number
                ]
                for y0, y1 in crops.ink_bands(page):
                    if page_number == first and y1 <= first_top:
                        continue  # paper instructions above question 1
                    holders = [qid for qid, top, bottom in spans if top - 0.5 <= y0 and y1 <= bottom + 0.5]
                    if len(holders) != 1:
                        problems.append((entry["year"], entry["subject"], page_number, round(y0, 1), round(y1, 1), holders))
            doc.close()
        self.assertEqual(problems, [])

    def test_continuation_pages_carry_real_question_content(self):
        """A page is stitched only if it holds question content besides chrome."""
        _entry, q02 = self._question(104, "電子學（包括電力電子學）", 2)
        self.assertEqual([page["page"] for page in q02["source_pages"]], [1])
        _entry, q04 = self._question(108, "電力系統", 4)
        self.assertEqual([page["page"] for page in q04["source_pages"]], [2])
        # 106 papers split 「等／類／科」 from 「別：／科：／目：」 into separate lines.
        _entry, q02_106 = self._question(106, "電子學（包括電力電子學）", 2)
        self.assertEqual([page["page"] for page in q02_106["source_pages"]], [1])

    def test_112_machinery_q2_does_not_swallow_q3(self):
        """Damaged-text papers use detected headings, not stale manual offsets."""
        entry, q02 = self._question(112, "電機機械", 2)
        _entry, q03 = self._question(112, "電機機械", 3)
        self.assertEqual(q02["boundary_method"], "pdf_ink_heading")
        self.assertEqual([page["page"] for page in q02["source_pages"]], [1])
        page = fitz.open(WORKSPACE / entry["pdf_path"])[1]
        q3_top = page.search_for("額定25")[0].y0
        first = q03["source_pages"][0]
        self.assertEqual(first["page"], 2)
        self.assertLessEqual(first["crop_rect"][1], q3_top)

    def test_114_distribution_q5_is_not_merged_into_q4(self):
        entry, q04 = self._question(114, "工業配電", 4)
        _entry, q05 = self._question(114, "工業配電", 5)
        page = fitz.open(WORKSPACE / entry["pdf_path"])[1]
        q5_top = min(
            block[1] for block in page.get_text("blocks")
            if "一加工廠的負載特性" in " ".join(block[4].split())
        )
        self.assertLess(q04["source_pages"][-1]["crop_rect"][3], q5_top)
        self.assertLessEqual(q05["source_pages"][0]["crop_rect"][1], q5_top)

    def test_crops_have_no_large_blank_band(self):
        """Page-bottom whitespace is trimmed per page before stitching."""
        from PIL import Image

        limit = 260  # px at 180 dpi (~104 pt); larger gaps are page leftovers
        offenders = []
        for entry in self.entries:
            for question in entry["questions"]:
                image = Image.open(WORKSPACE / question["question_crop"]).convert("L")
                width, height = image.size
                pixels = image.load()
                run = longest = 0
                for y in range(height):
                    if all(pixels[x, y] >= 245 for x in range(0, width, 3)):
                        run += 1
                        longest = max(longest, run)
                    else:
                        run = 0
                if longest > limit and question["app_question_id"] not in BLANK_BAND_ALLOWED:
                    offenders.append((question["app_question_id"], longest))
        self.assertEqual(offenders, [])


# Crops whose interior gap is part of the official layout (verified visually).
BLANK_BAND_ALLOWED: set[str] = set()


if __name__ == "__main__":
    unittest.main()
