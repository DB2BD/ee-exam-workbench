# -*- coding: utf-8 -*-
"""data/taxonomy/question-types.json (題型 layer) and chapter-corrections.json: coverage, references, consistency."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = json.loads((ROOT / "data" / "taxonomy" / "question-types.json").read_text(encoding="utf-8"))
CORRECTIONS = json.loads((ROOT / "data" / "taxonomy" / "chapter-corrections.json").read_text(encoding="utf-8"))["corrections"]
DAG_IDS = set(re.findall(r"^  '([a-z0-9-]+)': \{", (ROOT / "src" / "data" / "knowledge-dag.js").read_text(encoding="utf-8"), re.M))
DASH = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
TAX = json.loads(DASH[DASH.index("QUESTION_TAXONOMY_MAP = ") + 24:DASH.index("\n};", DASH.index("QUESTION_TAXONOMY_MAP = ")) + 2])
NOTES = sorted(p.stem for p in ROOT.glob("02_題解/技師題解/0*/canonical/EE-*.md"))


class TestQuestionTypes(unittest.TestCase):
    def test_every_pe_question_has_one_primary_type(self):
        self.assertEqual(sorted(TYPES["questions"]), NOTES)
        for qid, q in TYPES["questions"].items():
            self.assertIn(q["type"], TYPES["types"], qid)
            self.assertLessEqual(len(q.get("secondary", [])), 2, qid)
            for s in q.get("secondary", []):
                self.assertIn(s, TYPES["types"], qid)

    def test_type_fields_and_references(self):
        types = TYPES["types"]
        for tid, t in types.items():
            self.assertRegex(tid, r"^(ct|el|em|emach|ps|dist)-[a-z0-9-]+$")
            self.assertIn(t["chapter"], DAG_IDS, tid)
            self.assertTrue(t["chapter"].startswith(tid.split("-")[0] + "-"), tid)
            self.assertTrue(2 <= len(t["name"]) <= 16, tid)
            self.assertTrue(2 <= len(t["cues"]) <= 4, tid)
            self.assertTrue(t["firstMove"].strip(), tid)
            self.assertTrue(1 <= len(t["prereqs"]) <= 4, tid)
            for p in t["prereqs"]:
                self.assertTrue(p in types or p in DAG_IDS, (tid, p))
            self.assertTrue(1 <= len(t["confusers"]) <= 3, tid)
            for c in t["confusers"]:
                self.assertIn(c, types, (tid, c))
                self.assertNotEqual(c, tid)

    def test_type_chapter_matches_question_chapter(self):
        for qid, q in TYPES["questions"].items():
            self.assertEqual(TYPES["types"][q["type"]]["chapter"], q["chapter"], qid)
            built = TAX[qid]
            corrected = {c["qid"]: c["to"] for c in CORRECTIONS}
            if qid in corrected:
                self.assertEqual(q["chapter"], corrected[qid], qid)
            elif built["source"] != "manual-topic-confirmed":
                self.assertEqual(built["primaryChapter"], q["chapter"], qid)

    def test_corrections_are_pending_for_statistics_but_in_graph_links(self):
        links = json.loads((ROOT / "data" / "knowledge" / "question-links.json").read_text(encoding="utf-8"))["links"]
        self.assertTrue(CORRECTIONS)
        for c in CORRECTIONS:
            self.assertIn(c["to"], DAG_IDS)
            self.assertTrue(c["reason"].strip())
            # statistics (anchors, mastery) keep the old chapter until the learner decides
            self.assertEqual(TAX[c["qid"]]["primaryChapter"], c["from"], c["qid"])
            self.assertNotEqual(TAX[c["qid"]]["source"], "manual-topic-confirmed", c["qid"])
            # the 觀念相依 tracer already uses the corrected chapter
            self.assertEqual(links["PE:" + c["qid"]]["nodeIds"][0], c["to"], c["qid"])


if __name__ == "__main__":
    unittest.main()
