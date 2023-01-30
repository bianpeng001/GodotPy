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
        self.offset_y = 20
        self.offset_z = 15

        self.center_x = 0
        self.center_y = 0
        self.center_z = 0

        self.press_time = 0

    def _create(self):
        set_process(self.py_capsule, process=True, input=False)
        #gp.set_process(self.py_capsule, True)
        #gp.set_process_input(self.py_capsule, True)
        #gp.connect(self.py_capsule, "ready", test_callback)
        #gp.connect(self.py_capsule, "ready", self._ready)
        connect(self.py_capsule, "ready", self._ready)
        self.main_camera = find_node(self.py_capsule, 'MainCamera')

        self.update_camera()

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
                self.on_mouse_drag()
        else:
            if self.is_left_button_pressed:
                self.is_left_button_pressed = False
                self.on_mouse_button_up()
        
    def on_mouse_button_down(self):
        input = get_input()
        x,y,z = screen_to_world(self.main_camera, input.x, input.y)
        self.start_x = x
        self.start_y = y
        self.start_z = z

        self.press_time = get_time()

        pass
    
    # TODO： begin_drag(), end_drag(), drag()
    def on_mouse_drag(self):
        input = get_input()

        # 拖拽场景，用移动摄像头来实现
        x,y,z = screen_to_world(self.main_camera, input.x, input.y)
        #print_line((x,y,z))
        dx = x - self.start_x
        dy = y - self.start_y
        dz = z - self.start_z

        self.center_x -= dx
        self.center_y -= dy
        self.center_z -= dz

        self.update_camera()
        
    # 刷新camera位置和朝向
    def update_camera(self):
        set_position(self.main_camera, 
            self.center_x + self.offset_x,
            self.center_y + self.offset_y,
            self.center_z + self.offset_z)
        lookat(self.main_camera,
            self.center_x,
            self.center_y,
            self.center_z)

    def on_mouse_button_up(self):
        input = get_input()

        print_line(get_delta_time())
        print('asasdfasdf')

        t = get_time()
        if t - self.press_time < 100:
            a = gp.instantiate('res://models/City01.tscn')
            x,y,z = screen_to_world(self.main_camera, input.x, input.y)
            set_position(a, x, y, z)
        pass

    def _ready(self):
        print_line(f"camera controller ready")
        
        



