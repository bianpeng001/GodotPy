#
# 2023年2月20日 bianpeng
#

from game.core import *

class Effect:
    def __init__(self):
        self.config_id = 0
        self.node = None
        #self.position = None
        self.time = 0
        self.life_time = 1

#
# 特效管理，缓存复用特效对象
#
class EffectMgr:
    def __init__(self):
        self.effect_list = []
        self._back_effect_list = []

        self.cache_list = []
    
    def play1(self, x,y,z, x1,y1,z1):
        effect = Effect()
        effect.time = 0
        effect.life_time = 1
        effect.node = instantiate('res://effects/Strike01.tscn')
        Node3D.set_position(effect.node, x,y,z)
        Node3D.look_at(effect.node, x1,y1,z1)

        self.add(effect)

    def add(self, effect):
        self.effect_list.append(effect)

    def update(self, delta_time):
        tmp = self.effect_list
        self.effect_list = self._back_effect_list
        self._back_effect_list = tmp

        for effect in self._back_effect_list:
            effect.time += delta_time
            if effect.time < effect.life_time:
                self.add(effect)
            else:
                #self.cache_list.append(effect)
                Node.destroy(effect.node)




    