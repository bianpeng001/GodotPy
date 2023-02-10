#
# 2023年2月4日 bianpeng
#

# 一个玩家
class Player:
    def __init__(self):
        self.player_id = 0
        self.player_name = '刘备'

        self.city_list = []
        self.troop_list = []
        # 主城
        self.base_city_id = 0

    def load(self):
        pass

    def save(self):
        pass

# 玩家管理器
class PlayerMgr:
    def __init__(self):
        self.player_dict = {}
        self.player_id_seed = 100

        self.main_player = None

    @property
    def main_player_id(self):
        return self.main_player.player_id

    def create_player(self):
        p = Player()

        self.player_id_seed += 1
        p.player_id = self.player_id_seed

        self.player_dict[p.player_id] = p
        return p

    def get_player(self, player_id):
        return self.player_dict[player_id]


