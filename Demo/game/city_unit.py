#
# 2023年2月8日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import *
from game.config_mgr import new_city_name

from game.city_controller import CityController

#
# 城池
# 内政，治安，农业，商业
# 战斗状态下，治安越来越差，且毫无收益
# 影响因素，自然灾害，麻匪，朝廷征收，摊派，督邮的敲诈啥的，神仙显灵
#
# 城池, 根据发展也是有级别的. 可以是, 县郡州
#
class CityUnit(Unit):
    def __init__(self):
        super().__init__()

        # 控制器
        self._controller = CityController(self)
        # 半径
        self.radius = 3
        # 名字
        self.unit_name = new_city_name()
        # 级别
        self.city_type = CT_XIAN

        # 军团，城市组合，某个城作为首府，控制周围的其他城
        #self.lead_city_id = 0
        #self.city_group = []

        # 城内武将
        self.hero_list = []
        #  附属建筑
        self.building_list = []

        # 军队数量,区别于居民人口
        self.army_amount = RangeValue(random_int(1000, 2000), 5000)
        # 士气
        self.army_moral = RangeValue(100, 100)
        self.damage = 10
        self.defense = 10
        
        # 粮食
        self.rice_amount = RangeValue(random_int(100, 1000), 1000000)
        # 银两
        self.money_amount = RangeValue(random_int(100, 1000), 1000000)

        # 治安,农业，商业的发展程度
        self.order_points = RangeValue(50, 100)
        self.farm_points = RangeValue(50, 100)
        self.trade_points = RangeValue(50, 100)

        # 居民人口 = 治安 + 务农 + 经商
        self.population = RangeValue(
                1000 + random_int(0, 200),
                10000 + random_int(0, 9)*10000,
                100000)
        self.population_growth_rate = 0

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

        # 质量
        self.mass = 300

    # 初始化城内武将
    def init(self):
        for i in range(random_range(5, 10)):
            hero = game_mgr.hero_mgr.new_hero()
            hero.owner_city_id = self.unit_id
            log_debug('new hero', self.unit_name, hero.hero_id, hero.hero_name)
            
            self.hero_list.append(hero.hero_id)

    # 加载模型
    def load_model(self):
        # TODO: 这里后面需要控制的更加精细一些
        is_gate = self.unit_name.endswith('关')
        is_hill = len(self.unit_name) == 3 and self.unit_name[-1] in ('岭','山')

        if is_gate:
            path = 'res://models/Gate01.tscn'
        elif is_hill:
            path = 'res://models/Hill02/Hill02.tscn'
        elif self.city_type == CT_XIAN:
            path = 'res://models/City02.tscn'
        else:
            path = 'res://models/City01.tscn'
            
        
        self.model_node = OS.instantiate(path)
        if is_gate:
            self.model_node.set_scale(1.2,1.2,1.2)

        controller = self.get_controller()
        controller.apply_position()
        controller.set_title(self.unit_name)
        controller.set_flag_color()
        
    def get_hero_count(self):
        return len(self.hero_list)


