import sys

from game.core import NodeObject, print_line
import GodotPy as gp

#
# handle input events
#
class InputController(NodeObject):
    def __init__(self):
        super().__init__()
        print_line('create InputController')
        self.mouse_pressed = [False, False, False, False]

    def _create(self):
        gp.set_process(self.py_capsule, True)
        gp.set_process_input(self.py_capsule, True)
        gp.connect(self.py_capsule, "ready", self._ready)

    def on_key_pressed(self, keycode, pressed):
        print_line(f'key pressed: keycode={keycode} press={pressed}')

    def on_mouse_button(self, button, pressed, x, y):
        print_line(f'mouse button: {button} {pressed} x={x} y={y}')
        is_pressed = pressed != 0
        self.mouse_pressed[button] = is_pressed

    def on_mouse_move(self, x, y):
        if self.mouse_pressed[1]:
            print_line(f'mouse move: x={x} y={y}')

    def _process(self):
        pass



