import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("bqp", ROOT / "scripts" / "build_question_points.py")
bqp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bqp)


class QuestionPointsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids, cls.res, cls.src, cls.errors = bqp.build()
        cls.data = json.loads(bqp.OUT_JSON.read_text(encoding="utf-8"))

    def test_build_has_no_errors(self):
        self.assertEqual(self.errors, [])

    def test_generated_files_fresh(self):
        ordered = {q: self.res[q] for q in self.ids}
        self.assertEqual(self.data, ordered)
        js = bqp.OUT_JS.read_text(encoding="utf-8")
        self.assertIn("const QUESTION_POINTS = ", js)
        body = js.split("const QUESTION_POINTS = ", 1)[1].rsplit(";", 1)[0]
        self.assertEqual(json.loads(body), ordered)

    def test_323_entries(self):
        self.assertEqual(len(self.data), 323)

    def test_every_paper_sums_to_100(self):
        paper = {}
        for qid, r in self.data.items():
            _, y, s, _ = qid.split("-")
            paper[(y, s)] = paper.get((y, s), 0) + r["total"]
        self.assertEqual(len(paper), 66)
        self.assertEqual({k: v for k, v in paper.items() if v != 100}, {})

    def test_parts_consistent(self):
        for qid, r in self.data.items():
            if r["parts"]:
                self.assertEqual(sum(p["points"] for p in r["parts"]), r["total"], qid)

    def test_spot_checks(self):
        self.assertEqual(self.data["EE-114-03-1"]["total"], 15)
        self.assertEqual(self.data["EE-114-03-5"]["total"], 30)
        self.assertEqual([p["points"] for p in self.data["EE-114-03-5"]["parts"]], [20, 10])
        self.assertEqual([p["points"] for p in self.data["EE-114-01-1"]["parts"]], [5, 15])
        # header-only paper (score in "每小題 10 分，共 20 分")
        self.assertEqual(self.data["EE-114-04-1"]["total"], 20)
        self.assertEqual([p["points"] for p in self.data["EE-114-04-1"]["parts"]], [10, 10])
        # whole-question only
        self.assertEqual(self.data["EE-114-01-4"], {"total": 20, "parts": []})

    def test_overrides_respected(self):
        orig = bqp.OVERRIDES
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "o.json"
            p.write_text(json.dumps({"EE-114-01-1": {"total": 20, "parts": [
                {"label": "（一）", "points": 20}], "reason": "test"}}), encoding="utf-8")
            bqp.OVERRIDES = p
            try:
                ids, res, src, errors = bqp.build()
            finally:
                bqp.OVERRIDES = orig
        self.assertEqual(src["EE-114-01-1"], "override")
        self.assertEqual(res["EE-114-01-1"]["parts"], [{"label": "（一）", "points": 20}])
        self.assertEqual(errors, [])

    def test_bad_override_fails_validation(self):
        orig = bqp.OVERRIDES
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "o.json"
            p.write_text(json.dumps({"EE-114-01-1": {"total": 30}}), encoding="utf-8")
            bqp.OVERRIDES = p
            try:
                _, _, _, errors = bqp.build()
            finally:
                bqp.OVERRIDES = orig
        self.assertTrue(any("totals" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
