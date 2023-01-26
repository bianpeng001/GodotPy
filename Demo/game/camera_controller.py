from game.core import NodeObject, print_line
import GodotPy as gp

import sys

def test_callback():
    print_line("test_callback")

class CameraController(NodeObject):
    def __init__(self):
        super().__init__()
        print_line('create camera controller')

    def post_create(self):
        #gp.set_process(self.py_capsule, True)
        gp.set_process_input(self.py_capsule, True)
        #gp.connect(self.py_capsule, "ready", test_callback)
        gp.connect(self.py_capsule, "ready", self._ready)
        pass

    def process(self):
        #print_safe(str(self.py_capsule))
        print_line('process')
        pass

    def _ready(self):
        print_line(f"ready _ready:{sys.getrefcount(self._ready)}")
        
    def on_key_pressed(self, keycode, pressed):
        print_line(f'key pressed: keycode={keycode} press={pressed}')

    def on_mouse_button(self, button, x, y):
        print_line(f'mouse move: button={button} x={x} y={y}')


