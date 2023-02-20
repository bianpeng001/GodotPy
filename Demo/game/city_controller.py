#
# 2023年2月2日 bianpeng
#

import random

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import Controller

# 城池
class CityController(Controller):
    def __init__(self):
        super().__init__()

        # 控制属性
        self.ai_tick_time = 0

    def set_title(self, text):
        title_node = find_node(self.model_node, 'HUD/Title')
        if title_node:
            Label3D.set_text(title_node, text)

    def set_flag_color(self):
        flag_node = find_node(self.model_node, 'Flag')
        if flag_node:
            mesh_instance3d_load_material(flag_node, 0, 'res://models/Color/Green.tres')

    # 驱动ai tick
    def drive_ai_tick(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.3:
            self.on_ai_tick(self.ai_tick_time)
            self.ai_tick_time = 0

    # 计算资源增长
    def _calc_resource(self, amount, growth_rate, delta_time, max_amount):
        value =  amount + growth_rate * delta_time
        if value > max_amount:
            value = max_amount
        return round(value)

    def grow_resource(self, delta_time):
        city = self.get_unit()

        city.army_amount = self._calc_resource(city.army_amount, 
                city.growth_rate, delta_time, city.max_amount_limit)
        city.money_amount = self._calc_resource(city.money_amount, 
                city.growth_rate, delta_time, city.max_amount_limit)
        city.rice_amount = self._calc_resource(city.rice_amount, 
                city.growth_rate, delta_time, city.max_amount_limit)

    def on_ai_tick(self, tick_time):
        city = self.get_unit()

        # create troop for fight
        if city.army_amount > 1000:
            city.army_amount -= 1000

            x,y,z = city.get_location()

            troop = game_mgr.unit_mgr.create_troop()
            troop.owner_city_id = city.unit_id
            troop.owner_player_id = city.owner_player_id

            troop.set_army_amount(1000)
            troop.set_position(x,y,z)


    def update(self):
        self.drive_ai_tick()

