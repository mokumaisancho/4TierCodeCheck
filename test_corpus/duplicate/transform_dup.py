
def transform_a(data):
    result = []
    for item in data:
        cleaned = item.strip().lower()
        if cleaned:
            result.append(cleaned)
    return result

def transform_b(data):
    result = []
    for item in data:
        cleaned = item.strip().lower()
        if cleaned:
            result.append(cleaned)
    return result
