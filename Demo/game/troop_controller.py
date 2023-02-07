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
        self.v = Vector3()
        self.v.set(1, 0, 0)

    def on_ai_tick(self):
        unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        #print_line(unit.unit_name)

    def process_ai(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.1:
            self.ai_tick_time = 0
            self.on_ai_tick()

    def process_move(self):
        delta = game_mgr.delta_time

        x,y,z = self.unit.get_location()
        x += self.v.x * delta
        y += self.v.y * delta
        z += self.v.z * delta
        self.unit.set_location(x,y,z)

    def update(self):
        self.process_ai()
        self.process_move()


