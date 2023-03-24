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
        self.show_time = 0

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.dialog_label = self.ui_obj.find_node('Label')

    def init(self, text, show_time = 1):
        self.show_time += show_time
        self.dialog_label.set_text(text)

        w1,h1 = OS.viewport_get_size()
        _,_,w2,h2 = self.ui_obj.get_rect()
        log_util.debug(f'size: {w1} {h1}, {w2} {h2}')
        self.popup((w1-w2)/2, h1-h2)
        #self.popup((1152-w2)/2, 648-h2)




