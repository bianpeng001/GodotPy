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
# 简单的数学库
#------------------------------------------------------------

#
# Plane
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
# Ray
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

        d = (x1*plane.n_x + y1*plane.n_y + z1*plane.n_z) / \
            (ray.n_x*plane.n_x + ray.n_y*plane.n_y + ray.n_z*plane.n_z)
        return d

    def get_point(self, d):
        return self.x0+self.n_x*d, self.y0+self.n_y*d, self.z0+self.n_z*d

#
#
#
class Vector4:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.w = 0

#
# 四元组
#
class Quaternion:
    def __init__(self):
        self.s = 0
        self.v = Vector3(1, 0, 0)

    def mul_vector(self, x,y,z):
        v = Vector4()
        # TODO:
        return v

#
# 向量
#
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
Vector3.left = Vector3.x_axis
Vector3.forward = Vector3(0, 0, -1)

#------------------------------------------------------------
# 模式相关的
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

# [-1, 1]
def random_x():
    return 2*(random.random()-0.5)

# 环状区域内随机
def random_xx(mid):
    v = random_x()
    return v + min if v >= 0 else v - min

# [(-1,-1,-1), (1,1,1)]
def random_x3(x, y, z):
    return random_x()*x, random_x()*y, random_x()*z

def random_max(max=1):
    return random.random()*max

def random_range(start, stop, step=1):
    return random.rand_range(start, stop, step)

def random_num(min, max):
    return min + random.random() * (max - min)

def random_100():
    return random_int(0, 100)

# random.random() => [0, 1)
def random_1():
    return random.random()

# => [min, max], 包括头尾
def random_int(min, max):
    return random.randint(min, max)

#
def random_select_item(item_list):
    if not item_list or len(item_list) == 0:
        return None, -1
    index = random.randint(0, len(item_list)-1)
    return item_list[index], index

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

def hsv_to_rgb(h,s,v):
    if s == 0:
        return (v,v,v)
    f, i = math.modf(h*6)
    p,q,t = v*(1-s), v*(1-s*f), v*(1-s*(1-f))
    i = round(i) % 6
    if i == 0:
        return (v,t,p)
    elif i == 1:
        return (q,v,p)
    elif i == 2:
        return (p,v,t)
    elif i == 3:
        return (p,q,v)
    elif i == 4:
        return (t,p,v)
    elif i == 5:
        return (v,p,q)
    
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
    def set_window_rect(cls, x,y,width,height):
        gp.set_window_rect(x,y,width,height)

    @classmethod
    def get_window_size(cls):
        return gp.get_window_size()

    @classmethod
    def set_window_title(cls, title):
        return gp.window_set_title(title)
        
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

    @classmethod
    def set_custom_mouse_cursor(cls, cursor,shape,x,y):
        gp.set_custom_mouse_cursor(cursor,shape,x,y)

# ResCapsule 对应的方法
class ResCapsule:
    def __init__(self, res):
        self.res = res
        
    @classmethod
    def load_resource(cls, path):
        return ResCapsule(gp.load_resource(path))
    
    def duplicate(self):
        return ResCapsule(gp.resource_duplicate(self.res))
    
    def set_shader_color(self, name, r,g,b,a):
        gp.material_set_color(self.res, name, r,g,b,a)

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
log_debug = log_util.debug

#------------------------------------------------------------
# gdobj 封装
#------------------------------------------------------------

