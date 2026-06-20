import csv
from datetime import date
from dateutil.relativedelta import relativedelta
from CLI import CLI, AnalysisType, AnalysisPeriod
import data_processor
import nbp_sessions

class DataflowManager:
    def __init__(self):
        self.cli = CLI()

    def get_date_range(self, period):
        today = date.today()
        if period == AnalysisPeriod.ONE_WEEK:
            return today - relativedelta(weeks=1), today
        elif period == AnalysisPeriod.TWO_WEEKS:
            return today - relativedelta(weeks=2), today
        elif period == AnalysisPeriod.ONE_MONTH:
            return today - relativedelta(months=1), today
        elif period == AnalysisPeriod.ONE_QUARTER:
            return today - relativedelta(months=3), today
        elif period == AnalysisPeriod.SIX_MONTHS:
            return today - relativedelta(months=6), today
        elif period == AnalysisPeriod.ONE_YEAR:
            return today - relativedelta(years=1), today
        return today, today

    def run(self):
        while True:
            self.cli.acquire_information()
            
            headers = []
            table = []
            title = ""

            try:
                if self.cli.selected_analysis == AnalysisType.SESSION_ANALYSIS:
                    start, end = self.get_date_range(self.cli.analysis_period)
                    quotes = nbp_sessions.fetch_quotes(self.cli.selected_currency.value, start, end)
                    sessions = [float(q.mid) for q in quotes]
                    
                    results = data_processor.calculate_sessions(sessions)
                    title = "Session Analysis"
                    headers = ["Measure", "Result"]
                    table = [
                        ["Rising", results["rising"]],
                        ["Losing", results["losing"]],
                        ["Flat", results["flat"]]
                    ]
                    
                elif self.cli.selected_analysis == AnalysisType.STATISTICAL_MEASURE:
                    start, end = self.get_date_range(self.cli.analysis_period)
                    quotes = nbp_sessions.fetch_quotes(self.cli.selected_currency.value, start, end)
                    sessions = [float(q.mid) for q in quotes]
                    
                    results = data_processor.calculate_statistical_measures(sessions)
                    title = "Statistical Measures"
                    headers = ["Measure", "Value"]
                    table = [
                        ["Median", f"{results['median']:.4f}"],
                        ["Mode", f"{results['mode']:.4f}"],
                        ["Standard Deviation", f"{results['standard deviation']:.4f}"],
                        ["Coefficient of Variation", f"{results['coefficient of variation']:.4f}"]
                    ]
                    
                elif self.cli.selected_analysis == AnalysisType.CHANGE_DISTRIBUTION:
                    start_date = self.cli.start_date.date()
                    if self.cli.change_period == 'monthly':
                        end_date = start_date + relativedelta(months=1)
                    else:
                        end_date = start_date + relativedelta(months=3)

                    primary_currency = self.cli.selected_currency.value
                    secondary_currency = self.cli.secondary_currency.value

                    if primary_currency == 'PLN':
                        quotes = nbp_sessions.fetch_quotes(self.cli.secondary_currency.value, start_date, end_date)
                        sessions1 = [float(1.0)]*len(quotes)
                        sessions2 = [float(q.mid) for q in quotes]
                    elif secondary_currency == 'PLN':
                        quotes = nbp_sessions.fetch_quotes(self.cli.selected_currency.value, start_date, end_date)
                        sessions1 = [float(q.mid) for q in quotes]
                        sessions2 = [float(1.0)]*len(quotes)
                    else:
                        quotes1 = nbp_sessions.fetch_quotes(self.cli.selected_currency.value, start_date, end_date)
                        quotes2 = nbp_sessions.fetch_quotes(self.cli.secondary_currency.value, start_date, end_date)
                        sessions1 = [float(q.mid) for q in quotes1]
                        sessions2 = [float(q.mid) for q in quotes2]
                    
                    results, ratio_ranges = data_processor.calculate_change_distribution(sessions1, sessions2, steps=10)
                    title = "Change Distribution"
                    headers = ["Range Start", "Range End", "Count"]
                    table = []
                    for i in range(len(results)):
                        table.append([f"{ratio_ranges[i]:.4f}", f"{ratio_ranges[i+1]:.4f}", results[i]])
                        
                self.cli.display_table(table, headers, title)

                if self.cli.ask_export():
                    try:
                        filename = f"export_{self.cli.selected_analysis.name.lower()}_{self.cli.selected_currency.name.lower()}"
                        analysis = self.cli.selected_analysis
                        suffix = ''
                        if analysis == AnalysisType.CHANGE_DISTRIBUTION:
                            suffix += f"_{self.cli.secondary_currency.name.lower()}_{self.cli.change_period.lower()}_{self.cli.start_date.date().isoformat()}"
                        if analysis == AnalysisType.STATISTICAL_MEASURE:
                            suffix += f"_{self.cli.analysis_period.name.lower()}_{date.today().isoformat()}"
                        if analysis == AnalysisType.SESSION_ANALYSIS:
                            suffix += f"_{self.cli.analysis_period.name.lower()}_{date.today().isoformat()}"

                        suffix += '.csv'
                        filename += suffix

                        with open(filename, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(headers)
                            writer.writerows(table)
                        self.cli.my_print('success', f"Exported to {filename}")
                    except PermissionError:
                        self.cli.my_print('error', "Permission denied.")
                    except Exception:
                        self.cli.my_print('error', 'Export to csv failed.')
            except Exception as e:
                self.cli.my_print('error', f"An error occurred: {e}")

            if not self.cli.ask_repeat():
                break
