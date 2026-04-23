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

    def print_error(self, *args):
        for arg in args:
            print(Fore.RED + str(arg), end='')
        print(Fore.RESET)

    def print_info(self,*args):
        for arg in args:
            print(Fore.YELLOW + str(arg), end='')
        print(Fore.RESET)

    def print_success(self, *args):
        for arg in args:
            print(Fore.GREEN + str(arg), end='')
        print(Fore.RESET)

    def print_default(self, *args):
        for arg in args:
            print(Fore.RESET + str(arg), end='')
        print(Fore.RESET)

    def get_input(self):
        print(Fore.LIGHTGREEN_EX+'INPUT: ', end='')
        return input()


    def aquire_analysis_type(self):
        self.print_default("select type of statistical analysis\n")
        self.print_info(int(AnalysisType.SESSION_ANALYSIS), "- Session analysis")
        self.print_info(int(AnalysisType.STATISTICAL_MEASURE), "- Statistical measure")
        self.print_info(int(AnalysisType.CHANGE_DISTRIBUTION),"- Change distribution\n")

        user_input = self.get_input()
        selected_analysis = None
        if len(user_input) != 1:
            self.print_error("\nINPUT INVALID (only one character allowed)\n")
            self.aquire_analysis_type()

        try:
            selected_analysis = int(user_input)
        except ValueError:
            self.print_error("\nINPUT INVALID (please enter a number)\n")
            self.aquire_analysis_type()

        if  not AnalysisType.has_value(selected_analysis):
            self.print_error("\nINPUT INVALID (number not in available types)\n")
            self.aquire_analysis_type()
        else:
            self.selected_analysis = AnalysisType(selected_analysis)

if __name__ == "__main__":
    cli = CLI()
    cli.aquire_analysis_type()
    cli.print_success('\nselected: ',cli.selected_analysis)

