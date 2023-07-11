#
# 2023年2月4日 bianpeng
#

import math

from game.core import log_debug, hsv_to_rgb
from game.game_mgr import *
from game.player_ai import *

#
# 玩家的控制器, ai驱动器
#
class PlayerController:
    def __init__(self, player):
        self.player = player
        
        self.brain_comp = PlayerBrainComponent()
        self.brain_comp.setup(self)
        self.init_ai()
        
    def init_ai(self):
        brain_comp = self.get_brain_comp()
        brain_comp.blackboard = PlayerBlackboard()
        
        brain_comp.add_state('start', AIState_PlayerStart())
        brain_comp.add_state('develop', AIState_PlayerDevelop())
        
        brain_comp.goto_state('start')
    
    def get_brain_comp(self):
        return self.brain_comp
    
    def get_player(self):
        return self.player
    
    def update(self, delta_time):
        if self.get_brain_comp().enabled:
            self.get_brain_comp().update(delta_time)

#
# 一个玩家
#
class Player:
    def __init__(self):
        self.player_id = 0
        
        self.player_name = '刘备'
        self.first_name = '刘'
        
        # 资产列表, 城池,武将, 以及军队
        self.city_list = []
        self.hero_list = []
        self.troop_list = []
        
        # 主城, 治所
        self.main_city_id = 0
        # 玩家对应的英雄
        self.main_hero_id = 0
        
        # 资源总数
        self.total_rice_amount = 0
        self.total_iron_amount = 0
        self.total_stone_amount = 0
        self.total_wood_amount = 0
        self.total_money_amount = 0
        
        # 旗帜的颜色
        self.flag_color = (1,1,1)
        self.flag_mat = None
        self.troop_flag_mat = None
        
        # 控制器, AI等
        self._controller = PlayerController(self)

    def get_controller(self):
        return self._controller
        
    def get_main_hero(self):
        return game_mgr.hero_mgr.get_hero(self.main_hero_id)
    
    def on_leave_scene(self):
        self.flag_mat = None

    def load(self):
        pass

    def save(self):
        pass

#
# 玩家管理器
#
class PlayerMgr:
    def __init__(self):
        self.player_dict = {}
        self.next_player_id = 10000
        
        self.update_list = []
        
        self.main_player = None
        self.main_player_id = 0
        
    def new_player(self):
        self.next_player_id += 1
        
        player = Player()
        player.player_id = self.next_player_id
        self.player_dict[player.player_id] = player
        self.update_list.append(player.get_controller())

        h,_ = math.modf(((player.player_id - 10000)*30) / 360)
        player.flag_color = hsv_to_rgb(
            h,
            0.7 + 0.2*random_1(),
            0.7 + 0.3*random_1())
        
        return player
    
    def set_main_player(self, player):
        self.main_player = player
        self.main_player_id = player.player_id
        player.get_controller().get_brain_comp().enabled = False

    def get_player(self, player_id):
        player = self.player_dict.get(player_id, None)
        if not player:
            log_debug(f'player not found: {player_id}')
            return None
        
        return player

    def loop_players(self):
        return self.player_dict.values()
    
    def update(self, delta_time):
        for controller in self.update_list:
            controller.update(delta_time)




