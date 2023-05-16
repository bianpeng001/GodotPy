#
# 2023年4月25日 bianpeng
#

from game.base_type import *
from game.core import log_debug, random_1
from game.game_mgr import *


#
# 黑板
#
class PlayerBlackboard(AIBlackboard):
    def __init__(self):
        super().__init__()
        self.state_start_time = 0

    def get_state_time(self):
        return game_mgr.sec_time - self.state_start_time

#
# 基类
#
class AIState_Player(AIState):
    def enter(self, brain_comp):
        blackboard = brain_comp.get_blackboard()
        blackboard.state_start_time = game_mgr.sec_time
        
        self.do_enter(brain_comp)
        
    def do_enter(self, brain_comp):
        pass

#
# 发展, 经济, 出战等等
#
class AIState_PlayerDevelop(AIState_Player):
    def update(self, brain_comp):
        log_debug('AIState_PlayerDevelop', brain_comp.get_player().player_name)

#
# 开始节点, 开始一阵以后, 应该进入内政
#
class AIState_PlayerStart(AIState_Player):
    def update(self, brain_comp):
        #log_debug('AIState_PlayerStart', brain_comp.get_player().player_name)
        blackboard = brain_comp.get_blackboard()
        if blackboard.get_state_time() > 10:
            brain_comp.goto_state('develop')

#
# 玩家的AI组件
#
class PlayerBrainComponent(Component, AIMachine):
    def __init__(self):
        super().__init__()
        AIMachine.__init__(self)
        
        self.enabled = True
        self.tick_time = random_1() * 3
        
    def update(self, delta_time):
        self.tick_time += delta_time
        if self.tick_time > 3:
            self.on_tick(self.tick_time)
            self.tick_time = 0
            
    def get_player(self):
        return self.get_controller().get_player()
    
    # 驱动一次ai
    def on_tick(self, delta_time):
        self.ai_state.update(self)
    


