#
# 2023年1月31日 bianpeng
#

import math
import random

from game.core import *

#
#
#
class BaseConfig:
    def __init__(self):
        self.config_id = 0
        self.config_name = ''

class AnimConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        self.anim_name = ''
        self.anim_speed_scale = 1.0

class CityConfig(BaseConfig):
    def __init__(self):
        super().__init__()

class HeroConfig(BaseConfig):
    def __init__(self):
        super().__init__()

class EffectConfig(BaseConfig):
    def __init__(self):
        self.life_time = 1.0
        #self.rpath = 'res://effects/Shoot01.tscn'
        self.res_path = ''

class DialogConfig(BaseConfig):
    def __init__(self):
        pass

#
# 回目, 章节
#
class ChapterConfig(BaseConfig):
    def __init__(self):
        self.num = 1
        self.title = ''
        self.script = []

#
# 剧情
#
class StoryConfig(BaseConfig):
    def __init__(self):
        self.start_game_story = [
            '某朝某年, 某不第书生山中遇南华老仙, 得授天书习得符法, 治病救人',
            '因聚集民众, 高举义旗, 几年后终于被击败',
            '昔日的帝国千疮百孔, 四方豪杰蠢蠢欲动',
            '这几年你出生入死, 颇有军功, 该何去何从',
        ]
        
#
# 技能, 一个state
# 一次结算, 技能伤害, 需要一个公式, 这里配一个基础伤害
#
class SkillConfig(BaseConfig):
    def __init__(self):
        self.damage = 10

#
# 物品配置
#
class ItemConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.item_name = ''
        self.desc = ''
        # 是否唯一
        self.item_count = 1

#
# 奖励, 物品的id,数量,胜率
#
class RewardConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.item_id = 0
        self.item_count = 1
        self.win_rate = 1

#
# 活动配置
#
class ActivityConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.duration = 0
        self.infinite = False
        self.title = ''
        self.rewards = []
        self.color =  (1.0,1.0,1.0)

#
# 奖品
#
class RewardConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0


#
# 兵种的配置, 相克
#
class ArmyTypeConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.name = ''

        # 消耗, 维持这个部队, 的基础消耗, 距离本城的距离有关
        self.supply = 1
        # 攻击距离
        self.attack_range = 1
        # 视野距离
        self.vision_range = 1
        # 伤害
        self.damage = 2
        # 防御
        self.defense = 1
        # 行军速度
        self.speed = 0.5

ARMY_TYPE_SIZE = 10

#
# 阵型
#
class ArmyFormConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.name = ''
        self.speed = 0.5
        self.damage = 1
        self.defense = 1

ARMY_FORM_SIZE = 10

#
# 熟练度: 龙虎狮象熊豹鹰狼
#
class ArmyMasteryConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.name = ''

ARMY_MASTERY_SIZE = 8


#
# 官爵, 用汉朝官爵
#
class RankConfig(BaseConfig):
    def __init__(self):
        self.config_id = 0
        self.name = ''

RANK_SIZE = 12

