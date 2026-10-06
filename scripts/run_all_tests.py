# -*- coding: utf-8 -*-
"""
run_all_tests.py
================
Runs all automated unit, integration, and architecture tests.
Part of the TDD & Anti-Entropy Quality Gate.

Usage:
  python3 scripts/run_all_tests.py                 # all files, parallel (cpu_count jobs)
  python3 scripts/run_all_tests.py --jobs 1        # serial, single process
  python3 scripts/run_all_tests.py -k pacing       # name filter (repeatable)
  python3 scripts/run_all_tests.py --file test_pacing.py
"""

import argparse
import concurrent.futures
import glob
import os
import re
import subprocess
import sys
import time
import unittest

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(WORKSPACE, 'tests')

# Files that run generators / touch checked-in files (e.g. reports/*.json).
# They run one after another in a single lane, never concurrently with each other.
SERIAL_FILES = {
    'test_build_pipeline.py',
    'test_furnace_series_path_114.py',
    'test_knowledge_graph_generation.py',
    'test_legacy_gk_generators_are_safe.py',
    'test_obsidian_knowledge_generation.py',
}


def test_files(selected):
    if selected:
        names = [os.path.basename(f) for f in selected]
        missing = [n for n in names if not os.path.exists(os.path.join(TESTS_DIR, n))]
        if missing:
            print('Unknown test file(s): ' + ', '.join(missing))
            sys.exit(2)
        return sorted(set(names))
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(TESTS_DIR, 'test_*.py')))


def run_serial(patterns, files):
    print("Running Test Suite across all modules (TDD Quality Gate)...")
    loader = unittest.TestLoader()
    if patterns:
        loader.testNamePatterns = [p if '*' in p else '*%s*' % p for p in patterns]
    suite = unittest.TestSuite()
    for name in files:
        suite.addTests(loader.discover(start_dir=TESTS_DIR, pattern=name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def run_one(name, patterns):
    cmd = [sys.executable, '-m', 'unittest', 'discover', '-s', TESTS_DIR, '-p', name]
    for p in patterns:
        cmd += ['-k', p]
    start = time.time()
    done = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True)
    out = done.stderr + done.stdout
    m = re.search(r'Ran (\d+) tests?', out)
    return name, done.returncode == 0, int(m.group(1)) if m else 0, time.time() - start, out


def run_parallel(patterns, files, jobs):
    print('Running %d test files with %d parallel jobs...' % (len(files), jobs))
    serial = [f for f in files if f in SERIAL_FILES]
    parallel = [f for f in files if f not in SERIAL_FILES]
    results = []

    def serial_lane():
        return [run_one(f, patterns) for f in serial]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        lane = pool.submit(serial_lane) if serial else None
        futures = [pool.submit(run_one, f, patterns) for f in parallel]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())
        if lane:
            results.extend(lane.result())

    total = 0
    failed = []
    for name, ok, count, secs, out in sorted(results):
        total += count
        print('%s %-55s %4d tests %6.1fs' % ('ok  ' if ok else 'FAIL', name, count, secs))
        if not ok:
            failed.append((name, out))
    for name, out in failed:
        print('\n===== %s =====\n%s' % (name, out))
    print('\nRan %d tests in %d files; %d file(s) failed.' % (total, len(results), len(failed)))
    return not failed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-k', dest='patterns', action='append', default=[], metavar='PATTERN',
                        help='only run tests whose name matches (substring or fnmatch; repeatable)')
    parser.add_argument('--file', dest='files', action='append', default=[], metavar='test_x.py',
                        help='only load this test file (repeatable)')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 1,
                        help='parallel test files (default: cpu count; 1 = serial in-process)')
    args = parser.parse_args()

    os.chdir(WORKSPACE)
    sys.path.insert(0, WORKSPACE)
    files = test_files(args.files)
    if args.jobs <= 1:
        ok = run_serial(args.patterns, files)
    else:
        ok = run_parallel(args.patterns, files, args.jobs)
    if not ok:
        print("Test suite failed!")
        sys.exit(1)
    print("\nALL TESTS PASSED! Quality gate verified.")


if __name__ == '__main__':
    main()
