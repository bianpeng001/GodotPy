#
# 2023年4月17日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *

#
# 一个技能, 可能有多个阶段组成
# 用来控制技能的生命周期, 以及事件触发. 这个管理器后面可能会更加复杂一些.
#
class SkillItem:
    def __init__(self, config_id):
        self.item_id = 0
        self.config_id = config_id
        self.life_time = 1
        self.time = 0
        self.on_complete_cb = None

    def update(self):
        pass
    
    def on_start(self):
        log_debug('skill start', self.item_id, self.config_id)
    
    def on_complete(self):
        log_debug('skill complete', self.item_id, self.config_id)
        if self.on_complete_cb:
            self.on_complete_cb()

#
# 技能管理
#
class SkillMgr:
    def __init__(self):
        self.item_list = []
        self.back_item_list = []
        self.next_item_id = 10000

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
    def create_skill_item(self, config_id, on_complete_cb = None):
        cfg = game_mgr.config_mgr.get_skill(config_id)
        self.next_item_id += 1
        
        item = SkillItem(config_id)
        item.item_id = self.next_item_id
        item.time = 0
        item.life_time = cfg.life_time
        item.on_complete_cb = on_complete_cb
        
        self.add_skill(item)
        item.on_start()
        
        return item