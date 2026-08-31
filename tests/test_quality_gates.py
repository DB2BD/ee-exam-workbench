# -*- coding: utf-8 -*-
"""Quality gates for static builds and the review-page boundary.

The review page is rendered by browser globals, so the filter controls need a
small, dependency-free boundary that can be exercised without a DOM.  The
contract below intentionally names that boundary:

* ``getReviewSubjectFilterValues(questions)`` returns sorted subject IDs.
* ``getReviewChapterFilterValues(questions, subject_id)`` returns sorted
  chapter labels for that subject (without leaking chapters from another
  subject).

If the core seam is not present yet these tests fail with a clear message;
that is preferable to coupling tests to ``innerHTML`` implementation details.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]


class TestReviewPageSeams(unittest.TestCase):
    """Exercise subject/chapter behavior through pure browser boundaries."""

    def _run_node(self, expression):
        review_source = (WORKSPACE / "src/components/reviewPage.js").read_text(encoding="utf-8")
        domain_path = WORKSPACE / "src/domain/questionRecord.js"
        domain_source = domain_path.read_text(encoding="utf-8") if domain_path.exists() else ""
        alias_path = WORKSPACE / "src/data/taxonomyAliases.js"
        alias_source = alias_path.read_text(encoding="utf-8") if alias_path.exists() else ""
        dag_source = (WORKSPACE / "src/data/knowledge-dag.js").read_text(encoding="utf-8")
        source = domain_source + "\n" + alias_source + "\n" + dag_source + "\n" + review_source
        script = f"""
