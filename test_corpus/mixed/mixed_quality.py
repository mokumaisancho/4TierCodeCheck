
class GoodCode:
    def clean(self):
        return "nice"

def bad_func():  # TODO: refactor
    x = 1
    y = 2
    z = 3  # unused
    if x:
        if y:
            return x + y
