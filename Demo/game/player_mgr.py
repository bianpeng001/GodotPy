#
# 2023年2月4日 bianpeng
#

from game.core import log_debug, hsv_to_rgb
from game.game_mgr import *
from game.player_ai import PlayerAIComponent

#
# 一个玩家
#
class Player:
    def __init__(self):
        self.player_id = 0
        self.player_name = '刘备'
        self.first_name = '刘'

        self.city_list = []
        self.troop_list = []
        self.hero_list = []
        
        # 主城
        self.main_city_id = 0
        # 自己的英雄本体
        self.main_hero_id = 0
        
        # 旗帜的颜色
        self.flag_color = (1,1,1)
        self.flag_mat = None

        # 资源总数
        self.total_rice_amount = 0
        self.total_iron_amount = 0
        self.total_stone_amount = 0
        self.total_wood_amount = 0
        self.total_money_amount = 0
        
        # ai 组件
        self.ai_comp = PlayerAIComponent(self)

    def get_ai_comp(self):
        return self.ai_comp
        
    def get_main_hero(self):
        return game_mgr.hero_mgr.get_hero(self.main_hero_id)
    
    def on_leave_scene(self):
        self.flag_mat = None

    def load(self):
        pass

    def save(self):
        pass
    
    def update(self, delta_time):
        if self.get_ai_comp().enabled:
            self.get_ai_comp().update(delta_time)
            
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
        player = Player()
        
        self.next_player_id += 1
        player.player_id = self.next_player_id
        self.player_dict[player.player_id] = player
        self.update_list.append(player)

        player.flag_color = hsv_to_rgb((player.player_id - 10000)*30/360,
            0.7, 1)
        
        return player
    
    def set_main_player(self, player):
        self.main_player = player
        self.main_player_id = player.player_id
        player.get_ai_comp().enabled = False

    def get_player(self, player_id):
        player = self.player_dict.get(player_id, None)
        if not player:
            log_debug(f'player not found: {player_id}')
            return None
        
        return player

    def loop_players(self):
        return self.player_dict.values()
    
    def update(self, delta_time):
        for player in self.update_list:
            player.update(delta_time)




