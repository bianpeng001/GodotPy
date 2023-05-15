#
# 2023年2月20日 bianpeng
#

from game.core import log_debug, OS, obstacle
from game.game_mgr import *

#
# effect实例
#
class EffectItemBase:
    def __init__(self, config_id):
        # 配置id
        self.config_id = config_id
        # 生命周期
        self.life_time = get_effect_config(self.config_id).life_time
        
        # 实例id
        self.item_id = 0
        # 释放者
        self.caster_unit_id = 0
        # 特效时间
        self.time = 0
        # 特效对应的节点
        self.node = None
        
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
        self.node = OS.instantiate(get_effect_config(self.config_id).res_path)
        
    def update(self):
        pass

#
# 粒子特效
#
class ParticleEffectItem(EffectItemBase):
    def update(self):
        pass

#
# 飘字, 也是个特效
#
class TextEffectItem(EffectItemBase):
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

#
#
#
class BigTextEffectItem(EffectItemBase):
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
        x1,y1 = get_main_camera().world_to_screen(x,y+8-5*((self.time/self.life_time))**2,z)
        self.node.set_position(x1-56,y1+32)

#
# 普通特效
#
class SimpleEffectItem(EffectItemBase):
    def update(self):
        pass


#
# 特效管理，缓存复用特效对象
#
class EffectMgr:
    def __init__(self):
        self.next_item_id = 10000
        
        self.effect_list = []
        self.back_effect_list = []

        self.cache_list = []
        
        self.effect_class_dict = {
            2001: ParticleEffectItem,
            2002: TextEffectItem,
            2003: SimpleEffectItem,
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
            effect_class = self.get_effect_class(config_id)
            effect = effect_class(config_id)
            effect.load()

        self.next_item_id += 1
        effect.item_id = self.next_item_id
        
        effect.time = 0
        effect.set_visible(True)
        
        self.effect_list.append(effect)
        return effect
    
    def play_effect2(self, config_id):
        effect_item = self.new_effect(config_id)
        effect_item.caster_unit_id = 0
        return effect_item
    
    def play_effect3(self, caster_unit_id, config_id):
        effect_item = self.new_effect(config_id)
        effect_item.caster_unit_id = caster_unit_id
        return effect_item
    
    @obstacle
    def play_effect1(self, x,y,z, x1,y1,z1):
        effect = self.new_effect(0)
        
        effect.time = 0
        effect.life_time = 3

        effect.node.set_position(x,y,z)
        effect.set_visible(True)
        effect.node.look_at(x1,y1,z1)
        ps = effect.node.find_node('CPUParticles3D')
        ps.set_emitting(True)
        
    # 伤害飘字
    def play_damage(self, value, attach_unit):
        effect_item = self.new_effect(2002)
        
        effect_item.caster_unit_id = 0
        effect_item.set_text(value)
        effect_item.attach_unit = attach_unit
        
        return effect_item
        
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
                    self.effect_list.append(effect)
                else:
                    effect.set_visible(False)
                    self.cache_list.append(effect)
            self.back_effect_list.clear()


