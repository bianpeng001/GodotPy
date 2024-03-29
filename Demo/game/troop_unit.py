#
# 2023年2月10日 bianpeng
#
from game.core import log_debug, OS
from game.game_mgr import *
from game.base_type import *
from game.troop_controller import TroopController

#
# 部队
#
class TroopUnit(Unit):
    def __init__(self):
        super().__init__()

        self._controller = TroopController(self)

        # 基本特征参数
        self.radius = 3
        # 行军速度
        self.speed = 0.6

        # 所属城
        self.base_city_id = 0
        # 主将
        self.chief_hero_id = 0
        # 武将列表
        self.hero_list = []

        # 兵种类型
        self.army_type = AT_NONE
        # 军队数量
        self.army_amount = RangeValue(0, 1000)
        # 暴击率
        self.critical_rate = 50

        # 模型的类型
        self.model_type = 3
        # 质量
        self.mass = 10

        # 目标信息
        # TODO: 这几个数据, 也许不应该放在这里
        self.target_pos = (0, 0)
        self.target_unit_id = 0

        # 战斗策略
        self.chase_target = False
        self.enter_target = False
        self.stay_when_no_target = False


    def load_model(self):
        #path = 'res://models/Troop01.tscn'
        path = f'res://models/Troop{self.model_type:02}.tscn'
        
        self.model_node = OS.instantiate(path)
        controller = self.get_controller()
        controller.apply_position()

    def get_hero_count(self):
        return len(self.hero_list)



