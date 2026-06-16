import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from CLI import AnalysisType, AnalysisPeriod, Currency


class TestAnalysisType(unittest.TestCase):
    """Tests for AnalysisType enum."""

    def test_has_value_session_analysis(self):
        self.assertTrue(AnalysisType.has_value(1))

    def test_has_value_statistical_measure(self):
        self.assertTrue(AnalysisType.has_value(2))

    def test_has_value_change_distribution(self):
        self.assertTrue(AnalysisType.has_value(3))

    def test_has_value_zero_invalid(self):
        """Value 0 does not exist in the enum."""
        self.assertFalse(AnalysisType.has_value(0))

    def test_has_value_out_of_range(self):
        """Values outside the 1-3 range should return False."""
        self.assertFalse(AnalysisType.has_value(4))
        self.assertFalse(AnalysisType.has_value(-1))
        self.assertFalse(AnalysisType.has_value(100))

    def test_enum_member_count(self):
        """AnalysisType should have exactly 3 values."""
        self.assertEqual(len(AnalysisType), 3)

    def test_enum_values_match_names(self):
        """Verification of value to name assignments."""
        self.assertEqual(AnalysisType.SESSION_ANALYSIS.value, 1)
        self.assertEqual(AnalysisType.STATISTICAL_MEASURE.value, 2)
        self.assertEqual(AnalysisType.CHANGE_DISTRIBUTION.value, 3)


class TestAnalysisPeriod(unittest.TestCase):
    """Tests for AnalysisPeriod enum."""

    def test_has_value_all_valid(self):
        """All values 1-6 should be recognized."""
        for i in range(1, 7):
            with self.subTest(value=i):
                self.assertTrue(AnalysisPeriod.has_value(i))

    def test_has_value_zero_invalid(self):
        self.assertFalse(AnalysisPeriod.has_value(0))

    def test_has_value_seven_invalid(self):
        self.assertFalse(AnalysisPeriod.has_value(7))

    def test_has_value_negative_invalid(self):
        self.assertFalse(AnalysisPeriod.has_value(-1))

    def test_enum_member_count(self):
        """AnalysisPeriod should have exactly 6 values."""
        self.assertEqual(len(AnalysisPeriod), 6)

    def test_enum_values_match_names(self):
        """Verification of value to name assignments."""
        self.assertEqual(AnalysisPeriod.ONE_WEEK.value, 1)
        self.assertEqual(AnalysisPeriod.TWO_WEEKS.value, 2)
        self.assertEqual(AnalysisPeriod.ONE_MONTH.value, 3)
        self.assertEqual(AnalysisPeriod.ONE_QUARTER.value, 4)
        self.assertEqual(AnalysisPeriod.SIX_MONTHS.value, 5)
        self.assertEqual(AnalysisPeriod.ONE_YEAR.value, 6)

    def test_to_string_contains_all_values(self):
        """to_string() should contain numbers 1-6."""
        result = AnalysisPeriod.to_string(", ")
        for i in range(1, 7):
            self.assertIn(str(i), result)

    def test_to_string_with_different_dividers(self):
        """to_string() should work with different dividers."""
        result_comma = AnalysisPeriod.to_string(", ")
        result_newline = AnalysisPeriod.to_string("\n")
        # Both versions should contain the same elements
        self.assertIn("one week", result_comma)
        self.assertIn("one week", result_newline)

    def test_to_string_contains_period_names(self):
        """to_string() should contain readable period names."""
        result = AnalysisPeriod.to_string(", ")
        self.assertIn("one week", result)
        self.assertIn("one year", result)


class TestCurrency(unittest.TestCase):
    """Tests for Currency enum."""

    def test_has_value_usd(self):
        self.assertTrue(Currency.has_value("USD"))

    def test_has_value_eur(self):
        self.assertTrue(Currency.has_value("EUR"))

    def test_has_value_chf(self):
        self.assertTrue(Currency.has_value("CHF"))

    def test_has_value_gbp(self):
        self.assertTrue(Currency.has_value("GBP"))

    def test_has_value_invalid_code(self):
        """Non-existent currency code should return False."""
        self.assertFalse(Currency.has_value("XYZ"))

    def test_has_value_empty_string(self):
        """Empty string should not be recognized."""
        self.assertFalse(Currency.has_value(""))

    def test_has_value_lowercase_invalid(self):
        """Lowercase code should not be recognized (enum is case-sensitive)."""
        self.assertFalse(Currency.has_value("usd"))

    def test_has_value_partial_code(self):
        """Incomplete currency code should return False."""
        self.assertFalse(Currency.has_value("US"))

    def test_to_string_contains_usd(self):
        """to_string() should contain 'USD'."""
        result = Currency.to_string(", ")
        self.assertIn("USD", result)

    def test_to_string_contains_eur(self):
        """to_string() should contain 'EUR'."""
        result = Currency.to_string(", ")
        self.assertIn("EUR", result)

    def test_to_string_is_string(self):
        """to_string() should return str type."""
        result = Currency.to_string(", ")
        self.assertIsInstance(result, str)

    def test_currency_count(self):
        """Enum should contain > 0 currencies."""
        self.assertGreater(len(Currency), 0)

    def test_all_values_are_three_letter_codes(self):
        """All currency codes should have length 3 and consist of letters."""
        for currency in Currency:
            with self.subTest(currency=currency.name):
                self.assertEqual(len(currency.value), 3)
                self.assertTrue(currency.value.isalpha())


if __name__ == "__main__":
    unittest.main()
