#
# 2023年1月31日 bianpeng
#

# 这里尽量保持空依赖，在别的地方往这里塞
# 这样，game_mgr就能在别的地方被随意引用了
# 主要是模块这种机制，是不让循环引用的。因为他有toplevel语句
# 相比之下Delphi的Unit，是可以循环引用的。java，c#的引用的话,两个包是可以互相引用的。

from game.core import *

#
# 总管理器
#
class GameMgr():
    def __init__(self):
        super().__init__()
        
        # 游戏路径
        self.game_path = log_util.game_path
        # 场景的根节点
        self.scene_root_obj = None
        
        # 底层管理器
        from game.event_mgr import EventMgr
        self._event_mgr = EventMgr()
        from game.coroutine_mgr import CoroutineMgr
        self._coroutine_mgr = CoroutineMgr()
        self._input_mgr = None
        
        # 上层管理器
        self.camera_mgr = None
        self.ground_mgr = None
        self.troop_mgr = None
        self.unit_mgr = None
        self.ui_mgr = None
        self.hero_mgr = None
        self.effect_mgr = None
        self.hud_mgr = None
        self.skill_mgr = None
        
        # 玩法业务逻辑
        self.game_play = None
        
        # update的列表
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
        
        # 城市AI
        self.enable_city_ai = False

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
        # 这里的顺序的原则, 消息生产者在前, 消息处理者在后
        self.update_list = [
            self.input_mgr.update,
            
            self.game_play.update,
            self.player_mgr.update,
            self.unit_mgr.update,
            self.hero_mgr.update,
            self.skill_mgr.update,
            
            self.ground_mgr.update,
            self.ui_mgr.update,
            
            self.effect_mgr.update,
            self.camera_mgr.update,
            self.hud_mgr.update,
        ]

    # 判断是否同盟
    def is_league(self, unit_a, unit_b):
        # TODO: 如果是同盟
        return unit_a.owner_player_id == unit_b.owner_player_id

    # 得到一个带颜色的名字
    def get_unit_name_label(self, unit):
        fmt = '[color={0}]{1}[/color]'
        color = ''
        if unit.owner_player_id == 0:
            color = 'white'
        elif unit.owner_player_id == get_main_player_id():
            color = 'green'
        else:
            color = 'red'

        return fmt.format(color, unit.unit_name)

game_mgr = GameMgr()

# 一些简化工具方法

def get_player(player_id):
    return game_mgr.player_mgr.get_player(player_id)

def get_player_name(player_id):
    if player_id > 0:
        p = get_player(player_id)
        return p.player_name
    return ''

def get_main_player():
    return game_mgr.player_mgr.main_player

def get_main_player_id():
    return game_mgr.player_mgr.main_player_id

def get_main_camera():
    return game_mgr.camera_mgr.main_camera

# 
def check_owner(unit, player):
    return unit.owner_player_id == player.player_id

def check_main_owner(unit):
    return unit.owner_player_id == get_main_player_id()
    
#
# 鼠标位置, raycast到地面的世界坐标
#
def get_cursor_position():
    camera = get_main_camera()
    screen_xy = game_mgr.input_mgr.get_mouse_pos()
    return camera.screen_to_world(*screen_xy)

def get_hero(hero_id):
    if hero_id > 0:
        return game_mgr.hero_mgr.get_hero(hero_id)

def get_hero_name(hero_id):
    hero = get_hero(hero_id)
    return hero.hero_name if hero else ''

def get_unit(unit_id):
    if unit_id > 0:
        return game_mgr.unit_mgr.get_unit(unit_id)

def get_unit_name(unit_id):
    unit = get_unit(unit_id)
    return unit.unit_name if unit else ''

def get_effect_config(config_id):
    return game_mgr.config_mgr.get_effect(config_id)

def get_skill_config(config_id):
    return game_mgr.config_mgr.get_skill(config_id)

def first(item_list, predicate):
    for item in item_list:
        if predicate(item):
            return item

__all__ = [
    'game_mgr',
    'get_main_player',
    'get_main_player_id',
    'get_main_camera',
    'get_cursor_position',
    'get_player',
    'get_player_name',
    'get_hero',
    'get_hero_name',
    'get_unit',
    'get_unit_name',
    'get_effect_config',
    'get_skill_config',
    'check_owner',
    'check_main_owner',
    'first',
]


