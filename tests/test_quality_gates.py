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
import re
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


class TestSlicingAndLinkGate(unittest.TestCase):
    def _fixture(self):
        temp_root = Path(tempfile.mkdtemp(prefix="ee-workbench-slicing-"))
        self.addCleanup(shutil.rmtree, temp_root, ignore_errors=True)
        (temp_root / "scripts").mkdir()
        for name in [
            "dashboard-data.js", "solutions-bundle.js",
            "national-exams-data.js", "national-solutions-bundle.js",
        ]:
            shutil.copy2(WORKSPACE / name, temp_root / name)
        shutil.copy2(
            WORKSPACE / "scripts/verify_slicing_and_links.py",
            temp_root / "scripts/verify_slicing_and_links.py",
        )
        shutil.copytree(
            WORKSPACE / "📝 個人題解與錯題本",
            temp_root / "📝 個人題解與錯題本",
        )
        (temp_root / "fixture-crop.png").write_bytes(b"fixture")
        for note in (temp_root / "📝 個人題解與錯題本").glob("*/canonical/EE-*.md"):
            text = note.read_text(encoding="utf-8")
            note.write_text(re.sub(r"^source_crop:\s*.*$", "source_crop: fixture-crop.png", text, flags=re.MULTILINE), encoding="utf-8")
        self._rewrite_questions(temp_root / "national-exams-data.js", "national", lambda questions: [q.__setitem__(7, "https://example.test/paper.pdf") for q in questions])
        return temp_root

    def _rewrite_questions(self, path, family, mutate):
        text = path.read_text(encoding="utf-8")
        if family == "pe":
            match = re.search(r"questions:\s*(\[[\s\S]*?\])\s*,\s*\n\s*sevenLayers", text)
        else:
            match = re.search(r"questions:\s*(\[[\s\S]*?\])\s*\n\s*\};", text)
        self.assertIsNotNone(match)
        questions = json.loads(match.group(1))
        mutate(questions)
        replacement = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
        path.write_text(text[:match.start(1)] + replacement + text[match.end(1):], encoding="utf-8")

    def _run_gate(self, temp_root):
        return subprocess.run(
            [sys.executable, "scripts/verify_slicing_and_links.py"],
            cwd=temp_root, capture_output=True, text=True,
        )

    def test_clean_fixture_passes(self):
        completed = self._run_gate(self._fixture())
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def test_missing_canonical_note_fails_the_process(self):
        temp_root = self._fixture()
        canonical = next((temp_root / "📝 個人題解與錯題本").glob("*/canonical/EE-*.md"))
        canonical.unlink()
        completed = self._run_gate(temp_root)
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("missing=1", completed.stdout)

    def test_duplicate_and_extra_canonical_notes_fail(self):
        duplicate_root = self._fixture()
        note = next((duplicate_root / "📝 個人題解與錯題本").glob("*/canonical/EE-*.md"))
        shutil.copy2(note, note.with_name("EE-duplicate-copy.md"))
        duplicate = self._run_gate(duplicate_root)
        self.assertNotEqual(duplicate.returncode, 0, duplicate.stdout)
        self.assertIn("duplicate=1", duplicate.stdout)

        extra_root = self._fixture()
        note = next((extra_root / "📝 個人題解與錯題本").glob("*/canonical/EE-*.md"))
        extra = note.with_name("EE-EXTRA.md")
        extra.write_text(re.sub(r"^qid:\s*\S+", "qid: EE-EXTRA", note.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE), encoding="utf-8")
        completed = self._run_gate(extra_root)
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("extra=1", completed.stdout)

    def test_invalid_crop_and_full_page_embed_fail(self):
        invalid_root = self._fixture()
        note = next((invalid_root / "📝 個人題解與錯題本").glob("*/canonical/EE-*.md"))
        note.write_text(re.sub(r"^source_crop:\s*.*$", "source_crop: missing-crop.png", note.read_text(encoding="utf-8"), flags=re.MULTILINE), encoding="utf-8")
        invalid = self._run_gate(invalid_root)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout)
        self.assertIn("invalid_crop=1", invalid.stdout)

        full_root = self._fixture()
        note = next((full_root / "📝 個人題解與錯題本").glob("*/canonical/EE-*.md"))
        (full_root / "fixture_p1.png").write_bytes(b"fixture")
        note.write_text(re.sub(r"^source_crop:\s*.*$", "source_crop: fixture_p1.png", note.read_text(encoding="utf-8"), flags=re.MULTILINE), encoding="utf-8")
        full = self._run_gate(full_root)
        self.assertNotEqual(full.returncode, 0, full.stdout)
        self.assertIn("full_page_embed=1", full.stdout)

    def test_pe_and_gk_missing_solution_bundle_entries_fail(self):
        pe_root = self._fixture()
        self._rewrite_questions(pe_root / "dashboard-data.js", "pe", lambda questions: questions[0].__setitem__(6, "missing-pe-solution.md"))
        pe = self._run_gate(pe_root)
        self.assertNotEqual(pe.returncode, 0, pe.stdout)
        self.assertIn("PE Total: 323 | Slicing Failures: 1", pe.stdout)

        gk_root = self._fixture()
        self._rewrite_questions(gk_root / "national-exams-data.js", "national", lambda questions: questions[0].__setitem__(6, "missing-gk-solution.md"))
        gk = self._run_gate(gk_root)
        self.assertNotEqual(gk.returncode, 0, gk.stdout)
        self.assertIn("National Exams Total: 161 | Slicing Failures: 1", gk.stdout)

    def test_gk_pdf_failure_is_checked_for_regular_and_composite_mc_items(self):
        regular_root = self._fixture()
        self._rewrite_questions(regular_root / "national-exams-data.js", "national", lambda questions: questions[0].__setitem__(7, "missing.pdf"))
        regular = self._run_gate(regular_root)
        self.assertNotEqual(regular.returncode, 0, regular.stdout)
        self.assertIn("PDF Link Issues: 1", regular.stdout)

        mc_root = self._fixture()
        def break_mc(questions):
            next(q for q in questions if re.search(r"-MC\d+$", q[0])).__setitem__(7, "missing-mc.pdf")
        self._rewrite_questions(mc_root / "national-exams-data.js", "national", break_mc)
        mc = self._run_gate(mc_root)
        self.assertNotEqual(mc.returncode, 0, mc.stdout)
        self.assertIn("PDF Link Issues: 1", mc.stdout)


