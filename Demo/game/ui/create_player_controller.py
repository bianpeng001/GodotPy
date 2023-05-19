#
# 2023年4月1日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED
from game.config_mgr import new_hero_name

#
# 创建新主公
#
class CreatePlayerController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close(cancel=False,close=False)
        
        label = self.ui_obj.find_node('Panel/Label')
        label.set_text(game_mgr.config_mgr.new_player_text)
        
        self.ui_obj.find_node('Panel/BtnChange').connect(PRESSED, self.change_click)
        self.text_edit = self.ui_obj.find_node('Panel/TextEdit')
        
    def change_click(self):
        self.player_name = new_hero_name()
        self.text_edit.set_text(self.player_name)
        
    def show_dialog(self, ok_cb):
        self.change_click()
        
        self.popup_screen_center()
        self.ok_cb = ok_cb
        
    def on_ok_click(self):
        self.defer_close()
        #log_debug(self.player_name)
        if self.ok_cb:
            self.ok_cb(self.player_name)



