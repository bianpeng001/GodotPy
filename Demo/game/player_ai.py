#
# 2023年4月25日 bianpeng
#

from game.base_type import *
from game.core import log_debug
from game.game_mgr import *


#
#
#
class PlayerBlackboard(AIBlackboard):
    def __init__(self):
        super().__init__()
        

#
#
#
class AIState_Player(AIState):
    pass

#
#
#
class AIState_PlayerStart(AIState_Player):
    def update(self, brain_comp):
        log_debug('AIState_PlayerStart')

#
# 玩家的AI组件
#
class PlayerBrainComponent(Component, AIMachine):
    def __init__(self):
        super().__init__()
        AIMachine.__init__(self)
        
        self.enabled = True
        self.tick_time = 0
        
    def update(self, delta_time):
        self.tick_time += delta_time
        if self.tick_time > 0.1:
            self.on_tick(self.tick_time)
            self.tick_time = 0
            
    def get_player(self):
        return self.get_controller().get_player()
    
    # 驱动一次ai
    def on_tick(self, delta_time):
        self.ai_state.update(self)
    