#
# 配置管理器
#
class ConfigMgr:
    def __init__(self):
        
        # 标题栏
        # 猛男传,豪杰志,
        # 何谓豪杰? 生而鸡狗, 屠龙灭凤, 以天道无私, 生生不息.
        # 生而龙凤, 屠鸡灭狗, 不值一笑.
        # 邓艾: 出身寒微不是耻辱，能屈能伸方为丈夫
        self.app_title = '豪杰是怎样练成的'
        
        # 光标资源
        self.default_cursor = 'res://DefaultCursor.png'
        self.drag_cursor = 'res://DragCursor.png'
        
        # 太守的发言
        self.neizheng_strap_dialog_list = [
            '为政之道，务于多闻。', 
            '兵卒有制，虽庸将未败。',
            '吾心如称，不能为人作轻重。',
            '以弱为强者，非惟天时，抑亦人谋也。',
            '国之大务，莫先于戒备。',
            '主公不必多虑。',
            '大丈夫岂郁郁久居人下。',
        ]

        # 游戏时长跟现实时长的单位转换, 用来更新游戏内日历
        self.play_time_scale = 1000
        
        self.story = StoryConfig()
        # 剧情
        self.init_story_config()
        # 章节
        self.init_chapter_config()
        # 特效
        self.init_effect_config()
        # 技能
        self.init_skill_config()
        # 活动
        self.init_activity_config()
        # 奖励和物品
        self.init_reward_config()
        # 阵型
        self.init_army_form_config()
        # 兵种, 兵种熟练度
        self.init_army_type_config()
        # 爵位
        self.init_rank_config()
                
        # rvo 参数
        self.rvo_factor = 90
        # rvo 斥力半径, 之外是不提供斥力的, 是距离**2
        self.rvo_sqrdis = 7*7

        # 进入视野, 失去视野
        self.sight_sqrdis = 6*6
        self.lose_sight_sqrdis = 8*8

        self.city_sight_sqrdis = 8*8
        self.city_lose_sight_sqrdis = 10*10
        
        # 单位秒, 每帧的时长, 有时候用固定值就挺好的
        self.frame_seconds = 1.0/60
        # 军队移动的速度的倍速, 全局缩放
        self.troop_speed_scale = 2
        
        # 修正走路卡主的参数
        
        # 行军过程里block住, 停了n帧不动, 则开始转转弯
        self.start_fix_time = 0.8
        # 修正block的步长
        self.fix_block_step = 0.1
        
        # 武将体力增速
        self.hero_ap_growth = 3/60

        # 势力之间的友好度
        self.friendly_levels = [ None, '险恶','敌对','普通','友好','盟友' ]

        self.first_city_name = '平安'
        self.new_player_text = '请问尊姓大名?'
        self.satrap_titles = [ None, '亭长','县令','太守','州牧','天子', ]

        # 年号
        self.year_name = [ None, '光和','黄龙','建安','初平', '章武', '永嘉', ]
        
    def init_story_config(self):
        self.story_dict = {}
        
    def init_skill_config(self):
        self.skill_dict = {}
        
        def add(skill):
            self.skill_dict[skill.config_id] = skill
            
        skill = SkillConfig()
        skill.config_id = 3001
        skill.skill_name = '普通攻击'
        skill.effect_id = 2001
        skill.life_time = 1.0
        skill.cooldown = 8.0
        # 伤害每千人
        skill.damage = 60
        add(skill)
        
        self.skill_words = [
            # 成语大师
            '赤膊上阵','战鼓雷鸣','出生入死','暗渡陈仓','势如破竹',
            '狼烟滚滚','你死我活','烽烟四起','擒贼先擒王','杀声震天',
            '枪林弹雨','奋不顾身','尸骨遍地','刀光剑影','机智勇敢',
            '硝烟弥漫','狂轰乱炸','一马当先','血流成河','智勇双全',
            '战火纷飞','出其不意','前赴后继','炮火连天','腥风血雨',
            '浩浩荡荡','冲锋陷阵','孤军奋战','奋勇杀敌','千军万马',
            '撒豆成兵','毁天灭地','引天雷击','突击斩首','快马重刀',
            '一决生死','日不移影','滚木礌石','引蛇出洞','声东击西',

            # 其他成语
            '义薄云天','两肋插刀',
            
            # 技能
            '火攻','水攻','挑战','单挑',
            '木牛流马','箭雨','诈降','诱敌深入','舌战群儒',
            '水淹七军','阵前倒戈','虚张声势','围三缺一',
            '风声鹤唳','草木皆兵','草船借箭','地道战','地雷战',
            '奇门遁甲','雷法','十面埋伏','穷追猛打',

            '挑衅','嘲讽','侮辱','骂街','大力出奇迹','劝降','色诱',
            '恐吓','威胁','冷箭',
            '劝降','鸿门宴','摔杯为号','鸣金收兵','擂鼓助威',
            '以少胜多','以多欺少','好运玩家','狗屎运','霉运当头','吹牛','饮酒误事',
            '乔装改扮','自吹自擂','忽悠',

            # 36计
            '瞒天过海', '围魏救赵', '借刀杀人', '以逸待劳', '趁火打劫', 
            '声东击西', '金蝉脱壳', '抛砖引玉', '擒贼擒王',
            '关门捉贼', '浑水摸鱼', '打草惊蛇', '无中生有', '上屋抽梯',
            '笑里藏刀', '顺手牵羊', '调虎离山', '李代桃僵', '借尸还魂',
            '指桑骂槐', '隔岸观火', '树上开花', '暗渡陈仓', '假道伐虢',
            '假痴不癫', '欲擒故纵', '釜底抽薪', '远交近攻', '反客为主',
            '偷梁换柱', '走为上计',
            '反间计', '美人计', '苦肉计', '空城计',  '连环计',
        ]
        
    def get_skill_word(self):
        return select_one(self.skill_words)
        
    def get_skill(self, config_id):
        return self.skill_dict.get(config_id, None)
        
    def init_effect_config(self):
        self.effect_dict = {}
        
        def add(effect):
            self.effect_dict[effect.config_id] = effect
        
        # 射箭
        effect = EffectConfig()
        effect.config_id = 2001
        effect.life_time = 2.0
        effect.res_path = 'res://effects/Shoot01.tscn'
        add(effect)
        
        # 飘字
        effect = EffectConfig()
        effect.config_id = 2002
        effect.life_time = 1.5
        effect.res_path = 'res://ui/TextEffect.tscn'
        add(effect)
        
        # 地上插旗
        effect = EffectConfig()
        effect.config_id = 2003
        effect.life_time = 1.5
        effect.res_path = 'res://models/Flag02.tscn'
        add(effect)
        
        # 技能飘字
        effect = EffectConfig()
        effect.config_id = 2004
        effect.life_time = 1.5
        effect.res_path = 'res://ui/BigTextEffect.tscn'
        add(effect)
        
    def get_effect(self, config_id):
        return self.effect_dict.get(config_id, None)

    def init_chapter_config(self):
        self.chapter_dict = {}

    def init_activity_config(self):
        self.activity_dict = {}
        
        def add(item):
            self.activity_dict[item.config_id] = item

        item = ActivityConfig()
        item.config_id = 3001
        item.infinite = True
        item.title = '空闲'
        item.color = (1.0,1.0,1.0)
        add(item)
        self.activity_config_idle = item

        item = ActivityConfig()
        item.config_id = 3002
        item.duration = 20
        item.title = '探访'
        item.rewards = [5001,5002]
        item.color = (0.0,0.5,0.0)
        add(item)

        item = ActivityConfig()
        item.config_id = 3003
        item.duration = 100
        item.title = '探亲'
        item.color = (0.0,0.5,0.0)
        add(item)

        item = ActivityConfig()
        item.config_id = 3004
        item.infinite = True
        item.title = '出战'
        item.color = (1.0,0.5,0.0)
        add(item)

        item = ActivityConfig()
        item.config_id = 3005
        item.duration = 100
        item.title = '受伤'
        item.color = (1.0,0.0,0.0)
        add(item)

    def get_activity_config(self, config_id):
        if config_id > 0:
            return self.activity_dict.get(config_id, None)
        return self.activity_config_idle

    def init_reward_config(self):
        self.item_config_dict = {}

        def add_item(item):
            self.item_config_dict[item.config_id] = item

        item = ItemConfig()

        item = ItemConfig()
        item.config_id = 4001
        item.item_name = '名将'
        item.desc = '从名将卡池中抽取'
        item.item_count = 9999
        add_item(item)

        item = ItemConfig()
        item.config_id = 4002
        item.item_name = '名将'
        item.desc = '从名将卡池中抽取高级名将'
        item.item_count = 9999
        add_item(item)

        # 普通物品
        item = ItemConfig()
        item.config_id = 4011
        item.item_name = '玉玺'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4012
        item.item_name = '九锡'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4013
        item.item_name = '孙子兵法'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4014
        item.item_name = '孟德新书'
        add_item(item)

        # 武器
        item = ItemConfig()
        item.config_id = 4101
        item.item_name = '虎头錾金枪'
        item.item_count = 9999
        add_item(item)

        item = ItemConfig()
        item.config_id = 4102
        item.item_name = '龙胆亮银枪'
        item.item_count = 9999
        add_item(item)

        item = ItemConfig()
        item.config_id = 4103
        item.item_name = '青龙偃月刀'
        item.item_count = 9999
        add_item(item)

        item = ItemConfig()
        item.config_id = 4104
        item.item_name = '丈八蛇矛'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4105
        item.item_name = '方天画戟'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4106
        item.item_name = '倚天剑'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4107
        item.item_name = '环首刀'
        add_item(item)

        # 甲
        #明光甲,缀鳞甲、山文甲、乌锤甲、白布甲、皂绢甲、布背甲、步兵甲、皮甲、木甲、锁予甲、马甲'
        item = ItemConfig()
        item.config_id = 4151
        item.item_name = '札甲'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4152
        item.item_name = '两当铠'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4153
        item.item_name = '黑光铠'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4154
        item.item_name = '明光铠'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4155
        item.item_name = '皮甲'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4156
        item.item_name = '布甲'
        add_item(item)

        # 马
        item = ItemConfig()
        item.config_id = 4201
        item.item_name = '赤兔马'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4202
        item.item_name = '爪黄飞电'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4203
        item.item_name = '乌骓马'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4204
        item.item_name = '夜照玉狮子'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4205
        item.item_name = '黄骠马'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4206
        item.item_name = '汗血马'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4207
        item.item_name = '绝影'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4208
        item.item_name = '盗骊'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4209
        item.item_name = '飒露紫'
        add_item(item)

        item = ItemConfig()
        item.config_id = 4210
        item.item_name = '特勒骠'
        add_item(item)

        # https://www.zhihu.com/question/48718055
        # 快航、惊帆
        # 一名 绝地，足不践土。二名 翻羽，行越飞禽。三名 奔宵，野行万里。四名 越影，逐日而行。五名 逾辉，毛色炳耀。六名 超光，一形十影。七名 腾雾，乘云而奔。八名 挟翼，身有肉翅。
        # 骅骝、绿耳、盗骊、骐骥、纤离。
        # 《古今注》：一曰追风，二曰白兔，三曰蹑景，四曰追电，五曰飞翩，六曰铜爵，七曰晨凫。
        # 《西京杂记》：汉文帝自代还，有良马九匹，皆天下骏足也。名曰浮云、赤电、绝群、逸群、紫燕骝、禄螭骢、龙子、嶙驹、绝尘，号九逸。有来宣能御。
        #

        #---------------------------------

        self.reward_config_dict = {}
        
        def add_reward(item):
            self.reward_config_dict[item.config_id] = item

        item = RewardConfig()
        item.config_id = 5001
        item.item_id = 4001
        item.item_count = 1
        item.win_rate = 50
        add_reward(item)

        item = RewardConfig()
        item.config_id = 5002
        item.item_id = 4101
        item.item_count = 1
        item.win_rate = 50
        add_reward(item)

    def get_reward_config(self, config_id):
        return self.reward_config_dict.get(config_id, None)

    def get_item_config(self, config_id):
        return self.item_config_dict.get(config_id, None)


    def init_army_type_config(self):
        self.army_type_list = [ None for i in range(ARMY_TYPE_SIZE) ]

        def add_type(item):
            self.army_type_list[item.config_id] = item

        # 兵种相克, 一个二维表
        self.army_fight_table = [ 1.0 for i in range(ARMY_TYPE_SIZE*ARMY_TYPE_SIZE) ]
        def set_fight_factor(attack, defend, value):
            self.army_fight_table[ARMY_TYPE_SIZE*attack+defend] = value

        item = ArmyTypeConfig()
        item.config_id = 0
        # 民兵, 乡兵, 没有武器,从事后勤
        item.name = '厢兵'   
        item.supply = 0.1
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 1
        item.name = '盾兵'
        item.supply = 1
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 2
        item.name = '枪兵'
        item.supply = 1
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 3
        item.name = '弓兵'
        item.supply = 4
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 4
        item.name = '骑兵'
        item.supply = 8
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 5
        item.name = '器械'
        item.supply = 10
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 6
        item.name = '水军'
        item.supply = 4
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 7
        item.name = '辎重'
        item.supply = 0.2
        item.speed = 0.1
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 8
        item.name = '火器'
        item.supply = 3
        add_type(item)

        item = ArmyTypeConfig()
        item.config_id = 9
        item.name = ''
        add_type(item)

        set_fight_factor(0, 3, 0.5)
        set_fight_factor(0, 4, 2.0)
        
        set_fight_factor(1, 3, 2.0)
        set_fight_factor(1, 4, 2.0)
        
        set_fight_factor(2, 0, 0.5)
        set_fight_factor(2, 3, 0.8)
        set_fight_factor(2, 4, 2.5)
        
        set_fight_factor(3, 0, 2.0)
        set_fight_factor(3, 1, 0.8)
        set_fight_factor(3, 4, 3.0)

        # 兵种熟练度
        self.army_mastery_list = [ None for i in range(ARMY_MASTERY_SIZE) ]
        def add_mastery(item):
            self.army_mastery_list[item.config_id] = item

    def get_fight_factor(self, attack, defend):
        return self.army_fight_table[ARMY_TYPE_SIZE*attack+defend]

    def get_army_type_config(self, config_id):
        return self.army_type_list[config_id]

    def get_army_type_list(self):
        return list(map(lambda x: x.name, filter(lambda x: bool(x.name), self.army_type_list)))

    def init_army_form_config(self):
        self.army_form_list = [ None for i in range(ARMY_FORM_SIZE) ]

        # 八阵图: 天、地、风、云、龙、虎、鸟、蛇
        def add_form(item):
            self.army_form_list[item.config_id] = item

        item = ArmyFormConfig()
        item.config_id = 0
        item.name = '方阵'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 1
        item.name = '长蛇阵'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 2
        item.name = '鱼鳞阵'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 3
        item.name = '却月阵'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 4
        item.name = '八卦阵'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 5
        item.name = '鸳鸯镇'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 6
        item.name = '五行阵'
        add_form(item)

        item = ArmyFormConfig()
        item.config_id = 7
        item.name = '梅花阵'
        add_form(item)
        

    def get_army_form_factor(self, attack, defend):
        return 1.0

    def get_army_form_list(self):
        return list(map(lambda x: x.name, filter(lambda x: x, self.army_form_list)))

    def init_rank_config(self):
        self.rank_config_list = [ None for i in range(RANK_SIZE) ]
        def add(item):
            self.rank_config_list[item.config_id] = item

        item = RankConfig()
        item.config_id = 1
        add(item)


    #----------------------------------------------------------------
    # 公式定义在此, 参数有点多
    #----------------------------------------------------------------
    
    def calc_skill_damage(self, skill_config_id, src_troop, target_unit):
        cfg = self.get_skill(skill_config_id)
        
        f1 = src_troop.army_amount.value / 1000 + src_troop.level*0.8
        f2 = src_troop.army_moral.value / 100
        value = cfg.damage * f1 * f2
        
        # 伤害跟军队人数正比
        value *= src_troop.army_amount.value/100
        
        value = round(value - target_unit.defense)
        
        # 暴击率
        if src_troop.critical_rate > 0 and \
                random_100() < src_troop.critical_rate:
            value *= 2
        
        # 保底伤害, 不能给加血吧?
        if value <= 0:
            value = 1
            
        return value

    # 伤害结算
    def calc_damage(self, 
            a_damage, a_level,
            b_defense, b_level):
        value = damage - defense
        
        return value if value > 0 else 1

    # 政治属性对应的,二次化的一个系数,
    # 空的时候给0.3,意思就是有时候,有太守,
    # 如果政治属性太低,这个比例不增反降
    def get_zhengzhi_ratio(self, hero):
        if hero:
            x = hero.zheng/100
            return x*x
        else:
            return 0.3

    # 治安公式
    def calc_order_growth_rate(self, satrap_hero, hero):
        value = 0

        if satrap_hero:
            value += satrap_hero.zheng*0.2

        if hero:
            value += hero.wu*0.5 + hero.tong*0.3

        value *= self.get_zhengzhi_ratio(satrap_hero)*0.2
        #log_debug('rice growth', value)

        return round(value)

    # 大米增长公式
    def calc_rice_growth_rate(self, satrap_hero, hero):
        value = 0

        if satrap_hero:
            value += satrap_hero.zheng*0.53

        if hero:
            value += hero.zheng*0.37 + hero.zhi*0.1

        value *= self.get_zhengzhi_ratio(satrap_hero)
        #log_debug('rice growth', value)

        return round(value)

    # 银两增长公式
    def calc_money_growth_rate(self, satrap_hero, hero):
        value = 0
        
        if satrap_hero:
            value += satrap_hero.zheng*0.43

        if hero:
            value += hero.zheng*0.37 + hero.zhi*0.2
            
        value *= self.get_zhengzhi_ratio(satrap_hero)

        return round(value)

    # 人口
    def calc_population_growth_rate(self, satrap_hero):
        value = 0

        if satrap_hero:
            value += satrap_hero.zheng*0.51 + \
                    satrap_hero.mei*0.31 + \
                    satrap_hero.tong*0.18

        return round(value)

    # 军队增长
    def calc_army_growth_rate(self, satrap_hero):
        value = 50

        if satrap_hero:
            value += satrap_hero.tong*0.61 +\
                    satrap_hero.mei*0.39
            
        return round(value)

    # percent = [0, 100]
    def calc_mass(self, percent, max_mass):
        v = percent * max_mass * 0.001
        v = math.trunc(v)*10
        return v

    def format_colored_label(self, value):
        if value > 0.01:
            return f'[color=green]+{value}[/color]'
        elif value < -0.01:
            return f'[color=red]-{value}[/color]'
        else:
            return ''

    def format_amount_label(self, value):
        value = math.floor(value)
        if value < 100000:
            return str(value)
        elif value < 100000000:
            value /= 10000
            return f'{value:.1f}万'
        else:
            value /= 100000000
            return f'{value:.1f}亿'

