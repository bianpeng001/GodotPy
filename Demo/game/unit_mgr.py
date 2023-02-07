#
# 2023年2月3日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.config_mgr import new_city_name

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

    def update(self):
        pass

    def set_location(self, x, y, z):
        self.location.set(x, y, z)

        if self.model_node:
            set_position(self.model_node, x, y, z)

    def get_location(self):
        loc = self.location
        return loc.x, loc.y, loc.z

# 部队
class TroopUnit(Unit):
    def __init__(self):
        super().__init__()

        # 所属城
        self.owner_city_id = None
        self.radius = 2

    def load_model(self):
        self.unit_name = f'部队_{self.unit_id}'

        self.model_node = instantiate('res://models/Troop01.tscn')
        self.controller = get_py_object(find_node(self.model_node, 'Controller'))

        loc = self.location
        set_position(self.model_node, loc.x,loc.y,loc.z)

        print_line(f'Controller: {self.controller}')

# 城池
class CityUnit(Unit):
    def __init__(self):
        super().__init__()

        self.radius = 3
        self.unit_name = new_city_name()

    def load_model(self):
        self.model_node = instantiate('res://models/City01.tscn')
        self.controller = get_py_object(find_node(self.model_node, 'Controller'))

        loc = self.location
        set_position(self.model_node, loc.x, loc.y, loc.z)
        
        self.controller.set_title(self.unit_name)
        print_line(f'Controller: {self.controller}')

##############################################################
# UnitMgr
##############################################################
class UnitMgr:
    def __init__(self):
        self.unit_id_seed = 100
        self.unit_dict = {}
        self.update_list = []
        self.dead_list = []

    def get_next_unit_id(self):
        self.unit_id_seed += 1
        return self.unit_id_seed

    def update(self, delta_time):
        i = 0
        count = len(self.update_list)

        while i < count:
            unit = self.update_list[i]
            unit.update()
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

    def create_city(self):
        return self.create_unit(CityUnit)

    def create_troop(self):
        return self.create_unit(TroopUnit)



