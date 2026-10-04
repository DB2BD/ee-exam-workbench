# -*- coding: utf-8 -*-
"""Keep the EE-114-01-3 taxonomy evidence aligned across public data seams."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QID = "EE-114-01-3"
CHAPTER = "ct-second-order-rlc"
QUESTION_TITLE = "EE-114-01-3 二階 RLC 暫態題"
QUESTION_NODE_ID = "q-ee-114-01-3"
QUESTION_REVISION = "qid-EE-114-01-3-v2"


def read_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def read_dashboard_taxonomy():
    source = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
    match = re.search(
        r"const QUESTION_TAXONOMY_MAP\s*=\s*(\{.*?\});\nconst SOLUTION_REVIEW_METADATA",
        source,
        re.DOTALL,
    )
    if not match:
        raise AssertionError("dashboard-data.js is missing QUESTION_TAXONOMY_MAP")
    return json.loads(match.group(1))


class TestEE114RlcTaxonomyConsistency(unittest.TestCase):
    def test_second_order_rlc_evidence_is_consistent_across_public_seams(self):
        golden = read_json("data/taxonomy/golden-set.json")
        taxonomy = read_dashboard_taxonomy()
        graph_nodes = {
            node["nodeId"]: node
            for node in read_json("data/knowledge/nodes.json")["nodes"]
        }
        graph_links = read_json("data/knowledge/question-links.json")["links"]

        positive_chapters = [
            group["chapterId"]
            for group in golden["positiveCases"]
            if QID in group["questionIds"]
        ]
        with self.subTest("human-reviewed golden set"):
            self.assertEqual(positive_chapters, [CHAPTER])

        positive_cases = {
            group["chapterId"]: group["questionIds"]
            for group in golden["positiveCases"]
        }
        exceptions = golden["coverageExceptions"]
        with self.subTest("first- and second-order sparse coverage is accurate"):
            self.assertEqual(len(positive_cases["ct-first-order-rc-rl"]), 2)
            self.assertIn("兩題", exceptions["ct-first-order-rc-rl"])
            # 2026-10-04 stem re-audit moved three RLC transient questions here.
            self.assertEqual(len(positive_cases[CHAPTER]), 4)
            self.assertIn("四題", exceptions[CHAPTER])

        with self.subTest("dashboard primary chapter remains stable"):
            self.assertEqual(taxonomy[QID]["primaryChapter"], CHAPTER)

        with self.subTest("canonical graph question link uses the RLC node"):
            link = graph_links[f"PE:{QID}"]
            self.assertEqual(link["qid"], QID)
            self.assertEqual(link["nodeIds"], [CHAPTER])

        question_node = graph_nodes[QUESTION_NODE_ID]
        with self.subTest("canonical graph question title names second-order RLC"):
            self.assertEqual(question_node["title"], QUESTION_TITLE)

        with self.subTest("canonical graph question revision records the correction"):
            self.assertEqual(question_node["nodeRevisionHash"], QUESTION_REVISION)

        versions = [
            read_json(f"data/taxonomy/{name}")["taxonomyVersion"]
            for name in ("golden-set.json", "alias-map.json", "overrides.json")
        ]
        with self.subTest("taxonomy version metadata stays synchronized"):
            self.assertEqual(len(set(versions)), 1)
            self.assertNotEqual(versions[0], "2026.09.25")


if __name__ == "__main__":
    unittest.main()
