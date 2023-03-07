#
# 2023年3月3日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 剧情
#
class StoryPanelController(UIController, PopupTrait):
    def __init__(self):
        pass


    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.image = self.ui_obj.find_node('Image')
        self.label = self.ui_obj.find_node('Label')

        self.image.set_visible(False)
        self.label.set_visible(False)


    def init(self):
        pass


