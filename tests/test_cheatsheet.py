# -*- coding: utf-8 -*-
"""K6 失分點速查卡 data pipeline tests."""

import copy
import json
import os
import subprocess
import unittest
from pathlib import Path

from scripts import build_cheatsheet as bc
from scripts import build_cheatsheet_sources as bcs

ROOT = Path(__file__).resolve().parent.parent


def good_doc():
    return {"subject": "01", "items": [
        {"category": "method_trap", "text": "短句", "qids": ["EE-104-01-1"]}],
        "assumption_templates": []}


class TestSources(unittest.TestCase):
    def test_covers_all_notes(self):
        doc = bcs.build()
        self.assertEqual(len(doc["notes"]), 323)
        self.assertEqual(len({n["qid"] for n in doc["notes"]}), 323)
        self.assertEqual(len(doc["condition_cards"]), 30)
        self.assertEqual(len(doc["question_doubts"]), 15)
        n = next(n for n in doc["notes"] if n["qid"] == "EE-104-01-1")
        self.assertEqual(len(n["pitfalls"]), 3)
        self.assertIn("\\Omega", n["pitfalls"][0])
        c = next(n for n in doc["notes"] if n["qid"] == "EE-105-01-3")
        self.assertTrue(c["conditions"])

    def test_sources_file_fresh(self):
        self.assertEqual(bcs.OUT.read_text(encoding="utf-8"), bcs.render(bcs.build()))


class TestValidator(unittest.TestCase):
    KNOWN = {"EE-104-01-1", "EE-105-01-3"}

    def errs(self, doc):
        return bc.validate({"01": doc}, self.KNOWN)

    def test_good(self):
        self.assertEqual(self.errs(good_doc()), [])

    def test_unknown_qid(self):
        d = good_doc()
        d["items"][0]["qids"] = ["EE-999-01-9"]
        self.assertTrue(any("unknown qid" in e for e in self.errs(d)))

    def test_too_many_items(self):
        d = good_doc()
        d["items"] = d["items"] * (bc.MAX_ITEMS + 1)
        self.assertTrue(any("exceeds limit" in e for e in self.errs(d)))

    def test_examples_not_counted(self):
        d = good_doc()
        ex = dict(d["items"][0], example=True)
        d["items"] = d["items"] + [ex] * bc.MAX_ITEMS
        self.assertEqual(self.errs(d), [])

    def test_overlong_text_and_bad_category(self):
        d = good_doc()
        d["items"][0]["text"] = "字" * (bc.MAX_TEXT + 1)
        self.assertTrue(any("text length" in e for e in self.errs(d)))
        d = good_doc()
        d["items"][0]["category"] = "nope"
        self.assertTrue(any("category" in e for e in self.errs(d)))

    def test_too_many_templates(self):
        d = good_doc()
        t = {"situation": "缺條件", "how_to_write": "先寫假設", "qids": ["EE-104-01-1"]}
        d["assumption_templates"] = [t] * (bc.MAX_TEMPLATES + 1)
        self.assertTrue(any("assumption_templates" in e for e in self.errs(d)))

    def test_real_data_valid(self):
        self.assertEqual(bc.validate(bc.load_files(), bc.dashboard_qids()), [])

    def test_example_skipped_in_output(self):
        docs = {"01": good_doc()}
        docs["01"]["items"].append({"category": "calc_check", "text": "範例專用字串", "qids": ["EE-104-01-1"], "example": True})
        md, js, errors = bc.build(docs, self.KNOWN)
        self.assertEqual(errors, [])
        self.assertIn("短句", md)
        self.assertIn("EE-104-01-1", md)
        self.assertNotIn("範例專用字串", md + js)


class TestGeneratedFresh(unittest.TestCase):
    def test_md_and_js_fresh(self):
        md, js, errors = bc.build()
        self.assertEqual(errors, [])
        self.assertEqual(bc.OUT_MD.read_text(encoding="utf-8"), md)
        self.assertEqual(bc.OUT_JS.read_text(encoding="utf-8"), js)

    def test_bundle_order(self):
        text = (ROOT / "scripts" / "build_workbench.py").read_text(encoding="utf-8")
        self.assertLess(text.index("cheatsheet.generated.js"), text.index("passbookGenerator.js"))


class TestPassbookSection(unittest.TestCase):
    def run_node(self, data_expr):
        script = f"""
        const {{ renderCheatsheetSectionHtml }} = require({json.dumps(str(ROOT / 'src/components/passbookGenerator.js'))});
        console.log(JSON.stringify(renderCheatsheetSectionHtml({data_expr})));
        """
        proc = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_empty(self):
        self.assertEqual(self.run_node("null"), "")
        self.assertEqual(self.run_node("{subjects: [], assumption_templates: []}"), "")

    def test_present_and_escaped(self):
        data = ('{subjects:[{id:"01",name:"電路學",categories:[{id:"method_trap",label:"方法選擇陷阱",'
                'items:[{text:"<img src=x onerror=1>",qids:["EE-104-01-1"]}]}]}],'
                'assumption_templates:[{subject_name:"電路學",situation:"缺 <b>",how_to_write:"寫假設",qids:["EE-105-01-3"]}]}')
        html = self.run_node(data)
        self.assertIn("參、失分點速查卡", html)
        self.assertIn("&lt;img src=x onerror=1&gt;", html)
        self.assertNotIn("<img", html)
        self.assertNotIn("<b>", html)
        self.assertIn("缺條件時怎麼寫假設", html)
        self.assertIn("EE-105-01-3", html)

    def test_bundled_data_variable(self):
        script = f"""
        const vm = require('vm'), fs = require('fs');
        const ctx = vm.createContext({{}});
        vm.runInContext(fs.readFileSync({json.dumps(str(bc.OUT_JS))}, 'utf8') + '; this.n = CHEATSHEET_DATA.subjects.length;', ctx);
        console.log(ctx.n);
        """
        proc = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertGreaterEqual(int(proc.stdout.strip()), 0)


if __name__ == "__main__":
    unittest.main()
