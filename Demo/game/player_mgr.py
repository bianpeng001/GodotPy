#
# 2023年2月4日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.player_ai import PlayerAIComponent

#
# 一个玩家
#
class Player:
    def __init__(self):
        self.player_id = 0
        self.player_name = '刘备'

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
        self.next_player_id = 100

        self.main_player = None
        
        self.update_list = []

    @property
    def main_player_id(self):
        return self.main_player.player_id

    def new_player(self):
        player = Player()

        self.next_player_id += 1
        player.player_id = self.next_player_id
        self.player_dict[player.player_id] = player
        
        return player

    def get_player(self, player_id):
        player = self.player_dict.get(player_id, None)
        if not player:
            log_debug(f'player not found: {player_id}')
            return None
        
        return player

    def loop_player(self):
        return self.player_dict.values()
    
    def update(self, delta_time):
        for player in self.update_list:
            player.update(self, delta_time)
            



