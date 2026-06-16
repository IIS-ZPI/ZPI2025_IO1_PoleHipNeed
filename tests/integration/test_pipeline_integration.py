import csv
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import data_proceser as dp_module
from CLI import AnalysisType, AnalysisPeriod, Currency


def _make_mock_response(rates: list) -> MagicMock:
    """Pomocnik — tworzy zamockowany obiekt odpowiedzi HTTP."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"rates": rates}
    return mock_resp


def _build_dp(analysis_type, currency, period=None,
              secondary_currency=None, start_date=None, change_period=None):
    """
    Tworzy instancję data_proceser z wstrzykniętym zamockowanym CLI.
    Omija __init__ (który instantiuje prawdziwe CLI z efektami ubocznymi).
    """
    instance = object.__new__(dp_module.data_proceser)

    mock_cli = MagicMock()
    mock_cli.selected_analysis = analysis_type
    mock_cli.selected_currency = currency
    mock_cli.secondary_currency = secondary_currency
    mock_cli.analysis_period = period
    mock_cli.start_date = start_date
    mock_cli.change_period = change_period

    # Jeden obrót pętli — potem zatrzymaj
    mock_cli.ask_repeat.return_value = False
    mock_cli.ask_export.return_value = False

    instance.cli = mock_cli
    return instance


# ---------------------------------------------------------------------------
# INT-05: obsługa błędu API — nie crashuje aplikacji
# ---------------------------------------------------------------------------

class TestAPIErrorHandledGracefully(unittest.TestCase):
    """
    INT-05: data_proceser.run() łapie błędy HTTP i nie propaguje wyjątku.

    Weryfikuje, że try/except w run() działa poprawnie dla różnych typów błędów.
    """

    @patch("nbp_sessions.requests.get")
    def test_api_404_does_not_crash(self, mock_get):
        """Status 404 z API — run() powinien zakończyć się bez wyjątku."""
        mock_get.return_value.status_code = 404

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        try:
            dp.run()
        except Exception as e:
            self.fail(f"run() rzucił nieoczekiwany wyjątek: {e}")

    @patch("nbp_sessions.requests.get")
    def test_network_error_does_not_crash(self, mock_get):
        """Błąd sieciowy (RequestException) — run() powinien go obsłużyć."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("timeout")

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        try:
            dp.run()
        except Exception as e:
            self.fail(f"run() rzucił nieoczekiwany wyjątek: {e}")

    @patch("nbp_sessions.requests.get")
    def test_error_message_displayed_to_user(self, mock_get):
        """Po błędzie API, CLI powinno wyświetlić komunikat błędu."""
        mock_get.return_value.status_code = 404

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        dp.run()

        dp.cli.my_print.assert_called_with('error', unittest.mock.ANY)

    @patch("nbp_sessions.requests.get")
    def test_run_exits_after_ask_repeat_false(self, mock_get):
        """run() powinien zakończyć pętlę gdy ask_repeat() zwraca False."""
        mock_get.return_value.status_code = 404

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()
        dp.cli.ask_repeat.return_value = False

        dp.run()

        dp.cli.ask_repeat.assert_called_once()


# ---------------------------------------------------------------------------
# INT-06: Pełny pipeline SESSION_ANALYSIS
# ---------------------------------------------------------------------------

