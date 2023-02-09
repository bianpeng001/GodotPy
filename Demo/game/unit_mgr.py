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
        self._unit_id_seed = 10000

        self.unit_dict = {}
        
        self.update_list = []
        self.back_update_list = []

        self.dead_list = []

    def get_next_unit_id(self):
        self._unit_id_seed += 1
        return self._unit_id_seed

    def update(self, delta_time):
        self._call_update()
        self._exec_dead_list()

    def _call_update(self):
        # swap update list
        tmp = self.back_update_list
        self.back_update_list = self.update_list
        self.update_list = tmp

        # call update on every unit
        if len(self.back_update_list) > 0:
            for unit in self.back_update_list:
                unit.controller.update()
                if unit.is_dead:
                    self.dead_list.append(unit)
                else:
                    self.update_list.append(unit)
            self.back_update_list.clear()

    def _exec_dead_list(self):
        # destroy dead list
        if len(self.dead_list) > 0:
            for unit in self.dead_list:
                unit.on_dead()
                #print_line(f'remove unit: {unit.unit_id}')
                self.unit_dict.pop(unit.unit_id)
            self.dead_list.clear()

    def create_unit(self, unit_class_):
        unit = unit_class_()

        unit.unit_id = self.get_next_unit_id()
        self.unit_dict[unit.unit_id] = unit
        self.update_list.append(unit)
        #print_line(f'add unit: {unit.unit_id}')

        #unit.owner_player_id = game_mgr.player_mgr.main_player_id
        unit.init()
        unit.load_model()

        return unit

    def get_unit(self, unit_id):
        return self.unit_dict.get(unit_id, None)

    def create_city(self):
        return self.create_unit(CityUnit)

    def create_troop(self):
        return self.create_unit(TroopUnit)

    def find_unit(self, predicate):
        #self.update_list()
        pass


