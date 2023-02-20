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
        self.ai_bb = None

    def ai_enter_state(self, new_state):
        if self.ai_state:
            self.ai_state.leave(self)
            self.ai_state = None

        self.ai_state = new_state

        if self.ai_state:
            self.ai_state.enter(self)

#
class AIBlackboard:
    pass

# AI状态机的单独状态, 生命周期
class AIState:
    def enter(self, controller):
        pass

    def update(self, controller):
        pass

    def leave(self, controller):
        pass

#------------------------------------------------------------
#
#------------------------------------------------------------

# 单位类型
UT_CITY = 1
UT_TROOP = 2

# 场景中的单位
class Unit:
    def __init__(self):
        self.unit_type = None

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
        # 控制器
        self._controller = None

        # 场景里面的属性
        self.location = Vector3()
        self.rotation = Vector3()
        self.radius = 1
        
        # 模型
        self.model_node = None

    # 创建之后，初始化，这里身份信息已经确定了
    def init(self):
        pass

    def load_model(self):
        pass

    def set_location(self, x, y, z):
        self.location.set(x, y, z)

        if self.model_node:
            Node3D.set_position(self.model_node, x, y, z)

    def get_location(self):
        loc = self.location
        return loc.x, loc.y, loc.z

    # 最后清除的时候，回调
    def on_dead(self):
        if self.model_node:
            Node.destroy(self.model_node)
            self.model_node = None

    def set_dead(self):
        self.is_dead = True

    def get_controller(self):
        return self._controller


# 单位的控制器
class Controller(AIMachine):
    def __init__(self):
        super().__init__()
        
        self._unit = None

    @property
    def unit_id(self):
        return self._unit.unit_id

    def get_unit(self):
        return self._unit

    @property
    def model_node(self):
        return self.get_unit().model_node

    # 首次update之前
    def start(self):
        pass

    def update(self):
        pass

    def get_blackboard(self):
        return None

