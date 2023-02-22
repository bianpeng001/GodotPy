#
# 2023年1月31日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.event_name import APP_LAUNCH, START_GAME

# 主循环, 控制主游戏生命周期
# enter_tree, up to down
# ready, down to up, 当mainloop收到ready的时候，整个场景都ready过了
class MainLoop(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        set_process(self.get_node(), process=True, input=False)
        connect(self.get_node(), "ready", self._ready)
        
        from game.game_play import GamePlay
        game_mgr.game_play = GamePlay()

        game_mgr.event_mgr.emit(APP_LAUNCH)

    def _ready(self):
        log_util.debug('MainLoop ready')
        # start game
        game_mgr.event_mgr.emit(START_GAME)

    def _process(self):
        if not game_mgr.paused:
            # cache time/frame_number
            game_mgr.frame_number += 1
            game_mgr.time = OS.get_time()
            game_mgr.sec_time = game_mgr.time * 0.001
            game_mgr.delta_time = OS.get_delta_time()
            
            game_mgr.update()

        

        
