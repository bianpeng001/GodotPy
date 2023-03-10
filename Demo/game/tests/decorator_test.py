#
# decorator test
#


class Prop:
    def __init__(self, value):
        self.value = value

    def __get__(self, obj, owner):
        print('call', obj, owner)
        return self.value


class A:
    x = Prop(1234)
    def __init__(self):
        pass


a = A()

print(a.x)

