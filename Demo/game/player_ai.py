#
# 2023年4月25日 bianpeng
#

from game.base_type import *
from game.core import *
from game.game_mgr import *

#
# 玩家的AI组件
#
class PlayerAIComponent(Component):
    def __init__(self, player):
        super().__init__()
        
        self.player = player
        self.enabled = True
        
        self.tick_time = 0
        
    def update(self, delta_time):
        self.tick_time += delta_time
        if self.tick_time > 0.1:
            self.on_tick(self.tick_time)
            self.tick_time = 0
    
    # 驱动一次ai
    def on_tick(self, delta_time):
        pass
    


