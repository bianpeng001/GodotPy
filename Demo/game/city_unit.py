#
# 2023年2月8日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import Unit, LimitValue
from game.config_mgr import new_city_name, new_hero_name

from game.city_controller import CityController

# 城池
# 内政，治安，农业，商业
# 战斗状态下，治安越来越差，且毫无收益
# 影响因素，自然灾害，麻匪，朝廷征收，摊派，督邮的敲诈啥的，神仙显灵
#
# 城池, 根据发展也是有级别的. 可以是, 县郡州
#
class CityUnit(Unit, UnitTrait):
    def __init__(self):
        super().__init__()

        # 控制器
        self._controller = CityController()
        self._controller._unit = self

        self.radius = 3
        self.unit_name = new_city_name()

        # 军团，城市组合，某个城作为首府，控制周围的其他城
        self.leader_city = 0
        self.city_group = []

        # 城内武将
        self.hero_list = []
        #  附属建筑
        self.building_list = []

        # 军队数量,区别于居民人口
        self.army_amount = LimitValue(random_int(1000, 2000), 100000)
        # 粮食
        self.rice_amount = LimitValue(random_int(100, 1000), 1000000)
        # 银两
        self.money_amount = LimitValue(random_int(100, 1000), 1000000)

        # 士气
        self.army_moral = 50
        self.defense = 100
        
        # 治安,农业，商业的发展程度
        self.order_points = 50
        self.farmer_points = 50
        self.trader_points = 50

        # 居民人口 = 治安 + 务农 + 经商
        self.population = LimitValue(1000 + random_int(0, 200),
                10000 + random_int(0, 9)*10000)
        self.polulation_growth_rate = 0

        # 太守(总督,县尉,郡守)
        self.satrap = 0

        # 税务官
        self.fax_incharge = 0
        # 税率,税率过高会影响士气,破坏治安
        self.fax_rate = 10

        # 由于人口是一个动态的, 工作人数用百分比最好

        # 治安官
        self.order_incharge = 0
        # 治安人数
        self.order_mass = 0
        
        # 农业官
        self.farmer_incharge = 0
        # 农民数量, 改成百分比
        self.farmer_mass = 0
        
        # 商业官
        self.trader_incharge = 0
        # 商人数量
        self.trader_mass = 0

        # AI运行开关
        self.enable_ai = True
        
        # 友好城市,通商
        self.friend_city_list = []

        # 模型
        self.model_type = 1
        # 质量
        self.mass = 500

    def init(self):
        for i in range(10):
            hero = game_mgr.hero_mgr.new_hero()
            hero.city_id = self.unit_id
            hero.hero_name = new_hero_name()
            log_util.debug('new hero', self.unit_name, hero.hero_id, hero.hero_name)
            
            self.hero_list.append(hero.hero_id)

    def load_model(self):
        is_gate = self.unit_name.endswith('关')

        if self.model_type == 1:
            path = 'res://models/City01.tscn'
            if is_gate:
                path = 'res://models/Gate01.tscn'
        else:
            path = 'res://models/City02.tscn'
        
        self.model_node = FNode3D.instantiate(path)
        if is_gate:
            self.model_node.set_scale(1.8,1.8,1.8)

        self.get_controller().apply_position()
        self.get_controller().set_title(self.unit_name)
        self.get_controller().set_flag_color()




