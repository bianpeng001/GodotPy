#
# 2023年2月9日 bianpeng
#

MALE = 1
FEMAIL = 0

class Hero:
    def __init__(self):
        self.hero_id = 0

        self.name = ''
        self.gender = MALE

        self.born_year = 0
        self.dead_year = 0

    def get_age(self):
        return 

class HeroMgr:
    def __init__(self):
        self.hero_dict = {}
        self.hero_id_seed = 1000

    def new_hero(self):
        self.hero_id_seed += 1

        hero = Hero()
        hero.hero_id = self.hero_id_seed
        self.hero_dict[hero.hero_id] = hero

        return hero


