#
# 2023年4月11日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import UIController
from game.event_name import PRESSED
from game.ui.ui_traits import PopupTrait, HeroListTrait

#
# 指令界面
#
class CmdPanelController(UIController, PopupTrait):
    def __init__(self):
        pass
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        
        


