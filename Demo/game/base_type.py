#
# 2023年2月8日 bianpeng
#

from game.core import *

#
class Unit:
    def __init__(self):
        self.unit_id = None
        self.unit_name = ''

        # 所属君主
        self.owner_player_id = None

        # 战斗属性
        self.hp = self.maxhp = 100
        self.location = Vector3()
        self.rotation = Vector3()
        self.radius = 1
        self.dead = False

        # 模型
        self.model_node = None
        # 控制器
        self.controller = None

    def load_model(self):
        pass

    def set_location(self, x, y, z):
        self.location.set(x, y, z)

        if self.model_node:
            Node3D.set_position(self.model_node, x, y, z)

    def get_location(self):
        loc = self.location
        return loc.x, loc.y, loc.z

#
class Controller:
    def __init__(self):
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


        
