#
# 2023年2月8日 bianpeng
#

import io
import math

from game.core import log_debug, Vector3

#
# AI状态机
#
class AIMachine:
    def __init__(self):
        # 当前活动状态
        self.ai_state = None
        # 状态集合
        self.state_dict = { }
        # 数据共享
        self.blackboard = None
        
    def get_blackboard(self):
        return self.blackboard

    def _enter_state(self, new_state):
        if self.ai_state:
            self.ai_state.leave(self)
            self.ai_state = None

        self.ai_state = new_state

        if self.ai_state:
            self.ai_state.enter(self)

    def goto_state(self, name):
        state = self.state_dict.get(name, None)
        if state:
            self._enter_state(state)

    def add_state(self, name, state):
        self.state_dict[name] = state
        

#
# AI状态之间交流数据的黑板
#
class AIBlackboard:
    def __init__(self):
        pass

#
# AI状态机的单独状态, 生命周期
#
class AIState:
    def __init__(self):
        pass

    def enter(self, controller):
        pass

    def update(self, controller):
        pass

    def leave(self, controller):
        pass

# sequence
class AISequence(AIState):
    def __init__(self):
        pass

# selector
class AISelector(AIState):
    def __init__(self):
        pass

#
# 单位类型
#

# 城池
UT_CITY = 1
# 军队
UT_TROOP = 2


# 城市的级别
# 村
CT_CUN = 1
# 县
CT_XIAN = 2
# 郡
CT_JUN = 3
# 州
CT_ZHOU = 4

# 势力之间的友好度
YHD_Labels = ['险恶','敌对','普通','友好','盟友']

#
# 场景中的单位
#
class Unit:
    def __init__(self):
        # 控制器
        self._controller = None

        # 身份
        self.unit_id = 0
        self.unit_name = ''
        # 类型
        self.unit_type = None
        # 所属君主
        self.owner_player_id = None

        # 伤害，防御
        self.damage = 10
        # 暴击率10%
        self.critical_strike = 10
        # 防御
        self.defense = 10
        # 等级
        self.level = 1
        # 护甲(城防)
        self.armor_amount = RangeValue(100, 100)
        # 血量(主要是指军队数量)
        self.army_amount = RangeValue(0, 1000)
        self.army_moral = RangeValue(100, 100)

        # 生死存亡
        self.is_dead = False
        
        # 场景里面的属性
        self.unit_position = Vector3()
        self.unit_rotation = Vector3()
        self.radius = 1
        # 质量, 用于一些物理运算
        self.mass = 1
        self.speed = 1

        # 模型
        self.model_node = None

    # 创建之后，初始化，这里身份信息已经确定了
    def init(self):
        pass

    def load_model(self):
        pass

    def get_position(self):
        return self.unit_position.get_xyz()

    def get_xz(self):
        return self.unit_position.get_xz()

    def get_x(self):
        return self.unit_position.x

    def get_z(self):
        return self.unit_position.z

    def set_position(self, x,y,z):
        self.unit_position.set(x,y,z)
        self.get_controller().apply_position()
        
    def get_rotation(self):
        return self.unit_rotation.get_xyz()
    
    def set_rotation(self, x,y,z):
        self.unit_rotation.set(x,y,z)

    # 最后清除的时候，回调
    def on_dead(self):
        if self.model_node:
            self.model_node.destroy()
            self.model_node = None

    def set_death(self):
        self.is_dead = True

    def get_controller(self):
        return self._controller

#
# 角色单位的控制器
#
class Controller:
    def __init__(self, unit):
        self._unit = unit
        
        self.hud_comp = HUDComponent()
        self.hud_comp.setup(self)
        
    def get_hud_comp(self):
        return self.hud_comp

    @property
    def unit_id(self):
        return self._unit.unit_id

    def get_unit(self):
        return self._unit
    
    def get_model_node(self):
        return self.get_unit().model_node

    # 首次update之前
    def start(self):
        pass

    # 每帧调用
    def update(self):
        pass

    def apply_position(self):
        node = self.get_model_node()
        if node:
            node.set_position(*self.get_unit().get_position())
            
    def apply_transform(self):
        node = self.get_model_node()
        if node:
            node.set_position(*self.get_unit().get_position())
            node.set_rotation(*self.get_unit().get_rotation())

    def apply_rotation(self):
        node = self.get_model_node()
        if node:
            node.set_rotation(*self.get_unit().get_rotation())
            
