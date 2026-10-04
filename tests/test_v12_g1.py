# -*- coding: utf-8 -*-
"""v1.2 QA group G1: modal nesting, reserved mock/blind questions, mock scoring, passbook, theme."""

import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOID = {"meta", "link", "br", "img", "input", "hr", "source", "area", "base", "col", "embed", "param", "track", "wbr"}


class AncestorParser(HTMLParser):
    """Records, for each element id, the ids of all its ancestors."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.ancestors = {}
        self.skip = None

    def handle_starttag(self, tag, attrs):
        if self.skip:
            return
        if tag in ("script", "style"):
            self.skip = tag
            return
        d = dict(attrs)
        if d.get("id"):
            self.ancestors[d["id"]] = [i for _, i in self.stack if i]
        if tag not in VOID:
            self.stack.append((tag, d.get("id")))

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip:
                self.skip = None
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def run_node(files, expression, storage=None, globals_js=""):
    sources = "\n".join((ROOT / f).read_text(encoding="utf-8") for f in files)
    script = f"""
const vm = require('vm');
const data = {json.dumps(storage or {}, ensure_ascii=False)};
const localStorage = {{ getItem: k => (k in data ? data[k] : null), setItem: (k, v) => {{ data[k] = String(v); }}, removeItem: k => {{ delete data[k]; }} }};
const context = {{ console, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(globals_js + chr(10) + sources + chr(10) + 'globalThis.__r = (' + expression + ');', ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(context.__r));
"""
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


SCHEDULE = """
var DAILY_SCHEDULE = { tasks: {
  'CORE-01': { kind: 'core', qids: ['EE-114-01-3'] },
  'MIX-01': { kind: 'mix', qids: ['EE-108-01-2'] },
  'MOCK114-01': { kind: 'mock114', qids: ['EE-114-01-1', 'EE-114-01-2', 'EE-114-01-3'] },
  'BLIND108-01': { kind: 'blind108', qids: ['EE-108-01-1', 'EE-108-01-2'] } } };
"""
POOL = ["EE-114-01-1", "EE-114-01-2", "EE-114-01-3", "EE-108-01-1", "EE-108-01-2", "EE-110-01-1", "EE-110-01-2", "EE-110-01-3"]
POOL_JS = json.dumps([[q] for q in POOL])


class TestBackupModalNesting(unittest.TestCase):
    def test_modals_not_inside_solution_modal(self):
        parser = AncestorParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        for modal in ("backup-modal", "manual-label-modal"):
            self.assertIn(modal, parser.ancestors)
            self.assertNotIn("solution-modal", parser.ancestors[modal], modal)
        self.assertIn("solution-modal", parser.ancestors)

    def test_more_menu_title_renamed(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("考前速查手冊（列印）", html)
        self.assertNotIn("15天奪榜本", html)


class TestReservedQuestions(unittest.TestCase):
    FILES = ["src/state/practiceStore.js"]

    def locked(self, completed=None):
        storage = {"EE_EXAM_TODAY_TASK_V1": json.dumps({"completed": completed or {}, "active": None})}
        return sorted(run_node(self.FILES, "Array.from(practiceLockedQids())", storage, SCHEDULE))

    def test_locked_until_completed_except_core_mix(self):
        # 114-01-3 is also in CORE-01 and 108-01-2 in MIX-01, so they stay practisable.
        self.assertEqual(self.locked(), ["EE-108-01-1", "EE-114-01-1", "EE-114-01-2"])
        self.assertEqual(self.locked({"MOCK114-01": "2026-10-20T00:00:00Z"}), ["EE-108-01-1"])

    def test_whole_paper_is_reserved(self):
        sched = "var DAILY_SCHEDULE = { tasks: { 'MOCK114-06': { kind: 'mock114', qids: ['EE-114-06-1', 'EE-114-06-5'] } } };"
        out = run_node(self.FILES, "['EE-114-06-1','EE-114-06-3','EE-114-05-3'].map(q => practiceLockedQids().has(q))", {}, sched)
        self.assertEqual(out, [True, True, False])

    def test_corrupt_storage_is_tolerated(self):
        out = run_node(self.FILES, "Array.from(practiceLockedQids()).length", {"EE_EXAM_TODAY_TASK_V1": "{bad"}, SCHEDULE)
        self.assertEqual(out, 3)

    def test_queues_never_draw_locked_questions(self):
        expr = f"""(() => {{
          const qs = {POOL_JS};
          const bad = new Set(['EE-108-01-1', 'EE-114-01-1', 'EE-114-01-2']);
          let leaked = 0;
          for (let i = 0; i < 200; i++) {{
            const plain = createDailyPracticeQueue(qs, {{ count: 3 }});
            const weighted = createWeightedPracticeQueue(qs, {{ count: 3, weightOf: () => 1 }});
            plain.concat(weighted).forEach(q => {{ if (bad.has(q)) leaked += 1; }});
          }}
          return {{ leaked, size: createDailyPracticeQueue(qs, {{ count: 8 }}).length }};
        }})()"""
        out = run_node(self.FILES, expr, {}, SCHEDULE)
        self.assertEqual(out["leaked"], 0)
        self.assertEqual(out["size"], 5)

    def test_completed_mock_is_released(self):
        storage = {"EE_EXAM_TODAY_TASK_V1": json.dumps({"completed": {"MOCK114-01": "x", "BLIND108-01": "y"}})}
        out = run_node(self.FILES, f"createDailyPracticeQueue({POOL_JS}, {{ count: 8 }}).length", storage, SCHEDULE)
        self.assertEqual(out, 8)


class TestPassbook(unittest.TestCase):
    FILES = ["src/state/practiceStore.js", "src/components/passbookGenerator.js"]

    def test_top15_excludes_reserved(self):
        expr = f"""(() => {{
          const qs = {POOL_JS}.map(q => [q[0], '01', Number(q[0].split('-')[1]), 1, 'topic', [], '', '', 3]);
          const top = generatePassbookData(qs, {{}}, {{}}, {{}}).topAnchorQuestions.map(i => i.qid);
          return top;
        }})()"""
        top = run_node(self.FILES, expr, {}, SCHEDULE)
        self.assertEqual(sorted(top), sorted(["EE-114-01-3", "EE-108-01-2", "EE-110-01-1", "EE-110-01-2", "EE-110-01-3"]))

    def test_topic_uses_markdown_pipeline_or_escapes(self):
        out = run_node(self.FILES[1:], "[passbookTopicHtml('a <b> & $x$')]", {}, "")
        self.assertIn("&lt;b&gt;", out[0])
        out = run_node(self.FILES[1:], "[passbookTopicHtml('**粗** $x$')]", {}, "function processMarkdownWithMath(s) { return '<p>MD:' + s + '</p>'; }")
        self.assertEqual(out[0], "<p>MD:**粗** $x$</p>")

    def test_modal_source_has_no_own_scores(self):
        src = (ROOT / "src/components/passbookGenerator.js").read_text(encoding="utf-8")
        self.assertNotIn("掌握率", src)
        self.assertNotIn("預估：", src)
        self.assertIn("考前速查手冊（列印）", src)
        self.assertIn("passbookKeydown_", src)


class TestMockScoring(unittest.TestCase):
    FILES = [
        "src/data/questionPoints.generated.js", "src/data/targetAllocation.generated.js", "src/domain/studyPlan.js",
        "src/state/sm2Store.js", "src/state/resultCardStore.js",
    ]

    def test_mock_uses_main_factors_even_for_basic_tier(self):
        out = run_node(self.FILES, """(() => {
          const basicQid = Object.keys(QUESTION_POINTS).find(q => studyTierFor(q) === 'basic');
          const model = buildResultModel(basicQid);
          const marks = model.parts.map(() => 'o');
          return { tier: model.tier, total: model.total, practice: scoreResult(model, marks).estimate,
                   mock: scoreResult(model, marks, 'mock').estimate };
        })()""")
        self.assertEqual(out["tier"], "basic")
        self.assertEqual(out["mock"], out["total"])
        self.assertEqual(out["practice"], out["total"] / 2)

    def test_saved_mock_record_is_marked_exam(self):
        out = run_node(self.FILES, """(() => {
          const basicQid = Object.keys(QUESTION_POINTS).find(q => studyTierFor(q) === 'basic');
          const m = buildResultModel(basicQid);
          const parts = m.parts.map(p => ({ label: p.label, points: p.points, mark: 'o' }));
          const mock = saveResultRecord({ qid: basicQid, source: 'mock', mockId: 'm1', parts, at: 1 }, { skipSM2: true });
          const prac = saveResultRecord({ qid: basicQid, source: 'today', parts, at: 2 }, { skipSM2: true });
          return { mock: mock.record, prac: prac.record, total: m.total };
        })()""")
        self.assertEqual(out["mock"]["tier"], "basic")
        self.assertEqual(out["mock"]["scoring"], "exam")
        self.assertEqual(out["mock"]["estimate"], out["total"])
        self.assertNotIn("scoring", out["prac"])
        self.assertEqual(out["prac"]["estimate"], out["total"] / 2)


class TestThemeAndCss(unittest.TestCase):
    def test_theme_follows_system_unless_manual(self):
        main = (ROOT / "src/main.js").read_text(encoding="utf-8")
        self.assertIn("prefers-color-scheme: dark", main)
        self.assertIn("readThemePreference", main)

    def test_css_registered_and_scoped(self):
        css = (ROOT / "src/styles/v12-g1.css").read_text(encoding="utf-8")
        for needle in (".passbook-overlay", "#toast", ".result-card-mark.on[data-mark=\"tri\"]:hover", ".more-tools-panel"):
            self.assertIn(needle, css)


if __name__ == "__main__":
    unittest.main()
