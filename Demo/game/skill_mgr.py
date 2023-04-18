#
# 2023年4月17日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *

#
# 一个技能, 可能有多个阶段组成.
#
class SkillItem:
    def __init__(self, config_id):
        self.config_id = config_id
        self.life_time = 1
        self.time = 0

    def update(self):
        pass
    
    def on_start(self):
        pass
    
    def on_complete(self):
        pass
    

#
# 技能管理
#
class SkillMgr:
    def __init__(self):
        self.item_list = []
        self.back_item_list = []

    def update(self, delta_time):
        tmp = self.item_list
        self.item_list = self.back_item_list
        self.back_item_list = tmp

        if len(self.back_item_list) > 0:
            for item in self.back_item_list:
                item.time += delta_time
                item.update()
                if item.time < item.life_time:
                    self.add_skill(item)
                else:
                    item.on_complete()
                    
            self.back_item_list.clear()

    def add_skill(self, item):
        self.item_list.append(item)
        
    # 释放技能
    def cast_skill(self, config_id):
        cfg = game_mgr.config_mgr.get_skill(config_id)
        item = SkillItem(config_id)
        item.time = 0
        item.life_time = cfg.life_time
        self.add_skill(item)
        item.on_start()
        
        