#
# 基本组件, 根据功能管理数据和代码, 避免Controller膨胀
#
class Component:
    def __init__(self):
        self._controller = None
    
    def get_controller(self):
        return self._controller
    
    # 用方法初始化
    def setup(self, controller):
        self._controller = controller
        
#
# 控制hud
#
class HUDComponent(Component):
    def __init__(self):
        super().__init__()
        
        # 用于强制重建hud
        self._valid = False

    def is_valid(self):
        return self._valid
    
    def set_valid(self, value):
        self._valid = value
    
    # 用来刷新UI
    def refresh_hud(self, hud_item):
        pass

#
# UI 面板控制器
#
class UIController:
    def __init__(self):
        self._show = True
        self.ui_obj = None
        self.prev_panel = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

    def show(self):
        self._show = True
        self.ui_obj.set_visible(True)
        self.on_show(True)

    def is_show(self):
        return self._show

    def hide(self):
        self._show = False
        self.ui_obj.set_visible(False)
        self.on_show(False)
        
        if self.prev_panel:
            self.prev_panel.show()
            self.prev_panel = None
            
    def set_prev_panel(self, prev_panel):
        self.prev_panel = prev_panel
        prev_panel.defer_close()
        
    def on_show(self, show):
        pass

#
# 本方法在UI可见时才生效, 用于事件响应
#
def when_visible(fun):
    def _fun(self, *args, **kwargs):
        if self.is_show():
            return fun(self, *args, **kwargs)
        else:
            log_debug('ignore func when not visible', self)
    
    return _fun

#
# 区间
#
class RangeValue:
    def __init__(self, value, max_value=None, min_value=0):
        self.value = value

        if max_value == None:
            self.max_value = value
        else:
            self.max_value = max_value

        self.min_value = min_value

    def grow(self, growth_rate, delta_time):
        delta = growth_rate * delta_time
        self.add(delta)

    def add(self, delta):
        value = self.value + delta
        if value > self.max_value:
            self.value = self.max_value
        elif value < self.min_value:
            self.value = self.min_value
        else:
            self.value = value

    def get_value(self):
        return round(self.value)

    def get_round(self):
        return round(self.value)

    def get_floor(self):
        return math.floor(self.value)
        
# 一个螺旋形的遍历
# 812
# 703
# 654
def narudo_range(n):
    steps = ((0, 1),(1, 0),(0, -1),(-1, 0))
    step_index = 0

    def next_step():
        nonlocal steps,step_index
        
        dx,dy = steps[step_index]
        step_index = (step_index+1) % 4
        return dx,dy

    def one_line():
        nonlocal x,y

        dx,dy = next_step()
        j = 0
        while j < i:
            x+=dx
            y+=dy
            yield x,y
            j += 1

    x,y = 0,0
    i = 1
    while i < n:
        for a in one_line():
            yield a
        for a in one_line():
            yield a
        i += 1

#
# 漩涡
#
def narudo_range2(start, n):
    steps = ((0, 1),(1, 0),(0, -1),(-1, 0))
    step_index = 0

    def next_step():
        nonlocal steps, step_index
        
        dx,dy = steps[step_index]
        step_index = (step_index+1) % 4
        return dx,dy

    def one_edge():
        nonlocal x,y

        dx,dy = next_step()
        j = 0
        while j < i:
            x+=dx
            y+=dy
            yield x,y
            j += 1

    x,y = -start,-start
    i = start*2
    while i < n:
        for a in one_edge():
            yield a
        for a in one_edge():
            yield a
        i += 1

#
# 军队里面武将占位信息
# 武将ID, 位置
#
class HeroSlot:
    def __init__(self):
        self.hero_id = 0
        self.pos_index = 0

#
# 
#
class TwoFoldList:
    def __init__(self):
        self.list = []
        self.back_list = []

    def append(self, item):
        self.list.append(item)

    def update(self):
        self.swap()
        if self.back_list:
            try:
                for item in self.back_list:
                    self.do_update(item)
            finally:
                self.back_list.clear()

    def update_cb(self, cb):
        self.swap()
        if self.back_list:
            try:
                for item in self.back_list:
                    cb(item)
            finally:
                self.back_list.clear()

    def swap(self):
        tmp = self.list
        self.list = self.back_list
        self.back_list = tmp

    def do_update(self, item):
        pass


    def get_list(self):
        return self.list

#
#
#
class StringBuilder(io.StringIO):
    def writeln(self, text):
        self.write(text)
        self.write('\n')

