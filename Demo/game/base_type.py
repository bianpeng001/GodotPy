#
# 2023年2月8日 bianpeng
#

from game.core import *

#
class Unit:
    def __init__(self):
        self.unit_id = None
        self.unit_name = ''
        self.unit_type = None

        # 所属君主
        self.owner_player_id = None

        # 生死存亡
        self.is_dead = False
        # 控制器
        self.controller = None

        # 场景里面的属性
        self.location = Vector3()
        self.rotation = Vector3()
        self.radius = 1
        
        # 模型
        self.model_node = None

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


#
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
class Controller(AIMachine):
    def __init__(self):
        super().__init__()
        
        self.unit = None

    @property
    def unit_id(self):
        return self.unit.unit_id

    @property
    def model_node(self):
        return self.unit.model_node

    def update(self):
        pass



#
class AIState:
    def enter(self, controller):
        pass

    def update(self, controller):
        pass

    def leave(self, controller):
        pass



