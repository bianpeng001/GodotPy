#
# 2023年2月10日 bianpeng
#
from game.core import *
from game.game_mgr import game_mgr
from game.base_type import Unit, UT_TROOP
from game.troop_controller import TroopController

# 部队
class TroopUnit(Unit):
    def __init__(self):
        super().__init__()
        self.unit_type = UT_TROOP

        self.controller = TroopController()
        self.controller.unit = self

        # 所属城
        self.owner_city_id = None
        self.radius = 2
        # 行军速度
        self.speed = 2.4

        # 武将
        self.hero_list = []
        # 主将
        self.leader_hero_id = 0

        self.army_amount = 0

    def load_model(self):
        self.unit_name = f'部队_{self.unit_id}'

        self.model_node = instantiate('res://models/Troop01.tscn')
        Node3D.set_position(self.model_node,*self.get_location())

    def set_army_amount(self, value):
        self.army_amount = value

