#
# 2023年1月30日 bianpeng
#

import math
import random

import GodotPy as gp

#
class Plane:
    def __init__(self, x0, y0 ,z0, n_x, n_y, n_z):
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

        self.n_x = n_x
        self.n_y = n_y
        self.n_z = n_z

#
class Ray:
    def __init__(self, x0, y0, z0, n_x, n_y, n_z):
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

        self.n_x = n_x
        self.n_y = n_y
        self.n_z = n_z

    def raycast(self, plane):
        ray = self
        x1 = plane.x0 - ray.x0
        y1 = plane.y0 - ray.y0
        z1 = plane.z0 - ray.z0

        d = (x1*plane.n_x + y1*plane.n_y + z1*plane.n_z) /\
            (ray.n_x*plane.n_x + ray.n_y*plane.n_y + ray.n_z*plane.n_z)
        return d

    def get_point(self, d):
        return self.x0+self.n_x*d, self.y0+self.n_y*d, self.z0+self.n_z*d

# Vector3
class Vector3:
    def __init__(self):
        self.x = self.y = self.z = 0

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, left, right):
        self.x = left.x + right.x
        self.y = left.y + right.y
        self.z = left.z + right.z

    def offset(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

    def scale(self, sx, sy, sz):
        self.x *= sx
        self.y *= sy
        self.z *= sz

    def scale1(self, s):
        self.x *= s
        self.y *= s
        self.z *= s

    def normlize(self):
        len = math.sqrt(self.dot(self))
        if len > 0:
            self.scale1(1 / len)
    
    def __add___(self, right):
        v = Vector3()
        v.x = self.x + right.x
        v.y = self.y + right.y
        v.z = self.z + right.z
        return v

    def __sub__(self, right):
        v = Vector3()
        v.x = self.x - right.x
        v.y = self.y - right.y
        v.z = self.z - right.z
        return v

    def dot(self, right):
        return self.x*right.x + self.y*right.y + self.z*right.z

    def dot3(self, x, y, z):
        return self.x*x + self.y*y + self.z*z

    def cross(self, right):
        pass

    def clone(self):
        v = Vector3()
        v.set(self.x, self.y, self.z)
        return v

    def get_xyz(self):
        return self.x, self.y, self.z

# 单例
class Singleton:
    _instance = None
    @classmethod
    def get_instance(class_):
        if not class_._instance:
            class_._instance = class_()
        return class_._instance

    def __init__(self):
        pass
   

# 对应于godot场景树的节点，的容器
class NodeObject:
    def __init__(self):
        # 记录一个node的指针
        self.node_capsule = None

    def _get_node(self):
        return self.node_capsule

    def get_node(self):
        return self.node_capsule
    
    def on_mouse_button(self, button, pressed, x, y):
        pass

    def on_key_pressed(self, keycode, pressed):
        pass

    def on_mouse_move(self, x, y):
        pass

    def _ready(self):
        print_line(f'{type(self).__name__} ready')

    def _process(self):
        pass

    def _physics_process(self):
        pass

    # 构造函数之后回调
    def _create(self):
        pass

# [-1, 1]
def random_x():
    return 2*(random.random()-0.5)

# [(-1,-1,-1), (1,1,1)]
def random_x_vector3(x, y, z):
    return random_x()*x, random_x()*y, random_x()*z

def random_max(max):
    return random.random()*max

def print_line(*args, **kwargs):
    if not args:
        return
    
    if len(args) == 1:
        a = args[0]
        gp.print_line(str(a))
    else:
        a = ' '.join([str(x) for x in args])
        gp.print_line(a)

def find_node(node, path):
    return gp.find_node(node, path)

def set_process(node, process=False, input=False, physics=False):
    if process:
        gp.set_process(node, True)
    
    if input:
        gp.set_process_input(node, True)

    if physics:
        gp.set_physics_process(node, True)

def connect(node, signal, callback):
    gp.connect(node, signal, callback)

def get_position(node):
    return gp.get_position(node)

def set_position(node, x, y, z):
    gp.set_position(node, x, y, z)

def set_scale(node, x, y, z):
    gp.set_scale(node, x, y, z)

def lookat(node, x, y, z):
    gp.lookat(node, x, y, z)

def screen_to_world(camera, x, y):
    return gp.screen_to_world(camera, x, y)

def world_to_screen(camera, x, y, z):
    return gp.world_to_screen(camera, x, y, z)

def get_time():
    return gp.get_time()

def get_delta_time():
    return gp.get_delta_time()

def instantiate(path):
    return gp.instantiate(path)

def get_py_object(node):
    return gp.get_py_object(node)

def get_parent(node):
    return gp.get_parent(node)

def raycast_shape(camera, x,y,z):
    return gp.raycast_shape(camera, x,y,z)

def set_position_2d(node, x, y):
    gp.set_position_2d(node, x, y)

def set_visible_2d(node, v):
    gp.set_visible_2d(node, v)

def find_control(camera, x, y):
    return gp.find_control(camera, x, y)

#
class Node:
    @classmethod
    def find_node(cls, node, path):
        return gp.find_node(node, path)

#
class Label3D:
    @classmethod
    def set_text(cls, node, text):
        gp.label3d_set_text(node, text)

# 
class Node3D:
    @classmethod
    def set_position(self,node,x,y,z):
        gp.set_position(node,x,y,z)

class OS:
    @classmethod
    def get_time(cls):
        return gp.get_time()

    @classmethod
    def get_delta_time(cls):
        return gp.get_delta_time()

#
class Camera3D:
    @classmethod
    def world_to_screen(cls, camera, x, y, z):
        return gp.world_to_screen(camera, x,y,z)
    
    @classmethod
    def screen_to_world(cls, camera, x,y):
        return gp.screen_to_world(camera, x,y)