const vm = require('vm');
const source = {json.dumps(source, ensure_ascii=False)};
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context, {{ filename: 'reviewPage.js' }});
const result = ({expression});
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"review-page seam invocation failed:\n{completed.stderr}",
        )
        return json.loads(completed.stdout)

    def test_subject_filter_values_are_unique_and_sorted(self):
        questions = [
            ["EE-1", "02", 114, 1, "二極體", [], "", "", 1, "verified", [], True],
            ["EE-2", "01", 114, 2, "節點電壓", [], "", "", 1, "verified", [], True],
            ["EE-3", "02", 113, 1, "整流", [], "", "", 1, "verified", [], True],
        ]
        result = self._run_node(
            "context.getReviewSubjectFilterValues(" + json.dumps(questions, ensure_ascii=False) + ")"
        )
        self.assertEqual(result, ["01", "02"])

    def test_chapter_filter_values_are_scoped_to_selected_subject(self):
        questions = [
            ["EE-1", "01", 114, 1, "節點電壓法與網目電流法", [], "", "", 1, "verified", [], True],
            ["EE-2", "02", 114, 1, "二極體整流與濾波電路", [], "", "", 1, "verified", [], True],
        ]
        result = self._run_node(
            "context.getReviewChapterFilterValues("
            + json.dumps(questions, ensure_ascii=False)
            + ", '01')"
        )
        self.assertEqual(result, ["節點電壓法與網目電流法"])

    def test_classifier_rules_resolve_to_canonical_dag_nodes(self):
        # Run the check inside the VM because REVIEW_CHAPTER_RULES is a module
        # lexical binding rather than a browser global.
        review_source = (WORKSPACE / "src/components/reviewPage.js").read_text(encoding="utf-8")
        dag_source = (WORKSPACE / "src/data/knowledge-dag.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const context = {{ console }};
vm.createContext(context);
const source = {json.dumps(dag_source + chr(10) + review_source + chr(10) + "globalThis.__missing = ['01','02','03','04','05','06'].flatMap(s => getReviewChapterRuleIds(s)).filter(id => !KNOWLEDGE_DAG[id]);", ensure_ascii=False)};
vm.runInContext(source, context);
process.stdout.write(JSON.stringify(context.__missing));
"""
        completed = subprocess.run(["node", "-e", script], cwd=WORKSPACE, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), [])

    def test_classifier_fails_closed_on_equal_conflicting_signals(self):
        question = [
            "EE-ambiguous", "03", 114, 1,
            "拉普拉斯轉換與傅立葉級數", [], "", "", 3, "verified", [], True,
        ]
        result = self._run_node(
            "context.getReviewTypeLabel(" + json.dumps(question, ensure_ascii=False) + ")"
        )
        self.assertEqual(result, "待人工複核")

    def test_alias_normalization_maps_english_text_to_textbook_chapter(self):
        question = [
            "EE-laplace", "01", 114, 1,
            "Solve the Laplace transform circuit in the s-domain", [], "", "", 3, "verified", [], True,
        ]
        result = self._run_node(
            "context.getReviewTypeLabel(" + json.dumps(question, ensure_ascii=False) + ")"
        )
        self.assertEqual(result, "S 域拉氏轉換電路求解")

    def test_dc_motor_alias_does_not_fall_into_induction_torque(self):
        question = [
            "EE-105-04-5", "04", 105, 5,
            "外激式直流電動機減磁與降壓調速，求轉速", [], "", "", 3, "needs_manual_review", [], True,
        ]
        result = self._run_node(
            "context.getReviewTypeLabel(" + json.dumps(question, ensure_ascii=False) + ")"
        )
        self.assertEqual(result, "直流電機 (分激/串激特性與調速)")

    def test_manual_topic_label_overrides_auto_classifier_for_same_subject(self):
        question = [
            "EE-manual-label", "02", 114, 1,
            "返馳式轉換器與連續導通", [], "", "", 3, "needs_manual_review", [], True,
        ]
        expression = (
            "(() => { "
            "context.findQuestionRecord = qid => qid === 'EE-manual-label' ? "
            + json.dumps(question, ensure_ascii=False)
            + " : null; "
            "context.renderReviewPage = () => {}; "
            "context.replaceManualTopicLabels({'EE-manual-label': {chapterId: 'el-bjt-bias-small-signal'}}); "
            "return context.getReviewTypeLabel("
            + json.dumps(question, ensure_ascii=False)
            + "); })()"
        )
        result = self._run_node(expression)
        self.assertEqual(result, "BJT 偏壓分析與小訊號模型")

    def test_manual_label_options_are_scoped_to_selected_subject(self):
        result = self._run_node("context.getManualLabelOptions('02').map(item => item.id)")
        self.assertIn("el-pe-buck-boost", result)
        self.assertNotIn("ct-thevenin-norton", result)

    def test_manual_review_queue_follows_selected_subject(self):
        questions = [
            ["EE-manual-02", "02", 114, 1, "返馳式轉換器", [], "", "", 3, "needs_manual_review", [], True],
            ["EE-manual-04", "04", 114, 1, "直流電機調速", [], "", "", 3, "needs_manual_review", [], True],
        ]
        expression = (
            "(() => { "
            "context.document = { getElementById: () => ({ value: '02' }) }; "
            "context.getActiveQuestionsList = () => "
            + json.dumps(questions, ensure_ascii=False)
            + "; return context.getManualReviewQuestions().map(q => q[0]); })()"
        )
        result = self._run_node(expression)
        self.assertEqual(result, ["EE-manual-02"])

    def test_manual_label_modal_renders_crop_and_subject_selector(self):
        question = [
            "EE-manual-ui", "02", 114, 1, "返馳式轉換器與連續導通", [], "", "", 3,
            "needs_manual_review", [], True,
        ]
        expression = (
            "(() => { "
            "const elements = {}; "
            "['manual-label-modal','manual-label-body','manual-label-progress','manual-label-prev','manual-label-next']"
            ".forEach(id => elements[id] = { classList: { add: () => {}, remove: () => {} }, querySelector: () => null, innerHTML: '', innerText: '', disabled: false }); "
            "elements['manual-label-modal'].classList = { added: '', add(value) { this.added = value; }, remove() {} }; "
            "context.document = { body: { style: {} }, getElementById: id => elements[id] }; "
            "context.getActiveQuestionsList = () => " + json.dumps([question], ensure_ascii=False) + "; "
            "context.getSubjectMeta = () => ({ name: '電子學（含電力電子）', icon: '' }); "
            "context.renderQuestionTopic = text => text; "
            "context.showToast = () => {}; "
            "context.findQuestionRecord = () => " + json.dumps(question, ensure_ascii=False) + "; "
            "context.QUESTION_CROP_MAP = { 'EE-manual-ui': 'assets/questions/EE-manual-ui.png' }; "
            "context.resolveImageMapUrl = src => src; "
            "context.openManualLabelModal(); "
            "return { "
            "opened: elements['manual-label-modal'].classList.added === 'show', "
            "progress: elements['manual-label-progress'].innerText, "
            "hasCrop: elements['manual-label-body'].innerHTML.includes('assets/questions/EE-manual-ui.png'), "
            "hasSelector: elements['manual-label-body'].innerHTML.includes('manual-label-select'), "
            "hasQid: elements['manual-label-body'].innerHTML.includes('EE-manual-ui') "
            "}; })()"
        )
        result = self._run_node(expression)
        self.assertEqual(result, {"opened": True, "progress": "1 / 1", "hasCrop": True, "hasSelector": True, "hasQid": True})

    def test_manual_label_backup_normalizes_legacy_and_null_values(self):
        question = [
            "EE-manual-valid", "02", 114, 1, "返馳式轉換器與連續導通", [], "", "", 3,
            "needs_manual_review", [], True,
        ]
        expression = (
            "(() => { "
            "context.findQuestionRecord = qid => qid === 'EE-manual-valid' ? "
            + json.dumps(question, ensure_ascii=False)
            + " : null; "
            "context.renderReviewPage = () => {}; "
            "context.replaceManualTopicLabels({"
            "'EE-null': null, "
            "'EE-empty': {chapterId: ''}, "
            "'EE-manual-valid': {chapterId: 'el-pe-buck-boost', source: 'backup', updatedAt: '2026-09-01T00:00:00Z'}"
            "}); "
            "return context.getManualTopicLabels(); })()"
        )
        result = self._run_node(expression)
        self.assertEqual(
            result,
            {
                "EE-manual-valid": {
                    "chapterId": "el-pe-buck-boost",
                    "source": "backup",
                    "updatedAt": "2026-09-01T00:00:00Z",
                }
            },
        )


class TestBuildReproducibility(unittest.TestCase):
    """A fixed input tree must produce byte-identical HTML across timezones."""

    def _build_in_temp_workspace(self, timezone):
        temp_root = Path(tempfile.mkdtemp(prefix="ee-workbench-build-"))
        self.addCleanup(shutil.rmtree, temp_root, ignore_errors=True)
        shutil.copytree(WORKSPACE / "src", temp_root / "src")
        (temp_root / "scripts").mkdir()
        shutil.copy2(WORKSPACE / "scripts/build_workbench.py", temp_root / "scripts/build_workbench.py")
        env = os.environ.copy()
        env.update({"SOURCE_DATE_EPOCH": "1700000000", "TZ": timezone})
        completed = subprocess.run(
            [sys.executable, "scripts/build_workbench.py"],
            cwd=temp_root,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        return (temp_root / "index.html").read_bytes()

    def test_build_is_reproducible_independent_of_local_clock(self):
        utc_west = self._build_in_temp_workspace("Etc/GMT+12")
        utc_east = self._build_in_temp_workspace("Pacific/Kiritimati")
        self.assertEqual(
            utc_west,
            utc_east,
            "build output must not embed wall-clock/local-time state",
        )


class TestHtmlJavaScriptSyntaxGate(unittest.TestCase):
    def test_inline_javascript_syntax_gate_passes(self):
        checker = WORKSPACE / "scripts/check_html_js_syntax.py"
        # The checker writes short-lived extracted blocks beside itself.  Run
        # it in an isolated copy so a test never dirties the checkout (and so
        # read-only CI/test sandboxes can still exercise the gate).
        temp_root = Path(tempfile.mkdtemp(prefix="ee-workbench-syntax-"))
        self.addCleanup(shutil.rmtree, temp_root, ignore_errors=True)
        (temp_root / "scripts").mkdir()
        shutil.copy2(checker, temp_root / "scripts/check_html_js_syntax.py")
        shutil.copy2(WORKSPACE / "index.html", temp_root / "index.html")
        completed = subprocess.run(
            [sys.executable, "scripts/check_html_js_syntax.py"],
            cwd=temp_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertNotIn("Syntax Error", completed.stdout)


if __name__ == "__main__":
    unittest.main()
