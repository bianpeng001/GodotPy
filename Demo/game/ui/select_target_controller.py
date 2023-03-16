#
# 2023年3月16日 bianpeng
#

from game.core import log_debug
from game.base_type import UIController
from game.game_mgr import *
from game.event_name import PRESSED
from game.ui.ui_traits import *

#
# 选择目标
#
class SelectTargetController(UIController, PopupTrait):
    def __init__(self):
        self.target_name = ''
        self.target_type = 0
        self.target_unit_id = 0

        self.select_callback = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.bind_ok_cancel_close(close=False)

    def show_dialog(self, select_callback):
        self.select_callback = select_callback
        self.popup(240, 70)
    
    def on_close_click(self):
        self.defer_close()
        game_mgr.ui_mgr.pop_panel()

    def on_ok_click(self):
        self.defer_close()
        game_mgr.ui_mgr.pop_panel()

        self.target_name = '长坂坡'
        
        if self.select_callback:
            self.select_callback()




