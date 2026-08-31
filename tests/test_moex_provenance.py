# -*- coding: utf-8 -*-
"""Tests for the official MOEX source and question-crop contract."""

import json
import pathlib
import unittest


WORKSPACE = pathlib.Path(__file__).resolve().parents[1]


class TestMoexProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((WORKSPACE / "data/moex-national-exams.json").read_text(encoding="utf-8"))
        cls.crops = json.loads((WORKSPACE / "data/moex-question-crops.json").read_text(encoding="utf-8"))

    def test_source_manifest_has_explicit_availability(self):
        self.assertEqual(len(self.source["entries"]), 25)
        self.assertEqual(sum(e["status"] == "downloaded" for e in self.source["entries"]), 23)
        self.assertEqual(sum(e["status"] != "downloaded" for e in self.source["entries"]), 2)
        for entry in self.source["entries"]:
            if entry["status"] == "downloaded":
                self.assertTrue(entry["official_url"].startswith("https://wwwq.moex.gov.tw/"))
                self.assertTrue((WORKSPACE / entry["target_path"]).read_bytes().startswith(b"%PDF-"))
                self.assertEqual(len(entry["sha256"]), 64)
            else:
                self.assertIn("reason", entry)

    def test_every_downloaded_paper_has_question_and_figure_assets(self):
        manifest_count = sum(
            entry.get("question_count", len(entry.get("questions", [])))
            for entry in self.crops["entries"]
        )
        self.assertEqual(self.crops["summary"]["questions"], manifest_count)
        crop_by_key = {(e["year"], e["subject"]): e for e in self.crops["entries"]}
        ids = set()
        for entry in self.source["entries"]:
            crop_entry = crop_by_key[(entry["year"], entry["subject"])]
            if entry["status"] != "downloaded":
                self.assertEqual(crop_entry["question_count"], 0)
                continue
            self.assertGreater(crop_entry["question_count"], 0)
            for question in crop_entry["questions"]:
                self.assertNotIn(question["question_id"], ids)
                ids.add(question["question_id"])
                q_path = WORKSPACE / question["question_crop"]
                self.assertTrue(q_path.exists() and q_path.stat().st_size > 0)
                for figure in question["figure_crops"]:
                    f_path = WORKSPACE / figure
                    self.assertTrue(f_path.exists() and f_path.stat().st_size > 0)
        self.assertEqual(len(ids), manifest_count)

    def test_engineering_math_mc_manifest_mapping(self):
        records = [
            question
            for entry in self.crops["entries"]
            if entry["subject"] == "工程數學" and entry["year"] in {110, 111, 112}
            for question in entry.get("questions", [])
            if question.get("question_id", "").startswith(
                f"GK-{entry['year']}-工程數學-MC"
            )
        ]
        self.assertEqual(len(records), 60)
        for year in (110, 111, 112):
            yearly = [record for record in records if record["question_id"].startswith(f"GK-{year}-")]
            self.assertEqual(len(yearly), 20)
            self.assertEqual(
                {record["app_question_number"] for record in yearly},
                set(range(101, 121)),
            )
        self.assertEqual(
            {record["question_id"].rsplit("-", 1)[-1] for record in records},
            {f"MC{index:02d}" for index in range(1, 21)},
        )
        for record in records:
            self.assertRegex(record["question_id"], r"^GK-(110|111|112)-工程數學-MC\d{2}$")

    def test_engineering_math_matrix_crops_keep_leading_rows(self):
        """Regression guard for matrix rows placed above the question number."""
        by_id = {
            question["question_id"]: question
            for entry in self.crops["entries"]
            for question in entry.get("questions", [])
        }
        # These rows sit 12–18 pt above the Arabic number in the source PDF;
        # a crop beginning at the number silently changed a 3x3 matrix to 2x3.
        expected = {
            "GK-110-工程數學-MC03": 726.2,
            "GK-110-工程數學-MC07": 588.1,
            "GK-111-工程數學-MC02": 426.6,
        }
        for qid, top_limit in expected.items():
            first_page = by_id[qid]["source_pages"][0]
            self.assertLessEqual(first_page["crop_rect"][1], top_limit, qid)

    def test_compiled_records_keep_crop_provenance(self):
        data_text = (WORKSPACE / "national-exams-data.js").read_text(encoding="utf-8")
        match = __import__("re").search(r"questions:\s*(\[[\s\S]+?\])\s*\}\;", data_text)
        records = json.loads(match.group(1))
        gk_records = [record for record in records if record[0].startswith("GK-")]
        manifest_count = sum(
            entry.get("question_count", len(entry.get("questions", [])))
            for entry in self.crops["entries"]
        )
        self.assertEqual(len(gk_records), manifest_count)
        self.assertTrue(all(len(record) >= 18 for record in gk_records))
        self.assertTrue(all(record[14] for record in gk_records))
        self.assertTrue(all(isinstance(record[15], list) for record in gk_records))
        q1 = next(record for record in gk_records if record[0] == "GK-114-01-1")
        self.assertEqual(q1[9], "verified")
        self.assertTrue(q1[6])


if __name__ == "__main__":
    unittest.main()
