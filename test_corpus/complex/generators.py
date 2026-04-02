
def fib_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def chunk_iterator(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]
