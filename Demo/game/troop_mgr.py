#
# 2023年2月1日 bianpeng
#

from game.core import *

#
class TroopMgr(Singleton):
    def __init__(self):
        self.troops = {}
    

troop_mgr = TroopMgr.get_instance()