# 提供一些基础的服务
class FObject:
    def __init__(self):
        self._gdobj = None

    # 当在python端,对于这个handle的引用归零, 则可以清理掉c那边缓存的python对象

    # def __del__(self):
    #     #可以在这里关联，但似乎又过于频繁了，这样做的话
    #     log_util.debug(f'__del__ {self.get_gdobj().get_type_name()}')
    #     pass

    def get_gdobj(self):
        return self._gdobj

    def is_valid(self):
        return self.get_gdobj().is_valid()

    def connect(self, signal, callback):
        gp.node_connect(self.get_gdobj(), signal, callback)
        
    def clear_connection(self, signal):
        gp.node_clear_connection(self.get_gdobj(), signal)

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

    def reparent(self, new_parent_obj) -> None:
        gp.reparent(self.get_gdobj(), new_parent_obj.get_gdobj())

    def get_parent(self):
        parent_gdobj = gp.get_parent(self.get_gdobj())
        return GetWrappedObject(parent_gdobj)

    def set_process(self, process=False,input=False,physics=False) -> None:
        gp.set_process(self.get_gdobj(), process)
        gp.set_process_input(self.get_gdobj(), input)
        gp.set_physics_process(self.get_gdobj(), physics)
    
    def find_control(self, x:float,y:float):
        gdobj = gp.find_control(self.get_gdobj(), x, y)
        return GetWrappedObject(gdobj)

    def set_last(self):
        gp.node_set_last(self.get_gdobj())
        
    def set_name(self, name: str) -> None:
        gp.node_set_name(self.get_gdobj(), name)
        
    def get_name(self):
        return gp.node_get_name(self.get_gdobj())

class FNode3D(FNode):
    def set_position(self, x:float, y:float, z:float) -> None:
        gp.set_position(self.get_gdobj(), x,y,z)

    def set_rotation(self, x:float, y:float, z:float) -> None:
        gp.set_rotation(self.get_gdobj(), x,y,z)

    def set_scale(self, sx:float,sy:float,sz:float) -> None:
        gp.set_scale(self.get_gdobj(), sx,sy,sz)

    def set_scale1(self, s:float) -> None:
        gp.set_scale(self.get_gdobj(), s, s, s)

    def get_position(self):
        return gd.get_position(self.get_gdobj())

    def look_at(self, x:float, y:float, z:float) -> None:
        gp.look_at(self.get_gdobj(), x,y,z)

    def set_visible(self, value: bool) -> None:
        gp.node3d_set_visible(self.get_gdobj(), value)

    def get_forward(self):
        return gp.get_forward(self.get_gdobj())

    # @classmethod
    # def instantiate(cls, path):
    #     gdobj = gp.instantiate(path)
    #     return GetWrappedObject(gdobj)

class FCamera3D(FNode3D):
    def screen_to_world(self, x:float, y:float) -> None:
        return gp.screen_to_world(self.get_gdobj(), x, y)

    def world_to_screen(self, x:float, y:float, z:float) -> None:
        return gp.world_to_screen(self.get_gdobj(), x,y,z)

class FVisualInstance3D(FNode3D):
    pass

class FMeshInstance3D(FVisualInstance3D):
    def load_material(self, index: int, path: str):
        gp.mesh_instance3d_load_material(self.get_gdobj(), index, path)

    def set_albedo_color(self, r,g,b):
        gp.mesh_instance3d_set_albedo_color(self.get_gdobj(), r,g,b)

    def set_surface_material(self, surface, mat):
        gp.mesh_instance3d_set_surface_material(self.get_gdobj(), surface, mat)

class FAnimationPlayer(FNode):
    def play(self, anim_name: str) -> None:
        gp.animation_player_play(self.get_gdobj(), anim_name)

    def stop(self):
        pass

    def pause(self):
        pass

    def set_speed_scale(self, speed:float) -> None:
        gp.animation_player_set_speed_scale(self.get_gdobj(), speed)

class FLabel3D(FNode3D):
    def set_text(self, text: str) -> None:
        gp.label3d_set_text(self.get_gdobj(), text)

class FCPUParticles3D(FVisualInstance3D):
    def set_emitting(self, value: bool) -> None:
        gp.cpu_particle_set_emitting(self.get_gdobj(), value)

