from enum import IntEnum
from colorama import Fore


class AnalysisType(IntEnum):
    SESSION_ANALYSIS = 1
    STATISTICAL_MEASURE = 2
    CHANGE_DISTRIBUTION = 3

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class CLI:
    def __init__(self):
        self.selected_analysis = None
        print(Fore.CYAN+"NBP Data Analysis Tool by PoleHipNeed",Fore.RESET)

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


    def aquire_analysis_type(self):
        selected_analysis = None

        self.my_print('default', "select type of statistical analysis\n")
        self.my_print('info', int(AnalysisType.SESSION_ANALYSIS), "- Session analysis")
        self.my_print('info', int(AnalysisType.STATISTICAL_MEASURE), "- Statistical measure")
        self.my_print('info', int(AnalysisType.CHANGE_DISTRIBUTION),"- Change distribution\n")

        user_input = self.get_input()

        if len(user_input) != 1:
            self.my_print('error', "\nINPUT INVALID (only one character allowed)\n")
            self.aquire_analysis_type()
            return

        try:
            selected_analysis = int(user_input)
        except ValueError:
            self.my_print('error', "\nINPUT INVALID (please enter a number)\n")
            self.aquire_analysis_type()
            return

        if  not AnalysisType.has_value(selected_analysis):
            self.my_print('error', "\nINPUT INVALID (number not in available types)\n")
            self.aquire_analysis_type()
        else:
            self.selected_analysis = AnalysisType(selected_analysis)
            self.my_print('success', '\nselected: ', cli.selected_analysis.name)


if __name__ == "__main__":
    cli = CLI()
    cli.aquire_analysis_type()

