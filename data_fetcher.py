from datetime import date
from dateutil.relativedelta import relativedelta
from nbp_sessions import fetch_quotes


def fetch_currency_data(currency_code, analysis_type, analysis_period=None, start_date=None):
    today = date.today()
    
    if analysis_type == 3:
        if not start_date:
            return None
        start = start_date.date() if hasattr(start_date, 'date') else start_date
    else:
        days_map = {
            1: 7,      # ONE_WEEK
            2: 14,     # TWO_WEEKS
            3: 30,     # ONE_MONTH
            4: 90,     # ONE_QUARTER
            5: 180,    # SIX_MONTHS
            6: 365,    # ONE_YEAR
        }
        days = days_map.get(analysis_period, 30)
        start = today - relativedelta(days=days)
    
    try:
        return fetch_quotes(currency_code, start, today)
    except Exception as e:
        print(f"Błąd podczas pobierania danych dla {currency_code}: {e}")
        return None


def fetch_secondary_currency_data(currency_code, start_date, end_date):
    try:
        return fetch_quotes(currency_code, start_date, end_date)
    except Exception as e:
        print(f"Błąd podczas pobierania danych dla {currency_code}: {e}")
        return None