class TestPagesStaging(unittest.TestCase):
    def _fixture(self, root):
        (root / "libs").mkdir(parents=True)
        (root / "index.html").write_text("<!doctype html>", encoding="utf-8")
        (root / "dashboard-data.js").write_text(
            "const QUESTION_CROP_MAP = {};\nconst PE_DATA = { questions: [],\nsevenLayers: [] };",
            encoding="utf-8",
        )
        (root / "solutions-bundle.js").write_text("const IMAGE_MAP = {};", encoding="utf-8")
        (root / "national-exams-data.js").write_text(
            "const NATIONAL_DATA = { questions: []\n};", encoding="utf-8",
        )
        (root / "national-solutions-bundle.js").write_text(
            "const NATIONAL_IMAGE_MAP = {};", encoding="utf-8",
        )
        for name in ("katex.min.css", "katex.min.js", "auto-render.min.js", "marked.min.js"):
            (root / "libs" / name).write_text("fixture", encoding="utf-8")

    def _run_staging(self, root):
        env = os.environ.copy()
        env["PAGES_STAGE_ROOT"] = str(root)
        env["PAGES_STAGE_DEST"] = str(root / "_site")
        return subprocess.run(
            [sys.executable, str(WORKSPACE / "scripts/stage_pages_artifact.py")],
            cwd=root, env=env, capture_output=True, text=True,
        )

    def test_staging_contains_runtime_assets_but_not_repository_internals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            completed = self._run_staging(root)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            site = root / "_site"
            for name in ("index.html", "dashboard-data.js", "solutions-bundle.js", "national-exams-data.js", "national-solutions-bundle.js"):
                self.assertTrue((site / name).is_file(), name)
            for name in ("katex.min.css", "katex.min.js", "auto-render.min.js", "marked.min.js"):
                self.assertTrue((site / "libs" / name).is_file(), name)
            self.assertFalse((site / ".git").exists())
            self.assertFalse((site / "tests").exists())
            self.assertIn("Pages staging", completed.stdout)

    def test_staging_fails_closed_when_any_runtime_library_is_missing(self):
        runtime_names = ("katex.min.css", "katex.min.js", "auto-render.min.js", "marked.min.js")
        for missing_name in runtime_names:
            with self.subTest(missing_name=missing_name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self._fixture(root)
                (root / "libs" / missing_name).unlink()
                completed = self._run_staging(root)
                self.assertNotEqual(completed.returncode, 0, completed.stdout)
                self.assertIn(missing_name, completed.stderr)

    def test_staging_rejects_absolute_and_parent_runtime_references(self):
        for unsafe in ("/tmp/outside.png", "../outside.png"):
            with self.subTest(unsafe=unsafe), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self._fixture(root)
                (root / "solutions-bundle.js").write_text(
                    f"const IMAGE_MAP = {{\"EE-test\": {json.dumps(unsafe)}}};",
                    encoding="utf-8",
                )
                completed = self._run_staging(root)
                self.assertNotEqual(completed.returncode, 0, completed.stdout)
                self.assertIn("不安全引用路徑", completed.stderr)


if __name__ == "__main__":
    unittest.main()
