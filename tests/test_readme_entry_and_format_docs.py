import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

CURRENT_DOCS = (
    "docs/上榜被動模考_114年六科執行包.md",
    "docs/上榜被動複測_108年六科執行包.md",
    "docs/上榜預設24時段_核心題路徑.md",
    "AGENT-SOLVE.md",
    "📝 個人題解與錯題本/TEMPLATE_題解與錯題筆記範本.md",
    ".agents/rules/exam_solution_standards.md",
)
LEGACY_TERMS = ("五區塊", "得分點拆解", "完整教學推導")


class ReadmeEntryTest(unittest.TestCase):
    def setUp(self):
        self.text = README.read_text(encoding="utf-8")

    def test_first_table_has_exactly_three_rows(self):
        section = self.text.split("## 先從這裡開始", 1)[1].split("\n## ", 1)[0]
        rows = [l for l in section.splitlines() if l.startswith("|")]
        data_rows = [l for l in rows if not re.match(r"^\|\s*:?-", l)][1:]
        self.assertEqual(len(data_rows), 3, data_rows)
        self.assertIn("上榜逐日開工表_115年.md", data_rows[0])
        self.assertIn("index.html", data_rows[1])
        self.assertIn("上榜精確解答邊界_條件題處理.md", data_rows[2])

    def test_appendix_keeps_moved_links(self):
        self.assertIn("## 附錄：路徑細節與其他入口", self.text)
        appendix = self.text.split("## 附錄：路徑細節與其他入口", 1)[1]
        for name in ("上榜預設24時段_核心題路徑.md", "上榜被動模考_114年六科執行包.md", "上榜錯因修復索引_114-108.md"):
            self.assertIn(name, appendix)

    def test_no_removed_ppi_feature_mentioned(self):
        self.assertNotIn("上榜預測", self.text)

    def test_current_docs_do_not_describe_legacy_five_block_format(self):
        for rel in CURRENT_DOCS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            body = text
            for term in LEGACY_TERMS:
                self.assertNotIn(term, body, f"{rel} still mentions {term}")


if __name__ == "__main__":
    unittest.main()
