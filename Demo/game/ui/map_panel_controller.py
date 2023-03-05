#
# 2023年3月3日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

# 世界地图
class MapPanelController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnClose').connect(PRESSED, self.on_close_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED, self.on_close_click)
        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED, self.on_ok_click)

    def on_ok_click(self):
        self.defer_close()


    def on_close_click(self):
        self.defer_close()
        

