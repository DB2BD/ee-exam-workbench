# -*- coding: utf-8 -*-
"""Learning data capacity and recovery measurement tests."""

import unittest

from scripts.measure_learning_data_capacity import measure


class TestLearningDataCapacity(unittest.TestCase):
    def test_capacity_report_contains_measured_recovery_time_and_threshold(self):
        result = measure()
        self.assertTrue(result["generatedAt"])
        self.assertEqual(result["sourceIdentity"]["canonicalGraphRevision"], result["graphRevision"])
        self.assertEqual(result["outputIdentity"]["kind"], "learning-data-capacity")
        self.assertIsInstance(result["checks"], list)
        self.assertEqual(result["blockingFailures"], [])
        self.assertGreaterEqual(result["recoveryTimeMs"], 0)
        self.assertEqual(result["recoveryTimeThresholdMs"], 250)
        self.assertIs(result["recoveryTimePass"], result["recoveryTimeMs"] <= result["recoveryTimeThresholdMs"])
        self.assertEqual(result["measuredIssueEventCount"], 5000)


if __name__ == "__main__":
    unittest.main()
