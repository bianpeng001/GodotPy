#
# 2023年2月9日 bianpeng
#

from game.core import *
from game.game_mgr import *

# Hero 是纯数据Entity，不存在实体

# 性别
FEMAIL = 0
MALE = 1

# attrs [0, 100]
# 忠义，智力，武力，统率，政治，魅力，敏捷, 野心
ATTR_ZHONG = 0
ATTR_ZHI = 1
ATTR_WU = 2
ATTR_TONG = 3
ATTR_ZHENG = 4
ATTR_MEI = 5
ATTR_MIN = 6
ATTR_YEXIN = 7 

MAX = 8

# tags 部分武将拥有特殊属性

# 武圣，单挑无敌
TAG_WU_SHENG = 0

# 雄心壮志（决定称帝）
TAG_DA_ZHI = 1

# 酒色财气
TAG_JIU = 2
TAG_SE = 3
TAG_CAI = 4
TAG_QI = 5

# 莽夫
TAG_MANG = 6
# 修真
TAG_XIU_ZHEN = 7
# 隐忍
TAG_YIN_REN = 8
# 反骨
TAG_FAN_GU = 9

# 好运
TAG_LUCKY = 10
# 好运
TAG_UNLUCKY = 11

# 健康状态
JK_HEALTH = 0
JK_INJURED = 1
JK_DEAD = 2


# 活动

# 空闲
ACT_IDLE = 0
# 内政
ACT_NEIZHENG = 1
# 出战
ACT_CHUZHAN = 2
# 受伤
ACT_SHOUSHANG = 3
# 旅途
ACT_TRAVEL = 4

#
# 英雄(逻辑单位，没有实体)
# TODO: 还要搞一个3D的捏脸数据，用来区分一下形象
#
class Hero:
    def __init__(self):
        self.hero_id = 0
        self.hero_name = ''
        self.gender = MALE
        
        # 主公
        self.owner_player_id = 0

        # 生卒年份
        self.born_year = 0
        self.dead_year = 0

        # 头像
        self.avatar = 0

        # 父母
        self.father_id = 0
        self.mother_id = 0

        # 配偶
        self.spouse_id = 0

        # 人物属性: 德智武
        self.attr = [ 0 for i in range(MAX) ]
        self.tags = []

        # 老病残孕
        self.health = JK_HEALTH

        # 这个要用来做控制了,不能同时做两件事情
        # 军队，内政(政,农,商..)，空闲
        self.activity = 0
        self.activity_time = 0

        # 行动力
        self.action_points = 80

        # 所在城市id
        self.city_id = 0
        self.troop_id = 0
        
        # 人物传记, 就是要记录个人的一些关键节点
        self.biography = []
        
    def get_age(self):
        return game_mgr.game_data.cur_year - self.born_year + 1

    def set_age(self, age):
        self.born_year = game_mgr.game_data.cur_year - age + 1

    @property
    def age(self):
        return self.get_age()

    def get_attr(self, attr_type):
        return self.attr[attr_type]

    def has_tag(self, tag_type):
        return tag_type in self.tags

    @property
    def wuli(self):
        return self.get_attr(ATTR_WU)

    @property
    def zhili(self):
        return self.get_attr(ATTR_ZHI)

    @property
    def zhengzhi(self):
        return self.get_attr(ATTR_ZHENG)

    @property
    def tongshuai(self):
        return self.get_attr(ATTR_TONG)

    @property
    def meili(self):
        return self.get_attr(ATTR_MEI)
    
#
# 武将管理器，所有的武将都在这里，就像一个数据库
#
class HeroMgr:
    def __init__(self):
        self.hero_dict = {}
        self.hero_id_seed = 1000

        # 武将活动, 比如移动,啥的,是需要时间的
        self.hero_activity_list = []
        self.back_hero_activity_list = []

    # 支持随机英雄和经典英雄
    def new_hero(self):
        hero = Hero()

        self.hero_id_seed += 1
        hero.hero_id = self.hero_id_seed
        self.hero_dict[hero.hero_id] = hero

        # 随机一个属性出来
        for i in range(len(hero.attr)):
            hero.attr[i] = random_int(10, 75)
        remain_points = 100
        for i in range(len(hero.attr)):
            if remain_points <= 0:
                break
            else:
                v = random_int(0, 89 - hero.attr[i])
                if v > remain_points:
                    v = remain_points
                hero.attr[i] += v
                remain_points -= v

        # 这种随机产生的英雄,得分不能太高了,
        # 经典英雄,才有牛逼的数值

        hero.hero_name = f'武将_{hero.hero_id}'

        cur_year = game_mgr.game_data.cur_year
        hero.born_year = cur_year - random_int(12, 40)
        # 命中注定的寿命，通过一些事件会发生改变
        hero.dead_year = hero.born_year + random_int(50, 100)

        return hero

    def get_hero(self, hero_id):
        return self.hero_dict.get(hero_id, None)

    # 英雄当前的活动, 安全调用, 判断是否存在
    def set_hero_activity(self, hero_id, activity, duration = 0):
        if hero_id != 0:
            hero = self.get_hero(hero_id)
            hero.activity = activity
            hero.activity_time = duration
    
    # 这个英雄是否是主公?
    def is_main_hero(self, hero_id):
        hero = self.get_hero(hero_id)
        player = game_mgr.player_mgr.get_player(hero.owner_player_id)
        return hero.hero_id == player.main_hero_id
    
    # 刷新武将的活动
    def update_activity(self, hero, delta_time):
        if hero.activity != ACT_IDLE:
            if hero.activity_time > 0:
                hero.activity_time -= delta_time
                if hero.activity_time <= 0:
                    hero.activity = ACT_IDLE
                    
    def update(self, delta_time):
        for hero in self.hero_dict.values():
            self.update_activity(hero, delta_time)

if __name__ == '__main__':
    import json

    def encode_hero(obj):
        if isinstance(obj, Hero):
            return (obj.hero_id, obj.hero_name, obj.gender, obj.born_year)
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

