#
# 2023年1月30日 bianpeng
#

import math
import random

import GodotPy as gp

#------------------------------------------------------------
#
#------------------------------------------------------------

# Plane
class Plane:
    def __init__(self, x0, y0 ,z0, n_x, n_y, n_z):
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

        self.n_x = n_x
        self.n_y = n_y
        self.n_z = n_z

# Ray
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

        d = (x1*plane.n_x + y1*plane.n_y + z1*plane.n_z) / \
            (ray.n_x*plane.n_x + ray.n_y*plane.n_y + ray.n_z*plane.n_z)
        return d

    def get_point(self, d):
        return self.x0+self.n_x*d, self.y0+self.n_y*d, self.z0+self.n_z*d

# Vector3
class Vector3:
    up = None
    right = None
    forward = None

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, b):
        self.x += b.x
        self.y += b.y
        self.z += b.z

    def offset(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

    def scale3(self, sx, sy, sz):
        self.x *= sx
        self.y *= sy
        self.z *= sz

    def scale(self, s):
        self.x *= s
        self.y *= s
        self.z *= s

    def scaled(self, s):
        v = self.clone()
        v.scale(s)
        return v

    def normlize(self):
        len = self.length()
        if len > 0:
            self.scale(1.0 / len)

    def normlized(self):
        v = self.clone()
        v.normlize()
        return v
    
    def __add__(self, b):
        v = self.clone()
        v.x += b.x
        v.y += b.y
        v.z += b.z
        return v

    def __sub__(self, b):
        v = self.clone()
        v.x -= b.x
        v.y -= b.y
        v.z -= b.z
        return v

    def __mul__(self, s):
        v = self.clone()
        v.scale(s)
        return v

    def __str__(self):
        return f'({self.x},{self.y},{self.z})'

    def length(self):
        return self.magnitude()

    def magnitude(self):
        return math.sqrt(self.sqr_magnitude())

    def sqr_magnitude(self):
        return self.dot(self)

    def dot(self, b):
        return self.x*b.x + self.y*b.y + self.z*b.z

    def dot3(self, x, y, z):
        return self.x*x + self.y*y + self.z*z

    def cross(self, b):
        a = self
        v = Vector3()
        v.x = a.y*b.z - a.z*b.y
        v.y = a.z*b.x - a.x*b.z
        v.z = a.x*b.y - a.y*b.x
        return v

    def clone(self):
        v = Vector3()
        v.set(self.x, self.y, self.z)
        return v

    def get_xyz(self):
        return self.x, self.y, self.z

Vector3.up = Vector3(0, 1, 0)

#------------------------------------------------------------
# pattern
#------------------------------------------------------------

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

#
class BaseMgr:
    pass
   
#------------------------------------------------------------
#
#------------------------------------------------------------

# 对应于godot场景树的节点，的容器
class NodeObject:
    def __init__(self):
        # 记录一个node的指针
        self.node_capsule = None
        self._gdobj = None

    def _get_node(self):
        return self.node_capsule

    def get_node(self):
        return self.node_capsule

    # start gdobj

    def get_obj(self):
        return GetWrappedObject(self._gdobj)

    def get_gdobj(self):
        return self._gdobj

    # end of gdobj
    
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

#------------------------------------------------------------
# api
#------------------------------------------------------------

# [-1, 1]
def random_x():
    return 2*(random.random()-0.5)

# [(-1,-1,-1), (1,1,1)]
def random_x_vector3(x, y, z):
    return random_x()*x, random_x()*y, random_x()*z

def random_max(max):
    return random.random()*max

def random_range(min, max):
    return min + random.random() * (max - min)

def print_line(*args, **kwargs):
    if not args:
        return
    
    if len(args) == 1:
        a = args[0]
        gp.print_line(str(a))
    else:
        a = ' '.join([str(x) for x in args])
        gp.print_line(a)

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

def look_at(node, x, y, z):
    gp.look_at(node, x, y, z)

def screen_to_world(camera, x, y):
    return gp.screen_to_world(camera, x, y)

def world_to_screen(camera, x, y, z):
    return gp.world_to_screen(camera, x, y, z)

def get_py_object(node):
    return gp.get_py_object(node)

def get_parent(node):
    return gp.get_parent(node)

def raycast_shape(camera, x,y,z):
    return gp.raycast_shape(camera, x,y,z)

def set_surface_color(node, index, r, g, b):
    gp.material_set_albedo_color(node, index, r, g, b)

def mesh_instance3d_load_material(node, index, path):
    gp.mesh_instance3d_load_material(node, index, path)

#------------------------------------------------------------
# api
#------------------------------------------------------------

#
class Node:
    @classmethod
    def get_parent(cls, node):
        return gp.get_parent(node)

    @classmethod
    def destroy(cls, node):
        gp.destroy(node)

    @classmethod
    def connect(cls, node, signal, cb):
        gp.connect(node, signal, cb)

class OS:
    @classmethod
    def get_time(cls):
        return gp.get_time()

    @classmethod
    def get_delta_time(cls):
        return gp.get_delta_time()

    @classmethod
    def set_window_size(cls, width, height, x, y):
        gp.set_window_size(width, height, x, y)

#
class Debug:
    @classmethod
    def get_monitor(cls, monitor_type):
        return gp.debug_get_monitor(monitor_type)

    @classmethod
    def get_drawcall(cls):
        return int(cls.get_monitor(13))

    @classmethod
    def get_fps(cls):
        return int(cls.get_monitor(0))

#------------------------------------------------------------
# log util
#------------------------------------------------------------

class LogUtil:
    def __init__(self):
        self.enable_debug = True
        self.enable_error = True

    def debug(self, *args):
        if self.enable_debug:
            print_line('[DEBUG]', *args)

    def error(self, *args):
        if self.enable_error:
            print_line('[ERROR]', *args)

    def print(self, msg):
        print_line(msg)

log_util = LogUtil()
logutil = log_util

#------------------------------------------------------------
# oop 封装
#------------------------------------------------------------

class FObject:
    def __init__(self):
        self._gdobj = None

    def get_gdobj(self):
        return self._gdobj

    def is_valid(self):
        return self.get_gdobj().is_valid()

    def connect(self, signal, callback):
        gp.connect(self.get_gdobj(), signal, callback)

class FNode(FObject):
    def destroy(self):
        gp.destroy(self.get_gdobj())

    def find_node(self, path):
        gdobj = gp.find_node(self.get_gdobj(), path)
        return GetWrappedObject(gdobj)

    def reparent(self, new_parent_obj):
        gp.reparent(self.get_gdobj(), new_parent_obj.get_gdobj())

    def get_parent(self):
        parent_gdobj = gp.get_parent(self.get_gdobj())
        return GetWrappedObject(parent_gdobj)

    def set_process(self, process=False,input=False,physics=False):
        gp.set_process(self.get_gdobj(), process)
        gp.set_process_input(self.get_gdobj(), input)
        gp.set_physics_process(self.get_gdobj(), physics)
    
    def find_control(self, x,y):
        gdobj = gp.find_control(self.get_gdobj(), x, y)
        return GetWrappedObject(gdobj)

class FNode3D(FNode):
    def set_position(self, x,y,z):
        gp.set_position(self.get_gdobj(), x,y,z)

    def set_rotation(self, x,y,z):
        gp.set_rotation(self.get_gdobj(), x,y,z)

    def set_scale(self, sx,sy,sz):
        gp.set_scale(self.get_gdobj(), sx, sy, sz)

    def get_position(self):
        return gd.get_position(self.get_gdobj())

    def look_at(self, x,y,z):
        gp.look_at(self.get_gdobj(), x,y,z)

    def set_visible(self, value):
        gp.set_visible(self.get_gdobj(), value)

    @classmethod
    def instantiate(cls, path):
        gdobj = gp.instantiate2(path)
        return GetWrappedObject(gdobj)

class FVisualInstance3D(FNode3D):
    pass

class FCamera3D(FNode3D):
    def screen_to_world(self, x,y):
        return gp.screen_to_world(self.get_gdobj(), x, y)

    def world_to_screen(self, x,y,z):
        return gp.world_to_screen(self.get_gdobj(), x,y,z)

class FMeshInstance3D(FNode3D):
    def load_material(self, index, path):
        gp.mesh_instance3d_load_material(self.get_gdobj(), index, path)

class FAnimationPlayer(FNode3D):
    def play(self, anim_name):
        gp.animation_player_play(self.get_gdobj(), anim_name)

    def stop(self):
        pass

    def pause(self):
        pass

    def set_speed_scale(self, speed):
        gp.animation_player_set_speed_scale(self.get_gdobj(), speed)

class FLabel3D(FNode3D):
    def set_text(self, text):
        gp.label3d_set_text(self.get_gdobj(), text)

class FCPUParticles3D(FVisualInstance3D):
    def set_emitting(self, value):
        gp.cpu_particle_set_emitting(self.get_gdobj(), value)

class FCanvasItem(FNode):
    def set_visible(self, show):
        gp.canvas_item_set_visible(self.get_gdobj(), show)

class FNode2D(FCanvasItem):
    def set_position(self, x,y):
        gp.node2d_set_position(self.get_gdobj(), x,y)

class FLabel(FCanvasItem):
    def __init__(self):
        super().__init__()
        self.text = None

    def set_text(self, text):
        if self.text == text:
            return
        self.text = text
        gp.label_set_text(self.get_gdobj(), text)

class FButton(FCanvasItem):
    pass

class FImage(FCanvasItem):
    pass

class FPanel(FCanvasItem):
    pass

   
# 类型到wrap类的映射
# 这个wrap的好处就是，利用oop，使得操作的对象上面只有对应类型能用的方法
# 不在直接使用node对应的原始的pygd_obj，那个对象只用来当做一个弱引用使用
FClassMap = [None for x in range(20)]

def GetWrappedObject(gdobj):
    if not gdobj:
        return None

    obj = gdobj.get_wrapped_object()
    if obj:
        return obj

    obj_type = gdobj.get_type()
    #log_util.debug(f'gdobj type={obj_type}')
    class_type = FClassMap[obj_type] or FObject

    obj = class_type()
    obj._gdobj = gdobj
    gdobj.set_wrapped_object(obj)

    return obj

#
FClassMap[1] = FNode
FClassMap[2] = FNode3D
FClassMap[3] = FMeshInstance3D
FClassMap[4] = FCPUParticles3D
FClassMap[5] = FAnimationPlayer
FClassMap[6] = FLabel3D
FClassMap[7] = FCamera3D

FClassMap[11] = FCanvasItem
FClassMap[12] = FNode2D
FClassMap[13] = FLabel

# 大话降龙
# https://www.mm1316.com/maoxian/dahuajianglong

