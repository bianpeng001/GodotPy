#
# 2023年1月30日 bianpeng
#
import math

from game.core import *
from game.game_mgr import game_mgr

# def test_callback():
#     print_line("test_callback")

# 镜头管理
class CameraMgr(NodeObject):
    def __init__(self):
        super().__init__()

        self.is_left_button_pressed = False

        self.offset = Vector3()
        self.offset.set(30, 35, 30)
        self.center = Vector3()
        self.drag_start = Vector3()

        self.press_time = 0

        game_mgr.camera_mgr = self

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
        input = game_mgr.input_mgr
        
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

        t = get_time()
        if t - self.press_time < 80:
            a = instantiate('res://models/City01.tscn')
            x,y,z = screen_to_world(self.main_camera, input.x, input.y)
            set_position(a, x, y, z)
        

    
        
