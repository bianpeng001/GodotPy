#
# 2023年1月31日 bianpeng
#

import sys

from game.core import *
from game.game_mgr import game_mgr

# 主循环, 控制主游戏生命周期
# enter_tree, up to down
# ready, down to up
class MainLoop(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        set_process(self.get_node(), process=True, input=False)
        connect(self.get_node(), "ready", self._ready)

        OS.set_window_size(608, 342, 3700, 1050)

    def init(self):
        from game.coroutine_mgr import CoroutineMgr
        from game.unit_mgr import UnitMgr
        from game.player_mgr import PlayerMgr
        from game.hero_mgr import HeroMgr
        from game.game_play import GamePlay

        game_mgr.co_mgr = CoroutineMgr()

        game_mgr.unit_mgr = UnitMgr()
        game_mgr.player_mgr = PlayerMgr()
        game_mgr.hero_mgr = HeroMgr()
        game_mgr.game_play = GamePlay()

    def _ready(self):
        self.init()
        log_util.debug('MainLoop ready')
        game_mgr.camera_mgr.update_camera()

        # test
        from game.wait import test1
        test1()

        # start game
        from game.event_name import START_GAME
        game_mgr.event_mgr.emit(START_GAME)

    def _process(self):
        if game_mgr.paused:
            return

        game_mgr.frame_number += 1
        game_mgr.time = OS.get_time()
        game_mgr.delta_time = OS.get_delta_time()

        delta_time = game_mgr.delta_time

        # coroutine first
        game_mgr.co_mgr.execute()

        # update all system
        game_mgr.input_mgr.update(delta_time)
        game_mgr.ui_mgr.update(delta_time)
        game_mgr.ground_mgr.update(delta_time)
        game_mgr.unit_mgr.update(delta_time)
        
