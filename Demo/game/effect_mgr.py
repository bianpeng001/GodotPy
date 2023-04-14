#
# 2023年2月20日 bianpeng
#

from game.core import log_debug, OS
from game.game_mgr import *

class Effect:
    def __init__(self, config_id):
        self.config_id = config_id
        
        cfg = game_mgr.config_mgr.get_effect(self.config_id)
        self.life_time = cfg.life_time
        self.res_path = cfg.res_path
        
        self.effect_id = 0
        self.node = None
        self.time = 0
        # 吸附到目标单位
        self.attach_unit = None

    def set_visible(self, value):
        self.node.set_visible(value)
        
    def load(self):
        if not self.node:
            self.node = OS.instantiate(self.res_path)
        
    def update(self):
        pass
    
    def set_position(self,x,y,z):
        self.node.set_position(x,y,z)
        
    def look_at(self, x,y,z):
        self.node.look_at(x,y,z)

#
# 特效管理，缓存复用特效对象
#
class EffectMgr:
    def __init__(self):
        self.effect_list = []
        self.back_effect_list = []

        self.cache_list = []
        self.effect_id_seed = 10000
        
    def revive_cache(self, config_id):
        index = -1
        for i in range(len(self.cache_list)):
            if self.cache_list[i].config_id == config_id:
                index = i
                break
            
        if index >= 0:
            return self.cache_list.pop(index)

    def new_effect(self, config_id):
        effect = self.revive_cache(config_id)
        if not effect:
            effect = Effect(config_id)
            effect.load()

        effect.effect_id = self.effect_id_seed
        self.effect_id_seed += 1
        effect.set_visible(True)
        
        self.add(effect)
        return effect
    
    def play_effect2(self, config_id):
        return self.new_effect(config_id)
    
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
                if effect.time < effect.life_time:
                    self.add(effect)
                else:
                    effect.set_visible(False)
                    self.cache_list.append(effect)
            self.back_effect_list.clear()
            

