import GodotPy as gp

def print_line(a):
    if isinstance(a, str):
        gp.print_line(a)
        #print(a)
    else:
        gp.print_line(str(a))
        #print(a)

# 对应于godot场景树
class NodeObject:
    def __init__(self):
        # 记录一个node的指针
        self.py_capsule = None
    
    def on_mouse_button(self, button, pressed, x, y):
        pass

    def on_key_pressed(self, keycode, pressed):
        pass

    def on_mouse_move(self, x, y):
        pass

    def _ready(self):
        pass

    def _process(self):
        pass

    # 构造函数之后回调
    def _create(self):
        pass


