#
# 2023年2月3日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.unit import CityUnit, TroopUnit

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

        unit.owner_player_id = game_mgr.player_mgr.main_player_id

        unit.load_model()

        return unit

    def get_unit(self, unit_id):
        return self.unit_dict.get(unit_id, None)

    def create_city(self):
        return self.create_unit(CityUnit)

    def create_troop(self):
        return self.create_unit(TroopUnit)

