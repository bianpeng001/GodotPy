import sys

import GodotPy as gp
from game.core import NodeObject, print_line
from game.input_controller import get_input

def test_callback():
    print_line("test_callback")

# 镜头管理
class CameraController(NodeObject):
    def __init__(self):
        super().__init__()
        print_line('create CameraController')

    def _create(self):
        gp.set_process(self.py_capsule, True)
        #gp.set_process_input(self.py_capsule, True)
        #gp.connect(self.py_capsule, "ready", test_callback)
        gp.connect(self.py_capsule, "ready", self._ready)
        self.main_camera = gp.find_node(self.py_capsule, 'MainCamera')
        pass

    def _process(self):
        #print_safe(str(self.py_capsule))
        input = get_input()
        if input:
            if input.is_mouse_pressed(1):
                x,y,z = gp.get_position(self.main_camera)
                print_line((x,y,z))

    def _ready(self):
        print_line(f"camera controller ready")
        
        



