#
# 2023年2月9日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

# Hero在都是纯数据，不存在实体

MALE = 1
FEMAIL = 0

# attrs [0, 100]
# 忠义，智力，武力，魅力，政治
ATTR_ZHONG = 0
ATTR_ZHI = 1
ATTR_WU = 2
ATTR_MEI = 3
ATTR_ZHENG = 4

MAX = 8

# tags

# 雄心壮志（决定称帝）
TAG_DAZHI = 1
# 酒色财气
TAG_JIU = 2
TAG_SE = 3
TAG_CAI = 4
TAG_QI = 5
TAG_MANGZHUANG = 6

#
# 英雄(逻辑单位，没有实体)
# TODO: 还要搞一个3D的捏脸数据，用来区分一下形象
#
class Hero:
    def __init__(self):
        self.hero_id = 0
        self.hero_name = ''
        self.gender = MALE

        # 生卒年份
        self.born_year = 0
        self.dead_year = 0

        # 头像
        self.avatar = 0

        # 父母
        self.father_id = 0
        self.mother_id = 0

        # 配偶
        self.spouse = 0

        # 人物属性: 德智武
        self.attr = [ 0 for i in range(MAX) ]
        self.tags = []

        # 老病残孕
        self.health = 0
        # 军队，内政(政,农,商..)，空闲
        self.state = 0

        # 所在城市id
        self.city_id = 0
        self.troop_id = 0
        # 主公
        self.owner_player_id = 0
        
    def get_age(self):
        return game_mgr.game_data.cur_year - self.born_year + 1

    def get_attr(self, attr_type):
        return self.attr[attr_type]

    def has_tag(self, tag_type):
        return tag_type in self.tags

#
# 武将管理器，所有的武将都在这里，就像一个数据库
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

        for i in range(len(hero.attr)):
            hero.attr[i] = random_int(10, 100)

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

