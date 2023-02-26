#
# 2023年2月8日 bianpeng
#
import random

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import Unit, UT_CITY
from game.config_mgr import new_city_name, new_hero_name

from game.city_controller import CityController

# 城池
class CityUnit(Unit):
    def __init__(self):
        super().__init__()
        self.unit_type = UT_CITY

        self._controller = CityController()
        self._controller._unit = self

        self.radius = 3
        self.unit_name = new_city_name()

        # 军团，城市组合，某个城作为首府，控制周围的其他城
        self.group_main_city_id = 0

        # 城内武将
        self.hero_list = []

        # 单个资源上限
        self.max_amount_limit = 1000000 + random_int(0, 50)*10000
        
        # 资源
        self.army_amount = random_int(100, 1000)
        self.rice_amount = random_int(100, 1000)
        self.iron_amount = random_int(100, 1000)
        self.stone_amount = random_int(100, 1000)
        self.wood_amount = random_int(100, 1000)
        self.money_amount = random_int(100, 1000)

        self.army_moral = 100

        # 资源增长率
        self.growth_rate = random_int(10, 30)

    def init(self):
        for i in range(5):
            hero = game_mgr.hero_mgr.new_hero()
            hero.city_id = self.unit_id
            hero.hero_name = new_hero_name()
            log_util.debug('new hero', self.unit_name, hero.hero_id, hero.hero_name)
            
            self.hero_list.append(hero.hero_id)

    def load_model(self):
        is_gate = self.unit_name.endswith('关')

        path = 'res://models/City01.tscn'
        if is_gate:
            path = 'res://models/Wall01.tscn'
        
        self.model_node = FNode3D.instantiate(path)
        self.get_controller().apply_position()
        self.get_controller().set_title(self.unit_name)

    def belong_to_main_player(self):
        return self.owner_player_id == game_mgr.get_main_player_id()

