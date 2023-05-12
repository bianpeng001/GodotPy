#
# 2023年2月20日 bianpeng
#

from game.core import log_debug, OS
from game.game_mgr import *


def get_config(config_id):
    return game_mgr.config_mgr.get_effect(config_id)

#
# effect实例
#
class EffectItem:
    def __init__(self, config_id):
        self.config_id = config_id
        self.life_time = get_config(self.config_id).life_time
        
        self.item_id = 0
        self.node = None
        self.time = 0
        
    def set_visible(self, value):
        if self.node:
            self.node.set_visible(value)
    
    def set_position(self,x,y,z):
        self.node.set_position(x,y,z)
        
    def look_at(self, x,y,z):
        self.node.look_at(x,y,z)
    
    def load(self):
        if not self.node:
            self.do_load()
            
    def do_load(self):
        self.node = OS.instantiate(get_config(self.config_id).res_path)
        
    def update(self):
        pass

#
# 粒子特效
#
class ParticleEffectItem(EffectItem):
    def update(self):
        pass

#
# 飘字, 也是个特效
#
class TextEffectItem(EffectItem):
    def __init__(self, config_id):
        super().__init__(config_id)
        
        # 吸附到目标单位
        self.attach_unit = None
        self.text_node = None
        
    def do_load(self):
        super().do_load()
        
        self.node.reparent(game_mgr.ui_mgr.text_effect_layer)
        self.text_node = self.node.find_node('Label')
        
    def update(self):
        x,y,z = self.attach_unit.get_position()
        x1,y1 = get_main_camera().world_to_screen(x,y+1+self.time*2,z)
        self.node.set_position(x1-40,y1)
    
    def set_text(self, value):
        self.text_node.set_color(1,0,0,1)
        self.text_node.set_text(str(value))

class BigTextEffectItem(EffectItem):
    def __init__(self, config_id):
        super().__init__(config_id)
        
        self.attach_unit = None
        self.text_node = None
        
    def do_load(self):
        super().do_load()
        
        self.node.reparent(game_mgr.ui_mgr.text_effect_layer)
        self.text_node = self.node.find_node('Label')
        
    def set_text(self, value):
        self.text_node.set_text(str(value))
        
    def update(self):
        x,y,z = self.attach_unit.get_position()
        x1,y1 = get_main_camera().world_to_screen(x,y+10-(self.time*2)**2,z)
        self.node.set_position(x1-72,y1)

#
# 普通特效
#
class SimpleEffectItem(EffectItem):
    pass


#
# 特效管理，缓存复用特效对象
#
class EffectMgr:
    def __init__(self):
        self.effect_list = []
        self.back_effect_list = []

        self.cache_list = []
        self.next_item_id = 10000
        
        self.effect_class_dict = {
            2001: ParticleEffectItem,
            2002: TextEffectItem,
            2004: BigTextEffectItem,
        }
    
    # 从cache复用
    def revive_cache(self, config_id):
        index = -1
        for i in range(len(self.cache_list)):
            if self.cache_list[i].config_id == config_id:
                index = i
                break
        
        if index >= 0:
            return self.cache_list.pop(index)
    
    def get_effect_class(self, config_id):
        return self.effect_class_dict.get(config_id, SimpleEffectItem)

    # 创建一个effect 实例
    def new_effect(self, config_id):
        effect = self.revive_cache(config_id)
        if not effect:
            effect = self.get_effect_class(config_id)(config_id)
            effect.load()

        self.next_item_id += 1
        effect.item_id = self.next_item_id
        effect.time = 0
        effect.set_visible(True)
        
        self.add(effect)
        return effect
    
    def play_effect2(self, config_id):
        effect_item = self.new_effect(config_id)
        return effect_item
    
    # 伤害飘字
    def play_damage(self, value, attach_unit):
        effect_item = self.new_effect(2002)
        
        effect_item.set_text(value)
        effect_item.attach_unit = attach_unit
        
        return effect_item
    
    # deprecated
    def play_effect1(self, x,y,z, x1,y1,z1):
        effect = self.new_effect(0)
        
        effect.time = 0
        effect.life_time = 3

        effect.node.set_position(x,y,z)
        effect.set_visible(True)
        effect.node.look_at(x1,y1,z1)
        ps = effect.node.find_node('CPUParticles3D')
        ps.set_emitting(True)

    def add(self, effect):
        self.effect_list.append(effect)

    def update(self, delta_time):
        # swap buffer
        tmp = self.effect_list
        self.effect_list = self.back_effect_list
        self.back_effect_list = tmp

        if len(self.back_effect_list) > 0:
            for effect in self.back_effect_list:
                effect.time += delta_time
                effect.update()
                if effect.time < effect.life_time:
                    self.add(effect)
                else:
                    effect.set_visible(False)
                    self.cache_list.append(effect)
            self.back_effect_list.clear()


