import requests


def _nbp_rates_link(currency_code : str, data_from : str, data_to : str):
    """
        Fetches NBP average rates for the given currency within a date range.
        CASE INSENSITIVE! - currency code may be provided in any case
        date format: YYYY-MM-DD
    """
    return f"http://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/{data_from}/{data_to}/?format=json"

def _nbp_rates_link(currency_code : str, number_of_sessions : int):
    """
        Fetches NBP average rates for the given currency for the last N sessions.
        CASE INSENSITIVE! - currency code may be provided in any case
        date format: YYYY-MM-DD
    """
    return f"http://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/last/{number_of_sessions}/?format=json"

def _fetch_nbp_rates(url : str):
    """Fetches data from the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Error while fetching NBP data")
    
def get_nbp_rates(currency_code : str, data_from : str, data_to : str):
    url = _nbp_rates_link(currency_code, data_from, data_to)
    return _fetch_nbp_rates(url)

def get_nbp_rates(currency_code : str, number_of_sessions : int):
    url = _nbp_rates_link(currency_code, number_of_sessions)
    return _fetch_nbp_rates(url)


if __name__ == "__main__":
    # Example usage
    try:
        rates = get_nbp_rates("USD", "2023-01-01", "2023-01-31")
        print(rates)
    except ValueError as e:
        print(e)