#
# 2023年2月9日 bianpeng
#

# 游戏存档
class GameData:
    def __init__(self):
        self.start_year = 160
        self.play_time = 0
        
        self.cur_year = 181
        self.cur_month = 1

        self.player_list = []
        self.hero_list = []
        self.city_list = []

    def load(self, path):
        pass

    def save(self, path):
        pass

    def get_cur_year(self):
        return self.start_year + int(self.play_time / (86400*365))
