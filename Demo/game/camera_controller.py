from game.core import BaseClass, print_safe
print_safe('camera controller loaded')

class CameraController(BaseClass):
    def __init__(self):
        super().__init__()
        print_safe('create camera controller')

    def process(self):
        #print_safe(str(self.py_capsule))
        print_safe('process')
        pass


