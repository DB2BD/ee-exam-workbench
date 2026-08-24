# -*- coding: utf-8 -*-
"""
run_all_tests.py
================
Runs all automated unit, integration, and architecture tests.
Part of the TDD & Anti-Entropy Quality Gate.
"""

import unittest
import sys
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)
sys.path.insert(0, WORKSPACE)

def main():
    print("🧪 Running Test Suite across all modules (TDD Quality Gate)...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(WORKSPACE, 'tests'), pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print("❌ Test suite failed!")
        sys.exit(1)
    else:
        print("\n🎉 ALL TESTS PASSED! Quality gate verified.")

if __name__ == '__main__':
    main()