def select_one(item_list, delete=False):
    item, index = random_select_item(item_list)
    if delete and index >= 0:
        item_list[index] = item_list[-1]
        item_list.pop()
    return item

#
# https://zh.wikipedia.org/wiki/%E4%B8%89%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92
#
_city_name_data = [
'洛阳','建业','成都','汉中','南皮','北平','武威','天水',
'庐江','会稽','江陵','长沙','零陵','桂阳','建宁','云南',
'西平','长安','宛城','许昌','小沛','下邳','武陵','江洲',
'陈留','平原','新野','襄阳','濮阳','河东','平阳','河内',
'弘农','涿郡','代郡','渔阳','上谷','辽西','玄菟','乐浪',
'白帝','燕国','辽东','魏郡','广平','钜鹿','常山','博陵',
'渤海','河间','清河','赵国','中山','太原','上党','乐平',
'西河','雁门','新兴','济南','乐安','北海','城阳','东莱',
'汝南','东郡','济阴','山阳','泰山','济北','寿春','任城',
'东平','颍川','汝南','弋阳','陈郡','谯郡','鲁郡','梁国',
'沛国','彭城','乌巢','东海','琅琊','东莞','广陵','京兆',
'冯翊','扶风','北地','新平','陇西','天水','南安','广魏',
'安定','武都','阴平','金城','西平','武威','张掖','酒泉',
'敦煌','西海','南阳','南乡','江夏','永安','南郡','武陵',
'贵阳','蜀郡','犍为','朱提','越隽','臧柯',
'建宁','永昌','汉中','广汉','梓潼','巴郡','巴西','巴东',
'九江','庐江','丹阳','吴兴','建安','吴郡','豫章','庐陵',
'交趾','九真','日南','南海','苍梧','合蒲','珠崖','柴桑',
'湖州','富春','官渡','中牟','箕谷','博望','野王','钜鹿',
'上庸','昌黎','涪陵','衡阳','郁林','桂林','兴古','汶山',
'合肥','易',

'沙丘','姑苏','徐州','虎丘','大非川',
'陈仓','谷城','狄道','逍遥津','古城',

'虎牢关','散关','大胜关','函谷关','雁门关','葭萌关','武关',
'玉门关','昭关','铁门关','居庸关','剑门关','娄山关','阳关',
'瞿塘关','仙霞关','汜水关','潼关','萧关','金堤关','昆仑关',
'崤关','绵竹关','涪水关','壹关','阳平关','蒲津关','天门关',
'七星关','倒马关','紫荆关','宁武关',

'烂柯山','芒砀山','牛头山','四明山','终南山','峨眉山',
'风陵渡','米仓山','瓦岗山','武当山','平顶山','五台山',
'狮驼岭','摩天岭','昆仑山','九宫山','桃花山','五指山',
'青城山','龙虎山','武当山','崆峒山','花果山','大荒山',
'得胜山','玉皇山','玉玺山','石头山','玉女山','括苍山',
'莲花山','小鬼山','大鬼山','天台山',
'将军山','清凉山','青石山',
'二龙山','贺兰山','长白山','太行山','猫儿山',
'青铜峡','瞿塘峡',
'三清山','玉虚峰','玉华峰','紫金山','缥缈峰','大明山',
'蝴蝶谷','恶人谷','绝龙岭',
'落凤坡','五丈原','长坂坡',
#'羽山','君山','庐山','华山','梁山',

'野猪林','乌林','绿林','榆林','胡林','虎林',

'云梦泽','鄱阳湖','雷泽','洞庭湖','太湖',

]

