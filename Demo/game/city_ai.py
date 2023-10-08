#
# 2023年2月20日 bianpeng
#

from game.core import *
from game.base_type import *
from game.game_mgr import *

#
#
#
class CityBlackboard(AIBlackboard):
    def __init__(self):
        super().__init__()

        pass

#
#
#
class AIState_City(AIState):
    def enter(self, brain_comp):
        blackboard = brain_comp.get_blackboard()
        blackboard.state_start_time = game_mgr.time_sec

        self.do_enter(brain_comp)

    def do_enter(self, brain_comp):
        pass


#
# 简单模式: 内政
#
class CityAI_Easy(AIState_City):
    def update(self, brain_comp):
        pass

#
# 城池的ai，决策发展和攻击。以及城池的军团
#
#
#
