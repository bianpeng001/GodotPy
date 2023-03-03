#
# 2023年1月31日 bianpeng
#

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
        from game.event_mgr import EventMgr
        self._event_mgr = EventMgr()
        from game.coroutine_mgr import CoroutineMgr
        self._coroutine_mgr = CoroutineMgr()

        # 上层管理器
        self._input_mgr = None
        self.camera_mgr = None
        self.ground_mgr = None
        self.troop_mgr = None
        self.unit_mgr = None
        self.ui_mgr = None
        self.hero_mgr = None
        self.effect_mgr = None
        self.hud_mgr = None

        # 场景的根节点
        self.scene_root_obj = None

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
        self.play_time = 0

    @property
    def event_mgr(self):
        return self._event_mgr

    @property
    def input_mgr(self):
        return self._input_mgr

    @property
    def co_mgr(self):
        return self._coroutine_mgr

    def update(self):
        # coroutine first
        self._coroutine_mgr.update()

        delta_time = self.delta_time
        self.play_time += delta_time

        # update all system
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
        self.update_list.append(self.hud_mgr.update)

game_mgr = GameMgr()

# 角色单位的共享实现
class UnitTrait:
    def owner_is_main_player(self):
        return self.owner_player_id == get_main_player_id()

# 一些简化工具方法

def get_main_player():
    return game_mgr.player_mgr.main_player

def get_main_player_id():
    return game_mgr.player_mgr.main_player_id

def get_main_camera():
    return game_mgr.camera_mgr.main_camera

def get_hero_name(hero_id):
    if hero_id == 0:
        return ''
    hero = game_mgr.hero_mgr.get_hero(hero_id)
    if not hero:
        return ''

    return hero.hero_name
    
def get_hero(hero_id):
    if hero_id == 0:
        return None
    hero = game_mgr.hero_mgr.get_hero(hero_id)

    return hero

