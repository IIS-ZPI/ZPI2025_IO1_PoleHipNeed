"""
run_tests.py — uruchamia wszystkie testy projektu.

Użycie:
    # Tylko testy jednostkowe (domyślnie):
    python tests/run_tests.py

    # Testy jednostkowe + integracyjne (bez sieci):
    python tests/run_tests.py --integration

    # Wszystkie testy włącznie z prawdziwym API NBP:
    python tests/run_tests.py --all
"""

import os
import sys
import io
import unittest
import argparse

# Zapewnij obsługę UTF-8 na Windows (polskie znaki w nazwach testów)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Dodaj katalog projektu do ścieżki
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
    parser = argparse.ArgumentParser(description="Runner testów projektu NBP Data Analysis")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--integration",
        action="store_true",
        help="Uruchom testy jednostkowe + integracyjne (bez prawdziwego API)"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Uruchom wszystkie testy włącznie z prawdziwym API NBP"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Szczegółowy output (domyślnie włączony)"
    )
    args = parser.parse_args()

    verbosity = 2

    # Ustaw flagę dla testów API
    if args.all:
        os.environ["INTEGRATION_TESTS"] = "1"

    # Zbierz testy
    unit_suite = collect_unit_tests()
    total_suite = unittest.TestSuite()
    total_suite.addTests(unit_suite)

    if args.integration or args.all:
        integration_suite = collect_integration_tests()
        total_suite.addTests(integration_suite)

    # Wyświetl nagłówek
    print("\n" + "=" * 60)
    print("  NBP Data Analysis — Test Runner")
    print("=" * 60)

    mode = "Wszystkie (z API)" if args.all else ("Jednostkowe + Integracyjne" if args.integration else "Jednostkowe")
    print(f"  Tryb: {mode}")
    print("=" * 60)

    # Uruchom
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(total_suite)

    # Podsumowanie
    print("\n" + "=" * 60)
    print("  PODSUMOWANIE")
    print("=" * 60)
    print(f"  Uruchomiono : {result.testsRun}")
    print(f"  Sukces      : {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  Pominięto   : {len(result.skipped)}")
    print(f"  Błędy       : {len(result.errors)}")
    print(f"  Niepowodzenia: {len(result.failures)}")

    status = "✅ WSZYSTKIE TESTY PRZESZŁY" if result.wasSuccessful() else "❌ NIEKTÓRE TESTY NIE PRZESZŁY"
    print(f"\n  {status}")
    print("=" * 60)

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
