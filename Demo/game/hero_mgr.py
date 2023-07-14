#
# 2023年2月9日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import RangeValue
from game.config_mgr import new_hero_name

# Hero 是纯数据Entity，不存在实体

# 性别
FEMAIL = 0
MALE = 1

# attrs [0, 100]
# 忠义，智力，武力，统率，政治，魅力，敏捷, 野望
ATTR_ZHONG = 0
ATTR_ZHI = 1
ATTR_WU = 2
ATTR_TONG = 3
ATTR_ZHENG = 4
ATTR_MEI = 5
ATTR_MIN = 6
ATTR_YEXIN = 7

ATTR_MAX = 8
attr_alias = {
    "wu": ATTR_WU,
    "zhi": ATTR_ZHI,
}

# tags 部分武将拥有特殊属性

# 的卢的卢, 今日妨吾; 的卢的卢, 檀溪救主.
TAG_DILU = 0

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

# 好运, 成功率*10
TAG_LUCKY = 10
# 霉运, 三国拉姆. 成功率*0.1
TAG_UNLUCKY = 11

# 武圣，单挑无敌
TAG_WU_SHENG = 12

# 健康状态
JK_HEALTH = 0
JK_INJURED = 1
JK_DEAD = 2

# 活动

# 空闲
ACT_IDLE = 3001
# 旅途, 寻访
ACT_TRAVEL = 3002
# 探亲
ACT_TANQIN = 3003
# 出战
ACT_CHUZHAN = 3004
# 受伤
ACT_SHOUSHANG = 3005

#
# 一个活动项
#
class ActivityItem:
    def __init__(self):
        self.config_id = 0
        self.start_time = 0
        self.finish_time = 0
        self.infinite = False


#
# 英雄(逻辑单位，没有实体)
# TODO: 还要搞一个3D的捏脸数据，用来区分一下形象
#
class Hero:
    def __init__(self):
        self.hero_id = 0
        
        # 姓名
        self.hero_name = ''
        # 字
        self.long_name = ''

        # 主公
        self.owner_player_id = 0
        self.owner_city_id = 0

        # 性别
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
        self.spouse_id = 0

        # 人物属性: 德智武
        self.attr = [ 0 for i in range(ATTR_MAX) ]
        self.tags = []

        # 老病残孕
        self.health = JK_HEALTH

        # 这个要用来做控制了,不能同时做两件事情
        # 军队，内政(政,农,商..)，空闲
        self.activity = None

        # 行动力, 体力
        self.ap = RangeValue(100, 100, 0)
        
        # 人物传记, 就是要记录个人的一些关键节点
        self.biography = []
        
    def get_age(self):
        return game_mgr.game_data.cur_year - self.born_year + 1

    def set_age(self, age:int):
        self.born_year = game_mgr.game_data.cur_year - age + 1

    @property
    def age(self):
        return self.get_age()

    @property
    def wu(self):
        return self.get_attr(ATTR_WU)

    @property
    def zhi(self):
        return self.get_attr(ATTR_ZHI)

    @property
    def zheng(self):
        return self.get_attr(ATTR_ZHENG)

    @property
    def tong(self):
        return self.get_attr(ATTR_TONG)

    @property
    def mei(self):
        return self.get_attr(ATTR_MEI)

    def get_attr(self, attr_type):
        return self.attr[attr_type]

    def has_tag(self, tag_type):
        return tag_type in self.tags

    def set_attr(self, attr_type, value):
        self.attr[attr_type] = value
    
    def init_attrs(self, *args, **kw_args):
        for k in kw_args:
            self.set_attr(attr_alias[k], kw_args[k])

