#
# 2023年1月31日 bianpeng
#

from game.core import Singleton, print_line

from game.troop_mgr import TroopMgr

class GameMgr(Singleton):
    def __init__(self):
        super().__init__()

        self.input_mgr = None
        self.camera_mgr = None
        self.ground_mgr = None

        self.troop_mgr = TroopMgr()

    def hello(self):
        pass

game_mgr = GameMgr.get_instance()


