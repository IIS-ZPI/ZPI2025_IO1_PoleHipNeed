import unittest
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
        with self.assertRaises(ValueError):
            calculate_change_distribution([1, 2], [1], 5)

    def test_change_distribution_invalid_steps(self):
        with self.assertRaises(ValueError):
            calculate_change_distribution([1, 2], [1, 2], 0)

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
        with self.assertRaises(ValueError):
            calculate_change_distribution(
                [10, 20, 30],
                [5, 0, 10],
                5
            )


class TestNBPSessions(unittest.TestCase):

    def test_subtract_months_end_of_month(self):
        self.assertEqual(
            subtract_months(date(2024, 3, 31), 1),
            date(2024, 2, 29)
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


if __name__ == "__main__":
    unittest.main()
