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

        self.player_name = ''
        self.ok_cb = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close(cancel=False,close=False)
        
        label = self.ui_obj.find_node('Panel/Label')
        label.set_text(game_mgr.config_mgr.new_player_text)
        
        btn_change = self.ui_obj.find_node('Panel/BtnChange')
        btn_change.connect(PRESSED, self.on_change_click)

        self.text_edit_obj = self.ui_obj.find_node('Panel/TextEdit')
        
    def on_change_click(self):
        self.player_name = game_mgr.hero_mgr.gen_unique_hero_name(consume=False)
        self.text_edit_obj.set_text(self.player_name)
        
    def show_dialog(self, ok_cb=None):
        self.on_change_click()
        
        self.popup_screen_center()
        self.ok_cb = ok_cb
        
    def on_ok_click(self):
        self.defer_close()
        if self.ok_cb:
            self.ok_cb(self.player_name)



