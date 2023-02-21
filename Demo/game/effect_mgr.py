#
# 2023年2月20日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

class Effect:
    def __init__(self):
        self.effect_id = 0
        self.config_id = 0
        self.node = None
        #self.position = None
        self.time = 0
        self.life_time = 1

    def set_visible(self, value):
        ps = find_node2(self.node, 'CPUParticles3D')
        ps.set_visible(value)

#
# 特效管理，缓存复用特效对象
#
class EffectMgr:
    def __init__(self):
        self.effect_list = []
        self._back_effect_list = []

        self.cache_list = []
        self.effect_id_seed = 1000

    def new_effect(self, config_id):
        self.effect_id_seed += 1

        if len(self.cache_list) > 0:
            effect = self.cache_list.pop()
            #print(f'reuse effect {effect.effect_id}')
        else:
            effect = Effect()
            effect.config_id = config_id
            effect.node = instantiate('res://effects/Strike01.tscn')

        effect.effect_id = self.effect_id_seed
        return effect
    
    def play_effect1(self, x,y,z, x1,y1,z1):
        effect = self.new_effect(0)
        
        effect.time = 0
        effect.life_time = 3

        Node3D.set_position(effect.node, x,y,z)
        effect.set_visible(True)
        ps = find_node2(effect.node, 'CPUParticles3D')
        #Node3D.look_at(effect.node, x1,1,z1)
        ps.look_at(x1,y1,z1)
        ps.set_emitting(True)

        self.add(effect)

    def add(self, effect):
        self.effect_list.append(effect)

    def update(self, delta_time):
        tmp = self.effect_list
        self.effect_list = self._back_effect_list
        self._back_effect_list = tmp

        if len(self._back_effect_list) > 0:
            for effect in self._back_effect_list:
                effect.time += delta_time

                if effect.time < effect.life_time:
                    self.add(effect)
                else:
                    #self.cache_list.append(effect)
                    #Node.destroy(effect.node)
                    effect.set_visible(False)
                    self.cache_list.append(effect)

            self._back_effect_list.clear()

            