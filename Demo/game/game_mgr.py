#
# 2023年1月31日 bianpeng
#

#------------------------------------------------------------
# event mgr
#------------------------------------------------------------
class EventMgr:
    def __init__(self):
        self.map = {}

    def add(self, name, handler):
        if not name in self.map:
            self.map[name] = [handler]
        else:
            self.map[name].append(handler)

    def remove(self, name, handler):
        if name in self.map:
            self.map[name].remove(handler)

    def emit(self, name, *args, **kwargs):
        if name in self.map:
            for handler in self.map[name]:
                handler.__call__(*args, **kwargs)

# 这里尽量保持空依赖，在别的地方往这里塞
# 这样，game_mgr就能在别的地方被随意引用了
# 主要是模块这种机制，是不让循环引用的。因为他有toplevel语句
# 相比之下Delphi的Unit，是可以循环引用的。java，c#的引用的话,两个包是可以互相引用的。

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

        self.update_list = []

        # 游戏数据管理
        self.game_data = None

        # 时间和帧数信息, time -> ms, sec_time -> s
        self.time = 0
        self.sec_time = 0
        self.delta_time = 0
        self.frame_number = 0
        self.paused = False
        self.game_time = 0

    @property
    def event_mgr(self):
        return self._event_mgr

    @property
    def input_mgr(self):
        return self._input_mgr

    def on_frame(self):
        # coroutine first
        self.co_mgr.execute()

        # update all system
        delta_time = self.delta_time
        self.game_time += delta_time

        for cb in self.update_list:
            cb(delta_time)

    def init_update_list(self):
        self.update_list = []
        
        self.update_list.append(self.input_mgr.update)
        self.update_list.append(self.game_play.update)
        self.update_list.append(self.effect_mgr.update)
        self.update_list.append(self.game_play.update)
        self.update_list.append(self.ui_mgr.update)
        self.update_list.append(self.ground_mgr.update)
        self.update_list.append(self.unit_mgr.update)

game_mgr = GameMgr()

def get_game_mgr():
    return game_mgr


