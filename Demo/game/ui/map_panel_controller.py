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

        self.bind_ok_cancel_close()

    def init(self):
        pass

    def on_ok_click(self):
        game_mgr.ui_mgr.pop_panel(self)

        

