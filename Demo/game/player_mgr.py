#
# 2023年2月4日 bianpeng
#

class Player:
    def __init__(self):
        self.player_id = None
        self.name = '刘备'

    def load(self):
        pass

    def save(self):
        pass

#
class PlayerMgr:
    def __init__(self):
        self.player_dict = {}
        self.player_id_seed = 10000

    def create_player(self):
        p = Player()

        self.player_id_seed += 1
        p.player_id = self.player_id_seed

        self.player_dict[p.player_id] = p
        return p

    def get_player(self, player_id):
        return self.player_dict[player_id]



