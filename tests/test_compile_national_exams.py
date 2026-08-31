# -*- coding: utf-8 -*-
"""Regression tests for deterministic national-exam compilation."""

import os
import sys
import unittest

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE, "scripts"))

from compile_national_exams import (
    choose_related_pe_qid,
    extract_content_tags,
    resolve_subject_id,
)


class TestCompileNationalExams(unittest.TestCase):

    def test_content_tags_are_sorted_deterministically(self):
        topic = "三相變壓器故障短路與功率因數之分析"
        body = "變壓器、故障、短路、功率、相量與阻抗"
        expected = sorted(extract_content_tags(topic, body))
        for _ in range(10):
            self.assertEqual(extract_content_tags(topic, body), expected)

    def test_unknown_subject_fails_closed(self):
        with self.assertRaises(ValueError):
            resolve_subject_id("不存在的考科")

    def test_cross_reference_tie_fails_closed(self):
        entries = [
            {"qid": "EE-110-01-1", "tags": {"電路學"}, "topic": "相量阻抗"},
            {"qid": "EE-111-01-2", "tags": {"電路學"}, "topic": "相量阻抗"},
        ]
        self.assertEqual(choose_related_pe_qid({"電路學"}, "相量阻抗", entries), "")

    def test_cross_reference_accepts_unique_best_match(self):
        entries = [
            {"qid": "EE-110-01-1", "tags": {"電路學"}, "topic": "戴維寧等效"},
            {"qid": "EE-111-01-2", "tags": {"電路學"}, "topic": "相量阻抗"},
        ]
        self.assertEqual(
            choose_related_pe_qid({"電路學", "等效定理"}, "戴維寧等效", entries),
            "EE-110-01-1",
        )


if __name__ == "__main__":
    unittest.main()
