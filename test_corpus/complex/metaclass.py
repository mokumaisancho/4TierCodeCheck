
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass
