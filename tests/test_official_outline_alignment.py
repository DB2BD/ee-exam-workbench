"""Regression coverage for alignment with the current official PE outline."""

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT = ROOT / "docs" / "上榜核心路徑_現行命題大綱對照.md"
EXPECTED_BY_SUBJECT = {
    "01": {"EE-114-01-3", "EE-112-01-2"},
    "02": {"EE-110-02-3", "EE-112-02-3"},
    "03": {"EE-113-03-6", "EE-113-03-3"},
    "04": {"EE-112-04-5", "EE-114-04-4"},
    "05": {"EE-114-05-2", "EE-114-05-5"},
    "06": {"EE-113-06-4", "EE-110-06-4"},
}


class TestOfficialOutlineAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ALIGNMENT.read_text(encoding="utf-8")
        cls.qids = set(re.findall(r"EE-\d{3}-\d{2}-\d+", cls.text))
        cls.status = {}
        for name in ("pe-solution-audit.json", "engineering-math-audit.json"):
            data = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
            cls.status.update({entry["qid"]: entry["audit_status"] for entry in data["entries"]})

    def test_all_twelve_core_chapters_map_to_verified_anchor_questions(self):
        expected = set().union(*EXPECTED_BY_SUBJECT.values())
        self.assertEqual(self.qids, expected)
        for subject, qids in EXPECTED_BY_SUBJECT.items():
            self.assertEqual({qid for qid in self.qids if qid.split("-")[2] == subject}, qids)
            for qid in qids:
                self.assertEqual(self.status.get(qid), "verified", qid)

    def test_current_official_source_and_scope_limits_are_explicit(self):
        for phrase in (
            "2026-09-23",
            "2026-09-17 更新",
            "2004-03-17 公告訂定",
            "共計６科目",
            "全部落在官方明列範圍內",
            "不代表六科大綱已全覆蓋",
            "不保證 115 年只考這些內容",
            "命題大綱只是範圍例示",
            "只證明核心章節未過期",
        ):
            self.assertIn(phrase, self.text)
        self.assertIn("file_id=1967", self.text)
        self.assertIn("sub_menu_id=613", self.text)

    def test_six_noncore_scope_rows_and_local_links_are_complete(self):
        for subject in ("電路學", "電子學", "工程數學", "電機機械", "電力系統", "工業配電"):
            self.assertRegex(self.text, rf"\| {subject} \| [^|]+ \|")
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        local_links = [target for target in links if "://" not in target]
        self.assertEqual(len(local_links), 14)
        for raw_target in local_links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (ALIGNMENT.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)


if __name__ == "__main__":
    unittest.main()
