import requests


def _nbp_rates_link(currency_code : str, data_from : str, data_to : str):
    """
        Pobiera notowania średnie NBP dla danej waluty z zakresu dat.
        CASE INSENSITIVE! - kod waluty jakkolwiek
        date format: YYYY-MM-DD
    """
    return f"http://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/{data_from}/{data_to}/?format=json"

def _nbp_rates_link(currency_code : str, number_of_sessions : int):
    """
        Pobiera notowania średnie NBP dla danej waluty z ostatnich sesji.
        CASE INSENSITIVE! - kod waluty jakkolwiek
        date format: YYYY-MM-DD
    """
    return f"http://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/last/{number_of_sessions}/?format=json"

def _fetch_nbp_rates(url : str):
    """Pobiera dane z podanego URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Błąd podczas pobierania danych NBP")
    
def get_nbp_rates(currency_code : str, data_from : str, data_to : str):
    url = _nbp_rates_link(currency_code, data_from, data_to)
    return _fetch_nbp_rates(url)

def get_nbp_rates(currency_code : str, number_of_sessions : int):
    url = _nbp_rates_link(currency_code, number_of_sessions)
    return _fetch_nbp_rates(url)


if __name__ == "__main__":
    # Przykładowe użycie
    try:
        rates = get_nbp_rates("USD", "2023-01-01", "2023-01-31")
        print(rates)
    except ValueError as e:
        print(e)