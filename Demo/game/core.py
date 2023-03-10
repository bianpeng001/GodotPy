#
# 2023年1月30日 bianpeng
#

import sys
import math
import random
import traceback
import os

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

# 四元组
class Quaternion:
    def __init__(self):
        self.s = 0
        self.v = Vector3(1, 0, 0)

# 向量
class Vector3:
    up = None
    x_ais = None
    y_ais = None
    z_ais = None

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def copy(self, v):
        self.set(v.x,v.y,v.z)

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

    def normalize(self):
        len = self.length()
        if len > 0:
            self.scale(1.0 / len)

    def normalized(self):
        v = self.clone()
        v.normalize()
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
        return Vector3(self.x, self.y, self.z)

    def get_xyz(self):
        return self.x, self.y, self.z

    def get_xy(self):
        return self.x, self.y

    def get_xz(self):
        return self.x, self.z


Vector3.x_axis = Vector3(1, 0, 0)
Vector3.y_axis = Vector3(0, 1, 0)
Vector3.z_axis = Vector3(0, 0, 1)

Vector3.up = Vector3.y_axis

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

# 管理器的基类，提供一个空的update
class BaseMgr:
    def update(self):
        pass

#------------------------------------------------------------
#
#------------------------------------------------------------

# 对应于godot场景树的节点，的容器
class NodeObject:
    def __init__(self):
        self._gdobj = None

    # 这个是兼容原来的设计, c++端的FPyObject, 这里 get_obj() 实际就是 self
    # 但是,只有NodeObject才有,
    def get_obj(self):
        wrap_obj = GetWrappedObject(self._gdobj)
        # wrap_obj 跟 self 的区别是, NodeObject是FPyObject里面创建的Py对象自定义模块, 没有Node方法
        # wrap_obj 是节点自己对应的Py对象, 有Node方法
        return wrap_obj

    def get_gdobj(self):
        return self._gdobj
    
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
def random_x3(x, y, z):
    return random_x()*x, random_x()*y, random_x()*z

def random_max(max):
    return random.random()*max

def random_range(start, stop, step=1):
    return random.rand_range(start, stop, step)

def random_num(min, max):
    return min + random.random() * (max - min)

# random.random() => [0, 1)
# => [min, max], 包括头尾
def random_int(min, max):
    return random.randint(min, max)

def random_select_item(item_list):
    if not item_list:
        return None
    index = random.randint(0, len(item_list) - 1)
    return item_list[index]

def clamp(v):
    if v < 0:
        return 0.0
    elif v > 1.0:
        return 1.0
    else:
        return v

def print_line(*args, **kwargs):
    if not args:
        return
    
    if len(args) == 1:
        a = args[0]
        gp.print_line(str(a))
    else:
        a = ' '.join([str(x) for x in args])
        gp.print_line(a)

# def get_py_object(node):
#     return gp.get_py_object(node)

# def get_parent(node):
#     return gp.get_parent(node)

def raycast_shape(camera, x,y,z):
    return gp.raycast_shape(camera, x,y,z)

def set_surface_color(node, index, r, g, b):
    gp.material_set_albedo_color(node, index, r, g, b)


#------------------------------------------------------------
# api
#------------------------------------------------------------

class OS:
    @classmethod
    def get_time(cls):
        return gp.get_time()

    @classmethod
    def get_delta_time(cls):
        return gp.get_delta_time()

    @classmethod
    def set_window_rect(cls, x, y,width,height):
        gp.set_window_rect(x,y,width,height,)

    @classmethod
    def get_window_size(cls):
        return gp.get_window_size()

    @classmethod
    def viewport_get_size(cls):
        return gp.viewport_get_size()

    @classmethod
    def get_scene_root(cls):
        obj = gp.get_scene_root()
        return GetWrappedObject(obj)

    @classmethod
    def instantiate(cls, path):
        gdobj = gp.instantiate(path)
        return GetWrappedObject(gdobj)

    @classmethod
    def is_editor_hint(cls):
        return gp.is_editor_hint()
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
        
        self.game_path = os.path.abspath('.')
        self.skip = len(self.game_path) + 1

    def print_stack(self):
        s = traceback.extract_stack(limit=4)
        for it in s[:-2]:
            print_line(f'\t{it.filename[self.skip:]}:{it.lineno}')

    def debug(self, *args, st=True):
        if self.enable_debug:
            print_line('[DEBUG]', *args)
            if st:
                self.print_stack()

    def error(self, *args, st=True):
        if self.enable_error:
            print_line('[ERROR]', *args)
            if st:
                self.print_stack()

    def print(self, msg):
        print_line(msg)

