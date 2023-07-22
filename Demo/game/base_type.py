#
# 2023年2月8日 bianpeng
#

import io
import math
import traceback

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

    def enter(self, machine):
        pass

    def update(self, machine):
        pass

    def leave(self, machine):
        pass

#
# sequence
#
class AISequence(AIState):
    def __init__(self):
        pass

#
# selector
#
class AISelector(AIState):
    def __init__(self):
        pass

#
# 空闲
#
class AIState_Idle(AIState):
    def update(self, machine):
        pass

#
# 背包
#
class Package:
    def __init__(self, size):
        self.item_list = [ PackageItem(i) for i in range(size) ]
#
# 背包物品格
#
class PackageItem:
    def __init__(self, index):
        self._index = 0
        # 物品数量
        self.item_count = 0
        # 物品的id, 时机上是一个config_id
        self.item_id = 0

    @property
    def index(self):
        return self._index

#
# 单位类型
#

# 城池, 现在含义多了, 能驻军的地方豆角city, 实际可能是城池,山寨,关隘
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

# 军队的兵种类型, 子类型
# 兵种的类型, 消耗的资源, 也不一样

# 徒手
AT_NONE = 0
# 盾刀
AT_SHIELD = 1
# 长枪
AT_SPARE = 2
# 弓兵
AT_BOW = 3
# 骑兵
AT_RIDER = 4
# 器械(攻城车, 炮车)
AT_MECH = 5
# 船
AT_SHIP = 6
# 运输队
AT_TRANS = 7
# 火器
AT_SHOOT = 8
AT_GUN = 8


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
        self.critical_rate = 10
        # 防御
        self.defense = 10
        # 等级
        self.level = 1

        # 护甲(城防)
        self.armor_amount = RangeValue(100, 100)
        # 血量(主要是指军队数量)
        self.army_amount = RangeValue(0, 1000)
        # 士气
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

    def get_xz_sqrdis_to(self, unit):
        dx = unit.get_x() - self.get_x()
        dz = unit.get_z() - self.get_z()
        return dx*dx+dz*dz

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

BRAIN_TICK_TIME = 0.1
SIGHT_TICK_TIME = 0.1

#
# Brain 用来驱动AI
#
class BrainComponent(Component, AIMachine):
    def __init__(self):
        super().__init__()
        AIMachine.__init__(self)
        
        self.tick_time = 0
    
    def update(self, delta_time):
        self.tick_time += delta_time
        if self.tick_time > BRAIN_TICK_TIME:
            self.on_tick(self.tick_time)
            self.tick_time = 0
            
    def on_tick(self, tick_time):
        if self.ai_state:
            self.ai_state.update(self)
        
    def get_unit(self):
        return get_controller().get_unit()

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

    def on_show(self, show):
        pass

    def hide(self):
        self._show = False
        self.ui_obj.set_visible(False)
        self.on_show(False)
        
        if self.prev_panel:
            self.prev_panel.show()
            self.prev_panel = None
    
    # 这个prev机制的问题, 在于当成环的时候就gg了
    def set_prev_panel(self, prev_panel):
        self.prev_panel = prev_panel
        prev_panel.defer_close()

#
# 本方法在UI可见时才生效, 用于事件响应
#
def when_visible(fun):
    def _fun(self, *args, **kwargs):
        if self.is_show():
            return fun(self, *args, **kwargs)
        else:
            log_debug('panel hide', self)
            pass
    
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

    def get_hero(self):
        pass

#
# 双缓冲列表
#
class TwoFoldList:
    def __init__(self):
        self.list = []
        self.back_list = []

    def append(self, item):
        self.list.append(item)

    def update_items(self, cb=None):
        cb = cb or self.do_update
        self.swap()
        if self.back_list:
            for item in self.back_list:
                try:
                    cb(item)
                except Exception as err:
                    traceback.print_exception(err)
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
# 字符串构造
#
class StringBuilder(io.StringIO):
    def writeln(self, text):
        self.write(text)
        self.write('\n')