def new_city_name():
    if len(_city_name_data) > 0:
        return select_one(_city_name_data, delete=True)
    else:
        return '新城'

# 将来自动生成的话，也要按照这个姓氏比例来生成，省得一些小姓出现概率太高
# https://zh.wikipedia.org/wiki/%E4%B8%89%E5%9B%BD%E6%BC%94%E4%B9%89%E8%A7%92%E8%89%B2%E5%88%97%E8%A1%A8
_name_data = [
'张让','张角','张宝','张梁','张飞','张钧','张举','张纯',
'张济','张辽','张郃','张邈','张超','张杨','张虎','张虎',
'张闿','张燕','张昭','张纮','张英','张勋','张绣','张鲁',
'张陵','张衡','张南','张南','张武','张温','张温',
'张允','张横','张既','张卫','张松','张任','张肃','张翼',
'张著','张音','张爽','张裔','张达','张苞','张嶷','张韬',
'张普','张休','张茂','张当','张特','张约','张缉','张布',
'张遵','张绍','张峻','张悌','张尚','张华','张象','张节',
'张明','张俭','张球','张先','张承','张世平','张津','张弥',
'刘宏','刘焉','刘备','刘恢','刘陶','刘虞','刘辩','刘协',
'刘岱','刘表','刘范','刘晔','刘繇','刘艾','刘璋','刘安',
'刘延','刘辟','刘勋','刘禅','刘琦','刘琮','刘泌','刘封',
'刘先','刘馥','刘熙','刘度','刘贤','刘磐','刘瑰','刘巴',
'刘循','刘瑁','刘永','刘理','刘廙','刘豹','刘宁','刘琰',
'刘敏','刘劭','刘放','刘丞','刘谌','刘璿','刘瑶','刘琮',
'刘瓒','刘恂','刘璩','刘达','刘寔','刘苌','刘宠','刘郃',
'刘邠','刘晙','刘弘','刘雄','刘元起','刘略','刘纂','王允',
'王匡','王方','王颀','王昌','王邑','王立','王朗','王则',
'王垕','王楷','王忠','王植','王修','王琰','王威','王粲',
'王累','王平','王甫','王谋','王双','王双','王连','王伉',
'王肃','王建','王昶','王韬','王基','王经','王真','王含',
'王沈','王业','王惇','王瓘','王买','王颀','王祥','王濬',
'王浑','王戎','王观','王必','王子服','孙钟','孙仲','孙坚',
'孙策','孙权','孙仁','孙翊','孙匡','孙朗','孙韶','孙静',
'孙乾','孙观','孙瑜','孙高','孙皎','孙桓','孙礼','孙资',
'孙登','孙和','孙亮','孙峻','孙据','孙恩','孙干',
'孙闿','孙谦','孙恭','孙楷','孙休','孙皓','孙异','孙霖',
'孙河','孙冀','孙歆','孙秀','曹节','曹操','曹嵩','曹仁',
'曹洪','曹德','曹豹','曹性','曹昂','曹丕','曹植','曹纯',
'曹休','曹永','曹彰','曹熊','曹叡','曹真','曹遵','曹宇',
'曹芳','曹爽','曹羲','曹训','曹彦','曹据','曹髦','曹奂',
'曹霖','曹安民','曹腾','曹文叔','李傕','李儒','李肃','李典',
'李蒙','李别','李膺','李封','李乐','李暹','李通','李孚',
'李珪','李堪','李恢','李严','李丰','李丰','李丰','李伏',
'李意','李异','李辅','李福','李胜','李歆','李朋','李崇',
'李球','李虎','李撰','杨彪','杨密','杨琦','杨奉','杨丑',
'杨龄','杨秋','杨阜','杨修','杨怀','杨柏','杨松','杨洪',
'杨昂','杨任','杨锋','杨仪','杨陵','杨暨','杨颙','杨祚',
'杨综','杨欣','杨济','杨大将','陈蕃','陈琳','陈耽','陈宫',
'陈翔','陈生','陈登','陈武','陈横','陈兰','陈珪','陈纪',
'陈震','陈孙','陈就','陈应','陈修','陈群','陈矫','陈式',
'陈泰','陈炜','陈骞','陈俊','陈造','陈元','赵忠','赵弘',
'赵萌','赵岑','赵云','赵岐','赵彦','赵叡','赵范','赵衢',
'赵昂','赵月','赵累','赵祚','赵融','赵咨','赵统','赵广',
'赵直','赵颜','赵韪','马腾','马宇','马超','马元义','马日谛',
'马延','马良','马谡','马岱','马休','马铁','马玩','马忠',
'马忠','马遵','马钧','马邈','马玉','马汉','马融','韩忠',
'韩馥','韩当','韩遂','韩暹','韩融','韩胤','韩嵩','韩福',
'韩猛','韩珩','韩浩','韩玄','韩德','韩瑛','韩瑶','韩琼',
'韩琪','韩暨','韩综','韩祯','韩莒子','夏侯惇','夏侯渊','夏侯兰',
'夏侯恩','夏侯杰','夏侯德','夏侯存','夏侯楙','夏侯霸','夏侯威','夏侯惠',
'夏侯和','夏侯玄','夏侯咸','吕布','吕玲绮','吕虔','吕伯奢',
'吕范','吕旷','吕翔','吕蒙','吕通','吕义','吕常','吕建',
'吕凯','吕岱','吕霸','吕据','吕威璜','董卓','董重','董旻',
'董璜','董承','董昭','董袭','董和','董祀','董衡','董超',
'董允','董厥','董禧','董寻','董朝','胡轸','胡赤儿','胡才',
'胡华','胡班','胡济','胡质','胡忠','胡遵','胡烈','胡渊',
'胡奋','胡冲','胡邈','胡车儿','周毖','周奂','周瑜','周尚',
'周泰','周昕','周仓','周循','周胤','周善','周群','周平',
'周鲂','周旨','许劭','许昌','许韶','许攸','许褚','许定',
'许汜','许贡','许靖','许芝','许慈','许允','许晏','许仪',
'邓茂','邓龙','邓义','邓贤','邓芝','邓贤','邓艾','邓忠',
'邓程','邓敦','邓良','邓飏','邓铜','诸葛亮','诸葛瑾','诸葛均',
'诸葛虔','诸葛恪','诸葛瞻','诸葛诞','诸葛靓','诸葛绪','诸葛尚','诸葛原',
'吴匡','吴景','吴子兰','吴敦','吴硕','吴臣','吴懿','吴兰',
'吴质','吴班','吴纲','朱儁','朱治','朱灵','朱桓',
'朱光','朱然','朱褒','朱赞','朱恩','朱异','朱芳','司马徽',
'司马朗','司马懿','司马孚','司马馗','司马恂','司马进','司马通','司马师',
'司马昭','司马望','司马炎','司马攸','司马伷','蒋钦','蒋奇','蒋干',
'蒋琬','蒋济','蒋班','蒋舒','蒋斌','蒋显','蒋延','蒋义渠',
'丁原','丁管','丁奉','丁斐','丁仪','丁廙','丁咸','丁谧',
'丁封','丁立','黄盖','黄琬','黄祖','黄邵','黄忠','黄奎',
'黄权','黄皓','黄崇','黄承彦','郭胜','郭汜','郭嘉','郭图',
'郭常','郭奕','郭淮','郭恩','郭永','郭攸之','袁绍','袁术',
'袁隗','袁遗','袁逢','袁谭','袁熙','袁尚','袁胤',
'何进','何颙','何苗','何仪','何宗','何平','何晏','何曾',
'何植','何曼','荀攸','荀爽','荀谌','荀彧','荀绲','荀正',
'荀恽','荀恺','荀勗','程普','程旷','程昱','程远志',
'程秉','程咨','程银','程畿','程武','杜远','杜袭','杜琼',
'杜路','杜微','杜义','杜祺','杜预','公孙瓒','公孙越','公孙康',
'公孙渊','公孙度','公孙晃','公孙恭','公孙修','孟坦','孟达','孟光',
'孟获','孟优','孟节','孟宗','孟建','庞舒','庞统','庞德',
'庞羲','庞义','庞柔','庞会','庞德公','关羽','关纯','关定',
'关宁','关平','关兴','关索','关彝','薛兰','薛礼','薛综',
'薛悌','薛则','薛乔','薛莹','薛珝','徐荣','徐庶','徐晃',
'徐璆','徐康','徐盛','徐商','徐质','徐勋','蔡邕','蔡瑁',
'蔡阳','蔡和','蔡中','蔡勋','蔡林','高升','高顺','高览',
'高干','高沛','高定','高翔','高柔','陆康','陆绩','陆逊',
'陆抗','陆凯','陆景','陆纡','陆骏','傅婴','傅巽','傅干',
'傅彤','傅嘏','傅佥','傅士仁','崔烈','崔毅','崔勇','崔琰',
'崔钧','崔禹','崔谅','田丰','田楷','田世','田畴','田豫',
'田续','田章','郑泰','郑玄','郑度','郑文','郑伦','郑袤',
'郑宝','尹礼','尹楷','尹奉','尹默','尹赏','尹大目','秦琪',
'秦宓','秦良','秦明','秦朗','秦庆童','全琮','全端','全怿',
'全纪','全尚','全祎','钟缙','钟绅','钟繇','钟进','钟会',
'钟毓','严政','严纲','严舆','严畯','严象','严颜','严白虎',
'潘隐','潘凤','潘璋','潘濬','潘举','潘遂','文丑','文聘',
'文钦','文虎','文鸯','苏双','苏由','苏飞','苏越','苏颙',
'贾诩','贾华','贾逵','贾范','贾充','宋果','宋宪','宋忠',
'宋谦','宋白','成廉','成宜','成济','成倅','成何','阎圃',
'阎晏','阎宇','阎象','阎芝','范滂','范康','范成','范方',
'范疆','卫弘','卫凯','卫道玠','卫演','卫瓘','左丰','左灵',
'左慈','左咸','樊稠','樊能','樊建','樊岐','彭伯','彭安',
'彭羕','彭和','辛评','辛毗','辛敞','辛明','鲍信','鲍忠',
'鲍隆','鲍素','伍琼','伍孚','伍习','伍延','陶谦','陶商',
'陶应','陶濬','华雄','华佗','华歆','华核','桓阶','桓范',
'桓嘉','桓彝','岑眰','岑璧','岑威','岑昏','于禁','于糜',
'于吉','于诠','焦触','焦炳','焦彝','焦伯','费观','费祎',
'费诗','费耀','冯礼','冯习','冯𬘘','冯方','孔伷','孔融',
'孔昱','孔宙','孔秀','魏续','魏延','魏邈','魏平','皇甫嵩',
'皇甫闿','皇甫郦','淳于琼','淳于导','淳于丹','裴景','裴秀','裴元绍',
'管亥','管宁','管辂','管邈','向宠','向朗','向举','唐周',
'唐咨','唐彬','侯览','侯成','侯音','侯选','龚景','龚都',
'龚起','祖茂','祖郎','祖弼','吉太','吉邈','吉穆','乐进',
'乐就','乐肇','凌操','凌统','凌烈','凌封','种拂',
'种邵','种辑','鲁馗','鲁肃','鲁芝','廖化','廖淳','廖立',
'留赞','留略','留平','金旋','金祎','金尚','姜叙','姜维',
'姜冏','卢植','卢逊','卢毓','乔瑁','乔玄','太史慈',
'太史享','牛辅','牛金','毋丘俭','毋丘甸','丘建','丘本','史涣',
'史迹','甘宁','甘瑰','申耽','申仪','石苞','石广元','伏完',
'伏德','任峻','任夔','吾彦','吾粲','步骘','步协','步阐',
'邢贞','邢道荣','典韦','典满','宗宝','宗预','尚弘','尚广',
'昌豨','昌奇','法真','法正','沮授','沮鹄','段珪','段煨',
'爰青','爰邵','韦康','韦晃','夏恽','夏恂','耿武','耿纪',
'郝萌','郝昭','眭固','眭元进','万政','万彧','虞翻','虞汜',
'虞松','雷薄','雷铜','臧旻','臧霸','蒯良','蒯越','审配',
'审荣','滕胤','滕修','穆顺','穆顺','霍峻','霍弋','戴员',
'戴陵','糜竺','糜芳','糜威','边让','边洪','窦武','封谞',
'蹇硕','邹靖','闵贡','俞涉','颜良','方悦','檀敷','逢纪',
'麹义','满宠','毛玠','应劭','苟安','武安国','士孙瑞','和洽',
'伊籍','邴原','谷利','桥蕤','纪灵','笮融','简雍','阴夔',
'卞喜','路昭','车胄','祢衡','郗虑','顾雍','阚泽','骆统',
'妫览','脂习','晏明','牵弘','州泰','曾宣','施朔','党均',
'寗随','邵悌','郤正','干休','羊祜','楼玄','雍闿','沈莹',
'山涛','仇连','花永','巩志','鄂焕','戈定','苗泽','冷苞',
'赖恭','卓膺','谯周','翟元','殷纯','谭雄','靳祥','常雕',
'来敏','官充','詹习','盛勃','伦直','卑衍','柳甫','毕轨',
'司蕃','句安','葛雍','师纂','白寿','阳群','汪昭','区星',
'娄圭','慕容烈','濮阳兴','单子春','邯郸淳',

# 女性
'黄月英','孙尚香','甄宓','关银屏','贾南风','糜萍','甘梅','樊倩',
'邹兰','貂蝉','蔡文姬','步练师','张春华',
'马云禄','孙鲁班','孙鲁育','伏寿','辛宪英','孙大虎','孙小虎',
'诸葛果','曹羡','曹华','曹节','王元姬','张昌蒲','夏侯徽','夏侯兰',
'郭女王','张曼','张莲','关凤','王朝云','王弗',

# 历史人物, 用来丰富名字

'姜尚','吕望','闻仲','黄飞虎','苏护','姬昌','姬发','李耳','庄周',
'魏无忌','田文','黄歇','赵胜','赵奢','赵括','李牧',
'赵奢','赵括','白起','吴起','孙武','王翦','廉颇','伍子胥','庞涓','孙膑','田忌',
'项羽','项梁','英布','龙且','章邯','雍齿','夏侯婴','萧何','张良','韩信','樊哙',
'刘如意','刘兴居','刘肥','刘长','刘胜','田横','陈余','张耳',
'卫青','霍去病','李广','李陵','陈汤','班超','段颖','窦宪','班固',
'刘秀','王莽','蔡伦','邓禹','吴汉','马援','阴丽华',
'单福','曹吉利','曹阿瞒',
'慕容垂','慕容翰','苻坚','谢安','谢玄','桓温','刘裕','刘牢之','陈霸先','陈庆之','王羲之','沈约',
'王猛','王镇恶','李雄','拓跋圭','宇文护',
'杨坚','独孤伽罗','杨广','杨素','韩擒虎','高颖','陈叔宝','张丽华',
'李渊','刘文静','李靖','秦琼','尉迟恭','程咬金','杨林','魏文通','裴翠云','殷开山',
'翟让','窦建德','王世仁','萧铣','王仁则','朱粲',
'李元霸','宇文成都','裴元庆','李密','李绩','徐茂公','单雄信','罗士信','张烈',
'薛礼','薛仁贵','张士贵','侯君集','长孙无忌','苏定方',
'李白','杜甫','高适','王维','王昌龄','杜牧','李商隐','白居易','骆宾王','王勃',
'朱温','朱全忠','安禄山','高仙芝','哥舒翰','李克用','李存孝',
'郭威','赵匡胤','柴荣','寇准','富弼','蔡襄','赵普','曹彬','童贯','张叔夜',
'杨业','杨延昭','杨文广','孟良','焦赞','呼延灼','潘美','庞籍','狄青',
'宋江','李逵','武松','鲁达','林冲','杨志','秦明','公孙胜','晁盖','吴用',
'李纲','宗泽','岳飞','岳云','牛皋','汤怀','张宪','王贵','韩世忠','梁红玉','赵佶','赵构',
'辛弃疾','苏轼','苏辙','李清照','文天祥',
'徐达','常遇春','刘基','刘伯温','李文忠','李贞','傅友德','汤和','花云','俞通海',
'张士诚','陈友谅','王保保','李思齐',
'黄观','王华',
'戚继光','俞大猷','卢象升','孙承宗',
'李自成','罗汝才','张献忠','马守应','刘国能','李定国',

'卓文君','司马相如',
'潘金莲','李瓶儿','李二娘','赵飞燕','赵合德',
'吕四娘','秦良玉','花木兰','樊梨花','佘赛花',

'李侠','徐霞客','唐寅','周文宾','文征明',

'刘德华','李连杰','李小龙','甄子丹','张曼玉','林青霞','朱茵',
'黄麒英','黄飞鸿','梁宽','霍元甲','马永贞','方世玉','洪熙官','叶问','陈真','李国邦',
'于镇海','陈家洛',
'李逍遥','林月如','赵灵儿',
'燕赤霞','宁采臣','聂小倩',
'金庸','杨过','张无忌','黄药师','欧阳锋','洪七','段誉','乔峰','慕容复','周芷若','赵敏',
'令狐冲','岳不群','风清扬','吴天德',
'李霞','黄蓉','郭襄',
'沈浪','王怜花','李寻欢','白阿飞','荆无名','上官金虹','赵昆仑',
'叶开','傅红雪','叶孤城','楚留香','胡铁花','陆小凤','姬无病',
'谢晓峰','燕十三','郭大路','燕七','王动',
'李狗儿','杨大眼',
'贾贵','黄金标','白守业','石青山','孙富贵','张麻子',
'李秀莲','白展堂','吕轻侯','莫小贝','郭芙蓉','祝无双','燕小六','邢育森','佟湘玉',

'张三','李四','王五','赵六','张龙','赵虎','王朝','马汉',
'赵熊','赵绅','赵触','赵锤','赵明','赵大','赵二',

# 补充姓氏
'公羊龙','第五伦','纳兰光','公冶平','东野泰','南宫杰','新垣虎',
'岳秀','楚师','澹台灭明','赫连铁树','东方旭','轩辕青峰','百里扶苏',
'西门庆','鲜于通','钟离昧',
]

