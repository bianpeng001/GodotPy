#
# 2023年1月30日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

from game.event_name import *

# 定义按钮
LEFT_BUTTON = 1
RIGHT_BUTTON = 2
MIDDLE_BUTTON = 3
WHEEL_UP_BUTTON = 4
WHEEL_DOWN_BUTTON = 5

wheel_events = (
    None,
    LEFT_BUTTON_PRESS,
    None,
    None,
    WHEEL_UP_PRESS,
    WHEEL_DOWN_PRESS,
)

#
class MouseButtonData:
    def __init__(self):
        self.pressed = False
        self.press_x = self.press_y = 0
        self.press_time = 0
        self.drag = False

# 输入管理器
class InputMgr(NodeObject):
    def __init__(self):
        super().__init__()
        
        game_mgr._input_mgr = self

        self.x = self.y = 0
        self.mouse_pressed = [False, False, False, False]
        self.key_dict = {}

        # handle left button
        self.left_button = MouseButtonData()

    def _create(self):
        set_process(self._get_node(), process=False, input=True)
        connect(self._get_node(), "ready", self._ready)

    def _ready(self):
        print_line(f"InputMgr ready")

    def is_mouse_pressed(self, button):
        return self.mouse_pressed[button] if button <= MIDDLE_BUTTON else False

    def on_key_pressed(self, keycode, pressed):
        is_pressed = pressed != 0
        #print_line(f'key pressed: keycode={keycode} pressed={is_pressed}')
        
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
        #self.process_input_events()
        self.process_left_button()

    def process_left_button(self):
        last = self.left_button.pressed
        curr = self.mouse_pressed[LEFT_BUTTON]
        self.left_button.pressed = curr
        if last != curr:
            if curr:
                game_mgr.event_mgr.emit(LEFT_BUTTON_PRESS, self.x, self.y)
            else:
                if self.left_button.drag:
                    self.left_button.drag = False
                    game_mgr.event_mgr.emit(LEFT_BUTTON_END_DRAG)
                game_mgr.event_mgr.emit(LEFT_BUTTON_RELEASE)
        else:
            if curr:
                dx = self.x - self.left_button.press_x
                if dx*dx > 0:
                    if not self.left_button.drag:
                        self.left_button.drag = True
                        game_mgr.event_mgr.emit(LEFT_BUTTON_BEGIN_DRAG)
                    else:
                        game_mgr.event_mgr.emit(LEFT_BUTTON_DRAG, self.x, self.y)


    # def process_input_events(self):
    #     if self.is_mouse_pressed(LEFT_BUTTON):
    #         if not self.left_button.pressed:
    #             self.left_button.pressed = True
    #             self.left_button.press_x = self.x
    #             self.left_button.press_y = self.y

    #             game_mgr.event_mgr.emit(LEFT_BUTTON_PRESS, self.x, self.y)
    #         else:
    #             dx = self.x - self.left_button.press_x
    #             if dx*dx > 0:
    #                 if not self.left_button.drag:
    #                     self.left_button.drag = True
    #                     game_mgr.event_mgr.emit(LEFT_BUTTON_BEGIN_DRAG)
    #                 else:
    #                     game_mgr.event_mgr.emit(LEFT_BUTTON_DRAG)
    #     else:
    #         if self.left_button.pressed:
    #             self.left_button.pressed = False

    #             if self.left_button.drag:
    #                 self.left_button.drag = False
    #                 game_mgr.event_mgr.emit(LEFT_BUTTON_END_DRAG)
    #             game_mgr.event_mgr.emit(LEFT_BUTTON_RELEASE)

      