class TestFullSessionAnalysisPipeline(unittest.TestCase):
    """
    INT-06: Pełny pipeline dla analizy sesji.

    Sprawdza, że dane przechodzą przez: fetch_quotes → calculate_sessions
    → display_table z poprawnymi wartościami i strukturą tabeli.
    """

    @patch("nbp_sessions.requests.get")
    def test_display_table_called_with_correct_title(self, mock_get):
        """Tytuł tabeli dla SESSION_ANALYSIS powinien brzmieć 'Session Analysis'."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
        ])

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        dp.run()

        dp.cli.display_table.assert_called_once()
        _, _, title = dp.cli.display_table.call_args[0]
        self.assertEqual(title, "Session Analysis")

    @patch("nbp_sessions.requests.get")
    def test_display_table_has_three_rows(self, mock_get):
        """Tabela SESSION_ANALYSIS powinna mieć 3 wiersze: Rising, Losing, Flat."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
            {"effectiveDate": "2024-01-04", "mid": 4.05},
        ])

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        dp.run()

        table, headers, _ = dp.cli.display_table.call_args[0]
        self.assertEqual(len(table), 3)
        row_labels = [row[0] for row in table]
        self.assertIn("Rising", row_labels)
        self.assertIn("Losing", row_labels)
        self.assertIn("Flat", row_labels)

    @patch("nbp_sessions.requests.get")
    def test_session_counts_sum_equals_number_of_quotes(self, mock_get):
        """Suma Rising+Losing+Flat w tabeli == liczba kwotowań."""
        n_quotes = 5
        rates = [{"effectiveDate": f"2024-01-{i+2:02d}", "mid": 4.0 + i * 0.01}
                 for i in range(n_quotes)]
        mock_get.return_value = _make_mock_response(rates)

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        dp.run()

        table, _, _ = dp.cli.display_table.call_args[0]
        total = sum(row[1] for row in table)
        self.assertEqual(total, n_quotes)

    @patch("nbp_sessions.requests.get")
    def test_correct_headers_for_session_analysis(self, mock_get):
        """Nagłówki tabeli SESSION_ANALYSIS: ['Measure', 'Result']."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
        ])

        dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                       period=AnalysisPeriod.ONE_WEEK)
        dp.cli.acquire_information = MagicMock()

        dp.run()

        _, headers, _ = dp.cli.display_table.call_args[0]
        self.assertEqual(headers, ["Measure", "Result"])


# ---------------------------------------------------------------------------
# INT-07: Export CSV — pipeline + zapis pliku
# ---------------------------------------------------------------------------

class TestCSVExportPipeline(unittest.TestCase):
    """
    INT-07: Pełny pipeline + eksport do CSV.

    Sprawdza, że wyeksportowany plik ma poprawne nagłówki, wiersze i encoding.
    Używa tymczasowego katalogu — nie pozostawia plików po teście.
    """

    @patch("nbp_sessions.requests.get")
    def test_csv_file_is_created(self, mock_get):
        """Po wyborze eksportu plik CSV powinien zostać utworzony."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            try:
                dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                               period=AnalysisPeriod.ONE_WEEK)
                dp.cli.acquire_information = MagicMock()
                dp.cli.ask_export.return_value = True

                dp.run()

                expected_file = os.path.join(tmpdir, "export_SESSION_ANALYSIS.csv")
                self.assertTrue(os.path.exists(expected_file),
                                msg="Plik CSV nie został utworzony")
            finally:
                os.chdir(original_dir)

    @patch("nbp_sessions.requests.get")
    def test_csv_has_correct_headers(self, mock_get):
        """Pierwszy wiersz CSV powinien zawierać nagłówki ['Measure', 'Result']."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            try:
                dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                               period=AnalysisPeriod.ONE_WEEK)
                dp.cli.acquire_information = MagicMock()
                dp.cli.ask_export.return_value = True

                dp.run()

                csv_path = os.path.join(tmpdir, "export_SESSION_ANALYSIS.csv")
                with open(csv_path, encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header_row = next(reader)

                self.assertEqual(header_row, ["Measure", "Result"])
            finally:
                os.chdir(original_dir)

    @patch("nbp_sessions.requests.get")
    def test_csv_has_three_data_rows(self, mock_get):
        """CSV dla SESSION_ANALYSIS powinien mieć 3 wiersze danych (+ nagłówek)."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
            {"effectiveDate": "2024-01-04", "mid": 4.05},
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            try:
                dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                               period=AnalysisPeriod.ONE_WEEK)
                dp.cli.acquire_information = MagicMock()
                dp.cli.ask_export.return_value = True

                dp.run()

                csv_path = os.path.join(tmpdir, "export_SESSION_ANALYSIS.csv")
                with open(csv_path, encoding="utf-8") as f:
                    rows = list(csv.reader(f))

                self.assertEqual(len(rows), 4)  # nagłówek + 3 wiersze
            finally:
                os.chdir(original_dir)

    @patch("nbp_sessions.requests.get")
    def test_csv_not_created_when_export_declined(self, mock_get):
        """Gdy użytkownik odmawia eksportu, plik CSV nie powinien powstać."""
        mock_get.return_value = _make_mock_response([
            {"effectiveDate": "2024-01-02", "mid": 4.00},
            {"effectiveDate": "2024-01-03", "mid": 4.10},
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            try:
                dp = _build_dp(AnalysisType.SESSION_ANALYSIS, Currency.US_DOLLAR,
                               period=AnalysisPeriod.ONE_WEEK)
                dp.cli.acquire_information = MagicMock()
                dp.cli.ask_export.return_value = False  # odmowa eksportu

                dp.run()

                csv_path = os.path.join(tmpdir, "export_SESSION_ANALYSIS.csv")
                self.assertFalse(os.path.exists(csv_path),
                                 msg="Plik CSV nie powinien zostać utworzony")
            finally:
                os.chdir(original_dir)


if __name__ == "__main__":
    unittest.main()
