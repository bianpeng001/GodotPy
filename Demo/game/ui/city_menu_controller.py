#
# 2023年2月24日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 城池的上下文菜单的控制器
#
class CityMenuController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel').set_size(64, 30*4)
        btn_neizheng = self.ui_obj.find_node('Panel/BtnNeiZheng')
        btn_neizheng.connect(PRESSED, self.on_neizheng)
        btn_neizheng.set_position(2, 2)

        btn_chuzhan = btn_neizheng.dup()
        btn_chuzhan.set_text('出战')
        btn_chuzhan.set_position(2, 32)
        btn_chuzhan.connect(PRESSED, self.on_chuzhan)

        btn_tansuo = btn_neizheng.dup()
        btn_tansuo.set_text('探索')
        btn_tansuo.set_position(2, 62)
        btn_tansuo.connect(PRESSED, self.on_tansuo)

        btn_chakan = btn_neizheng.dup()
        btn_chakan.set_text('查看')
        btn_chakan.set_position(2, 92)
        btn_chakan.connect(PRESSED, self.on_chakan)

    # 内政
    def on_neizheng(self):
        self.defer_close()

        ui_mgr = game_mgr.ui_mgr

        city_unit = ui_mgr.context_unit
        log_debug(f'{city_unit.unit_name} neizheng')

        ui_mgr.neizheng_controller.init(city_unit)
        ui_mgr.neizheng_controller.popup(250, 100)
        ui_mgr.push_panel(ui_mgr.neizheng_controller)

    # 出战
    def on_chuzhan(self):
        self.defer_close()

        ui_mgr = game_mgr.ui_mgr

        city_unit = ui_mgr.context_unit
        log_debug(f'{city_unit.unit_name} chuzhan')

        ui_mgr.chuzhan_panel_controller.init(city_unit)
        ui_mgr.chuzhan_panel_controller.popup(250, 100)
        ui_mgr.push_panel(ui_mgr.chuzhan_panel_controller)

    # 探索
    def on_tansuo(self):
        self.defer_close()

        city_unit = game_mgr.ui_mgr.context_unit
        log_debug(f'{city_unit.unit_name} tansuo')

    # 查看
    def on_chakan(self):
        self.defer_close()

        city_unit = game_mgr.ui_mgr.context_unit
        log_debug(f'{city_unit.unit_name} chakan')



