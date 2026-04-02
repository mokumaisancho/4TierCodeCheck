
def with_dead_code():
    x = 1  # unused
    y = 2
    result = y * 2
    return result
    x = 3  # unreachable
    return x
