#
# 2023年1月31日 bianpeng
#

from game.core import Singleton, print_line

class GameMgr(Singleton):
    def __init__(self):
        super().__init__()

    def get_input(self):
        return self.input
    

