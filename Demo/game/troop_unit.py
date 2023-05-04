#
# 2023年2月10日 bianpeng
#
from game.core import log_debug, OS
from game.game_mgr import game_mgr, UnitTrait
from game.base_type import Unit, LimitValue
from game.troop_controller import TroopController

#
# 部队
#
class TroopUnit(Unit, UnitTrait):
    def __init__(self):
        super().__init__()

        self._controller = TroopController(self)

        # 基本特征参数
        self.radius = 3
        # 所属城
        self.owner_city_id = None
        # 行军速度
        self.speed = 0.6

        # 武将列表
        self.hero_list = []
        # 主将
        self.chief_hero_id = 0

        # 军队数量
        self.army_amount = LimitValue(0, 1000)
        
        # 士气
        self.army_moral = 100
        self.critical_strike = 50

        # 模型的类型
        self.model_type = 3
        self.mass = 10

        # 战斗策略
        # TODO: 这几个数据, 也许不应该放在这里
        self.target_pos = (0, 0)
        self.target_unit_id = 0
        # 追逐目标
        self.chase_target = False

    def load_model(self):
        #path = 'res://models/Troop01.tscn'
        path = f'res://models/Troop{self.model_type:02}.tscn'
        
        self.model_node = OS.instantiate(path)
        self.get_controller().apply_position()





