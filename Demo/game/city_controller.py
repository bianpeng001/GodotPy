#
# 2023年2月2日 bianpeng
#

import random

from game.core import *
from game.game_mgr import game_mgr


# 城池
class CityController(BaseController):
    def __init__(self):
        super().__init__()

        # 控制属性
        self.ai_tick_time = 0

    def set_title(self, text):
        title_node = find_node(self.model_node, 'HUD/Title')
        Label3D.set_text(title_node, text)

    def update_ai(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.3:
            self.on_ai_tick(self.ai_tick_time)
            self.ai_tick_time = 0

    def on_ai_tick(self, tick_time):
        city = self.unit

        city.army_amount += city.growth_rate * tick_time

        # create troop for fight
        if city.army_amount > 1000:
            city.army_amount -= 1000

            x,y,z = city.get_location()

            troop = game_mgr.unit_mgr.create_troop()
            troop.set_army_amount(1000)
            troop.owner_city_id = city.unit_id
            troop.set_location(x,y,z)

    def update(self):
        self.update_ai()

