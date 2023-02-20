#
# 2023年1月31日 bianpeng
#

# 这里尽量保持空依赖，在别的地方往这里塞
# 这样，game_mgr就能在别的地方被随意引用了
# 主要是模块这种机制，是不让循环引用的。因为他有toplevel语句
# 相比之下Delphi的Unit，是可以循环引用的。java，c#的引用的话,两个包是可以互相引用的。

from game.core import EventMgr

# 所有的系统的管理，单例
class GameMgr():
    def __init__(self):
        super().__init__()

        # init in boot.py
        # 底层管理器
        self._event_mgr = EventMgr()
        self._input_mgr = None
        self.co_mgr = None

        # 上层管理器
        self.camera_mgr = None
        self.ground_mgr = None
        self.troop_mgr = None
        self.unit_mgr = None
        self.ui_mgr = None
        self.hero_mgr = None
        self.effect_mgr = None

        # 玩法业务逻辑
        self.game_play = None

        # 游戏数据管理
        self.game_data = None

        # 时间和帧数信息
        self.time = 0
        self.delta_time = 0
        self.frame_number = 0
        self.paused = False

    @property
    def event_mgr(self):
        return self._event_mgr

    @property
    def input_mgr(self):
        return self._input_mgr

game_mgr = GameMgr()

def get_game_mgr():
    return game_mgr


