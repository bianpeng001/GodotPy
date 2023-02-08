#
# 2023年1月31日 bianpeng
#

import sys

from game.core import *
from game.game_mgr import game_mgr
from game.unit_mgr import UnitMgr
from game.player_mgr import PlayerMgr

# 主循环
class MainLoop(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        set_process(self._get_node(), process=True, input=False)
        connect(self._get_node(), "ready", self._ready)

    def init(self):
        game_mgr.unit_mgr = UnitMgr()
        game_mgr.player_mgr = PlayerMgr()

    def _ready(self):
        self.init()
        print_line('MainLoop ready')
        
        game_mgr.camera_mgr.update_camera()

    def _process(self):
        game_mgr.time = OS.get_time()
        game_mgr.delta_time = OS.get_delta_time()

        # update all system
        delta_time = game_mgr.delta_time

        game_mgr.input_mgr.update(delta_time)
        game_mgr.ui_mgr.update(delta_time)
        game_mgr.ground_mgr.update(delta_time)
        game_mgr.unit_mgr.update(delta_time)
        





