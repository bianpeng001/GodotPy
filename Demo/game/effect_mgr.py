#
# 2023年2月20日 bianpeng
#


class Effect:
    def __init__(self):
        self.config_id = 0
        self.node = None
        self.position = None
        self.time = 0
        self.life_time = 1

#
# 特效管理，缓存复用特效对象
#
class EffectMgr:
    def __init__(self):
        self.effect_list = []
        self._back_effect_list = []
    
    def play(self, x,y,z):
        pass

    def update(self, update_time):
        pass


    