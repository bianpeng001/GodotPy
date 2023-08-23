#
# 2023年8月8日 bianpeng
# audio manager
#

from game.core import *
from game.game_mgr import *

#
# 声音播放
#
class AudioMgr:
    def __init__(self):
        self.player = None

    def init(self):
        self.player = game_mgr.scene_root_obj.find_node('AudioStreamPlayer')
        log_debug(self.player)

    def play_sound(self, id):
        self.player.play(0)

    