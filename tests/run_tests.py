"""
run_tests.py — runs all tests for the project.

Usage:
    # Only unit tests (default):
    python tests/run_tests.py

    # Unit and integration tests (without real API):
    python tests/run_tests.py --integration

    # All tests including real NBP API:
    python tests/run_tests.py --all
"""

import os
import sys
import io
import unittest
import argparse

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
UNIT_DIR = os.path.join(TESTS_DIR, "unit")
INTEGRATION_DIR = os.path.join(TESTS_DIR, "integration")


def run_suite(loader, suite_name, verbosity=2):
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    print(f"\n{'='*60}")
    print(f"  {suite_name}")
    print(f"{'='*60}")
    result = runner.run(suite_name if isinstance(suite_name, unittest.TestSuite) else loader)
    return result


def collect_unit_tests():
    loader = unittest.TestLoader()
    return loader.discover(start_dir=UNIT_DIR, pattern="test_*.py")


def collect_integration_tests():
    loader = unittest.TestLoader()
    return loader.discover(start_dir=INTEGRATION_DIR, pattern="test_*.py")


def main():
    parser = argparse.ArgumentParser(description="NBP Data Analysis Test Runner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--integration",
        action="store_true",
        help="Run unit tests + integration tests (without real API)"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all tests including real NBP API"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Detailed output (default)"
    )
    args = parser.parse_args()

    verbosity = 2

    if args.all:
        os.environ["INTEGRATION_TESTS"] = "1"

    unit_suite = collect_unit_tests()
    total_suite = unittest.TestSuite()
    total_suite.addTests(unit_suite)

    if args.integration or args.all:
        integration_suite = collect_integration_tests()
        total_suite.addTests(integration_suite)

    print("\n" + "=" * 60)
    print("  NBP Data Analysis — Test Runner")
    print("=" * 60)

    mode = "All (with API)" if args.all else ("Unit + Integration" if args.integration else "Unit")
    print(f"  Mode: {mode}")
    print("=" * 60)

    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(total_suite)

    print("\n" + "=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)
    print(f"  Ran : {result.testsRun}")
    print(f"  Success: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  Skipped: {len(result.skipped)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")

    status = "✅ ALL TESTS PASSED" if result.wasSuccessful() else "❌ SOME TESTS FAILED"
    print(f"\n  {status}")
    print("=" * 60)

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
