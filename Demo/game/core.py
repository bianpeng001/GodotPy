import GodotPy as gp

# 对应于godot场景树的节点，的容器
class NodeObject:
    def __init__(self):
        # 记录一个node的指针
        self.py_capsule = None
        #self.node = None
    
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

def print_line(a):
    if isinstance(a, str):
        gp.print_line(a)
        #print(a)
    else:
        gp.print_line(str(a))
        #print(a)

def find_node(node, path):
    return gp.find_node(node, path)

def set_process(node, process=False, input=False):
    if process:
        gp.set_process(node, True)
    
    if input:
        gp.set_process_input(node, True)

def connect(node, signal, callback):
    gp.connect(node, signal, callback)


def get_position(node):
    return gp.get_position(node)

def set_position(node, x, y, z):
    gp.set_position(node, x, y, z)


