#
# 2023年2月3日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import TwoFoldList
from game.city_unit import CityUnit
from game.troop_unit import TroopUnit
from game.base_type import UT_CITY, UT_TROOP

#
# 单位管理, 目前只有城市和军团
#
class UnitMgr:
    def __init__(self):
        self._unit_id_seed = 10000

        self.unit_dict = {}
        
        # update, 事件
        self.update_list = TwoFoldList()

        # start, 事件, 第一次update之前
        self.start_list = TwoFoldList()

        # dead, 死亡队列
        self.dead_list = []

    def get_next_unit_id(self):
        self._unit_id_seed += 1
        return self._unit_id_seed

    def update(self, delta_time):
        self.start_list.update_cb(self._call_unit_start)
        self.update_list.update_cb(self._call_unit_update)
        self._exec_dead_list()

    def _call_unit_start(self, unit):
        unit.get_controller().start()

    def _call_unit_update(self, unit):
        unit.get_controller().update()
        if unit.is_dead:
            self.dead_list.append(unit)
        else:
            self.update_list.append(unit)

    def _exec_dead_list(self):
        # destroy dead list
        if len(self.dead_list) > 0:
            for unit in self.dead_list:
                unit.on_dead()
                #print_line(f'remove unit: {unit.unit_id}')
                self.unit_dict.pop(unit.unit_id)
            self.dead_list.clear()

    # 创建一个单位
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

    def create_city(self):
        return self.create_unit(CityUnit, UT_CITY)

    def create_troop(self):
        return self.create_unit(TroopUnit, UT_TROOP)

    def get_unit(self, unit_id):
        return self.unit_dict.get(unit_id, None)

    # find first match requirements unit
    def find_unit(self, predicate):
        return first(self.update_list.get_list(), predicate)

    def find_unit_by_name(self, name):
        return first(self.update_list.get_list(), lambda x: x.unit_name == name)

    def loop_cities(self):
        for unit in self.update_list.get_list():
            if unit.unit_type == UT_CITY:
                yield unit

    def loop_troops(self):
        for unit in self.update_list.get_list():
            if unit.unit_type == UT_TROOP:
                yield unit

    # 根据位置, 计算所在的九州的位置, 九州之外的叫做荒蛮之地
    def get_province(self, x, z):
        x = math.floor(x / 300)
        z = math.floor(z / 300)
        
        if x >= -1 and x <= 1 and z >= -1 and z <= 1:
            province = '雍冀兖豫徐青益荆扬'[(z+1)*3+(x+1)] + '州'
        else:
            province = '化外'
            
        return province
    
