#
# 2023年1月31日 bianpeng
#

import sys

from game.core import *
from game.game_mgr import game_mgr

from game.troop_mgr import TroopMgr
from game.city_mgr import CityMgr
from game.event_mgr import EventMgr

# 主循环
class MainLoop(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        set_process(self._get_node(), process=True, input=False)
        connect(self._get_node(), "ready", self._ready)

    def init(self):
        game_mgr._troop_mgr = TroopMgr()
        game_mgr._city_mgr = CityMgr()
        game_mgr._event_mgr = EventMgr()

    def _ready(self):
        self.init()
        print_line('MainLoop ready')
        
        game_mgr.camera_mgr.update_camera()
        game_mgr.ground_mgr.update()
        
        game_mgr._troop_mgr.test()

    def _process(self):
        delta_time = get_delta_time()

        game_mgr.input_mgr.update(delta_time)
        game_mgr.camera_mgr.update()
        game_mgr.ground_mgr.update()
        game_mgr.troop_mgr.update(delta_time)



