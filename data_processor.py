


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
    results = {
        "median":0,
        "mode":0,
        "standard deviation":0,
        "coefficient of variation":0
    }

