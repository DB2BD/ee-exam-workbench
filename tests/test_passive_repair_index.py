"""Regression coverage for the passive 114/108 repair index."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "上榜錯因修復索引_114-108.md"
CANONICAL_ROOT = ROOT / "📝 個人題解與錯題本"

SUBJECT_COUNTS = {
    "01": {114: 5, 108: 4},
    "02": {114: 4, 108: 5},
    "03": {114: 5, 108: 6},
    "04": {114: 5, 108: 5},
    "05": {114: 5, 108: 5},
    "06": {114: 5, 108: 5},
}

REPAIR_RULES = {
    "R": "重讀題幹，只寫已知、所求、限制條件與應用章節，再閉卷重開題。",
    "S": "只看題解第一個關鍵式，立即關閉題解，自己補完後續。",
    "F": "先寫公式成立條件，再代入本題數值；不直接背最後答案。",
    "C": "從第一個錯誤等號重算，最後用另一種代入、回代或量級檢查。",
    "K": "用三句話寫「物理／數學意義、變大時的方向、極端情況」。",
    "U": "在重寫答案的每個最終量旁補單位、參考方向與正負號意義。",
    "T": "對該題重做 8 分鐘起手式演練；時間到必須留下公式、圖或可得部分分的步驟。",
}

ROW_RE = re.compile(
    r"^\| `(?P<qid>EE-(?:114|108)-\d{2}-\d+)` \| "
    r"(?P<subject>[^|]+) \| (?P<chapter>[^|]+) \| "
    r"\[canonical 題解\]\((?P<link>[^)]+)\) \| "
    r"(?P<code>[RSFCKUT])：(?P<action>[^|]+) \|$"
)


def expected_qids():
    return {
        f"EE-{year}-{subject}-{number}"
        for subject, counts in SUBJECT_COUNTS.items()
        for year, count in counts.items()
        for number in range(1, count + 1)
    }


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    _, raw, _ = text.split("---", 2)
    values = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


class TestPassiveRepairIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = INDEX.read_text(encoding="utf-8")
        cls.rows = {
            match.group("qid"): match.groupdict()
            for line in cls.text.splitlines()
            if (match := ROW_RE.match(line))
        }
        cls.expected = expected_qids()

    def test_index_locks_exactly_59_unique_qids_in_the_two_years(self):
        self.assertEqual(len(self.expected), 59)
        self.assertEqual(set(self.rows), self.expected)
        self.assertEqual(len(self.rows), 59)
        self.assertEqual(
            sum(qid.startswith("EE-114-") for qid in self.rows),
            29,
        )
        self.assertEqual(
            sum(qid.startswith("EE-108-") for qid in self.rows),
            30,
        )

    def test_each_row_has_subject_chapter_canonical_link_and_fixed_action(self):
        self.assertEqual(len(self.rows), 59)
        for qid, row in self.rows.items():
            with self.subTest(qid=qid):
                self.assertTrue(row["subject"].strip())
                self.assertTrue(row["chapter"].strip())
                self.assertIn(row["code"], REPAIR_RULES)
                self.assertEqual(row["action"].strip(), REPAIR_RULES[row["code"]])

    def test_every_canonical_solution_link_is_local_and_resolves(self):
        for qid, row in self.rows.items():
            target = unquote(row["link"].split("#", 1)[0])
            resolved = (INDEX.parent / target).resolve()
            with self.subTest(qid=qid, target=row["link"]):
                self.assertTrue(resolved.is_file(), resolved)
                self.assertEqual(resolved.stem, qid)

    def test_all_59_canonical_solutions_are_verified(self):
        by_qid = {
            path.stem: path
            for path in CANONICAL_ROOT.glob("*/canonical/EE-*.md")
        }
        for qid in self.expected:
            with self.subTest(qid=qid):
                self.assertIn(qid, by_qid)
                values = frontmatter(by_qid[qid])
                self.assertEqual(values.get("qid"), qid)
                self.assertEqual(values.get("audit_status"), "verified")

    def test_fixed_rules_are_present_and_passive(self):
        self.assertIn("被動、免回填", self.text)
        self.assertIn("不需要把分數、錯因或日期輸入專案", self.text)
        for code, action in REPAIR_RULES.items():
            with self.subTest(code=code):
                self.assertIn(f"| `{code}` |", self.text)
                self.assertIn(action, self.text)

    def test_all_local_markdown_links_in_index_resolve(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertEqual(len(links), len(self.rows) + 1)
        self.assertIn("./上榜起手式急救卡_114-108.md", links)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            if not target or "://" in target:
                continue
            resolved = (INDEX.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.exists(), resolved)


if __name__ == "__main__":
    unittest.main()
