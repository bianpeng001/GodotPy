#
# 2023年1月30日 bianpeng
#

from game.core import *

instance = None

def get_input():
    return instance

# handle input events
class InputController(NodeObject):
    def __init__(self):
        global instance

        super().__init__()
        instance = self

        print_line('create InputController')
        self.x = self.y = 0
        self.mouse_pressed = [False, False, False, False]
        self.key_dict = {}

    def _create(self):
        set_process(self.py_capsule, process=False, input=True)
        connect(self.py_capsule, "ready", self._ready)

    def _ready(self):
        print_line(f"input controller ready")

    def on_key_pressed(self, keycode, pressed):
        is_pressed = pressed != 0
        #print_line(f'key pressed: keycode={keycode} pressed={is_pressed}')
        
        self.key_dict[keycode] = is_pressed

    def on_mouse_button(self, button, pressed, x, y):
        self.x = x
        self.y = y
        is_pressed = pressed != 0
        #print_line(f'mouse button: button={button} pressed={is_pressed} x={x} y={y}')

        self.mouse_pressed[button] = is_pressed

    def is_mouse_pressed(self, button):
        return self.mouse_pressed[button]

    def on_mouse_move(self, x, y):
        self.x = x
        self.y = y

        # if self.is_mouse_pressed(1):
        #     print_line(f'mouse move: x={x} y={y}')
        #     pass
        # else:
        #     pass




