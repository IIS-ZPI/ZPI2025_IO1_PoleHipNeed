from enum import IntEnum


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
        print("Hello, World!")

    def aquire_analysis_type(self):
        print("please select type of statistical analys")
        print("input number corresponding to one of these:")
        print(int(AnalysisType.SESSION_ANALYSIS), "- Session analysis")
        print(int(AnalysisType.STATISTICAL_MEASURE), "- Statistical measure")
        print(int(AnalysisType.CHANGE_DISTRIBUTION),"- Change distribution")

        user_input = input()
        selected_analysis = None
        if len(user_input) != 1:
            print("INPUT INVALID (only one character allowed)")
            self.aquire_analysis_type()

        try:
            selected_analysis = int(user_input)
        except ValueError:
            print("INPUT INVALID (please enter a number)")
            self.aquire_analysis_type()

        if  not AnalysisType.has_value(selected_analysis):
            print("INPUT INVALID (number not in available types)")
            self.aquire_analysis_type()
        else:
            self.selected_analysis = AnalysisType(selected_analysis)

if __name__ == "__main__":
    cli = CLI()
    cli.aquire_analysis_type()
    print(cli.selected_analysis)

