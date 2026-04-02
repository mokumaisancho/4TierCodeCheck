"""Medium complexity module."""

def process_data(data):
    results = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                results.append(item * 2)
            else:
                results.append(item + 1)
    return results

def calculate(x, y, operation):
    if operation == "add":
        return x + y
    elif operation == "sub":
        return x - y
    elif operation == "mul":
        return x * y
    else:
        raise ValueError(f"Unknown operation: {operation}")
