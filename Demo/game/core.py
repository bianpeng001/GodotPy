import GodotPy as gp

def print_safe(a):
    if isinstance(a, str):
        gp.print_line(a)
        #print(a)
    else:
        gp.print_line(str(a))
        #print(a)

class BaseClass:
    def __init__(self):
        self.py_capsule = None
    
    def print(self):
        print_safe(self.py_capsule)

