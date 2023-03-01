#
# 2023年2月10日 bianpeng
#
from game.core import *
from game.game_mgr import game_mgr, UnitTrait
from game.base_type import Unit, UT_TROOP
from game.troop_controller import TroopController

# 部队
class TroopUnit(Unit, UnitTrait):
    def __init__(self):
        super().__init__()
        self.unit_type = UT_TROOP

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
        self.leader_hero_id = 0

        self.army_amount = 0
        self.army_moral = 100

        self.model_type = 3

    def load_model(self):
        self.unit_name = f'部队_{self.unit_id}'

        #path = 'res://models/Troop01.tscn'
        path = f'res://models/Troop{self.model_type:02}.tscn'
        
        self.model_node = FNode3D.instantiate(path)
        self.get_controller().apply_position()

    def set_army_amount(self, value):
        self.army_amount = value

    def add_hero(self, hero_id):
        self.hero_list.append(hero_id)

