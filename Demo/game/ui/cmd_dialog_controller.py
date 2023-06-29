#
# 2023年5月19日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.event_name import *
from game.ui.ui_traits import PopupTrait

#
# 军令
#
class CmdDialogController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()

        self.on_confirmed_cb = None
        
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close()
        
        self.text_obj = self.ui_obj.find_node('Panel/Text')
        
    def show_dialog(self, text, on_confirmed_cb):
        self.on_confirmed_cb  = on_confirmed_cb
        self.text_obj.set_text(text)
        self.popup_screen_center()
        
    def on_ok_click(self):
        self.defer_close()
        if self.on_confirmed_cb:
            self.on_confirmed_cb()
            self.on_confirmed_cb = None
        
        
        