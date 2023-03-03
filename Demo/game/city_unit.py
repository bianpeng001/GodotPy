#
# 2023年2月8日 bianpeng
#
import random

from game.core import *
from game.game_mgr import *
from game.base_type import Unit, UT_CITY
from game.config_mgr import new_city_name, new_hero_name

from game.city_controller import CityController

# 城池
# 内政，治安，农业，商业
# 战斗状态下，治安越来越差，且毫无收益
# 影响因素，自然灾害，麻匪，朝廷征收，摊派，督邮的敲诈啥的，神仙显灵
#
class CityUnit(Unit, UnitTrait):
    def __init__(self):
        super().__init__()

        # 控制器
        self._controller = CityController()
        self._controller._unit = self

        self.unit_type = UT_CITY
        self.radius = 3
        self.unit_name = new_city_name()

        # 军团，城市组合，某个城作为首府，控制周围的其他城
        self.leader_city = 0
        self.city_group = []

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

        # 士气
        self.army_moral = 50
        # 治安,农业，商业的发展程度
        self.order_points = 100
        self.farmer_points = 100
        self.trader_points = 100

        # 居民人口 = 治安 + 务农 + 经商
        self.urban_mass = 1000 + random_int(100, 200)
        # 人口上限
        self.urban_mass_limit = 10000 + random_int(0, 9)*10000

        # 太守(总督)
        self.satrap = 0

        # 治安官
        self.order_incharge = 0
        # 治安人数
        self.order_mass = 0
        
        # 农业官
        self.farmer_incharge = 0
        # 农民数量
        self.farmer_mass = 0
        
        # 商业官
        self.trader_incharge = 0
        # 商人数量
        self.trader_mass = 0

        # 资源增长率, 基础增长率
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
        if is_gate:
            self.model_node.set_scale(1.8,1.8,1.8)

        self.get_controller().apply_position()
        self.get_controller().set_title(self.unit_name)




