#
# 2023年1月30日 bianpeng
#
import math

import GodotPy as gp
from game.core import *
from game.input_controller import get_input

def test_callback():
    print_line("test_callback")

# 镜头管理
class CameraController(NodeObject):
    def __init__(self):
        super().__init__()
        print_line('create CameraController')

        self.is_left_button_pressed = False
        self.offset_x = 15
        # 15*math.sin(math.pi/4)
        self.offset_y = 20
        self.offset_z = 15

    def _create(self):
        set_process(self.py_capsule, process=True, input=False)
        #gp.set_process(self.py_capsule, True)
        #gp.set_process_input(self.py_capsule, True)
        #gp.connect(self.py_capsule, "ready", test_callback)
        #gp.connect(self.py_capsule, "ready", self._ready)
        connect(self.py_capsule, "ready", self._ready)
        self.main_camera = find_node(self.py_capsule, 'MainCamera')

    def _process(self):
        #print_safe(str(self.py_capsule))
        self.handle_input()


    def handle_input(self):
        input = get_input()
        if not input:
            return
        
        if input.is_mouse_pressed(1):
            if not self.is_left_button_pressed:
                self.is_left_button_pressed = True
                self.on_mouse_button_down()
        else:
            if self.is_left_button_pressed:
                self.is_left_button_pressed = False
                self.on_mouse_button_up()
        
    def on_mouse_button_down(self):
        input = get_input()
        x,y,z = gp.screen_to_world(self.main_camera, input.x, input.y)
        print_line((x,y,z))
        set_position(self.main_camera, 
            x + self.offset_x,
            y + self.offset_y,
            z + self.offset_z)
        lookat(self.main_camera, x, y, z)

    def on_mouse_button_up(self):
        # input = get_input()
        # x,y,z = gp.screen_to_world(self.main_camera, input.x, input.y)
        # print_line((x,y,z))
        pass

    def _ready(self):
        print_line(f"camera controller ready")
        
        



