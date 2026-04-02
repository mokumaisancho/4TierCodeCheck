"""medium_error_handling.py - Medium complexity module."""

def process_data(data, filter_func=None):
    """Process data with optional filtering."""
    results = []
    for item in data:
        if filter_func and not filter_func(item):
            continue
        if isinstance(item, (int, float)):
            results.append(item * 2)
        elif isinstance(item, str):
            results.append(item.upper())
        else:
            results.append(str(item))
    return results

def calculate_stats(numbers):
    """Calculate basic statistics."""
    if not numbers:
        return None
    
    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    
    sorted_nums = sorted(numbers)
    mid = count // 2
    if count % 2 == 0:
        median = (sorted_nums[mid-1] + sorted_nums[mid]) / 2
    else:
        median = sorted_nums[mid]
    
    return {"mean": mean, "median": median, "count": count}
