import sys

from game.core import NodeObject, print_line
import GodotPy as gp

def test_callback():
    print_line("test_callback")

class CameraController(NodeObject):
    def __init__(self):
        super().__init__()
        print_line('create camera controller')

    def _post_create(self):
        #gp.set_process(self.py_capsule, True)
        #gp.set_process_input(self.py_capsule, True)
        #gp.connect(self.py_capsule, "ready", test_callback)
        #gp.connect(self.py_capsule, "ready", self._ready)
        pass

    def _process(self):
        #print_safe(str(self.py_capsule))
        print_line('process')
        pass

    def _ready(self):
        print_line(f"ready _ready:{sys.getrefcount(self._ready)}")
        



