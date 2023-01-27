import sys

from game.core import NodeObject, print_line
import GodotPy as gp

class InputController(NodeObject):
    def __init__(self):
        super().__init__()
        self.left_mouse_pressed = False

    def _post_create(self):
        gp.set_process(self.py_capsule, True)
        gp.set_process_input(self.py_capsule, True)
        gp.connect(self.py_capsule, "ready", self._ready)

    def on_key_pressed(self, keycode, pressed):
        print_line(f'key pressed: keycode={keycode} press={pressed}')

    def on_mouse_button(self, button, pressed, x, y):
        print_line(f'mouse button: {button} {pressed} x={x} y={y}')
        if button == 1:
            self.left_mouse_pressed = pressed != 0

    def on_mouse_move(self, x, y):
        if self.left_mouse_pressed:
            print_line(f'mouse move: x={x} y={y}')

    def _process(self):
        pass



        