class FCanvasItem(FNode):
    def set_visible(self, value: bool) -> None:
        self.visible = value
        gp.canvas_item_set_visible(self.get_gdobj(), value)
        
    def queue_redraw(self) -> None:
        gp.canvas_item_queue_redraw(self.get_gdobj())
    
    def draw_line(self, x1,y1,x2,y2, color, width):
        pass
    
    def draw_polyline(self, points, r:float, g:float, b:float, width:float) -> None:
        gp.canvas_item_draw_polyline(self.get_gdobj(), points, r,g,b, width)

class FControl(FCanvasItem):
    def set_position(self, x:float,y:float) -> None:
        gp.control_set_position(self.get_gdobj(), x,y)

    def set_size(self, w:float,h:float) -> None:
        gp.control_set_size(self.get_gdobj(), w,h)

    def get_rect(self):
        return gp.control_get_rect(self.get_gdobj())

    def set_modulate(self, r:float, g:float, b:float) -> None:
        gp.canvas_item_set_modulate(self.get_gdobj(), r,g,b)

    def set_self_modulate(self, r:float, g:float, b:float) -> None:
        gp.canvas_item_set_self_modulate(self.get_gdobj(), r,g,b)
        
    def set_tooltip(self, text: str) -> None:
        gp.control_set_tooltip(self.get_gdobj(), text)

class FTabBar(FControl):
    def get_current_tab(self):
        return gp.tab_bar_get_current_tab(self.get_gdobj())

    def set_current_tab(self, index:int) -> None:
        gp.tab_bar_set_current_tab(self.get_gdobj(), index)

class FLabel(FControl):
    def __init__(self):
        super().__init__()
        self.text = None

    def set_text(self, text):
        if self.text != text:
            self.text = text
            gp.label_set_text(self.get_gdobj(), text)
            
    def set_color(self, r:float, g:float, b:float, a:float) -> None:
        gp.label_set_color(self.get_gdobj(), r,g,b,a)

    def set_minimum_size(self, w:float, h:float) -> None:
        gp.label_set_minimum_size(self.get_gdobj(), w, h)

class FRichTextLabel(FControl):
    def set_text(self, text: str) -> None:
        gp.rich_text_label_set_text(self.get_gdobj(), text)

#
# button
#
class FBaseButton(FControl):
    def set_disabled(self, value: bool) -> None:
        gp.base_button_set_disabled(self.get_gdobj(), value)

    def is_pressed(self) -> bool:
        return gp.base_button_is_pressed(self.get_gdobj())

    def set_pressed(self, value: bool) -> None:
        gp.base_button_set_pressed(self.get_gdobj(), value)

    def set_text(self, text: str) -> None:
        self.text = text
        gp.button_set_text(self.get_gdobj(), text)

    def get_text(self):
        # TODO: 目前直接把缓存的返回就好
        return self.text

class FButton(FBaseButton):
    pass

class FTextureButton(FBaseButton):
    def set_normal_tex(self, res):
        gp.texture_button_set_texture(self.get_gdobj(), 0, res)
        
class FCheckBox(FBaseButton):
    pass

class FTextEdit(FControl):
    def get_text(self) -> str:
        return gp.text_edit_get_text(self.get_gdobj())

    def set_text(self, s: str) -> None:
        gp.text_edit_set_text(self.get_gdobj(), s)

class FPanel(FControl):
    pass

class FItemList(FControl):
    def set_item_list(self, item_list):
        pass

class FPanel(FControl):
    pass

class FTextureRect(FControl):
    def load_tex(self, path: str) -> None:
        gp.texture_rect_load_texture(self.get_gdobj(), path)

    def set_tex(self, tex) -> None:
        gp.texture_rect_set_texture(self.get_gdobj(), tex)

class FColorRect(FControl):
    pass

#
# 滑动条
#
class FRange(FControl):
    def get_value(self):
        return gp.range_get_value(self.get_gdobj())

    def set_value(self, value) -> None:
        gp.range_set_value(self.get_gdobj(), value)

class FScrollBar(FRange):
    pass

class FSlider(FRange):
    pass

class FProgressBar(FRange):
    pass

