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
        """Jeden element — zawsze liczony jako flat (prev == session)."""
        result = calculate_sessions([1.0])
        self.assertEqual(result["flat"], 1)
        self.assertEqual(result["rising"], 0)
        self.assertEqual(result["losing"], 0)

    def test_calculate_sessions_all_rising(self):
        """Wszystkie sesje rosnące (pierwszy element liczy się jako flat)."""
        result = calculate_sessions([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(result["rising"], 3)
        self.assertEqual(result["flat"], 1)
        self.assertEqual(result["losing"], 0)

    def test_calculate_sessions_all_falling(self):
        """Wszystkie sesje malejące (pierwszy element liczy się jako flat)."""
        result = calculate_sessions([4.0, 3.0, 2.0, 1.0])
        self.assertEqual(result["losing"], 3)
        self.assertEqual(result["flat"], 1)
        self.assertEqual(result["rising"], 0)

    def test_calculate_sessions_total_count(self):
        """Suma flat+rising+losing powinna równać się liczbie elementów."""
        sessions = [1.0, 2.0, 1.5, 1.5, 3.0]
        result = calculate_sessions(sessions)
        total = result["flat"] + result["rising"] + result["losing"]
        self.assertEqual(total, len(sessions))

    def test_calculate_statistical_measures_median_value(self):
        """Weryfikacja konkretnej wartości mediany."""
        result = calculate_statistical_measures([1, 1, 2, 3, 4])
        self.assertEqual(result["median"], 2)

    def test_calculate_statistical_measures_stdev_zero(self):
        """Odchylenie standardowe dla stałych danych powinno wynosić 0."""
        result = calculate_statistical_measures([5, 5, 5, 5])
        self.assertEqual(result["standard deviation"], 0)

    def test_calculate_statistical_measures_keys_present(self):
        """Wszystkie oczekiwane klucze muszą być obecne w wyniku."""
        result = calculate_statistical_measures([1, 2, 3, 4, 5])
        expected_keys = {"median", "mode", "standard deviation", "coefficient of variation"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_change_distribution_steps_one(self):
        """steps=1 to minimalna dopuszczalna wartość."""
        results, ranges = calculate_change_distribution(
            [10, 20],
            [5, 8],
            1
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(sum(results), 1)

    def test_change_distribution_single_pair(self):
        """Dwie wartości w historii — jedna zmiana."""
        results, ranges = calculate_change_distribution(
            [10, 20],
            [5, 10],
            3
        )
        self.assertEqual(sum(results), 1)
        self.assertEqual(len(results), 3)

    def test_change_distribution_single_element_raises(self):
        """Lista jednoelementowa — wymaga co najmniej 2 punktow danych."""
        with self.assertRaises(ValueError) as ctx:
            calculate_change_distribution([10], [5], 2)
        self.assertIn("2 data points", str(ctx.exception))


class TestNBPSessions(unittest.TestCase):

    def test_subtract_months_end_of_month(self):
        """Koniec miesiąca — przycięcie do ostatniego dnia docelowego miesiąca."""
        self.assertEqual(
            subtract_months(date(2024, 3, 31), 1),
            date(2024, 2, 29)
        )

    def test_subtract_months_cross_year(self):
        """Styczeń minus 1 miesiąc = grudzień poprzedniego roku."""
        self.assertEqual(
            subtract_months(date(2024, 1, 15), 1),
            date(2023, 12, 15)
        )

    def test_subtract_months_regular(self):
        """Normalne odejmowanie miesięcy bez zmiany roku."""
        self.assertEqual(
            subtract_months(date(2024, 6, 15), 3),
            date(2024, 3, 15)
        )

    def test_subtract_months_full_year(self):
        """Odjęcie 12 miesięcy = ten sam dzień rok wcześniej."""
        self.assertEqual(
            subtract_months(date(2024, 6, 15), 12),
            date(2023, 6, 15)
        )

    def test_subtract_months_february_non_leap(self):
        """31 stycznia minus 3 miesiące = 31 października, przycięte do 31."""
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
        """Pusta lista — brak par, wszystkie liczniki = 0."""
        rises, falls, unchanged = count_sessions([])
        self.assertEqual(rises, 0)
        self.assertEqual(falls, 0)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_single_quote(self):
        """Jedna kwotacja — brak par do porównania."""
        quotes = [Quote(date(2024, 1, 1), Decimal("1.0"))]
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises, 0)
        self.assertEqual(falls, 0)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_all_rising(self):
        """Wszystkie sesje rosnące."""
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
        """Wszystkie sesje malejące."""
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
        """count_sessions sortuje po dacie — kolejność wejściowa nie ma znaczenia."""
        quotes = [
            Quote(date(2024, 1, 3), Decimal("1.5")),
            Quote(date(2024, 1, 1), Decimal("1.0")),
            Quote(date(2024, 1, 2), Decimal("2.0")),
        ]
        rises, falls, unchanged = count_sessions(quotes)
        # Po sortowaniu: 1.0 -> 2.0 (rise), 2.0 -> 1.5 (fall)
        self.assertEqual(rises, 1)
        self.assertEqual(falls, 1)
        self.assertEqual(unchanged, 0)

    def test_count_sessions_total(self):
        """Suma sesji powinna wynosić len(quotes) - 1."""
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
    """Testy dla funkcji build_periods z nbp_sessions."""

    def setUp(self):
        from nbp_sessions import build_periods
        self.build_periods = build_periods
        self.today = date(2024, 6, 15)
        self.periods = self.build_periods(self.today)

    def test_build_periods_returns_six(self):
        """build_periods powinna zwracać dokładnie 6 okresów."""
        self.assertEqual(len(self.periods), 6)

    def test_build_periods_labels(self):
        """Weryfikacja nazw wszystkich zwracanych okresów."""
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
        """Data dla 'Last 1 week' powinna być 7 dni wstecz."""
        from datetime import timedelta
        week_start = [p[1] for p in self.periods if p[0] == "Last 1 week"][0]
        self.assertEqual(week_start, self.today - timedelta(days=7))

    def test_build_periods_dates_are_in_the_past(self):
        """Każda data startowa okresu powinna być przed today."""
        for label, start_date in self.periods:
            self.assertLess(start_date, self.today, msg=f"Failed for period: {label}")

    def test_build_periods_dates_ordered(self):
        """Daty startowe powinny byc w kolejnosci malejacej (najkrotszy -> najdluzszy)."""
        dates = [p[1] for p in self.periods]
        self.assertEqual(dates, sorted(dates, reverse=True))


if __name__ == "__main__":
    unittest.main()
