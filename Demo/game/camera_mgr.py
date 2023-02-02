#
# 2023年1月30日 bianpeng
#
import math

from game.core import *
from game.game_mgr import game_mgr
from game.input_mgr import *

# def test_callback():
#     print_line("test_callback")

def clamp(v):
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

        #self.is_left_button_pressed = False

        self.arm_length = 55
        self.arm_scale = 1.0
        self.arm_dir = Vector3()
        self.arm_dir.set(30, 35, 30)
        self.arm_dir.normlize()

        self.offset = Vector3()
        self.offset.set(self.arm_dir.x, self.arm_dir.y, self.arm_dir.z)
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

        game_mgr.event_mgr.add(WHEEL_UP_PRESS, self.on_wheel_up)
        game_mgr.event_mgr.add(WHEEL_DOWN_PRESS, self.on_wheel_down)

        game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, self.on_mouse_button_down)
        #game_mgr.event_mgr.add(LEFT_BUTTON_RELEASE, self.on_mouse_button_up)
        game_mgr.event_mgr.add(LEFT_BUTTON_DRAG, self.on_mouse_drag)

    def _ready(self):
        print_line("CameraMgr ready")

    def on_mouse_button_down(self, x, y):
        x,y,z = screen_to_world(self.main_camera, x, y)
        self.drag_start.set(x, y, z)

        self.press_time = get_time()
    
    # TODO： begin_drag(), end_drag(), drag()
    def on_mouse_drag(self, x, y):
        # 拖拽场景，用移动摄像头来实现
        x,y,z = screen_to_world(self.main_camera, x, y)
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
        pass

    def process_zoom(self, delta):
        input_mgr = game_mgr.input_mgr

        prev_norm = 1 + self.arm_scale
        self.arm_scale = clamp(self.arm_scale + delta)
        
        x1,y1,z1 = screen_to_world(self.main_camera, input_mgr.x, input_mgr.y)

        f = (1 + self.arm_scale) / prev_norm
        dx = (self.center.x - x1) * f
        dy = (self.center.y - y1) * f
        dz = (self.center.z - z1) * f

        self.center.set(x1+dx, y1+dy, z1+dz)

        self.offset.set(self.arm_dir.x, self.arm_dir.y, self.arm_dir.z)
        self.offset.scale1(self.arm_length * (1 + self.arm_scale) * 0.5)
        
        self.update_camera()

    def on_wheel_up(self):
        self.process_zoom(-0.05)

    def on_wheel_down(self):
        self.process_zoom(0.05)



