#
# 2023年2月10日 bianpeng
#
from game.core import *
from game.game_mgr import game_mgr, UnitTrait
from game.base_type import Unit, LimitValue
from game.troop_controller import TroopController

#
# 军团
#
class TroopUnit(Unit, UnitTrait):
    def __init__(self):
        super().__init__()

        self._controller = TroopController()
        self._controller._unit = self

        # 所属城
        self.owner_city_id = None
        self.radius = 2
        # 行军速度
        self.speed = 1.2

        # 武将
        self.hero_list = []
        # 主将
        self.chief_hero_id = 0

        # 军队数量
        self.army_amount = 0
        # 士气
        self.army_moral = 100

        # 模型的类型
        self.model_type = 3

        # 战斗策略
        self.target_pos = (0, 0)
        self.target_unit_id = 0

        # 追逐目标
        self.chase_target = False

    def load_model(self):
        #path = 'res://models/Troop01.tscn'
        path = f'res://models/Troop{self.model_type:02}.tscn'
        
        self.model_node = FNode3D.instantiate(path)
        self.get_controller().apply_position()





