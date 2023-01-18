import GodotPy as gp

gp.print('module loaded')


import sys
for a in sys.path:
    gp.print(a)

btn = gp.find_node('/root/Node3D/Button')
gp.print(repr(btn))

