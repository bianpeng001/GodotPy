#
# 2023年1月30日 bianpeng
#
import math

from game.core import *
from game.game_mgr import game_mgr
from game.input_mgr import *

# 镜头管理
class CameraMgr(NodeObject):
    def __init__(self):
        super().__init__()

        game_mgr.camera_mgr = self
        
        self.main_camera = None

        self.arm_length = 55
        self.arm_scale = 1.0
        self.arm_dir = Vector3(30, 35, 30).normalized()

        # 自拍杆的长度
        self.offset = self.arm_dir * self.arm_length
        # 自拍杆的手持位置
        self.center = Vector3()

        # 拖拽起始点
        self.drag_start = Vector3()

    def _create(self):
        self.get_obj().connect("ready", self._ready)
        self.main_camera = self.get_obj().find_node("MainCamera")

        game_mgr.event_mgr.add(WHEEL_UP_PRESS, self.on_wheel_up)
        game_mgr.event_mgr.add(WHEEL_DOWN_PRESS, self.on_wheel_down)

        game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, self.on_mouse_button_down)
        #game_mgr.event_mgr.add(LEFT_BUTTON_RELEASE, self.on_mouse_button_up)
        game_mgr.event_mgr.add(LEFT_BUTTON_DRAG, self.on_mouse_drag)

    def _ready(self):
        log_util.debug("CameraMgr ready")

    def on_mouse_button_down(self, x, y):
        x,y,z = self.main_camera.screen_to_world(x, y)
        self.drag_start.set(x, y, z)

    # TODO： begin_drag(), end_drag(), drag()
    def on_mouse_drag(self, x, y):
        # 拖拽场景，用移动摄像头来实现
        x,y,z = self.main_camera.screen_to_world(x, y)
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
        self.main_camera.set_position(
            self.center.x + self.offset.x,
            self.center.y + self.offset.y,
            self.center.z + self.offset.z)
        self.main_camera.look_at(
            self.center.x,
            self.center.y,
            self.center.z)

    def on_mouse_button_up(self):
        pass

    def process_zoom(self, delta):
        if game_mgr.ui_mgr.is_point_at_gui():
            return

        input_mgr = game_mgr.input_mgr
        x, y = input_mgr.get_mouse_pos()

        
        prev_norm = 1 + self.arm_scale
        self.arm_scale = clamp(self.arm_scale + delta)
        f = (1 + self.arm_scale) / prev_norm
        
        x1,y1,z1 = self.main_camera.screen_to_world(input_mgr.x, input_mgr.y)
        dx = (self.center.x - x1) * f
        dy = (self.center.y - y1) * f
        dz = (self.center.z - z1) * f

        self.center.set(x1+dx, y1+dy, z1+dz)
        self.offset = self.arm_dir * (self.arm_length * (1 + self.arm_scale) * 0.5)
        
        self.update_camera()

    def on_wheel_up(self):
        self.process_zoom(-0.05)

    def on_wheel_down(self):
        self.process_zoom(0.05)

    def set_center(self,x,y,z):
        self.center.set(x,y,z)
    
    def update(self, delta_time):
        pass

