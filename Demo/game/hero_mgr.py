#
# 2023年2月9日 bianpeng
#

from game.game_mgr import game_mgr

# Hero在都是纯数据，不存在实体

MALE = 1
FEMAIL = 0

# 忠诚，智力，武力，魅力，政治
ZHONG = 0
ZHI = 1
WU = 2
MEI = 3
ZHENG = 4
# 打tag，比如大志，单挑...，以应对一些特殊的行为


#
class Hero:
    def __init__(self):
        self.hero_id = 0

        self.hero_name = ''
        self.gender = MALE

        self.born_year = 0
        self.dead_year = 0

        # 人物属性: 德智武
        self.attr = [
            80,
            80,
            80,
            80,
            80,
        ]
        self.tag = []

        # 所在城市id
        self.city_id = 0
        self.troop_id = 0
        # 主公
        self.owner_player_id = 0
        

    def get_age(self):
        return game_mgr.game_data.cur_year - self.born_year + 1

#
class HeroMgr:
    def __init__(self):
        self.hero_dict = {}
        self.hero_id_seed = 1000

    def new_hero(self):
        self.hero_id_seed += 1

        hero = Hero()
        
        hero.hero_id = self.hero_id_seed
        self.hero_dict[hero.hero_id] = hero

        hero.hero_name = f'武将_{hero.hero_id}'

        return hero

    def get_hero(self, hero_id):
        return self.hero_dict.get(hero_id, None)

    

if __name__ == '__main__':
    import json

    def encode_hero(obj):
        if isinstance(obj, Hero):
            return (obj.hero_id, obj.hero_name, obj.gender,
                obj.born_year)
        else:
            return obj

    a = Hero()
    a.hero_name = 'jerry'
    a.hero_id = 100
    a.born_year = 101
    s = json.dumps(a, default=encode_hero)
    print(s)

    def decode_hero(data):
        obj = Hero()
        (obj.hero_id, obj.name, obj.gender,\
                obj.born_year) = data
        return obj

    b = decode_hero(json.loads(s))
    print(b)
