import sys
import os
import unittest
from datetime import date
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nbp_sessions import fetch_quotes, count_sessions, subtract_months, Quote
from data_processor import (
    calculate_sessions,
    calculate_statistical_measures,
    calculate_change_distribution,
)
from CLI import AnalysisPeriod


def _make_mock_response(rates: list) -> MagicMock:
    """Helper — creates a mocked HTTP response object with the provided rates."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"rates": rates}
    return mock_resp


# ---------------------------------------------------------------------------
# INT-01: fetch_quotes → calculate_sessions
# ---------------------------------------------------------------------------

class TestFetchQuotesIntoCalculateSessions(unittest.TestCase):
    """
    INT-01: Integration nbp_sessions.fetch_quotes + data_processor.calculate_sessions.

    Verifies that:
    - data returned by fetch_quotes (Decimal type in Quote.mid) is correctly
      converted to float before passing to calculate_sessions,
    - session results are consistent with actual rate changes,
    - sum of flat+rising+losing == number of quotes.
    """

    @patch("nbp_sessions.requests.get")
    def test_rising_then_falling_session(self, mock_get):
        """Rate rises, then falls — expected 1 rising and 1 losing."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
            {"effectiveDate": "2024-01-04", "mid": 4.05},
        ])

        quotes = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 4))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_sessions(sessions)

        self.assertEqual(result["rising"], 1)
        self.assertEqual(result["losing"], 1)
        self.assertEqual(result["flat"], 1)  # first element is always flat

    @patch("nbp_sessions.requests.get")
    def test_total_count_equals_number_of_quotes(self, mock_get):
        """Sum of all session types must equal the number of quotes."""
        rates = [{"effectiveDate": f"2024-01-{i:02d}", "mid": 4.0 + i * 0.01}
                 for i in range(2, 10)]
        mock_get.return_value = _make_mock_response(rates)

        quotes = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 9))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_sessions(sessions)

        total = result["flat"] + result["rising"] + result["losing"]
        self.assertEqual(total, len(sessions))

    @patch("nbp_sessions.requests.get")
    def test_flat_rate_detected(self, mock_get):
        """Constant rates — all sessions should be flat."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.00},
            {"effectiveDate": "2024-01-04", "mid": 4.00},
        ])

        quotes = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 4))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_sessions(sessions)

        self.assertEqual(result["flat"], 3)
        self.assertEqual(result["rising"], 0)
        self.assertEqual(result["losing"], 0)

    @patch("nbp_sessions.requests.get")
    def test_quotes_sorted_by_date_before_processing(self, mock_get):
        """
        API can return rates in any order.
        fetch_quotes does not sort — but count_sessions sorts.
        We check if the results are identical regardless of the input order.
        """
        ordered_rates = [
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
            {"effectiveDate": "2024-01-04", "mid": 4.05},
        ]
        reversed_rates = list(reversed(ordered_rates))

        mock_get.return_value = _make_mock_response(ordered_rates)
        quotes_ordered = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 4))

        mock_get.return_value = _make_mock_response(reversed_rates)
        quotes_reversed = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 4))

        rises_o, falls_o, unch_o = count_sessions(quotes_ordered)
        rises_r, falls_r, unch_r = count_sessions(quotes_reversed)

        self.assertEqual(rises_o, rises_r)
        self.assertEqual(falls_o, falls_r)
        self.assertEqual(unch_o, unch_r)


# ---------------------------------------------------------------------------
# INT-02: fetch_quotes → calculate_statistical_measures
# ---------------------------------------------------------------------------

class TestFetchQuotesIntoStatisticalMeasures(unittest.TestCase):
    """
    INT-02: Integration nbp_sessions.fetch_quotes + data_processor.calculate_statistical_measures.

    Verifies that real data from the API can be processed by the statistical module
    without exceptions and that the results make sense (e.g. stdev >= 0, median within data range).
    """

    @patch("nbp_sessions.requests.get")
    def test_statistical_measures_no_exception(self, mock_get):
        """Statistical calculations on data from the API should not raise exceptions."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": f"2024-01-{i:02d}", "mid": 3.90 + i * 0.05}
            for i in range(2, 7)
        ])

        quotes = fetch_quotes("EUR", date(2024, 1, 2), date(2024, 1, 6))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_statistical_measures(sessions)

        self.assertIn("median", result)
        self.assertIn("standard deviation", result)

    @patch("nbp_sessions.requests.get")
    def test_stdev_non_negative(self, mock_get):
        """Standard deviation should always be >= 0."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.10},
            {"effectiveDate": "2024-01-03", "mid": 4.05},
            {"effectiveDate": "2024-01-04", "mid": 4.20},
            {"effectiveDate": "2024-01-05", "mid": 3.95},
            {"effectiveDate": "2024-01-06", "mid": 4.15},
        ])

        quotes = fetch_quotes("EUR", date(2024, 1, 2), date(2024, 1, 6))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_statistical_measures(sessions)

        self.assertGreaterEqual(result["standard deviation"], 0)

    @patch("nbp_sessions.requests.get")
    def test_median_within_data_range(self, mock_get):
        """Median should be within the [min, max] range of the data."""
        rates_values = [4.10, 4.05, 4.20, 3.95, 4.15]
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": f"2024-01-{i+2:02d}", "mid": v}
            for i, v in enumerate(rates_values)
        ])

        quotes = fetch_quotes("EUR", date(2024, 1, 2), date(2024, 1, 6))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_statistical_measures(sessions)

        self.assertGreaterEqual(result["median"], min(sessions))
        self.assertLessEqual(result["median"], max(sessions))

    @patch("nbp_sessions.requests.get")
    def test_stdev_zero_for_constant_rates(self, mock_get):
        """Constant currency rate -> standard deviation = 0."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": f"2024-01-{i:02d}", "mid": 4.00}
            for i in range(2, 7)
        ])

        quotes = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 6))
        sessions = [float(q.mid) for q in quotes]
        result = calculate_statistical_measures(sessions)

        self.assertEqual(result["standard deviation"], 0)


