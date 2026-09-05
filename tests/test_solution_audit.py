# -*- coding: utf-8 -*-
"""Behavioral tests for solution-audit presentation and reporting seams."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSolutionAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = r'''
const fs = require('fs'), vm = require('vm');
const ctx = {
  console,
  window: { addEventListener() {} },
  document: { getElementById() { return null; }, body: {} },
};
vm.createContext(ctx);
for (const file of [
  'dashboard-data.js',
  'national-exams-data.js',
  'src/domain/questionRecord.js',
  'src/components/solutionModal.js',
]) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
const result = vm.runInContext(process.argv[1], ctx);
process.stdout.write(JSON.stringify(result));
'''

    def run_js(self, expression):
        completed = subprocess.run(
            ["node", "-e", self.script, expression],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout.splitlines()[-1])

    def test_known_manual_review_presentation_keeps_auditable_sources(self):
        result = self.run_js(
            "(() => { const q = DB_DATA.questions.find(q => q[0] === 'EE-112-02-1'); "
            "const p = getSolutionAuditPresentation(q[9], getSolutionReviewMetadata(q[0]), q); "
            "return {status:p.status, label:p.statusLabel, blocker:p.blocker, action:p.action, evidence:p.evidence, "
            "officialQuestionUrl:p.sources.officialQuestionUrl, solutionLink:p.sources.solutionLink, crop:p.sources.questionCrop, card:renderSolutionReviewCard(q[0], q)}; })()"
        )
        self.assertEqual(result["status"], "needs_manual_review")
        self.assertIn("人工覆核", result["label"])
        self.assertIn("missing_parameter", result["blocker"])
        self.assertTrue(result["action"])
        self.assertTrue(result["evidence"])
        self.assertTrue(result["officialQuestionUrl"])
        self.assertTrue(result["solutionLink"])
        self.assertTrue(result["crop"])
        self.assertNotIn("已校驗", result["label"])
        self.assertIn("missing_parameter", result["card"])
        self.assertIn("收斂所需動作", result["card"])
        self.assertIn("交叉證據", result["card"])
        self.assertIn("官方原題", result["card"])
        self.assertIn("solution-report-textarea", result["card"])
        self.assertNotIn("題解已校驗", result["card"])

    def test_solution_status_and_learning_status_are_separate(self):
        result = self.run_js(
            "(() => { const q = ['EE-verified', '01', 114, 1, '題目', [], 'solution.md', 'official.pdf', 3, 'verified', [], false]; "
            "const verified = getSolutionAuditPresentation('verified', null, q); "
            "const manual = getSolutionAuditPresentation('needs_manual_review', null, q); "
            "return {verified:verified.statusLabel, manual:manual.statusLabel, verifiedCard:renderSolutionReviewCard(q[0], q), learning0:getLearningStatusPresentation(0).label, learning1:getLearningStatusPresentation(1).label, learning2:getLearningStatusPresentation(2).label}; })()"
        )
        self.assertIn("已校驗", result["verified"])
        self.assertIn("人工覆核", result["manual"])
        self.assertIn("題解已校驗", result["verifiedCard"])
        self.assertNotIn("題解保留人工覆核", result["verifiedCard"])
        self.assertNotEqual(result["verified"], result["learning1"])
        self.assertNotEqual(result["manual"], result["learning2"])
        self.assertIn("未開始", result["learning0"])
        self.assertIn("已掌握", result["learning1"])
        self.assertIn("需二刷", result["learning2"])

    def test_report_builder_contains_locator_fields_without_network_action(self):
        result = self.run_js(
            "(() => { const q = ['EE-report', '02', 112, 1, '題目', [], 'solution.md', 'official.pdf', 3, 'needs_manual_review', [], false]; "
            "const report = buildSolutionIssueReport(q, 'missing_parameter', {auditStatus:'needs_manual_review', examFamily:'PE', version:QUESTION_SCHEMA_VERSION, subjectName:'02. 電子學'}); "
            "return report; })()"
        )
        for expected in ["EE-report", "1.0.0", "needs_manual_review", "PE", "112", "02. 電子學", "missing_parameter", "official.pdf", "solution.md"]:
            self.assertIn(expected, result)
        self.assertIn("回報題解問題", result)

    def test_missing_metadata_is_conservative_and_keeps_official_question_link(self):
        result = self.run_js(
            "(() => { const q = ['EE-missing', '01', 114, 2, '題目', [], 'solution.md', 'official.pdf', 3, 'needs_manual_review', [], false]; "
            "const p = getSolutionAuditPresentation(q[9], null, q); "
            "return {status:p.status, conservative:p.conservative, blocker:p.blocker, official:p.sources.officialQuestionUrl, card:renderSolutionReviewCard(q[0], q)}; })()"
        )
        self.assertEqual(result["status"], "needs_manual_review")
        self.assertTrue(result["conservative"])
        self.assertIn("未提供人工覆核備註", result["blocker"])
        self.assertEqual(result["official"], "official.pdf")
        self.assertIn("目前無法宣稱已校驗", result["card"])
        self.assertIn("solution-report-textarea", result["card"])

    def test_pe_manifest_materializes_manual_disposition_evidence(self):
        manifest = json.loads((ROOT / "data" / "pe-solution-audit.json").read_text(encoding="utf-8"))
        manual = [entry for entry in manifest["entries"] if entry.get("audit_status") == "needs_manual_review"]
        self.assertEqual(len(manual), 17)
        for entry in manual:
            for key in ("review_disposition", "review_blocker", "review_action", "review_evidence", "official_source_url"):
                self.assertTrue(entry.get(key), f"{entry['qid']} lacks manifest {key}")
            self.assertTrue(entry["official_source_url"].startswith("https://wwwq.moex.gov.tw/"))


if __name__ == "__main__":
    unittest.main()
