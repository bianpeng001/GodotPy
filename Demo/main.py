#import GodotPy as gp
#gp.print('main module loaded')

import sys
for a in sys.path:
    gp.print(a)

#btn = gp.find_node('/root/Node3D/Button')
#gp.print(repr(btn))

from game.core import NodeObject, print_line

print_line('main module loaded')

class TestClass(NodeObject):
    def __init__(self):
        super().__init__()

    def hello(self):
        #gp.print('hello')
        #gp.print(repr(self.py_capsule))
        #gp.print(repr(gp.find_node(self.py_capsule, '/root/Node3D/Button')))
        #gp.print(repr(gp.find_node(self.py_capsule, '/root/Node3D/Button1')))
        pass

        

