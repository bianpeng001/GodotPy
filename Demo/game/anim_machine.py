#
# 2023年2月18日 bianpeng
#

# 动作状态，对应一个动作或者几个动作的blendtree
class AnimState:
    def __init__(self):
        self.state_name = ''
        self.is_loop = False
        self.durtion = 1.0
        self.jumps = []

# 动作状态机
class AnimMachine:
    def __init__(self):
        pass

    def update(self, delta_time):
        pass

