# -*- coding: utf-8 -*-
"""Study-plan tiers, practice weights and score factors (WP2)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_target_allocation as bta  # noqa: E402

GENERATED = ROOT / "src" / "data" / "targetAllocation.generated.js"
DOMAIN = ROOT / "src" / "domain" / "studyPlan.js"


def run_node(expression):
    sources = [GENERATED, DOMAIN]
    script = (
        "const vm = require('vm');\nconst context = {};\nvm.createContext(context);\n"
        + "".join(f"vm.runInContext({json.dumps(p.read_text(encoding='utf-8'))}, context);\n" for p in sources)
        + f"process.stdout.write(JSON.stringify(vm.runInContext({json.dumps(expression)}, context)));\n"
    )
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


class TestStudyPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = bta.build()

    def test_generated_is_fresh(self):
        self.assertEqual(GENERATED.read_text(encoding="utf-8"), bta.render_js(self.data))

    def test_all_323_tiered(self):
        tiers = self.data["questionTiers"]
        self.assertEqual(len(tiers), 323)
        self.assertTrue(all(t["tier"] in ("main", "basic") for t in tiers.values()))

    def test_targets(self):
        s = self.data["subjects"]
        self.assertEqual({k: v["target"] for k, v in s.items()},
                         {"01": 75, "04": 75, "06": 60, "05": 55, "03": 60, "02": 55})
        self.assertEqual(sum(v["target"] for v in s.values()), 380)
        self.assertEqual({k: v["role"] for k, v in s.items()},
                         {"01": "high", "04": "high", "06": "combined", "05": "combined",
                          "03": "basic", "02": "basic"})

    def test_unknown_chapter_fails(self):
        cfg = json.loads(bta.SOURCE.read_text(encoding="utf-8"))
        cfg["subjects"]["01"]["mainChapters"].append({"id": "ct-nope"})
        orig = bta.SOURCE.read_text
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "x.json"
                p.write_text(json.dumps(cfg), encoding="utf-8")
                old = bta.SOURCE
                bta.SOURCE = p
                try:
                    with self.assertRaises(SystemExit):
                        bta.build()
                finally:
                    bta.SOURCE = old
        finally:
            del orig

    def test_spot_checks(self):
        t = self.data["questionTiers"]
        self.assertEqual(t["EE-114-01-3"]["tier"], "main")
        bjt = [q for q, v in t.items() if v["chapter"] == "el-bjt-bias-small-signal"]
        self.assertTrue(bjt)
        self.assertTrue(all(t[q]["tier"] == "main" for q in bjt))
        promoted = ("el-mosfet-bias-small-signal", "em-vector-analysis", "em-laplace-transform")
        self.assertTrue(all(v["tier"] == "main" for v in t.values() if v["chapter"] in promoted))
        prob = [q for q, v in t.items() if v["chapter"] == "em-probability-statistics"]
        self.assertTrue(prob)
        self.assertTrue(all(t[q]["tier"] == "main" for q in prob))

    def test_overrides(self):
        t = self.data["questionTiers"]
        for q in ("EE-104-06-3", "EE-108-06-2", "EE-110-06-4", "EE-113-06-3", "EE-114-06-2"):
            self.assertEqual(t[q]["tier"], "main", q)
            self.assertTrue(t[q].get("override"), q)
        for q in ("EE-104-06-5", "EE-105-06-5", "EE-106-06-5"):  # harmonics stay basic
            self.assertEqual(t[q]["tier"], "basic", q)
        self.assertIn("dist-harmonics-mitigation", self.data["subjects"]["06"]["basicChapters"])
        cfg = json.loads(bta.SOURCE.read_text(encoding="utf-8"))
        import tempfile
        for bad in ({"EE-999-06-9": "main"}, {"EE-104-06-3": "huge"}):
            cfg["questionOverrides"] = bad
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "x.json"
                p.write_text(json.dumps(cfg), encoding="utf-8")
                old, bta.SOURCE = bta.SOURCE, p
                try:
                    with self.assertRaises(SystemExit):
                        bta.build()
                finally:
                    bta.SOURCE = old

    def test_js_tier_and_weights(self):
        t = self.data["questionTiers"]

        def first(subject, chapter):
            return next(q for q, v in t.items() if v["subject"] == subject and v["chapter"] == chapter)

        cases = {
            first("01", "ct-second-order-rlc"): ("main", 3),          # high main
            first("01", "ct-two-port"): ("basic", 1),                 # high basic
            first("06", "dist-short-circuit-capacity"): ("main", 3),  # shared
            first("05", "ps-transient-stability-equal-area"): ("main", 3),
            first("05", "ps-economic-dispatch"): ("basic", 1),        # combined non-main
            first("03", "em-probability-statistics"): ("main", 2),    # basic-subject main
            first("02", "el-diode-rectifier"): ("main", 2),
            first("02", "el-bjt-bias-small-signal"): ("main", 2),    # v1.3.6 promoted to main
            first("02", "el-mosfet-bias-small-signal"): ("main", 2),
            first("03", "em-laplace-transform"): ("main", 2),
            first("02", "el-active-filter"): ("basic", 0.5),
            first("03", "em-vector-analysis"): ("main", 2),
        }
        out = run_node(json.dumps(list(cases)) + ".map(q=>[studyTierFor(q),practiceWeightFor(q)])")
        self.assertEqual([tuple(x) for x in out], list(cases.values()))

    def test_gk_and_unknown(self):
        out = run_node("['GK-114-01-1','EE-999-01-1',null,undefined].map(q=>[studyTierFor(q),practiceWeightFor(q)])")
        self.assertEqual(out, [[None, 0]] * 4)

    def test_roles_targets_constants(self):
        out = run_node("[studyRoleFor('01'),studyRoleFor('05'),studyRoleFor('02'),studyRoleFor('99'),"
                       "targetFor('04'),targetFor('02'),targetFor('99'),TOTAL_TARGET,PASS_LINE]")
        self.assertEqual(out, ["high", "combined", "basic", None, 75, 55, None, 380, 360])

    def test_score_factors(self):
        out = run_node("[['main','o'],['main','tri'],['main','x'],['basic','o'],['basic','tri'],['basic','x']]"
                       ".map(a=>scoreFactorFor(a[0],a[1]))")
        self.assertEqual(out, [1, 0.5, 0, 0.5, 0.25, 0])

    def test_all_weights_match_table(self):
        t = self.data["questionTiers"]
        out = run_node(json.dumps(list(t)) + ".map(q=>practiceWeightFor(q))")
        roles = {k: v["role"] for k, v in self.data["subjects"].items()}
        for (qid, v), w in zip(t.items(), out):
            role = roles[v["subject"]]
            if v["tier"] == "main":
                exp = 2 if role == "basic" else 3
            else:
                exp = 0.5 if role == "basic" else 1
            self.assertEqual(w, exp, qid)


if __name__ == "__main__":
    unittest.main()
