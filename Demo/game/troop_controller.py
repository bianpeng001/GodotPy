#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

#
class TroopController(NodeObject):
    def __init__(self):
        super().__init__()
    
    def _create(self):
        print_line('troop ok')

    def update(self):
        pass


