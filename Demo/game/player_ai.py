#
# 2023年4月25日 bianpeng
#

from game.base_type import *

#
# 玩家的AI组件
#
class PlayerAIComponent(Component):
    def __init__(self, player):
        super().__init__()
        
        self.player = player
        self.enabled = True
        
    def update(self, delta_time):
        if self.enabled:
            pass
    


