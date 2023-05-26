#
# 2023年2月28日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait

# npc对话框
class NpcDialogController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.show_time = 0

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.dialog_label = self.ui_obj.find_node('Label')

    def init(self, text='', show_time = 1):
        self.show_time = show_time
        self.dialog_label.set_text(text)

        #self.popup_screen_center()

        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup((screen_width-width)/2, screen_height-height)
        self.show()

    def show_text(self, text):
        self.dialog_label.set_text(text)





