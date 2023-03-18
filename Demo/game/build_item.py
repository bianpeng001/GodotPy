#
# 2023年3月4日 bianpeng
#
from game.core import *
from game.game_mgr import *


# 物件类型
BT_FRAM = 1
BT_IRON = 2

#
# 附属建筑, 归属于地块, 有一些功能
#
class BuildItem:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.build_type = 0

    def calc(self):
        pass
        