log_util = LogUtil()
log_util_debug = log_util.debug

#------------------------------------------------------------
# gdobj 封装
#------------------------------------------------------------

# 提供一些基础的服务
class FObject:
    def __init__(self):
        self._gdobj = None

    # def __del__(self):
    #     # TODO: 可以在这里关联，但似乎又过于频繁了，这样做的话
    #     log_util.debug(f'__del__ {self.get_gdobj().get_type_name()}')
    #     pass

    def get_gdobj(self):
        return self._gdobj

    def is_valid(self):
        return self.get_gdobj().is_valid()

    def connect(self, signal, callback):
        gp.connect(self.get_gdobj(), signal, callback)

    # 重载，可以用条件语句， if a: xxx
    def __bool__(self):
        return self.is_valid()

# 对应Node
class FNode(FObject):
    def destroy(self):
        gdobj = self._gdobj
        if gdobj:
            self._gdobj = None

            #print(f'destroy step1 refcnt={sys.getrefcount(gdobj)}')
            # 输出: 3
            # 在destroy里面看到的是4，是传参导致+1
            gp.destroy(gdobj) 
            #print(f'destroy step2 refcnt={sys.getrefcount(gdobj)}')
            # 输出: 2
            # 最后两个引用来自gdobj和getrefcount传参数
            
            # 实际到这里引用计数应该是1
            gdobj = None
            # 这里彻底释放，触发PyGDObj_dealloc
    
    def dup(self):
        dup_obj = gp.node_dup(self.get_gdobj())
        return GetWrappedObject(dup_obj)

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
        gp.set_scale(self.get_gdobj(), sx,sy,sz)

    def set_scale1(self, s):
        gp.set_scale(self.get_gdobj(), s, s, s)

    def get_position(self):
        return gd.get_position(self.get_gdobj())

    def look_at(self, x,y,z):
        gp.look_at(self.get_gdobj(), x,y,z)

    def set_visible(self, value):
        gp.node3d_set_visible(self.get_gdobj(), value)

    @classmethod
    def instantiate(cls, path):
        gdobj = gp.instantiate(path)
        return GetWrappedObject(gdobj)

class FCamera3D(FNode3D):
    def screen_to_world(self, x,y):
        return gp.screen_to_world(self.get_gdobj(), x, y)

    def world_to_screen(self, x,y,z):
        return gp.world_to_screen(self.get_gdobj(), x,y,z)

class FVisualInstance3D(FNode3D):
    pass

class FMeshInstance3D(FVisualInstance3D):
    def load_material(self, index, path):
        gp.mesh_instance3d_load_material(self.get_gdobj(), index, path)

    def set_albedo_color(self, r,g,b):
        gp.mesh_instance3d_set_albedo_color(self.get_gdobj(), r,g,b)

class FAnimationPlayer(FNode):
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
    def set_visible(self, value):
        self.visible = value
        gp.canvas_item_set_visible(self.get_gdobj(), value)

class FControl(FCanvasItem):
    def set_position(self, x,y):
        gp.control_set_position(self.get_gdobj(), x,y)

    def get_rect(self):
        return gp.control_get_rect(self.get_gdobj())

    def set_modulate(self,r,g,b):
        gp.canvas_item_set_modulate(self.get_gdobj(), r,g,b)

    def set_self_modulate(self, r,g,b):
        gp.canvas_item_set_self_modulate(self.get_gdobj(), r,g,b)

class FTabBar(FControl):
    def get_current_tab(self):
        return gp.tab_bar_get_current_tab(self.get_gdobj())

    def set_current_tab(self, index):
        gp.tab_bar_set_current_tab(self.get_gdobj(), index)

