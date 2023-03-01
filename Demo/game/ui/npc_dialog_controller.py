#
# 2023年2月28日 bianpeng
#

from game.game_mgr import game_mgr
from game.base_type import UIController
from game.ui.ui_traits import CloseTrait

# npc对话框
class NpcDialogController(UIController, CloseTrait):
    def __init__(self):
        self.show_time = 0

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.dialog_label = self.ui_obj.find_node('Label')

    def show_dialog(self, text, show_time = 1):
        self.show_time += show_time
        self.dialog_label.set_text(text)

        self.ui_obj.set_position(350, 480)
        self.show()




