"""Module with dead code."""

def process(x):
    if x > 0:
        return x * 2
    return 0
    # Dead code below
    print("This never runs")
    y = x + 1
    return y
