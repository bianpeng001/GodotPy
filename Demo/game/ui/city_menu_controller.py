#
# 2023年2月24日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

# 城池的上下文菜单的控制器
class CityMenuController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnNeiZheng').connect(PRESSED, self.on_neizheng)
        self.ui_obj.find_node('Panel/BtnChuZhan').connect(PRESSED, self.on_chuzhan)
        self.ui_obj.find_node('Panel/BtnTanSuo').connect(PRESSED, self.on_tansuo)

    # 内政
    def on_neizheng(self):
        self.defer_close()

        city_unit = game_mgr.ui_mgr.context_unit
        print_line(f'{city_unit.unit_name} neizheng')

        game_mgr.ui_mgr.neizheng_controller.init(city_unit)
        game_mgr.ui_mgr.neizheng_controller.popup(250, 100)

    # 出战
    def on_chuzhan(self):
        self.defer_close()

        city_unit = game_mgr.ui_mgr.context_unit
        print_line(f'{city_unit.unit_name} chuzhan')

        game_mgr.ui_mgr.chuzhan_panel_controller.init(city_unit)
        game_mgr.ui_mgr.chuzhan_panel_controller.popup(250, 100)

    # 探索
    def on_tansuo(self):
        ui_mgr = game_mgr.ui_mgr

        self.defer_close()
        print_line(f'{ui_mgr.context_unit.unit_name} tansuo')

