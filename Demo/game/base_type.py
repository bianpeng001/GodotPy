#
# 2023年2月8日 bianpeng
#

from game.core import *

#------------------------------------------------------------
#
#------------------------------------------------------------

# AI状态机
class AIMachine:
    def __init__(self):
        # ai state machine
        self.ai_state = None
        # blackboard
        self.blackboard = None

    def enter_state(self, new_state):
        if self.ai_state:
            self.ai_state.leave(self)
            self.ai_state = None

        self.ai_state = new_state

        if self.ai_state:
            self.ai_state.enter(self)

    def get_blackboard(self):
        return self.blackboard

# AI状态之间交流数据的黑板
class AIBlackboard:
    def __init__(self):
        self.value_dict = {}

    def get_value(self, key):
        return self.value_dict.get(key, None)

    def set_value(self, key, value):
        self.value_dict[key] = value

# AI状态机的单独状态, 生命周期
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

#------------------------------------------------------------
#
#------------------------------------------------------------

# 单位类型
# 城池
UT_CITY = 1
# 军队
UT_TROOP = 2

# 场景中的单位
class Unit:
    def __init__(self):
        self.unit_type = None

        # 控制器
        self._controller = None

        # 身份
        self.unit_id = 0
        self.unit_name = ''
        # 所属君主
        self.owner_player_id = None

        # 伤害，防御
        self.damage = 0
        self.defense = 0
        self.maxhp = self.hp = 100

        # 生死存亡
        self.is_dead = False
        
        # 场景里面的属性
        self.unit_position = Vector3()
        self.rotation = Vector3()
        self.radius = 1
        
        # 模型
        self.model_node = None

    # 创建之后，初始化，这里身份信息已经确定了
    def init(self):
        pass

    def load_model(self):
        pass

    def get_position(self):
        pos = self.unit_position
        return pos.x,pos.y,pos.z

    def get_xz(self):
        pos = self.unit_position
        return pos.x,pos.z

    def get_x(self):
        return self.unit_position.x

    def get_z(self):
        return self.unit_position.z

    def set_position(self, x,y,z):
        self.unit_position.set(x,y,z)
        self.get_controller().apply_position()

    # 最后清除的时候，回调
    def on_dead(self):
        if self.model_node:
            self.model_node.destroy()
            self.model_node = None

    def set_dead(self):
        self.is_dead = True

    def get_controller(self):
        return self._controller

# 角色单位的控制器
class Controller(AIMachine):
    def __init__(self):
        AIMachine.__init__(self)
        
        self._unit = None

    @property
    def unit_id(self):
        return self._unit.unit_id

    def get_unit(self):
        return self._unit
    
    def get_model_node(self):
        return self.get_unit().model_node

    @property
    def model_node(self):
        return self.get_model_node()

    # 首次update之前
    def start(self):
        pass

    def update(self):
        pass

    def apply_position(self):
        node = self.get_model_node()
        if node:
            node.set_position(*self.get_unit().get_position())

# UI 面板控制器
class UIController:
    def __self__(self):
        self.is_visible = True
        self.ui_obj = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

    def show(self):
        self.is_visible = True
        self.ui_obj.set_visible(True)

    def is_show(self):
        return self.is_visible

    def hide(self):
        self.is_visible = False
        self.ui_obj.set_visible(False)

#
# 本方法在UI可见时才生效, 用于事件响应
#
def RequireShow(func):
    def _func(self, *args,**kwargs):
        if self.is_show():
            return func(self, *args, **kwargs)
    
    return _func

# 有上限的值
class LimitValue:
    def __init__(self, value, value_limit):
        self.value = value
        self.value_limit = value_limit

    def grow(self, growth_rate, delta_time):
        delta = growth_rate * delta_time
        self.add(delta)

    def add(self, delta):
        self.value += delta
        if self.value >= self.value_limit:
            self.value = self.value_limit

    def get_value(self):
        return round(self.value)
        
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

def narudo_range2(start, n):
    steps = ((0, 1),(1, 0),(0, -1),(-1, 0))
    step_index = 0

    def next_step():
        nonlocal steps, step_index
        
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

    x,y = -start,-start
    i = start*2
    while i < n:
        for a in one_line():
            yield a
        for a in one_line():
            yield a
        i += 1



#
# 军队里面武将位置, 武将ID, 位置
#
class HeroSlot:
    def __init__(self):
        self.hero_id = 0
        self.pos_index = 0



