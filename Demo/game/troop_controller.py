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
    
    def _create(self):
        pass

    def on_ai_tick(self):
        unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        print_line(unit.unit_name)

    def update(self):
        print(1)
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.1:
            self.ai_tick_time = 0
            self.on_ai_tick()



