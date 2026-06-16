import unittest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nbp_wrapper import _nbp_rates_link, _fetch_nbp_rates, get_nbp_rates


class TestNBPRatesLink(unittest.TestCase):
    """
    Testy generowania URL przez _nbp_rates_link.
    UWAGA: W nbp_wrapper.py istnieją dwie funkcje o tej samej nazwie —
    druga definicja (last N sessions) nadpisuje pierwszą (zakres dat).
    Testujemy tylko wersję, która faktycznie istnieje w runtime.
    """

    def test_url_contains_currency_code(self):
        """URL powinien zawierać podany kod waluty."""
        url = _nbp_rates_link("USD", 10)
        self.assertIn("USD", url)

    def test_url_contains_session_count(self):
        """URL powinien zawierać liczbę sesji w ścieżce 'last/N'."""
        url = _nbp_rates_link("EUR", 5)
        self.assertIn("last/5", url)

    def test_url_contains_nbp_domain(self):
        """URL powinien wskazywać na API NBP."""
        url = _nbp_rates_link("CHF", 1)
        self.assertIn("api.nbp.pl", url)

    def test_url_is_string(self):
        """Funkcja powinna zwracać string."""
        url = _nbp_rates_link("GBP", 3)
        self.assertIsInstance(url, str)

    def test_url_currency_lowercase_preserved(self):
        """Kod waluty wpisany małymi literami powinien być zachowany w URL."""
        url = _nbp_rates_link("usd", 10)
        self.assertIn("usd", url)

    def test_url_different_session_counts(self):
        """Różne liczby sesji powinny generować różne URL-e."""
        url_5 = _nbp_rates_link("USD", 5)
        url_10 = _nbp_rates_link("USD", 10)
        self.assertNotEqual(url_5, url_10)

    def test_url_different_currencies(self):
        """Różne waluty powinny generować różne URL-e."""
        url_usd = _nbp_rates_link("USD", 5)
        url_eur = _nbp_rates_link("EUR", 5)
        self.assertNotEqual(url_usd, url_eur)


class TestFetchNBPRates(unittest.TestCase):
    """Testy _fetch_nbp_rates z mockowanym requests.get."""

    @patch("nbp_wrapper.requests.get")
    def test_success_returns_json(self, mock_get):
        """Status 200 — powinien zwrócić sparsowany JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": [{"mid": 4.0}]}
        mock_get.return_value = mock_response

        result = _fetch_nbp_rates("http://example.com")

        self.assertEqual(result["rates"][0]["mid"], 4.0)

    @patch("nbp_wrapper.requests.get")
    def test_success_calls_get_with_url(self, mock_get):
        """requests.get powinien być wywołany z przekazanym URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        _fetch_nbp_rates("http://test-url.com")

        mock_get.assert_called_once_with("http://test-url.com")

    @patch("nbp_wrapper.requests.get")
    def test_error_404_raises_value_error(self, mock_get):
        """Status 404 — powinien podnieść ValueError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            _fetch_nbp_rates("http://example.com")

    @patch("nbp_wrapper.requests.get")
    def test_error_500_raises_value_error(self, mock_get):
        """Status 500 — powinien podnieść ValueError."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            _fetch_nbp_rates("http://example.com")

    @patch("nbp_wrapper.requests.get")
    def test_error_non_200_raises_value_error(self, mock_get):
        """Dowolny status != 200 — powinien podnieść ValueError."""
        for status in [400, 403, 404, 500, 503]:
            with self.subTest(status=status):
                mock_response = MagicMock()
                mock_response.status_code = status
                mock_get.return_value = mock_response

                with self.assertRaises(ValueError):
                    _fetch_nbp_rates("http://example.com")

    @patch("nbp_wrapper.requests.get")
    def test_empty_rates_still_returned(self, mock_get):
        """Status 200 z pustą listą rates — powinien zwrócić strukturę bez błędu."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": []}
        mock_get.return_value = mock_response

        result = _fetch_nbp_rates("http://example.com")

        self.assertEqual(result["rates"], [])


class TestGetNBPRates(unittest.TestCase):
    """Testy get_nbp_rates (wersja z liczbą sesji) z mockowanym requests.get."""

    @patch("nbp_wrapper.requests.get")
    def test_returns_data_for_valid_input(self, mock_get):
        """Poprawne dane wejściowe — powinien zwrócić wynik z API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "currency": "US dollar",
            "code": "USD",
            "rates": [{"no": "001/A/NBP/2024", "effectiveDate": "2024-01-02", "mid": 4.0}]
        }
        mock_get.return_value = mock_response

        result = get_nbp_rates("USD", 1)

        self.assertIn("rates", result)
        self.assertEqual(len(result["rates"]), 1)

    @patch("nbp_wrapper.requests.get")
    def test_raises_on_api_error(self, mock_get):
        """Błąd API (status != 200) — get_nbp_rates powinien propagować ValueError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            get_nbp_rates("XYZ", 5)

    @patch("nbp_wrapper.requests.get")
    def test_get_is_called_once(self, mock_get):
        """Dla jednego wywołania get_nbp_rates, requests.get powinien być wywołany raz."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": []}
        mock_get.return_value = mock_response

        get_nbp_rates("EUR", 3)

        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
