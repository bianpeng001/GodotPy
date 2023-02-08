#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

# 部队
class TroopController(BaseController):
    def __init__(self):
        super().__init__()

        self.ai_tick_time = 0

    def on_ai_tick(self, tick_time):
        unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        #print_line(unit.unit_name)

    def update_ai(self, tick_time):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.1:
            self.on_ai_tick(self.ai_tick_time)
            self.ai_tick_time = 0

    def update_move(self):
        unit = self.unit
        delta = game_mgr.delta_time

        x,y,z = unit.get_location()
        x += unit.velocity.x * delta
        y += unit.velocity.y * delta
        z += unit.velocity.z * delta
        unit.set_location(x,y,z)

    def update(self):
        self.update_ai()
        self.update_move()


