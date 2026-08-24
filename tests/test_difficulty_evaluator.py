# -*- coding: utf-8 -*-
"""
test_difficulty_evaluator.py
============================
Unit tests for the 5-Dimensional Objective Difficulty Evaluation Engine.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from difficulty_evaluator import evaluate_question_difficulty

class TestDifficultyEvaluator(unittest.TestCase):

    def test_level_1_basic_ohm(self):
        topic = "利用基本歐姆定律與純電阻分壓，計算電路端電壓。（10 分）"
        stars, raw, breakdown = evaluate_question_difficulty("01", topic, score=10)
        self.assertIn(stars, [1, 2], "Basic Ohm's law should be 1 or 2 stars")
        self.assertLess(raw, 2.20)

    def test_level_3_rlc_transient(self):
        topic = "二階 RLC 並聯暫態電路，已知 R=10 歐姆, L=0.5H, C=20mF，求阻尼狀態與時域電壓響應 v(t)。（20 分）"
        stars, raw, breakdown = evaluate_question_difficulty("01", topic, score=20)
        self.assertIn(stars, [3, 4], "2nd-order RLC transient should be 3 or 4 stars")

    def test_level_5_svd_or_state_estimation(self):
        topic = "電力系統狀態估計（State Estimation, WLS）：推導加權最小平方法與 chi-square 壞資料檢測。（25 分）"
        stars, raw, breakdown = evaluate_question_difficulty("05", topic, score=25)
        self.assertEqual(stars, 5, "WLS state estimation with bad data detection must be 5 stars")
        self.assertGreaterEqual(raw, 3.30)

    def test_level_5_distance_relay(self):
        topic = "距離保護電驛三段式規劃：分析阻抗型與 Mho 電驛阻抗圓圖，規劃 Zone 1, Zone 2, Zone 3 延時協調。（25 分）"
        stars, raw, breakdown = evaluate_question_difficulty("05", topic, score=25)
        self.assertEqual(stars, 5, "Distance relay 3-zone coordination must be 5 stars")

if __name__ == '__main__':
    unittest.main()
