import GodotPy as gp

def print_line(a):
    if isinstance(a, str):
        gp.print_line(a)
        #print(a)
    else:
        gp.print_line(str(a))
        #print(a)

class NodeObject:
    def __init__(self):
        # 记录一个node的指针
        self.py_capsule = None
    
    def print(self):
        print_line(self.py_capsule)

    def on_mouse_button(self, button, x, y):
        pass

    def on_key_pressed(self, keycode, pressed):
        pass

    def on_mouse_move(self, x, y):
        pass

    def _ready(self):
        pass