#
# 武将管理器，所有的武将都在这里，就像一个数据库
#
class HeroMgr:
    def __init__(self):
        self.next_hero_id = 1000
        self.hero_dict = {}

        # 用于控制英雄不重名,但目前也没有更多的限制
        self.hero_name_set = set()

        self.init_big_heros()

    # 定义经典英雄, 这些英雄, 才是最牛逼的
    def init_big_heros(self):
        self.big_hero_list = []

        def create(hero_name):
            hero = Hero()
            for i in range(ATTR_MAX):
                hero.attr[i] = random_range(10, 50)
            self.rename_hero(hero_name, hero)
            self.big_hero_list.append(hero)

            return hero
        
        hero = create('刘备')
        hero = create('关羽')
        hero = create('张飞')
        hero = create('赵云')
        hero.init_attrs(wu=98,zhi=81)
        hero = create('马超')
        hero = create('黄忠')
        hero = create('诸葛亮')
        hero = create('庞统')
        hero = create('法正')
        hero = create('徐庶')
        hero = create('魏延')
        hero = create('姜维')
        hero = create('马岱')
        hero = create('刘禅')

        hero = create('曹操')
        hero = create('夏侯惇')
        hero = create('夏侯渊')
        hero = create('曹仁')
        hero = create('曹洪')
        hero = create('张辽')
        hero = create('许褚')
        hero = create('典韦')
        hero = create('于禁')
        hero = create('徐晃')
        hero = create('乐进')
        hero = create('李典')
        hero = create('贾诩')
        hero = create('荀彧')
        hero = create('荀攸')
        hero = create('程昱')
        hero = create('许攸')
        hero = create('郭嘉')

        hero = create('孙策')
        hero = create('孙权')
        hero = create('周瑜')
        hero = create('鲁肃')
        hero = create('吕蒙')
        hero = create('陆逊')
        hero = create('陆抗')
        hero = create('甘宁')
        hero = create('周泰')
        hero = create('黄盖')
        hero = create('程普')
        hero = create('太史慈')
        hero = create('诸葛瑾')

        hero = create('董卓')
        hero = create('吕布')
        hero = create('华雄')
        hero = create('郭汜')
        hero = create('李儒')

        hero = create('公孙瓒')
        
        hero = create('袁绍')
        hero = create('颜良')
        hero = create('文丑')
        hero = create('田丰')
        hero = create('沮授')

        hero = create('刘表')
        hero = create('张绣')
        hero = create('韩遂')
        hero = create('张鲁')
        hero = create('刘璋')

        hero = create('张良')
        hero = create('韩信')
        hero = create('萧何')

        hero = create('西施')
        hero = create('王昭君')
        hero = create('貂蝉')
        hero = create('赵飞燕')
        hero = create('杨玉环')
        hero = create('吕雉')


    # 支持随机英雄和经典英雄
    def new_hero(self, hero_name=None):
        hero = Hero()

        self.next_hero_id += 1
        hero.hero_id = self.next_hero_id
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

        # 随机一个唯一名字
        hero.hero_name = self.gen_unique_hero_name()

        cur_year = game_mgr.game_data.cur_year
        hero.born_year = cur_year - random_int(12, 40)
        # 命中注定的寿命，通过一些事件会发生改变
        hero.dead_year = hero.born_year + random_int(50, 100)

        return hero

    def get_hero(self, hero_id):
        return self.hero_dict.get(hero_id, None)

    def loop_heros(self):
        for hero_id in self.hero_dict:
            yield self.hero_dict[hero_id]
    
    # 这个英雄是否是主公?
    def is_main_hero(self, hero_id: int):
        hero = self.get_hero(hero_id)
        player = game_mgr.player_mgr.get_player(hero.owner_player_id)
        return hero.hero_id == player.main_hero_id
    
    #--------------------------------------------------------------
    # region of hero activity

    # 英雄当前的活动, 安全调用, 判断是否存在
    def set_hero_activity(self, hero_id:int, config_id:int):
        assert hero_id > 0
        
        cfg = game_mgr.config_mgr.get_activity_config(config_id)
        
        item = ActivityItem()
        item.config_id = config_id
        item.start_time = game_mgr.time_sec
        item.infinite = cfg.infinite
        item.finish_time = 0 if cfg.infinite else game_mgr.time_sec + cfg.duration
        item.title = cfg.title

        hero = self.get_hero(hero_id)
        hero.activity = item
    
    # 刷新武将的活动
    def update_hero_activity(self, hero):
        item = hero.activity
        if item and \
                not item.infinite and \
                game_mgr.time_sec > item.finish_time:
            hero.activity = None

    def is_hero_busy(self, hero):
        return hero.activity != None or hero.ap.value < 10

    def get_hero_activity_title(self, hero):
        item = hero.activity
        cfg = game_mgr.config_mgr.get_activity_config(
                item.config_id if item else ACT_IDLE)
        return cfg.title, cfg.color

    # region end
    #--------------------------------------------------------------

    #--------------------------------------------------------------
    # region 英雄不重名的控制
    
    def gen_unique_hero_name(self):
        while True:
            hero_name = new_hero_name()
            if hero_name not in self.hero_name_set:
                self.hero_name_set.add(hero_name)
                return hero_name

    def rename_hero(self, new_name, hero=None):
        self.hero_name_set.add(new_name)

        if hero:
            if hero.hero_name and hero.hero_name in self.hero_name_set:
                self.hero_name_set.remove(hero.hero_name)
            hero.hero_name = new_name

    # region end
    #--------------------------------------------------------------

    # 逻辑帧
    def update(self, delta_time):
        for hero in self.hero_dict.values():
            self.update_hero_activity(hero)

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


