#
# 2023年3月3日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 定位面板，快速去到我的城，军队，武将
#
class GotoPanelController(UIController, PopupTrait):
    def __init__(self):
        pass
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj

