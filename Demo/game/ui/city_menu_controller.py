#
# 2023年2月24日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

# 城池的上下文菜单的控制器
class CityMenuController:
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnNeiZheng').connect('pressed', self.on_neizheng)
        self.ui_obj.find_node('Panel/BtnChuZhan').connect('pressed', self.on_chuzhan)
        self.ui_obj.find_node('Panel/BtnTanSuo').connect('pressed', self.on_tansuo)

    # 内政
    def on_neizheng(self):
        ui_mgr = game_mgr.ui_mgr
        ui_mgr.defer_close(self.ui_obj)

        print_line(f'{ui_mgr.context_unit.unit_name} neizheng')

        ui_mgr.neizheng_panel.set_visible(True)
        ui_mgr.neizheng_panel.set_position(250, 100)

    # 出战
    def on_chuzhan(self):
        ui_mgr = game_mgr.ui_mgr

        ui_mgr.defer_close(self.ui_obj)
        print_line(f'{ui_mgr.context_unit.unit_name} chuzhan')

    # 探索
    def on_tansuo(self):
        ui_mgr = game_mgr.ui_mgr

        ui_mgr.defer_close(self.ui_obj)
        print_line(f'{ui_mgr.context_unit.unit_name} tansuo')

