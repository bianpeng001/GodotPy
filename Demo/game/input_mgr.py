#
# 2023年1月30日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.event_name import *

#
# 定义按钮
#
LEFT_BUTTON = 1
RIGHT_BUTTON = 2
MIDDLE_BUTTON = 3
WHEEL_UP_BUTTON = 4
WHEEL_DOWN_BUTTON = 5

SPECIAL = 1 << 22
KEY_ESC = SPECIAL | 0x01
KEY_TAB = SPECIAL | 0x02
KEY_ENTER = SPECIAL | 0x05
KEY_PAUSE = SPECIAL | 0x09
KEY_PRINT = SPECIAL | 0x0A
KEY_HOME = SPECIAL | 0x0D
KEY_SHIFT = SPECIAL | 0x15
KEY_CTRL = SPECIAL | 0x16
KEY_F7 = SPECIAL | 0x22
KEY_F8 = SPECIAL | 0x23
KEY_F9 = SPECIAL | 0x24
KEY_F10 = SPECIAL | 0x25

#
# 滚轮的事件表 [button] = event_name
#
wheel_events = (
    None,
    LEFT_BUTTON_PRESS,
    RIGHT_BUTTON_PRESS,
    None,
    WHEEL_UP_PRESS,
    WHEEL_DOWN_PRESS,
)

#
# 鼠标操作的几个状态
#
class MouseButtonData:
    def __init__(self):
        # 是否按下
        self.pressed = False
        # 按下的初始位置
        self.press_x = 0
        self.press_y = 0
        # 按下的初始时间
        self.press_time = 0
        # 是否有drag行为
        self.drag = False

#
# 输入管理器, 处理鼠标键盘事件
#
class InputMgr(NodeObject):
    def __init__(self):
        super().__init__()
        
        game_mgr._input_mgr = self

        self.x = self.y = 0
        self.mouse_pressed = [False, False, False, False]
        self.key_dict = {}

        # handle left button
        self.left_button = MouseButtonData()
        self.left_button.event_press = LEFT_BUTTON_PRESS
        self.left_button.event_release = LEFT_BUTTON_RELEASE
        self.left_button.event_begin_drag = LEFT_BUTTON_BEGIN_DRAG
        self.left_button.event_drag = LEFT_BUTTON_DRAG
        self.left_button.event_end_drag = LEFT_BUTTON_END_DRAG
        self.left_button.event_click = LEFT_BUTTON_CLICK
        # handle right button
        self.right_button = MouseButtonData()
        self.right_button.event_press = RIGHT_BUTTON_PRESS
        self.right_button.event_release = RIGHT_BUTTON_RELEASE
        self.right_button.event_begin_drag = RIGHT_BUTTON_BEGIN_DRAG
        self.right_button.event_drag = RIGHT_BUTTON_DRAG
        self.right_button.event_end_drag = RIGHT_BUTTON_END_DRAG
        self.right_button.event_click = RIGHT_BUTTON_CLICK


    def _create(self):
        self.get_obj().set_process(input=True)
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        print_line(f"InputMgr ready")

    def is_mouse_pressed(self, button):
        return self.mouse_pressed[button] if button <= MIDDLE_BUTTON else False
    
    def get_mouse_pos(self):
        return self.x, self.y

    def on_key_pressed(self, keycode, pressed):
        is_pressed = pressed != 0
        #log_debug(f'key pressed: keycode={keycode} pressed={is_pressed}')
        if pressed:
            game_mgr.event_mgr.emit(KEY_PRESS, keycode)
                
        
        self.key_dict[keycode] = is_pressed

    def on_mouse_button(self, button, pressed, x, y):
        self.x = x
        self.y = y
        is_pressed = pressed != 0
        #print_line(f'mouse button: button={button} pressed={is_pressed} x={x} y={y}')

        if button <= MIDDLE_BUTTON:
            self.mouse_pressed[button] = is_pressed
        elif is_pressed:
            game_mgr.event_mgr.emit(wheel_events[button])

    def on_mouse_move(self, x, y):
        self.x = x
        self.y = y

    def update(self, delta_time):
        #self.process_left_button()
        self.process_mouse_button(LEFT_BUTTON, self.left_button)
        self.process_mouse_button(RIGHT_BUTTON, self.right_button)
    
    # 支持左右键的通用版本
    def process_mouse_button(self, button_id, mouse_data):
        event_mgr = game_mgr.event_mgr
        
        last = mouse_data.pressed
        curr = self.mouse_pressed[button_id]
        mouse_data.pressed = curr
        if last != curr:
            if curr:
                event_mgr.emit(mouse_data.event_press, self.x, self.y)
                mouse_data.press_x = self.x
                mouse_data.press_y = self.y
                mouse_data.press_time = game_mgr.time
            else:
                if mouse_data.drag:
                    mouse_data.drag = False
                    event_mgr.emit(mouse_data.event_end_drag)
                    event_mgr.emit(mouse_data.event_release)
                else:
                    # 从按下后，从没有进行过drag，则当做click事件
                    event_mgr.emit(mouse_data.event_release)
                    event_mgr.emit(mouse_data.event_click)
        else:
            if curr:
                dx = self.x - mouse_data.press_x
                if dx*dx > 4 and self.can_drag():
                    if not mouse_data.drag:
                        mouse_data.drag = True
                        event_mgr.emit(mouse_data.event_begin_drag)
                    else:
                        event_mgr.emit(mouse_data.event_drag, self.x, self.y)

    # 这个是原先的, 只处理左键的版本
    def process_left_button(self):
        last = self.left_button.pressed
        curr = self.mouse_pressed[LEFT_BUTTON]
        self.left_button.pressed = curr
        if last != curr:
            if curr:
                game_mgr.event_mgr.emit(LEFT_BUTTON_PRESS, self.x, self.y)
                self.left_button.press_x = self.x
                self.left_button.press_y = self.y
                self.left_button.press_time = game_mgr.time
            else:
                if self.left_button.drag:
                    self.left_button.drag = False
                    game_mgr.event_mgr.emit(LEFT_BUTTON_END_DRAG)
                    game_mgr.event_mgr.emit(LEFT_BUTTON_RELEASE)
                else:
                    # 从按下后，从没有进行过drag，则当做click事件
                    game_mgr.event_mgr.emit(LEFT_BUTTON_RELEASE)
                    game_mgr.event_mgr.emit(LEFT_BUTTON_CLICK)
        else:
            if curr:
                dx = self.x - self.left_button.press_x
                if dx*dx > 4 and self.can_drag():
                    if not self.left_button.drag:
                        self.left_button.drag = True
                        game_mgr.event_mgr.emit(LEFT_BUTTON_BEGIN_DRAG)
                    else:
                        game_mgr.event_mgr.emit(LEFT_BUTTON_DRAG, self.x, self.y)

    # 判断是否可以drag
    def can_drag(self):
        #camera = game_mgr.camera_mgr.main_camera
        #control = camera.find_control(self.x, self.y)
        #return control == None
        return not game_mgr.ui_mgr.is_point_at_gui()


