#
# 2023年3月4日 bianpeng
#
from game.core import *
from game.game_mgr import *


# 物件类型
# 农田
BT_FRAM = 1
# 矿场
BT_IRON = 2
# 工场
BT_WOOD = 3

#
# 附属建筑, 归属于地块, 有一些功能
#
class BuildItem:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.build_type = 0

    # 资源结算
    def calc_income(self):
        pass
        