# 复姓
fuxing_data = set([
    '诸葛','令狐','慕容','宇文','澹台','第五','公羊','公孙','公冶',
    '东野','南宫','新垣','士孙','邯郸','濮阳','淳于','皇甫','夏侯',
    '拓跋','纳兰','司马','叔孙','欧阳','欧冶','太史','司徒','鲜于',
    '轩辕','东郭','百里','段干','呼延','端木','独孤','上官','东方',
    '尉迟','钟离','申屠','长孙','西门','颛孙','主父','谷梁','宰父',
    '完颜','赫连','哥舒',
])

# def new_hero_name_v1():
#     if len(_name_data) > 0:
#         return select_one(_name_data, delete=False)
#     else:
#         return '李哪吒'


# 把名字, 分成姓,名,两段
def parse_hero_name(name):
    if len(name) == 2:
        return name[0],name[1]
    elif len(name) > 2:
        fname = name[:2]
        if fname not in fuxing_data:
            return name[:1], name[1:]
        else:
            return fname, name[2:]
    else:
        return '赵','大'


def new_hero_name():
    if len(_name_data) > 0:
        name1 = select_one(_name_data, delete=False)
        f1,n1 = parse_hero_name(name1)
        while 1:
            name2 = select_one(_name_data, delete=False)
            f2,n2 = parse_hero_name(name2)
            if f1 not in n2:
                return f1 + n2
    else:
        return '李哪吒'

