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
        self.dead = False
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
        self.dead = True
#
class Controller:
    def __init__(self):
        self.unit = None

        self.ai_state = None
        self.ai_bb = None

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



