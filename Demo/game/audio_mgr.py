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

        self.game_start_sound = ResCapsule.load_resource('res://sound/game-complete.wav')
        self.ground_click_sound = ResCapsule.load_resource('res://sound/ground-click.wav')

    def play_sound(self, id):
        match id:
            case 0:
                self.player.set_stream(self.game_start_sound.res)
            case 1:
                self.player.set_stream(self.ground_click_sound.res)
        self.player.play(0)
        self.player.set_volume(-20)

    def cleanup(self):
        self.game_start_sound = None
        self.ground_click_sound = None

