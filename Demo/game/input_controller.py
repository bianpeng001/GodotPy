import sys

from game.core import NodeObject, print_line
import GodotPy as gp

class InputController(NodeObject):
    def post_create(self):
        #gp.set_process(self.py_capsule, True)
        gp.set_process_input(self.py_capsule, True)
        gp.connect(self.py_capsule, "ready", self._ready)

    def on_key_pressed(self, keycode, pressed):
        print_line(f'key pressed: keycode={keycode} press={pressed}')

    def on_mouse_button(self, button, x, y):
        print_line(f'mouse button: {button} x={x} y={y}')

    def on_mouse_move(self, x, y):
        print_line(f'mouse move: x={x} y={y}')

