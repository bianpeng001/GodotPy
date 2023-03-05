#
# 2023年3月5日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

class MsgPanelController(UIController, PopupTrait):
    def __init__(self):
        pass


    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        