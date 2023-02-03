#
# 2023年2月3日 bianpeng
#

from game.core import *

###############################
# Units
###############################
class Unit:
    def __init__(self):
        self.unit_id = None
        self.unit_name = '桐乡渔叟'

        # 所属君主
        self.owner_player_id = None
        # 所属城
        self.owner_city_id = None

        # 战斗属性
        self.hp = self.maxhp = 100
        self.pos = Vector3()

        # 模型
        self.model_node = None
        self.controller = None

    def load_model(self):
        pass

    def update(self):
        pass

#
class TroopUnit(Unit):
    def __init__(self):
        super().__init__()

#
class CityUnit(Unit):
    def __init__(self):
        super().__init__()

    def load_model(self):
        self.model_node = instantiate('res://models/City01.tscn')
        set_position(self.model_node, 5, 0, 5)
        self.controller = get_py_object(find_node(self.model_node, 'Controller'))
        print_line(f'controller: {self.controller}')

###############################
# Units
###############################
class UnitMgr:
    def __init__(self):
        self.unit_dict = {}
        self.unit_id_seed = 100

    def get_next_unit_id(self):
        self.unit_id_seed += 1
        return self.unit_id_seed

    def update(self, delta_time):
        for v in self.unit_dict.values():
            v.update()

    def create_unit(self, unit_class_):
        unit = unit_class_()

        unit.unit_id = self.get_next_unit_id()
        self.unit_dict[unit.unit_id] = unit
        unit.load_model()

    def create_city(self):
        return self.create_unit(CityUnit)

    def create_troop(self):
        return self.create_unit(TroopUnit)



