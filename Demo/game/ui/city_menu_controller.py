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

        btn_neizheng = self.ui_obj.find_node('Panel/BtnNeiZheng')

        btn_list = []
        lbl_list = ['内政','出战','探索','查看']
        
        self.ui_obj.find_node('Panel').set_size(64, 30*len(lbl_list))
        for i in range(len(lbl_list)):
            if i > 0:
                btn = btn_neizheng.dup()
            else:
                btn = btn_neizheng
            btn.set_text(lbl_list[i])
            btn.set_position(2, 2 + i*30)
            btn_list.append(btn)
            

        btn_list[0].connect(PRESSED, self.on_neizheng)
        btn_list[1].connect(PRESSED, self.on_chuzhan)
        btn_list[2].connect(PRESSED, self.on_tansuo)
        btn_list[3].connect(PRESSED, self.on_chakan)

    def init(self, city_unit):
        self.city_unit = city_unit

    # 内政
    def on_neizheng(self):
        self.defer_close()

        ui_mgr = game_mgr.ui_mgr

        city_unit = self.city_unit
        log_debug(f'{city_unit.unit_name} neizheng')

        ui_mgr.neizheng_controller.init(city_unit)
        ui_mgr.neizheng_controller.set_position(250, 80)
        ui_mgr.push_panel(ui_mgr.neizheng_controller)

    # 出战
    def on_chuzhan(self):
        self.defer_close()

        ui_mgr = game_mgr.ui_mgr

        city_unit = self.city_unit
        log_debug(f'{city_unit.unit_name} chuzhan')

        ui_mgr.chuzhan_panel_controller.init(city_unit)
        ui_mgr.chuzhan_panel_controller.popup(250, 80)
        ui_mgr.push_panel(ui_mgr.chuzhan_panel_controller)

    # 探索
    def on_tansuo(self):
        self.defer_close()

        city_unit = self.city_unit
        log_debug(f'{city_unit.unit_name} tansuo')

    # 查看
    def on_chakan(self):
        self.defer_close()

        city_unit = self.city_unit
        log_debug(f'{city_unit.unit_name} chakan')



