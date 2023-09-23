#
# 2023年8月8日 bianpeng
# audio manager
#

from game.core import *
from game.game_mgr import *

class AudioItem:
    def __init__(self, path, volume_db):
        self.path = path
        self.volume_db = volume_db
        self.res_capsule = None

#
# 声音播放
#
class AudioMgr:
    def __init__(self):
        # 短音效
        self.player = None
        # 背景音乐, 需要一直播放
        self.bgm_player = None
        self.music_dict = {}

    def init(self):
        self.player = game_mgr.scene_root_obj.find_node('AudioMgr/AudioStreamPlayer')
        self.bgm_player = game_mgr.scene_root_obj.find_node('AudioMgr/AudioStreamPlayer2')
        log_debug(self.player)

        self.music_dict['game_start'] = ResCapsule.load_resource('res://sound/game-complete.wav')
        self.music_dict['ground_click'] = ResCapsule.load_resource('res://sound/ground-click.wav')


    def play_sound(self, id):
        sound = self.music_dict.get(id, None)
        if sound:
            self.player.set_stream(sound.res)
            self.player.play(0)
            #self.player.set_volume(-20)
            self.player.set_volume(-10)

    def cleanup(self):
        self.music_dict = None

