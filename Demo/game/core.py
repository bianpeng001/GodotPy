import GodotPy as gp

def print_safe(a):
    if isinstance(a, str):
        gp.print(a)
    else:
        gp.print(str(a))

class BaseClass:
    def __init__(self):
        self.py_capsule = None
    
    def print(self):
        print_safe(self.py_capsule)

