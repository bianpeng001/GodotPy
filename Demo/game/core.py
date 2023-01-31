#
# 2023年1月30日 bianpeng
#

import GodotPy as gp

# Vector3
class Vector3:
    def __init__(self):
        self.x = self.y = self.z = 0

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, left, right):
        self.x = left.x + right.x
        self.y = left.y + right.y
        self.z = left.z + right.z

    def inc(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z


# 单例
class Singleton:
    _instance = None
    @classmethod
    def get_instance(class_):
        if not class_._instance:
            class_._instance = class_()
        return class_._instance

    def __init__(self):
        pass
    

# 对应于godot场景树的节点，的容器
class NodeObject:
    def __init__(self):
        # 记录一个node的指针
        self.node_capsule = None

    def _get_node(self):
        return self.node_capsule
    
    def on_mouse_button(self, button, pressed, x, y):
        pass

    def on_key_pressed(self, keycode, pressed):
        pass

    def on_mouse_move(self, x, y):
        pass

    def _ready(self):
        print_line(f'{type(self)} ready')

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

def lookat(node, x, y, z):
    gp.lookat(node, x, y, z)

def screen_to_world(camera, x, y):
    return gp.screen_to_world(camera, x, y)

def get_time():
    return gp.get_time()

def get_delta_time():
    return gp.get_delta_time()

def instantiate(path):
    return gp.instantiate(path)



