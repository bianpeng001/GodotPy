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

        self.ui_obj.find_node('Panel').set_size(64, 30*3)
        btn_target = self.ui_obj.find_node('Panel/BtnTarget')
        btn_target.connect(PRESSED, self.on_select_target)
        btn_target.set_text('目标')
        btn_target.set_position(2, 2)

        btn_2 = btn_target.dup()
        btn_2.set_position(2, 32)

        btn_3 = btn_target.dup()
        btn_3.set_position(2, 62)

    def on_select_target(self):
        self.defer_close()

        dialog = game_mgr.ui_mgr.select_target_controller
        def select_cb():
            log_debug('target', dialog.target_unit_id, dialog.target_pos)

        dialog.init_dialog(select_cb)
        dialog.push_panel()




