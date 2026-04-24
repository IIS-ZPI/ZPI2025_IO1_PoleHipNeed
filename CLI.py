from enum import IntEnum, Enum
from tabulate import tabulate
from colorama import Fore
from datetime import datetime
from dateutil.relativedelta import relativedelta


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

            string += str(c.value)
            string += ' - '
            string += c.name.lower().replace('_', ' ')
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
        self.change_period = None

        print(Fore.CYAN+"----------------------------------------------\n"
                        "    NBP Data Analysis Tool by PoleHipNeed\n"
                        "----------------------------------------------",Fore.RESET)

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

    def acquire_information(self):
        self.acquire_analysis_type()
        self.acquire_currency()
        if self.selected_analysis == AnalysisType.CHANGE_DISTRIBUTION:
            self.acquire_secondary_currency()
            self.acquire_period_change_distribution()
            self.acquire_start_date()
        else:
            self.acquire_period()

    def acquire_analysis_type(self):
            selected_analysis = None

            self.my_print('default', "select type of statistical analysis ")
            self.my_print('info', int(AnalysisType.SESSION_ANALYSIS), "- Session analysis")
            self.my_print('info', int(AnalysisType.STATISTICAL_MEASURE), "- Statistical measure")
            self.my_print('info', int(AnalysisType.CHANGE_DISTRIBUTION),"- Change distribution ")

            user_input = self.get_input()

            if len(user_input) != 1:
                self.my_print('error', " INPUT INVALID (only one character allowed) ")
                self.acquire_analysis_type()
                return

            try:
                selected_analysis = int(user_input)
            except ValueError:
                self.my_print('error', " INPUT INVALID (please enter a number) ")
                self.acquire_analysis_type()
                return

            if  not AnalysisType.has_value(selected_analysis):
                self.my_print('error', " INPUT INVALID (number not in available types) ")
                self.acquire_analysis_type()
            else:
                self.selected_analysis = AnalysisType(selected_analysis)
                self.my_print('success',  'selected: ', cli.selected_analysis.name.lower().replace('_', ' '))


    def acquire_currency(self):
        selected_currency = None

        self.my_print('default', "select currency for analysis by inputting its code ")
        self.my_print('info', 'available currencies: ', Currency.to_string(', ')," ")

        selected_currency = self.get_input().upper()

        if not Currency.has_value(selected_currency):
            self.my_print('error', " INPUT INVALID (currency code not recognized) ")
            self.acquire_currency()
        else:
            self.selected_currency = Currency(selected_currency)
            self.my_print('success',  'selected: ', cli.selected_currency.name.lower().replace('_', ' '))

    def acquire_secondary_currency(self):
        selected_currency = None

        self.my_print('default', "select currency for comparison by inputting its code ")
        self.my_print('info', 'available currencies: ', Currency.to_string(', ')," ")

        selected_currency = self.get_input().upper()

        if not Currency.has_value(selected_currency):
            self.my_print('error', " INPUT INVALID (currency code not recognized) ")
            self.acquire_secondary_currency()
        else:
            self.secondary_currency = Currency(selected_currency)
            self.my_print('success',  'selected: ', cli.secondary_currency.name.lower().replace('_', ' '))

    def acquire_period(self):
        selected_period = None

        self.my_print('default', "select type of statistical analysis ")
        self.my_print('info', AnalysisPeriod.to_string('\n'),' ')

        user_input = self.get_input()

        if len(user_input) != 1:
            self.my_print('error', " INPUT INVALID (only one character allowed) ")
            self.acquire_period()
            return

        try:
            selected_period = int(user_input)
        except ValueError:
            self.my_print('error', " INPUT INVALID (please enter a number) ")
            self.acquire_period()
            return

        if not AnalysisPeriod.has_value(selected_period):
            self.my_print('error', " INPUT INVALID (number not in available periods) ")
            self.acquire_period()
        else:
            self.analysis_period = AnalysisPeriod(selected_period)
            self.my_print('success',  'selected: ', cli.analysis_period.name.lower().replace('_', ' '))

    def display_table(self, table, headers, title):
        print(Fore.LIGHTWHITE_EX + title + Fore.RESET)
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    def ask_repeat(self):
        self.my_print('default', "perform another analysis? (y/n) ")
        answer = self.get_input()
        if answer.lower() == 'y':
            return True
        elif answer.lower() == 'n':
            return False
        else:
            self.my_print('error', " INPUT INVALID (input y or n) ")
            return self.ask_repeat()

    def ask_export(self):
        self.my_print('default', "download table as csv? (y/n) ")
        answer = self.get_input()
        if answer.lower() == 'y':
            return True
        elif answer.lower() == 'n':
            return False
        else:
            self.my_print('error', " INPUT INVALID (input y or n) ")
            return self.ask_export()

    def acquire_period_change_distribution(self):
        self.my_print('default', "select timeframe length ")
        self.my_print('info', 1, "- monthly")
        self.my_print('info', 2, "- quarterly ")
        answer = self.get_input()
        if answer == '1':
            self.change_period = 'monthly'
        elif answer == '2':
            self.change_period = 'quarterly'
        else:
            self.my_print('error', " INPUT INVALID (input 1 or 2) ")
            return self.acquire_period_change_distribution()

    def acquire_start_date(self):
        self.my_print('default', "select start date (format: DD.MM.YYYY) ")

        user_input = self.get_input()

        try:
            start_date = datetime.strptime(user_input, "%d.%m.%Y")
        except ValueError:
            self.my_print('error', " INPUT INVALID (wrong date format) ")
            return self.acquire_start_date()

        today = datetime.today()

        if self.change_period == 'monthly':
            min_date = today - relativedelta(months=1)
        elif self.change_period == 'quarterly':
            min_date = today - relativedelta(months=3)
        else:
            self.my_print('error', " INTERNAL ERROR: change_period not set ")
            return self.acquire_start_date()

        if start_date > min_date:
            self.my_print(
                'error',
                f" INPUT INVALID (date insufficient, earliest allowed: {min_date.strftime('%d.%m.%Y')})"
            )
            return self.acquire_start_date()

        if start_date > today:
            self.my_print('error', " INPUT INVALID (date cannot be in the future)")
            return self.acquire_start_date()

        self.start_date = start_date

        self.my_print(
            'success',
            " selected: ",
            start_date.strftime("%d/%m/%Y")
        )

    def display_status(self):

        self.selected_analysis = None
        self.selected_currency = None
        self.secondary_currency = None
        self.analysis_period = None

if __name__ == "__main__":
    cli = CLI()
    # cli.acquire_period_change_distribution()
    # cli.acquire_start_date()
    # sample_table = [[1,2,3,4,2,3,4,1,2,3,4],[1,2,3,4,2,3,4,1,2,3,4],[1,2,3,4,2,3,4,1,2,3,4],[1,2,3,4,2,3,4,1,2,3,4]]
    # headers = ["A", "B", "C", "D","A", "B", "C","A","B","C","D"]
    # cli.display_table(sample_table, headers, 'sample table title')
    #
    # cli.ask_repeat()
    # cli.ask_export()
    cli.acquire_information()

