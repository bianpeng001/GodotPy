#
# 2023年2月8日 bianpeng
#

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

        self.controller = CityController()
        self.controller.unit = self

        self.radius = 3
        self.unit_name = new_city_name()

        # 城内武将
        self.hero_list = []
        
        # 资源
        self.army_amount = 800+random_max(100)
        self.rice_amount = 0
        self.iron_amount = 0
        self.stone_amount = 0
        self.wood_amount = 0
        self.money_amount = 0

        # 资源增长率
        self.growth_rate = 20 + random_max(30)

    def init(self):
        for i in range(5):
            hero = game_mgr.hero_mgr.new_hero()
            hero.city_id = self.unit_id
            hero.hero_name = new_hero_name()
            logutil.debug('new hero', self.unit_name, hero.hero_name)
            
            self.hero_list.append(hero.hero_id)

    def load_model(self):
        self.model_node = instantiate('res://models/City01.tscn')

        x,y,z = self.get_location()
        Node3D.set_position(self.model_node, x,y,z)
        
        self.controller.set_title(self.unit_name)
