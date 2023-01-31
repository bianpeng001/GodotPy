#
# 2023年1月30日 bianpeng
#

from game.core import *
from game.game_mgr import GameMgr

# 输入管理器
class InputMgr(NodeObject):
    def __init__(self):
        super().__init__()
        
        self.x = self.y = 0
        self.mouse_pressed = [False, False, False, False, False, False, False, False, False]
        self.key_dict = {}

        game_mgr = GameMgr.get_instance()
        game_mgr.input_mgr = self

    def _create(self):
        set_process(self._get_node(), process=False, input=True)
        connect(self._get_node(), "ready", self._ready)

        print_line('create InputMgr ok')

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

        self.mouse_pressed[button] = is_pressed

    def on_mouse_move(self, x, y):
        self.x = x
        self.y = y

