#
# 2023年2月20日 bianpeng
#

from game.core import *
from game.base_type import *
from game.game_mgr import game_mgr

class CityBlackboard(AIBlackboard):
    def __init__(self):
        pass

class AIState_City(AIState):
    pass


#
# 城池的ai，决策发展和攻击。以及城池的军团
#
#
#


#
class AIState_CityIdle(AIState_City):
    def update(self, controller):
        pass

