"""Module with complexity issues."""

def complex_function(a, b, c, d, e, f, g, h, i, j):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    return a + b + c + d
                return a + b + c
            return a + b
        return a
    return 0
