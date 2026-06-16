import statistics
from bisect import bisect_right

def calculate_sessions(sessions):
    results = {
        "rising" : 0,
        "losing" : 0,
        "flat" : 0,
    }
    prev = sessions[0]
    for session in sessions:
        if session == prev:
            results["flat"] += 1
        elif session < prev:
            results["losing"] += 1
        elif session > prev:
            results["rising"] += 1
        prev = session
    return results

def calculate_statistical_measures(sessions):
    measures = {
        "median": statistics.median(sessions),
        "mode": statistics.mode(sessions),
        "standard deviation": statistics.stdev(sessions),
        "coefficient of variation": statistics.pvariance(sessions)
    }
    return measures

def calculate_change_distribution(currency1_history, currency2_history,steps):
    if len(currency1_history) != len(currency2_history) or steps < 1:
        raise ValueError("Lengths of both histories must be equal and steps must be >= 1.")
    if len(currency1_history) < 2:
        raise ValueError("At least 2 data points are required to calculate changes.")
    if any(v == 0 for v in currency2_history):
        raise ValueError("Denominator (currency2) contains zero — cannot divide.")
    previous_ratio = currency1_history[0] / currency2_history[0]
    changes = []
    for i in range(1,len(currency1_history)):
        current_ratio = currency1_history[i] / currency2_history[i]
        changes.append(current_ratio - previous_ratio)
        previous_ratio = current_ratio
    max_ratio = max(changes)
    min_ratio = min(changes)
    step = (max_ratio - min_ratio) / steps
    ratio_ranges = [min_ratio + step * i for i in range(0,steps+1)]
    results = [0]*steps
    for ratio in changes:
        range_bucket = bisect_right(ratio_ranges,ratio) -1
        results[min(range_bucket,steps-1)] += 1
    return results, ratio_ranges


