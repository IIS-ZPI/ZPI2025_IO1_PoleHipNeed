from enum import IntEnum, Enum
from colorama import Fore


class AnalysisType(IntEnum):
    SESSION_ANALYSIS = 1
    STATISTICAL_MEASURE = 2
    CHANGE_DISTRIBUTION = 3

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class AnalysisPeriod(IntEnum):
    ONE_WEEK = 1
    TWO_WEEKS = 2
    ONE_MONTH = 3
    ONE_QUARTER = 4
    SIX_MONTHS = 5
    ONE_YEAR = 6

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def to_string(cls, divider):
        string = ''
        first = True
        for c in cls:
            if not first:
                string += divider
            string += c.name.lower().replace('_', ' ')
            string += ' - '
            string += str(c.value)
            first = False
        return string

class Currency(Enum):
    THAI_BAHT = 'THB'
    US_DOLLAR = 'USD'
    AUSTRALIAN_DOLLAR = 'AUD'
    HONG_KONG_DOLLAR = 'HKD'
    CANADIAN_DOLLAR = 'CAD'
    NEW_ZEALAND_DOLLAR = 'NZD'
    SINGAPORE_DOLLAR = 'SGD'
    EURO = 'EUR'
    HUNGARIAN_FORINT = 'HUF'
    SWISS_FRANC = 'CHF'
    BRITISH_POUND = 'GBP'
    UKRAINIAN_HRYVNIA = 'UAH'
    JAPANESE_YEN = 'JPY'
    CZECH_KORUNA = 'CZK'
    DANISH_KRONE = 'DKK'
    ICELANDIC_KRONA = 'ISK'
    NORWEGIAN_KRONE = 'NOK'
    SWEDISH_KRONA = 'SEK'
    ROMANIAN_LEU = 'RON'
    TURKISH_LIRA = 'TRY'
    ISRAELI_SHEKEL = 'ILS'
    CHILEAN_PESO = 'CLP'
    PHILIPPINE_PESO = 'PHP'
    MEXICAN_PESO = 'MXN'
    SOUTH_AFRICAN_RAND = 'ZAR'
    BRAZILIAN_REAL = 'BRL'
    MALAYSIAN_RINGGIT = 'MYR'
    INDONESIAN_RUPIAH = 'IDR'
    INDIAN_RUPEE = 'INR'
    SOUTH_KOREAN_WON = 'KRW'
    CHINESE_YUAN = 'CNY'
    SPECIAL_DRAWING_RIGHTS = 'XDR'
    POLISH_ZLOTY = 'PLN'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def to_string(cls, divider):
        string = ''
        first = True
        for c in cls._value2member_map_:
            if not first:
                string += divider
            string += c
            first = False
        return string

class CLI:
    def __init__(self):
        self.selected_analysis = None
        self.selected_currency = None
        self.secondary_currency = None
        self.analysis_period = None

        print(Fore.CYAN+"----------------------------------------------\n    "
                        "NBP Data Analysis Tool by PoleHipNeed\n----------------------------------------------\n",Fore.RESET)

    def my_print(self, message_type, *args):
        formatting = Fore.RESET

        if message_type == 'info':
            formatting = Fore.YELLOW
        if message_type == 'error':
            formatting = Fore.RED
        if message_type == 'success':
            formatting = Fore.GREEN

        for arg in args:
            print(formatting + str(arg), end='')
        print(Fore.RESET)

    def get_input(self):
        print(Fore.LIGHTGREEN_EX+'INPUT: ', end='')
        return input()


    def acquire_analysis_type(self):
            selected_analysis = None

            self.my_print('default', "select type of statistical analysis\n")
            self.my_print('info', int(AnalysisType.SESSION_ANALYSIS), "- Session analysis")
            self.my_print('info', int(AnalysisType.STATISTICAL_MEASURE), "- Statistical measure")
            self.my_print('info', int(AnalysisType.CHANGE_DISTRIBUTION),"- Change distribution\n")

            user_input = self.get_input()

            if len(user_input) != 1:
                self.my_print('error', "\nINPUT INVALID (only one character allowed)\n")
                self.acquire_analysis_type()
                return

            try:
                selected_analysis = int(user_input)
            except ValueError:
                self.my_print('error', "\nINPUT INVALID (please enter a number)\n")
                self.acquire_analysis_type()
                return

            if  not AnalysisType.has_value(selected_analysis):
                self.my_print('error', "\nINPUT INVALID (number not in available types)\n")
                self.acquire_analysis_type()
            else:
                self.selected_analysis = AnalysisType(selected_analysis)
                self.my_print('success', '\nselected: ', cli.selected_analysis.name.lower().replace('_', ' '))


    def acquire_currency(self):
        selected_currency = None

        self.my_print('default', "select currency for analysis by inputting its code\n")
        self.my_print('info', 'available currencies:\n', Currency.to_string(', '),"\n")

        selected_currency = self.get_input().upper()

        if not Currency.has_value(selected_currency):
            self.my_print('error', "\nINPUT INVALID (currency code not recognized)\n")
            self.acquire_currency()
        else:
            self.selected_currency = Currency(selected_currency)
            self.my_print('success', '\nselected: ', cli.selected_currency.name.lower().replace('_', ' '))

    def acquire_secondary_currency(self):
        selected_currency = None

        self.my_print('default', "select currency for comparison by inputting its code\n")
        self.my_print('info', 'available currencies:\n', Currency.to_string(', '),"\n")

        selected_currency = self.get_input().upper()

        if not Currency.has_value(selected_currency):
            self.my_print('error', "\nINPUT INVALID (currency code not recognized)\n")
            self.acquire_secondary_currency()
        else:
            self.secondary_currency = Currency(selected_currency)
            self.my_print('success', '\nselected: ', cli.secondary_currency.name.lower().replace('_', ' '))

    def acquire_period(self):
        selected_period = None

        self.my_print('default', "select type of statistical analysis\n")
        self.my_print('info', AnalysisPeriod.to_string('\n'),'\n')

        user_input = self.get_input()

        if len(user_input) != 1:
            self.my_print('error', "\nINPUT INVALID (only one character allowed)\n")
            self.acquire_period()
            return

        try:
            selected_period = int(user_input)
        except ValueError:
            self.my_print('error', "\nINPUT INVALID (please enter a number)\n")
            self.acquire_period()
            return

        if not AnalysisPeriod.has_value(selected_period):
            self.my_print('error', "\nINPUT INVALID (number not in available periods)\n")
            self.acquire_period()
        else:
            self.analysis_period = AnalysisPeriod(selected_period)
            self.my_print('success', '\nselected: ', cli.analysis_period.name.lower().replace('_', ' '))

if __name__ == "__main__":
    cli = CLI()
    cli.acquire_period()

