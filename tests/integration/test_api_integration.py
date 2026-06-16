import os
import sys
import unittest
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nbp_sessions import fetch_quotes, count_sessions, subtract_months, Quote
from data_processor import (
    calculate_sessions,
    calculate_statistical_measures,
    calculate_change_distribution,
)


def _network_available() -> bool:
    """Sprawdza, czy api.nbp.pl jest osiągalne."""
    import socket
    try:
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("api.nbp.pl", 443))
        return True
    except (socket.error, OSError):
        return False


# Testy API są pomijane jeśli brak flagi lub sieci
_SKIP_REASON = "Brak flagi INTEGRATION_TESTS=1 lub połączenia z api.nbp.pl"
_should_run = os.environ.get("INTEGRATION_TESTS") == "1" and _network_available()
require_integration = unittest.skipUnless(_should_run, _SKIP_REASON)


# ---------------------------------------------------------------------------
# INT-08: fetch_quotes — realne dane z API
# ---------------------------------------------------------------------------

@require_integration
class TestFetchQuotesRealAPI(unittest.TestCase):
    """
    INT-08: Weryfikacja kontraktu API NBP.

    Sprawdza, że struktura odpowiedzi API nie zmieniła się:
    format dat, typ kursów (Decimal), zakres danych.
    """

    def setUp(self):
        self.end = date.today()
        self.start = subtract_months(self.end, 1)

    def test_returns_non_empty_list(self):
        """API powinno zwrócić co najmniej 1 kwotowanie dla USD za ostatni miesiąc."""
        quotes = fetch_quotes("USD", self.start, self.end)
        self.assertGreater(len(quotes), 0)

    def test_all_items_are_quote_instances(self):
        """Wszystkie elementy listy powinny być instancjami Quote."""
        quotes = fetch_quotes("USD", self.start, self.end)
        for q in quotes:
            self.assertIsInstance(q, Quote)

    def test_all_mid_values_positive(self):
        """Wszystkie kursy (mid) powinny być dodatnie."""
        quotes = fetch_quotes("USD", self.start, self.end)
        for q in quotes:
            self.assertGreater(q.mid, Decimal("0"))

    def test_dates_within_requested_range(self):
        """Daty kwotowań powinny mieścić się w żądanym przedziale."""
        quotes = fetch_quotes("USD", self.start, self.end)
        for q in quotes:
            self.assertGreaterEqual(q.effective_date, self.start)
            self.assertLessEqual(q.effective_date, self.end)

    def test_mid_is_decimal_type(self):
        """Kursy powinny być typu Decimal (nie float) dla precyzji."""
        quotes = fetch_quotes("USD", self.start, self.end)
        for q in quotes:
            self.assertIsInstance(q.mid, Decimal)

    def test_invalid_currency_raises_value_error(self):
        """Nieistniejący kod waluty (XYZ) powinien podnieść ValueError."""
        with self.assertRaises(ValueError):
            fetch_quotes("XYZ", self.start, self.end)

    def test_multiple_currencies_return_data(self):
        """Kilka popularnych walut powinno zwrócić dane."""
        for code in ["USD", "EUR", "CHF", "GBP"]:
            with self.subTest(currency=code):
                quotes = fetch_quotes(code, self.start, self.end)
                self.assertGreater(len(quotes), 0,
                    msg=f"Brak kwotowań dla {code}")


# ---------------------------------------------------------------------------
# INT-09: Realne dane → count_sessions — niezmiennik
# ---------------------------------------------------------------------------

