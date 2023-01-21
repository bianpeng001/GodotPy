from game.core import BaseClass, print_line
print_line('camera controller loaded')
import GodotPy as gp

class CameraController(BaseClass):
    def __init__(self):
        super().__init__()
        print_line('create camera controller')

    def post_create(self):
        #gp.set_process(self.py_capsule, True)
        pass

    def process(self):
        #print_safe(str(self.py_capsule))
        print_line('process')
        pass