class FLabel(FControl):
    def __init__(self):
        super().__init__()
        self.text = None

    def set_text(self, text):
        if self.text != text:
            self.text = text
            gp.label_set_text(self.get_gdobj(), text)

    def set_minimum_size(self, w, h):
        gp.label_set_minimum_size(self.get_gdobj(), w, h)

class FRichTextLabel(FControl):
    def set_text(self, text):
        gp.rich_text_label_set_text(self.get_gdobj(), text)

class FBaseButton(FControl):
    def set_disabled(self, value):
        gp.base_button_set_disabled(self.get_gdobj(), value)

    def is_pressed(self):
        return gp.base_button_is_pressed(self.get_gdobj())

    def set_pressed(self, value):
        return gp.base_button_set_pressed(self.get_gdobj(), value)

class FButton(FBaseButton):
    def set_text(self, text):
        self.text = text
        gp.button_set_text(self.get_gdobj(), text)

    def get_text(self):
        # TODO: 目前直接把缓存的返回就好
        return self.text

class FCheckBox(FBaseButton):
    pass

class FImage(FControl):
    pass

class FPanel(FControl):
    pass

class FContainer(FControl):
    pass

class FHBoxContainer(FContainer):
    pass

class FVBoxContainer(FContainer):
    pass

class FSlider(FControl):
    def get_value(self):
        #return gp.slider_get_value(self.get_gdobj())
        return self.value

    def set_value(self, value):
        self.value = value
        gp.slider_set_value(self.get_gdobj(), value)

class FNode2D(FCanvasItem):
    def set_position(self, x,y):
        gp.node2d_set_position(self.get_gdobj(), x,y)
   
# 类型到wrap类的映射
# 这个wrap的好处就是，利用oop，使得操作的对象上面只有对应类型能用的方法
# 不在直接使用node对应的原始的pygd_obj，那个对象只用来当做一个弱引用使用
_FTypeList = [ None for i in range(64) ]

# 映射表,从godot的类型, 映射到 ftype
_TypeMap = {
    # core
    'FPyObject': FNode,
    'Node' : FNode,

    # 3d
    'Node3D' : FNode3D,
    'MeshInstance3D' : FMeshInstance3D,
    'CPUParticles3D' : FCPUParticles3D,
    'Camera3D' : FCamera3D,
    'Label3D' : FLabel3D,

    # animation
    'AnimationPlayer' : FAnimationPlayer,

    # 2d
    'Node2D' : FNode2D,

    # ui
    'CanvasItem' : FCanvasItem,
    'Label' : FLabel,
    'RichTextLabel' : FRichTextLabel,
    'Control' : FControl,
    'Button' : FButton,
    'TextureButton' : FBaseButton,
    'TabBar' : FTabBar,
    'CheckBox' : FCheckBox,
    'HSlider' : FSlider,
    'VSlider' : FSlider,
    'TextureRect' : FControl,
    'ColorRect' : FControl,
    'ScrollContainer' : FContainer,
    'HBoxContainer' : FHBoxContainer,
    'VBoxContainer' : FVBoxContainer,
    
}

# 传给c++,那边,当新增一个类型的时候,需要注册到py端,关键需要保持type_id一致
def _reg_type(type_name, type_id):
    f_type = _TypeMap.get(type_name, FNode)
    _FTypeList[type_id] = f_type
    log_util.debug(f'_reg_type: {type_name} -> {type_id} {f_type}')

# 对原始的gdobj,做一个包装的对象,包装好的对象里,有对应Node类型的方法
# gdobj的职责,是对c++端对象的一个弱引用
def GetWrappedObject(gdobj):
    if not gdobj:
        return None

    obj = gdobj.get_wrapped_object()
    if obj:
        return obj

    type_id = gdobj.get_type(_reg_type)
    f_type = _FTypeList[type_id]

    #type_name = gdobj.get_type_name()
    #log_util.debug(f'gdobj type_id={type_id} type={type_name}')

    obj = f_type()
    obj._gdobj = gdobj
    gdobj.set_wrapped_object(obj)

    return obj

# 大话降龙
# https://www.mm1316.com/maoxian/dahuajianglong

