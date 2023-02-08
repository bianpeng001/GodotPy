#
# 2023年2月3日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.config_mgr import new_city_name

from game.troop_controller import TroopController
from game.city_controller import CityController

##############################################################
# Units
##############################################################
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

# 部队
class TroopUnit(Unit):
    def __init__(self):
        super().__init__()
        self.controller = TroopController()
        self.controller.unit = self

        # 所属城
        self.owner_city_id = None
        self.radius = 2

        self.velocity = Vector3()
        self.velocity.set(1, 0, 0)

        self.army_amount = 0

    def load_model(self):
        self.unit_name = f'部队_{self.unit_id}'

        self.model_node = instantiate('res://models/Troop01.tscn')
        Node3D.set_position(self.model_node,*self.get_location())

    def set_army_amount(self, value):
        self.army_amount = value

# 城池
class CityUnit(Unit):
    def __init__(self):
        super().__init__()
        self.controller = CityController()
        self.controller.unit = self

        self.radius = 3
        self.unit_name = new_city_name()
        
        # 资源
        self.army_amount = 800
        self.rice_amount = 0
        self.iron_amount = 0
        self.stone_amount = 0
        self.wood_amount = 0

        self.growth_rate = 20

    def load_model(self):
        self.model_node = instantiate('res://models/City01.tscn')

        x,y,z = self.get_location()
        Node3D.set_position(self.model_node, x,y,z)
        
        self.controller.set_title(self.unit_name)

##############################################################
# UnitMgr
##############################################################
class UnitMgr:
    def __init__(self):
        self._unit_id_seed = 1000
        self.unit_dict = {}
        self.update_list = []
        self.dead_list = []

    def get_next_unit_id(self):
        self._unit_id_seed += 1
        return self._unit_id_seed

    def update(self, delta_time):
        i = 0
        count = len(self.update_list)

        while i < count:
            unit = self.update_list[i]
            unit.controller.update()
            if unit.dead:
                count -= 1
                self.update_list[i] = self.update_list[count]
                self.update_list.pop()

                self.dead_list.append(unit)
            else:
                i += 1

        for unit in self.dead_list:
            self.unit_dict.pop(unit.unit_id)
            pass

    def create_unit(self, unit_class_):
        unit = unit_class_()

        unit.unit_id = self.get_next_unit_id()
        self.unit_dict[unit.unit_id] = unit
        self.update_list.append(unit)

        unit.load_model()

        return unit

    def get_unit(self, unit_id):
        return self.unit_dict.get(unit_id, None)

    def create_city(self):
        return self.create_unit(CityUnit)

    def create_troop(self):
        return self.create_unit(TroopUnit)



