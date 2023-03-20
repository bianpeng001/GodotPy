#
# 2023年2月3日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.city_unit import CityUnit
from game.troop_unit import TroopUnit
from game.base_type import UT_CITY, UT_TROOP

#------------------------------------------------------------
# UnitMgr
#------------------------------------------------------------
class UnitMgr:
    def __init__(self):
        self._unit_id_seed = 10000

        self.unit_dict = {}
        
        # update, 事件
        self.update_list = []
        self.back_update_list = []

        # start, 事件机制, 第一次update之前
        self.start_list = []
        self.back_start_list = []

        # dead, 死亡队列
        self.dead_list = []

    def get_next_unit_id(self):
        self._unit_id_seed += 1
        return self._unit_id_seed

    def update(self, delta_time):
        self._call_start()
        self._call_update()
        self._exec_dead_list()

    def _call_start(self):
        tmp = self.start_list
        self.start_list = self.back_start_list
        self.back_start_list = tmp
        # 因为start过程里,可能创建其他对象,所以要前后两个start_queue

        if len(self.back_start_list) > 0:
            try:
                for unit in self.back_start_list:
                    unit.get_controller().start()
            finally:
                self.back_start_list.clear()

    def _call_update(self):
        tmp = self.back_update_list
        self.back_update_list = self.update_list
        self.update_list = tmp
        # 因为update过程里,可能创建其他对象,所以要前后两个update_list

        # call update on every unit
        if len(self.back_update_list) > 0:
            try:
                for unit in self.back_update_list:
                    unit.get_controller().update()

                    if unit.is_dead:
                        self.dead_list.append(unit)
                    else:
                        self.update_list.append(unit)
            finally:
                self.back_update_list.clear()

    def _exec_dead_list(self):
        # destroy dead list
        if len(self.dead_list) > 0:
            for unit in self.dead_list:
                unit.on_dead()
                #print_line(f'remove unit: {unit.unit_id}')
                self.unit_dict.pop(unit.unit_id)
            self.dead_list.clear()

    def create_unit(self, unit_class_, unit_type):
        unit = unit_class_()

        unit.unit_type = unit_type
        unit.unit_id = self.get_next_unit_id()

        self.unit_dict[unit.unit_id] = unit
        self.start_list.append(unit)
        self.update_list.append(unit)
        #print_line(f'add unit: {unit.unit_id}')

        unit.init()
        #unit.load_model()

        return unit

    def get_unit(self, unit_id):
        return self.unit_dict.get(unit_id, None)

    def create_city(self):
        return self.create_unit(CityUnit, UT_CITY)

    def create_troop(self):
        return self.create_unit(TroopUnit, UT_TROOP)

    # find first match requirements unit
    def find_unit(self, predicate):
        for unit in self.update_list:
            if predicate(unit):
                return unit

    def each_city(self):
        for unit in self.update_list:
            if unit.unit_type == UT_CITY:
                yield unit

