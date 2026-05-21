from __future__ import annotations

import argparse
import calendar
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable

import requests


API_URL = "https://api.nbp.pl/api/exchangerates/rates/A/{code}/{start}/{end}/?format=json"


@dataclass(frozen=True)
class Quote:
    effective_date: date
    mid: Decimal


def subtract_months(source_date: date, months: int) -> date:
    """Subtract whole calendar months from a date."""
    month_index = source_date.month - 1 - months
    year = source_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def fetch_quotes(code: str, start: date, end: date) -> list[Quote]:
    url = API_URL.format(code=code.upper(), start=start.isoformat(), end=end.isoformat())

    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 404:
            raise ValueError(
                f"No data found for currency '{code.upper()}'. "
                "Check the currency code (e.g., USD, EUR, CHF)."
            )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.SSLError as exc:
        raise RuntimeError(
            "SSL error while connecting to the NBP API. "
            "Ensure the environment has up-to-date certificates or use requests with certifi."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to connect to the NBP API: {exc}") from exc

    rates = payload.get("rates", [])
    if not rates:
        raise ValueError("The NBP API returned no quotes for the given range.")

    quotes: list[Quote] = []
    for item in rates:
        quotes.append(
            Quote(
                effective_date=date.fromisoformat(item["effectiveDate"]),
                mid=Decimal(str(item["mid"])),
            )
        )

    return quotes


def count_sessions(quotes: Iterable[Quote]) -> tuple[int, int, int]:
    ordered = sorted(quotes, key=lambda q: q.effective_date)
    rises = falls = unchanged = 0

    for previous, current in zip(ordered, ordered[1:]):
        if current.mid > previous.mid:
            rises += 1
        elif current.mid < previous.mid:
            falls += 1
        else:
            unchanged += 1

    return rises, falls, unchanged


def build_periods(today: date) -> list[tuple[str, date]]:
    return [
        ("Last 1 week", today.fromordinal(today.toordinal() - 7)),
        ("Last 2 weeks", today.fromordinal(today.toordinal() - 14)),
        ("Last 1 month", subtract_months(today, 1)),
        ("Last 1 quarter", subtract_months(today, 3)),
        ("Last 6 months", subtract_months(today, 6)),
        ("Last 1 year", subtract_months(today, 12)),
    ]


def print_results(currency: str, quotes: list[Quote], today: date) -> None:
    periods = build_periods(today)

    print(f"\nCurrency: {currency.upper()} (NBP average rate, table A)")
    print(f"Data range retrieved: {quotes[0].effective_date} -> {quotes[-1].effective_date}")
    print("\n{:<22} {:>10} {:>10} {:>12} {:>16}".format("Period", "Rise", "Fall", "Unchanged", "Number of sessions"))
    print("-" * 74)

    for period_name, start_date in periods:
        in_period = [q for q in quotes if start_date <= q.effective_date <= today]
        rise, fall, stable = count_sessions(in_period)
        sessions = max(0, len(in_period) - 1)

        print(
            "{:<22} {:>10} {:>10} {:>12} {:>16}".format(
                period_name,
                rise,
                fall,
                stable,
                sessions,
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analysis of rising/falling/unchanged sessions "
            "for a currency based on the NBP API."
        )
    )
    parser.add_argument(
        "currency",
        nargs="?",
        help="Currency code, e.g., USD, EUR, CHF",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    currency = (args.currency or input("Enter currency code (e.g., USD): ")).strip().upper()

    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Currency code must consist of 3 letters, e.g., USD.")

    today = date.today()
    one_year_ago = subtract_months(today, 12)

    quotes = fetch_quotes(currency, one_year_ago, today)
    print_results(currency, quotes, today)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nError: {exc}")
