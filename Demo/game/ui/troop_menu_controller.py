#
# 2023年2月24日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 军队的菜单
#
class TroopMenuController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        btn_list = []
        lbl_list = ['目标','策略','撤退']

        self.ui_obj.find_node('Panel').set_size(64, 30*len(lbl_list))
        btn_target = self.ui_obj.find_node('Panel/BtnTarget')

        for i in range(len(lbl_list)):
            if i > 0:
                btn = btn_target.dup()
            else:
                btn = btn_target
            btn.set_text(lbl_list[i])
            btn.set_position(2, 2 + i*30)
            btn_list.append(btn)

        btn_list[0].connect(PRESSED, self.on_select_target)
        

    def init(self, troop_unit):
        self.troop_unit = troop_unit

    def on_select_target(self):
        self.defer_close()

        dialog = game_mgr.ui_mgr.select_target_controller
        def select_cb():
            #log_debug('target', dialog.target_unit_id, dialog.target_pos)
            self.troop_unit.target_unit_id = dialog.target_unit_id
            self.troop_unit.target_pos = dialog.target_pos
            self.troop_unit.get_controller().reset_ai()

        dialog.init_dialog(select_cb)
        dialog.push_panel()



