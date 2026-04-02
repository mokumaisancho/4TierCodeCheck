
def process_items_a(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result

def process_items_b(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result
