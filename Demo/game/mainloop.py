#
# 2023年1月31日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

# 主循环
class MainLoop(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        set_process(self._get_node(), process=True, input=False)

        connect(self._get_node(), "ready", self._ready)

    def _ready(self):
        print_line('MainLoop ready')

        game_mgr.camera_mgr.update_camera()
        game_mgr.ground_mgr.update()

    def _process(self):
        delta_time = get_delta_time()

        game_mgr.camera_mgr.update()
        game_mgr.ground_mgr.update()
        game_mgr.troop_mgr.update(delta_time)




