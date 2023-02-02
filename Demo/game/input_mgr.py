#
# 2023年1月30日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

LEFT_BUTTON = 1
RIGHT_BUTTON = 2
MIDDLE_BUTTON = 3
WHEEL_UP = 4
WHEEL_DOWN = 5

LEFT_BUTTON_PRESS = 'left_button_press'
LEFT_BUTTON_RELEASE = 'left_button_release'

LEFT_BUTTON_BEGIN_DRAG = 'left_button_begin_drag'
LEFT_BUTTON_DRAG = 'left_button_drag'
LEFT_BUTTON_END_DRAG = 'left_button_end_drag'

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
        
        game_mgr.input_mgr = self

        self.x = self.y = 0
        self.mouse_pressed = [False, False, False, False, False, False, False, False, False]
        self.key_dict = {}

        # handle left button
        self.left_button = MouseButtonData()

    def _create(self):
        set_process(self._get_node(), process=False, input=True)
        connect(self._get_node(), "ready", self._ready)

    def _ready(self):
        print_line(f"InputMgr ready")

    def is_mouse_pressed(self, button):
        return self.mouse_pressed[button]

    def on_key_pressed(self, keycode, pressed):
        is_pressed = pressed != 0
        #print_line(f'key pressed: keycode={keycode} pressed={is_pressed}')
        
        self.key_dict[keycode] = is_pressed

    def on_mouse_button(self, button, pressed, x, y):
        self.x = x
        self.y = y
        is_pressed = pressed != 0
        #print_line(f'mouse button: button={button} pressed={is_pressed} x={x} y={y}')

        # if is_pressed and (button == WHEEL_UP or button == WHEEL_DOWN):
        #     self.mouse_pressed[button] = is_pressed
        # else:
        #     self.mouse_pressed[button] = is_pressed
        self.mouse_pressed[button] = is_pressed

    def on_mouse_move(self, x, y):
        self.x = x
        self.y = y

    def update(self, delta_time):
        self.process_input_events()

    def process_input_events(self):
        if self.is_mouse_pressed(LEFT_BUTTON):
            if not self.left_button.pressed:
                self.left_button.pressed = True
                self.left_button.press_x = self.x
                self.left_button.press_y = self.y

                game_mgr.event_mgr.emit(LEFT_BUTTON_PRESS, self.x, self.y)
            else:
                dx = self.x - self.left_button.press_x
                if dx*dx > 0:
                    if not self.left_button.drag:
                        self.left_button.drag = True
                        game_mgr.event_mgr.emit(LEFT_BUTTON_BEGIN_DRAG)
                    else:
                        game_mgr.event_mgr.emit(LEFT_BUTTON_DRAG)
        else:
            if self.left_button.pressed:
                self.left_button.pressed = False

                if self.left_button.drag:
                    self.left_button.drag = False
                    game_mgr.event_mgr.emit(LEFT_BUTTON_END_DRAG)
                game_mgr.event_mgr.emit(LEFT_BUTTON_RELEASE)

      



