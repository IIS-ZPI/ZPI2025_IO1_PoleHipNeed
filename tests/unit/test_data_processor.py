import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import date
from decimal import Decimal

from data_processor import (
    calculate_sessions,
    calculate_statistical_measures,
    calculate_change_distribution,
)
from nbp_sessions import Quote, subtract_months, count_sessions


class TestDataProcessor(unittest.TestCase):

    def test_calculate_sessions(self):
        sessions = [1.0, 1.0, 2.0, 1.5, 1.5]
        result = calculate_sessions(sessions)

        self.assertEqual(result["flat"], 3)
        self.assertEqual(result["rising"], 1)
        self.assertEqual(result["losing"], 1)

    def test_calculate_statistical_measures(self):
        data = [1, 2, 2, 3, 4]
        result = calculate_statistical_measures(data)

        self.assertEqual(result["median"], 2)
        self.assertEqual(result["mode"], 2)
        self.assertIn("standard deviation", result)
        self.assertIn("coefficient of variation", result)

    def test_change_distribution_invalid_lengths(self):
        with self.assertRaises(ValueError) as ctx:
            calculate_change_distribution([1, 2], [1], 5)
        self.assertIn("equal", str(ctx.exception))

    def test_change_distribution_invalid_steps(self):
        with self.assertRaises(ValueError) as ctx:
            calculate_change_distribution([1, 2], [1, 2], 0)
        self.assertIn(">= 1", str(ctx.exception))

    def test_change_distribution_valid(self):
        results, ranges = calculate_change_distribution(
            [10, 12, 15],
            [5, 6, 5],
            2
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(len(ranges), 3)
        self.assertEqual(sum(results), 2)

    def test_change_distribution_zero_denominator(self):
        with self.assertRaises(ValueError) as ctx:
            calculate_change_distribution(
                [10, 20, 30],
                [5, 0, 10],
                5
            )
        self.assertIn("zero", str(ctx.exception))

    def test_calculate_sessions_single_element(self):
        """Single element — always counted as flat (prev == session)."""
        result = calculate_sessions([1.0])
        self.assertEqual(result["flat"], 1)
        self.assertEqual(result["rising"], 0)
        self.assertEqual(result["losing"], 0)

    def test_calculate_sessions_all_rising(self):
        """All rising sessions (first element counted as flat)."""
        result = calculate_sessions([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(result["rising"], 3)
        self.assertEqual(result["flat"], 1)
        self.assertEqual(result["losing"], 0)

    def test_calculate_sessions_all_falling(self):
        """All falling sessions (first element counted as flat)."""
        result = calculate_sessions([4.0, 3.0, 2.0, 1.0])
        self.assertEqual(result["losing"], 3)
        self.assertEqual(result["flat"], 1)
        self.assertEqual(result["rising"], 0)

    def test_calculate_sessions_total_count(self):
        """Sum of flat+rising+losing should equal the number of elements."""
        sessions = [1.0, 2.0, 1.5, 1.5, 3.0]
        result = calculate_sessions(sessions)
        total = result["flat"] + result["rising"] + result["losing"]
        self.assertEqual(total, len(sessions))

    def test_calculate_statistical_measures_median_value(self):
        """Verification of specific median value."""
        result = calculate_statistical_measures([1, 1, 2, 3, 4])
        self.assertEqual(result["median"], 2)

    def test_calculate_statistical_measures_stdev_zero(self):
        """Standard deviation for constant data should be 0."""
        result = calculate_statistical_measures([5, 5, 5, 5])
        self.assertEqual(result["standard deviation"], 0)

    def test_calculate_statistical_measures_keys_present(self):
        """All expected keys must be present in the result."""
        result = calculate_statistical_measures([1, 2, 3, 4, 5])
        expected_keys = {"median", "mode", "standard deviation", "coefficient of variation"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_change_distribution_steps_one(self):
        """steps=1 is the minimum allowed value."""
        results, ranges = calculate_change_distribution(
            [10, 20],
            [5, 8],
            1
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(sum(results), 1)

    def test_change_distribution_single_pair(self):
        """Two values in history — one change."""
        results, ranges = calculate_change_distribution(
            [10, 20],
            [5, 10],
            3
        )
        self.assertEqual(sum(results), 1)
        self.assertEqual(len(results), 3)

    def test_change_distribution_single_element_raises(self):
        """Single element list — requires at least 2 data points."""
        with self.assertRaises(ValueError) as ctx:
            calculate_change_distribution([10], [5], 2)
        self.assertIn("2 data points", str(ctx.exception))


class TestNBPSessions(unittest.TestCase):

    def test_subtract_months_end_of_month(self):
        """End of month — truncate to the last day of the target month."""
        self.assertEqual(
            subtract_months(date(2024, 3, 31), 1),
            date(2024, 2, 29)
        )

    def test_subtract_months_cross_year(self):
        """January minus 1 month = December of previous year."""
        self.assertEqual(
            subtract_months(date(2024, 1, 15), 1),
            date(2023, 12, 15)
        )

    def test_subtract_months_regular(self):
        """Normal subtraction of months without year change."""
        self.assertEqual(
            subtract_months(date(2024, 6, 15), 3),
            date(2024, 3, 15)
        )

    def test_subtract_months_full_year(self):
        """Subtract 12 months = same day a year earlier."""
        self.assertEqual(
            subtract_months(date(2024, 6, 15), 12),
            date(2023, 6, 15)
        )

    def test_subtract_months_february_non_leap(self):
        """May 31 minus 3 months = February 29 (leap year), truncated to end of month."""
        self.assertEqual(
            subtract_months(date(2024, 5, 31), 3),
            date(2024, 2, 29)  # 2024 is a leap year
        )

    def test_count_sessions(self):
        quotes = [
            Quote(date(2024, 1, 1), Decimal("1.0")),
            Quote(date(2024, 1, 2), Decimal("2.0")),
            Quote(date(2024, 1, 3), Decimal("1.5")),
            Quote(date(2024, 1, 4), Decimal("1.5")),
        ]

        rises, falls, unchanged = count_sessions(quotes)

        self.assertEqual(rises, 1)
        self.assertEqual(falls, 1)
        self.assertEqual(unchanged, 1)

    def test_count_sessions_empty(self):
        """Empty list — no pairs, all counters = 0."""
        rises, falls, unchanged = count_sessions([])
        self.assertEqual(rises, 0)
        self.assertEqual(falls, 0)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_single_quote(self):
        """Single quote — no pairs to compare."""
        quotes = [Quote(date(2024, 1, 1), Decimal("1.0"))]
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises, 0)
        self.assertEqual(falls, 0)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_all_rising(self):
        """All rising sessions."""
        quotes = [
            Quote(date(2024, 1, 1), Decimal("1.0")),
            Quote(date(2024, 1, 2), Decimal("2.0")),
            Quote(date(2024, 1, 3), Decimal("3.0")),
        ]
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises, 2)
        self.assertEqual(falls, 0)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_all_falling(self):
        """All falling sessions."""
        quotes = [
            Quote(date(2024, 1, 1), Decimal("3.0")),
            Quote(date(2024, 1, 2), Decimal("2.0")),
            Quote(date(2024, 1, 3), Decimal("1.0")),
        ]
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises, 0)
        self.assertEqual(falls, 2)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_sorted_by_date(self):
        """count_sessions sorts by date — input order does not matter."""
        quotes = [
            Quote(date(2024, 1, 3), Decimal("1.5")),
            Quote(date(2024, 1, 1), Decimal("1.0")),
            Quote(date(2024, 1, 2), Decimal("2.0")),
        ]
        rises, falls, unchanged = count_sessions(quotes)
        # After sorting: 1.0 -> 2.0 (rise), 2.0 -> 1.5 (fall)
        self.assertEqual(rises, 1)
        self.assertEqual(falls, 1)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_total(self):
        """Sum of sessions should be len(quotes) - 1."""
        quotes = [
            Quote(date(2024, 1, 1), Decimal("1.0")),
            Quote(date(2024, 1, 2), Decimal("2.0")),
            Quote(date(2024, 1, 3), Decimal("1.5")),
            Quote(date(2024, 1, 4), Decimal("1.5")),
            Quote(date(2024, 1, 5), Decimal("3.0")),
        ]
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises + falls + unchanged, len(quotes) - 1)


class TestBuildPeriods(unittest.TestCase):
    """Tests for build_periods function from nbp_sessions."""

    def setUp(self):
        from nbp_sessions import build_periods
        self.build_periods = build_periods
        self.today = date(2024, 6, 15)
        self.periods = self.build_periods(self.today)

    def test_build_periods_returns_six(self):
        """build_periods should return exactly 6 periods."""
        self.assertEqual(len(self.periods), 6)

    def test_build_periods_labels(self):
        """Verification of all returned period names."""
        labels = [p[0] for p in self.periods]
        expected_labels = [
            "Last 1 week",
            "Last 2 weeks",
            "Last 1 month",
            "Last 1 quarter",
            "Last 6 months",
            "Last 1 year",
        ]
        self.assertEqual(labels, expected_labels)

    def test_build_periods_one_week_date(self):
        """Date for 'Last 1 week' should be 7 days ago."""
        from datetime import timedelta
        week_start = [p[1] for p in self.periods if p[0] == "Last 1 week"][0]
        self.assertEqual(week_start, self.today - timedelta(days=7))

    def test_build_periods_dates_are_in_the_past(self):
        """Each period start date should be before today."""
        for label, start_date in self.periods:
            self.assertLess(start_date, self.today, msg=f"Failed for period: {label}")

    def test_build_periods_dates_ordered(self):
        """Start dates should be in descending order (shortest -> longest)."""
        dates = [p[1] for p in self.periods]
        self.assertEqual(dates, sorted(dates, reverse=True))


if __name__ == "__main__":
    unittest.main()