# ---------------------------------------------------------------------------
# INT-03: fetch_quotes (dwie waluty) → calculate_change_distribution
# ---------------------------------------------------------------------------

class TestTwoCurrenciesIntoChangeDistribution(unittest.TestCase):
    """
    INT-03: Integration of two fetch_quotes calls + calculate_change_distribution.

    Verifies the data flow for two currencies through the entire chain:
    API mock -> Quote objects -> float -> calculate_change_distribution.
    """

    @patch("nbp_sessions.requests.get")
    def test_change_distribution_two_currencies(self, mock_get):
        """Two currencies, same number of quotes — correct change distribution."""
        rates_usd = {"rates": [
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
            {"effectiveDate": "2024-01-04", "mid": 4.05},
        ]}
        rates_eur = {"rates": [
            {"effectiveDate": "2024-01-02", "mid": 4.30},
            {"effectiveDate": "2024-01-03", "mid": 4.35},
            {"effectiveDate": "2024-01-04", "mid": 4.28},
        ]}

        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [rates_usd, rates_eur]

        quotes_usd = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 4))
        quotes_eur = fetch_quotes("EUR", date(2024, 1, 2), date(2024, 1, 4))

        sessions_usd = [float(q.mid) for q in quotes_usd]
        sessions_eur = [float(q.mid) for q in quotes_eur]

        results, ranges = calculate_change_distribution(sessions_usd, sessions_eur, steps=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(len(ranges), 3)
        self.assertEqual(sum(results), len(sessions_usd) - 1)

    @patch("nbp_sessions.requests.get")
    def test_mismatched_quote_counts_raises(self, mock_get):
        """
        If two currencies have a different number of quotes (e.g. public holidays),
        calculate_change_distribution should raise a ValueError.
        """
        rates_usd = {"rates": [
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
        ]}
        rates_eur = {"rates": [
            {"effectiveDate": "2024-01-02", "mid": 4.30},
        ]}

        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [rates_usd, rates_eur]

        quotes_usd = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 3))
        quotes_eur = fetch_quotes("EUR", date(2024, 1, 2), date(2024, 1, 2))

        sessions_usd = [float(q.mid) for q in quotes_usd]
        sessions_eur = [float(q.mid) for q in quotes_eur]

        with self.assertRaises(ValueError):
            calculate_change_distribution(sessions_usd, sessions_eur, steps=5)

    @patch("nbp_sessions.requests.get")
    def test_distribution_buckets_sum_equals_changes_count(self, mock_get):
        """Sum of all distribution buckets == number of quote pairs."""
        rates = [{"effectiveDate": f"2024-01-{i:02d}", "mid": 4.0 + i * 0.02}
                 for i in range(2, 8)]

        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [{"rates": rates}, {"rates": rates}]

        q1 = fetch_quotes("USD", date(2024, 1, 2), date(2024, 1, 7))
        q2 = fetch_quotes("EUR", date(2024, 1, 2), date(2024, 1, 7))

        s1 = [float(q.mid) for q in q1]
        s2 = [float(q.mid) for q in q2]

        results, _ = calculate_change_distribution(s1, s2, steps=3)

        self.assertEqual(sum(results), len(s1) - 1)


# ---------------------------------------------------------------------------
# INT-04: data_proceser.get_date_range → date ranges consistency
# ---------------------------------------------------------------------------

class TestGetDateRangeDateConsistency(unittest.TestCase):
    """
    INT-04: Integration data_proceser.get_date_range + nbp_sessions.subtract_months.

    Verifies that date ranges generated by the orchestrator are correct:
    - start < end for each period,
    - end == date.today(),
    - ranges do not overlap in an illogical way.
    """

    def setUp(self):
        """Creates a data_proceser instance without CLI initialization."""
        import dataflow_manager as dp_module
        self.dp = object.__new__(dp_module.DataflowManager)

    def test_all_periods_have_start_before_end(self):
        """For each AnalysisPeriod: start < end."""
        for period in AnalysisPeriod:
            with self.subTest(period=period.name):
                start, end = self.dp.get_date_range(period)
                self.assertLess(start, end,
                    msg=f"start >= end for period {period.name}")

    def test_end_date_is_today(self):
        """End date should always be today's date."""
        today = date.today()
        for period in AnalysisPeriod:
            with self.subTest(period=period.name):
                _, end = self.dp.get_date_range(period)
                self.assertEqual(end, today)

    def test_longer_period_has_earlier_start(self):
        """Longer period should have an earlier start date."""
        start_week, _ = self.dp.get_date_range(AnalysisPeriod.ONE_WEEK)
        start_year, _ = self.dp.get_date_range(AnalysisPeriod.ONE_YEAR)
        self.assertLess(start_year, start_week)

    def test_one_week_range_is_seven_days(self):
        """ONE_WEEK range should be exactly 7 days."""
        start, end = self.dp.get_date_range(AnalysisPeriod.ONE_WEEK)
        self.assertEqual((end - start).days, 7)

    def test_unknown_period_returns_same_day_range(self):
        """Unknown period (fallback) returns zero range: start == end == today."""
        start, end = self.dp.get_date_range(None)
        self.assertEqual(start, end)
        self.assertEqual(start, date.today())


if __name__ == "__main__":
    unittest.main()
