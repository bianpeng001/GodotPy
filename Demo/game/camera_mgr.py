#
# 2023年1月30日 bianpeng
#
import math

from game.core import *
from game.game_mgr import game_mgr
from game.input_mgr import *

# def test_callback():
#     print_line("test_callback")

def clamp(x, delta):
    v = x + delta
    if v < 0:
        return 0.0
    elif v > 1.0:
        return 1.0
    else:
        return v

# 镜头管理
class CameraMgr(NodeObject):
    def __init__(self):
        super().__init__()

        game_mgr.camera_mgr = self

        self.is_left_button_pressed = False
        self.is_wheel_up = False
        self.is_wheel_down = False

        self.arm_length = 55
        self.arm_norm = 1.0

        self.offset = Vector3()
        self.offset.set(30, 35, 30)
        self.offset.normlize()
        self.offset.scale1(self.arm_length)

        self.center = Vector3()
        self.drag_start = Vector3()

        self.press_time = 0

    def _create(self):
        set_process(self._get_node(), process=False, input=False)
        # gp.set_process(self._get_node(), True)
        # gp.set_process_input(self._get_node(), True)
        # gp.connect(self._get_node(), "ready", test_callback)
        # gp.connect(self._get_node(), "ready", self._ready)
        connect(self._get_node(), "ready", self._ready)
        self.main_camera = find_node(self._get_node(), 'MainCamera')

    def _ready(self):
        print_line("CameraMgr ready")

    def update(self):
        #print_safe(str(self._get_node()))
        self.handle_input()

    def handle_input(self):
        # left button
        if game_mgr.input_mgr.is_mouse_pressed(LEFT_BUTTON):
            if not self.is_left_button_pressed:
                self.is_left_button_pressed = True
                self.on_mouse_button_down()
            else:
                self.on_mouse_drag()
        else:
            if self.is_left_button_pressed:
                self.is_left_button_pressed = False
                self.on_mouse_button_up()

        # wheel up
        # if game_mgr.input_mgr.is_mouse_pressed(WHEEL_UP):
        #     if not self.is_wheel_up:
        #         self.is_wheel_up = True
        #         self.on_wheel(True)
        # else:
        #     if self.is_wheel_up:
        #         self.is_wheel_up = False

        # # wheel down
        # if game_mgr.input_mgr.is_mouse_pressed(WHEEL_DOWN):
        #     if not self.is_wheel_down:
        #         self.is_wheel_down = True
        #         self.on_wheel(False)
        # else:
        #     if self.is_wheel_down:
        #         self.is_wheel_down = False
        
    def on_mouse_button_down(self):
        input = game_mgr.input_mgr

        x,y,z = screen_to_world(self.main_camera, input.x, input.y)
        self.drag_start.set(x, y, z)

        self.press_time = get_time()
    
    # TODO： begin_drag(), end_drag(), drag()
    def on_mouse_drag(self):
        input = game_mgr.input_mgr

        # 拖拽场景，用移动摄像头来实现
        x,y,z = screen_to_world(self.main_camera, input.x, input.y)
        #print_line((x,y,z))
        dx = x - self.drag_start.x
        dy = y - self.drag_start.y
        dz = z - self.drag_start.z

        self.center.x -= dx
        self.center.y -= dy
        self.center.z -= dz

        self.update_camera()

    # 刷新camera位置和朝向
    def update_camera(self):
        set_position(self.main_camera,
            self.center.x + self.offset.x,
            self.center.y + self.offset.y,
            self.center.z + self.offset.z)
        lookat(self.main_camera,
            self.center.x,
            self.center.y,
            self.center.z)

    def on_mouse_button_up(self):
        input = game_mgr.input_mgr

        #print_line(get_delta_time())

        # t = get_time()
        # if t - self.press_time < 80:
        #     a = instantiate('res://models/City01.tscn')
        #     x,y,z = screen_to_world(self.main_camera, input.x, input.y)
        #     set_position(a, x, y, z)
        
    
    def on_wheel(self, up):
        self.arm_norm = clamp(self.arm_norm, 0.05 if up else -0.05)
        print_line(f'on_wheel: {self.arm_norm} {up}')
        self.offset.normlize()
        self.offset.scale1(self.arm_length * (0.5 + self.arm_norm * 0.5))