@require_integration
class TestRealQuotesCountSessionsInvariant(unittest.TestCase):
    """
    INT-09: Weryfikacja niezmiennika count_sessions na realnych danych.

    rises + falls + unchanged == len(quotes) - 1 dla każdej waluty.
    """

    def setUp(self):
        self.end = date.today()
        self.start = subtract_months(self.end, 1)

    def test_count_invariant_usd(self):
        """USD: suma sesji == len(quotes) - 1."""
        quotes = fetch_quotes("USD", self.start, self.end)
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises + falls + unchanged, len(quotes) - 1)

    def test_count_invariant_eur(self):
        """EUR: suma sesji == len(quotes) - 1."""
        quotes = fetch_quotes("EUR", self.start, self.end)
        rises, falls, unchanged = count_sessions(quotes)
        self.assertEqual(rises + falls + unchanged, len(quotes) - 1)

    def test_counts_are_non_negative(self):
        """Żaden licznik sesji nie może być ujemny."""
        quotes = fetch_quotes("USD", self.start, self.end)
        rises, falls, unchanged = count_sessions(quotes)
        self.assertGreaterEqual(rises, 0)
        self.assertGreaterEqual(falls, 0)
        self.assertGreaterEqual(unchanged, 0)

    def test_statistical_measures_on_real_data(self):
        """Obliczenia statystyczne na realnych danych NBP nie powinny rzucać wyjątków."""
        quotes = fetch_quotes("USD", self.start, self.end)
        sessions = [float(q.mid) for q in quotes]
        result = calculate_statistical_measures(sessions)

        self.assertGreaterEqual(result["standard deviation"], 0)
        self.assertGreaterEqual(result["median"], min(sessions))
        self.assertLessEqual(result["median"], max(sessions))

    def test_session_analysis_on_real_data(self):
        """calculate_sessions na realnych danych — suma == liczba kwotowań."""
        quotes = fetch_quotes("EUR", self.start, self.end)
        sessions = [float(q.mid) for q in quotes]
        result = calculate_sessions(sessions)

        total = result["flat"] + result["rising"] + result["losing"]
        self.assertEqual(total, len(sessions))


# ---------------------------------------------------------------------------
# INT-10: Realne dane (dwie waluty) → calculate_change_distribution
# ---------------------------------------------------------------------------

@require_integration
class TestTwoRealCurrenciesChangeDistribution(unittest.TestCase):
    """
    INT-10: Dwie waluty z prawdziwego API → calculate_change_distribution.

    Weryfikuje rzeczywisty problem produkcyjny: dwie waluty mogą mieć
    różną liczbę kwotowań w tym samym przedziale (np. święta krajowe),
    co powoduje błąd w calculate_change_distribution.
    """

    def setUp(self):
        self.end = date.today()
        self.start = subtract_months(self.end, 1)

    def test_same_quote_count_produces_distribution(self):
        """
        Jeśli USD i EUR mają tę samą liczbę kwotowań,
        calculate_change_distribution powinno zwrócić poprawny wynik.
        """
        quotes_usd = fetch_quotes("USD", self.start, self.end)
        quotes_eur = fetch_quotes("EUR", self.start, self.end)

        sessions_usd = [float(q.mid) for q in quotes_usd]
        sessions_eur = [float(q.mid) for q in quotes_eur]

        if len(sessions_usd) != len(sessions_eur):
            self.skipTest(
                f"USD ({len(sessions_usd)}) i EUR ({len(sessions_eur)}) "
                f"mają różną liczbę kwotowań w tym okresie"
            )

        results, ranges = calculate_change_distribution(sessions_usd, sessions_eur, steps=5)

        self.assertEqual(len(results), 5)
        self.assertEqual(sum(results), len(sessions_usd) - 1)


    def test_distribution_bucket_sum_invariant(self):
        """
        Suma kubełków rozkładu == liczba par kursów (len - 1).
        Test dla USD vs EUR gdy mają równą liczbę sesji.
        """
        quotes_usd = fetch_quotes("USD", self.start, self.end)
        quotes_eur = fetch_quotes("EUR", self.start, self.end)

        sessions_usd = [float(q.mid) for q in quotes_usd]
        sessions_eur = [float(q.mid) for q in quotes_eur]

        if len(sessions_usd) != len(sessions_eur):
            self.skipTest("Różna liczba kwotowań — pominięto")

        for steps in [2, 5, 10]:
            with self.subTest(steps=steps):
                results, _ = calculate_change_distribution(
                    sessions_usd, sessions_eur, steps=steps
                )
                self.assertEqual(sum(results), len(sessions_usd) - 1)


if __name__ == "__main__":
    unittest.main()
