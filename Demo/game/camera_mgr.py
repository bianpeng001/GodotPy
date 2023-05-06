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
        self.focus = Vector3()

        # 拖拽起始点
        self.drag_start = Vector3()

        # 动画移动的目标
        self.target_focus = Vector3()
        self.is_chase_target = False

    def _create(self):
        self.get_obj().connect("ready", self._ready)
        self.main_camera = self.get_obj().find_node("MainCamera")

        game_mgr.event_mgr.add(WHEEL_UP_PRESS, self.on_wheel_up)
        game_mgr.event_mgr.add(WHEEL_DOWN_PRESS, self.on_wheel_down)

        # game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, self.on_mouse_button_down)
        # game_mgr.event_mgr.add(LEFT_BUTTON_RELEASE, self.on_mouse_button_up)
        # game_mgr.event_mgr.add(LEFT_BUTTON_DRAG, self.on_mouse_drag)
        
        game_mgr.event_mgr.add(RIGHT_BUTTON_PRESS, self.on_mouse_button_down)
        game_mgr.event_mgr.add(RIGHT_BUTTON_RELEASE, self.on_mouse_button_up)
        game_mgr.event_mgr.add(RIGHT_BUTTON_DRAG, self.on_mouse_drag)

    def _ready(self):
        log_util.debug("CameraMgr ready")

    def on_mouse_button_down(self, x, y):
        x,y,z = self.main_camera.screen_to_world(x, y)
        self.drag_start.set(x, y, z)
        
        game_mgr.game_play.set_cursor(2)

    # TODO： begin_drag(), end_drag(), drag()
    def on_mouse_drag(self, x, y):
        # 拖拽场景，用移动摄像头来实现
        x,y,z = self.main_camera.screen_to_world(x, y)
        #print_line((x,y,z))
        dx = x - self.drag_start.x
        dy = y - self.drag_start.y
        dz = z - self.drag_start.z

        self.focus.x -= dx
        self.focus.y -= dy
        self.focus.z -= dz
        self.is_chase_target = False

        self.update_camera()

    # 刷新camera位置和朝向
    def update_camera(self):
        self.main_camera.set_position(
            self.focus.x + self.offset.x,
            self.focus.y + self.offset.y,
            self.focus.z + self.offset.z)
        self.main_camera.look_at(
            self.focus.x,
            self.focus.y,
            self.focus.z)

    def on_mouse_button_up(self):
        game_mgr.game_play.set_cursor(1)

    def process_zoom(self, delta):
        if game_mgr.ui_mgr.is_point_at_gui():
            return
        
        mx,my = game_mgr.input_mgr.get_mouse_pos()
        
        prev_norm = 1 + self.arm_scale
        self.arm_scale = clamp(self.arm_scale + delta)
        f = (1 + self.arm_scale) / prev_norm
        
        x1,y1,z1 = self.main_camera.screen_to_world(mx,my)
        dx = (self.focus.x - x1) * f
        dy = (self.focus.y - y1) * f
        dz = (self.focus.z - z1) * f

        self.focus.set(x1+dx, y1+dy, z1+dz)
        self.offset = self.arm_dir * (self.arm_length * (1 + self.arm_scale) * 0.5)
        
        self.update_camera()

    def on_wheel_up(self):
        self.process_zoom(-0.05)

    def on_wheel_down(self):
        self.process_zoom(0.05)

    # 直接设置focus
    def set_focus(self,x,y,z):
        self.focus.set(x,y,z)

    def get_focus_xz(self):
        return self.focus.x, self.focus.z

    def get_focus_xyz(self):
        return self.focus.x,self.focus.y,self.focus.z

    # 设置目标,然后快速飞过去
    def set_target_focus(self,x,y,z):
        self.target_focus.set(x,y,z)
        self.is_chase_target = True
    
    def update(self, delta_time):
        if self.is_chase_target:
            delta = self.focus - self.target_focus
            sqr_mag = delta.sqr_magnitude()
            if sqr_mag < 0.001:
                self.focus.copy(self.target_focus)
                self.is_chase_target = False
            else:
                self.focus = self.target_focus + delta * 0.9
            self.update_camera()



