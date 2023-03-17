#
# 2023年2月24日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 地面菜单
#
class GroundMenuController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnBuild').connect(PRESSED, self.on_build)

    # 建设
    def on_build(self):
        self.defer_close()

        game_mgr.ui_mgr.build_panel_controller.popup(250, 100)
        game_mgr.ui_mgr.push_panel(game_mgr.ui_mgr.build_panel_controller)

