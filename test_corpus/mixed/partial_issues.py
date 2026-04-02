
def okay_func():
    return "this is fine"

def bad_func():
    # FIXME: performance
    result = []
    for i in range(1000):
        if i % 2 == 0:
            if i % 3 == 0:
                result.append(i)
    return result