#
# 容器
#
class FContainer(FControl):
    pass

class FScrollContainer(FContainer):
    def get_hscroll_bar(self):
        hbar = gp.scroll_contailer_get_hscroll(self.get_gdobj())
        return GetWrappedObject(hbar)

    def get_vscroll_bar(self):
        vbar = gp.scroll_contailer_get_vscroll(self.get_gdobj())
        return GetWrappedObject(vbar)

class FHBoxContainer(FContainer):
    pass

class FVBoxContainer(FContainer):
    pass

class FNode2D(FCanvasItem):
    def set_position(self, x:float,y:float) -> None:
        gp.node2d_set_position(self.get_gdobj(), x,y)

class FSubViewport(FNode):
    def set_update_mode(self, mode):
        gp.f_viewport_set_update_mode(self.get_gdobj(), mode)

# 多边形工具
class FSurfaceTool:
    def __init__(self):
        self.st = gp.surface_tool_new()

    def set_uv(self, x:float,y:float) -> None:
        gp.surface_tool_set_uv(self.st, x,y)
        
    def set_uv2(self, x:float,y:float) -> None:
        gp.surface_tool_set_uv2(self.st, x,y)

    def set_color(self, r:float,g:float,b:float,a:float) -> None:
        gp.surface_tool_set_color(self.st, r,g,b,a)
        
    def set_custom(self, channel_index:int, r:float,g:float,b:float,a:float) -> None:
        gp.surface_tool_set_custom(self.st, r,g,b,a)

    def set_normal(self, x:float,y:float,z:float) -> None:
        gp.surface_tool_set_normal(self.st, x,y,z)
    
    def add_vertex(self, x:float,y:float,z:float) -> None:
        gp.surface_tool_add_vertex(self.st, x,y,z)

    def add_index(self, i:int) -> None:
        gp.surface_tool_add_index(self.st, i)

    def add_triangle(self, a:int, b:int ,c:int) -> None:
        self.add_index(a)
        self.add_index(b)
        self.add_index(c)

    # mi -> FMeshInstance3D
    def commit(self, mi):
        gp.surface_tool_commit(self.st, mi.get_gdobj())
        

# 后面这个得这么用      
# class FResource(FObject):
#     def dup(self):
#         return GetWrappedObject(gp.resource_duplicate(self.get_gdobj()))


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
    'Control' : FControl,
    'TextureRect' : FTextureRect,
    'ColorRect' : FColorRect,
    'TextureButton' : FTextureButton,
    'Button' : FButton,
    'TabBar' : FTabBar,
    'CheckBox' : FCheckBox,
    'HSlider' : FSlider,
    'VSlider' : FSlider,
    'HScrollBar' : FScrollBar,
    'VScrollBar' : FScrollBar,
    'Label' : FLabel,
    'RichTextLabel' : FRichTextLabel,
    'TextEdit' : FTextEdit,
    'Panel' : FPanel,

    'ScrollContainer' : FScrollContainer,
    'HBoxContainer' : FHBoxContainer,
    'VBoxContainer' : FVBoxContainer,
    'GridContainer' : FContainer,

    'ItemList' : FItemList,
    'SubViewport' : FSubViewport,
}

# 传给c++,那边,当新增一个类型的时候,需要注册到py端,关键需要保持type_id一致
def _reg_type(type_name: str, type_id: int)  -> None:
    f_type = _TypeMap.get(type_name, FNode)
    _FTypeList[type_id] = f_type
    log_debug(f'_reg_type: {type_name} -> {type_id} {f_type}')

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

# 标记即将过时的内容
def obstacle(fun):
    def _fun(*args, **kw_args):
        log_debug('obstacle func', fun)
        return fun(*args, **kw_args)
    return _fun

# 记一下时间
_cache_time = 0
def set_cache_time(sec_time):
    global _cache_time
    _cache_time = sec_time

def get_cache_time():
    return _cache_time



        