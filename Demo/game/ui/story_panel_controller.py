#
# 2023年3月3日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED
from game.wait import *

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

    def play_story(self):
        game_mgr.co_mgr.start(self.co_play_story())

    def co_play_story(self):
        yield WaitForSeconds(3)

        self.popup(350, 100)
        log_util_debug('begin play story')

        text_list = (
            '华夏大地,不知何许年也',
            '山河日月,一如汉唐',
            '此城虽小,也可励精图治',
            )
        for text in text_list:
            self.show_text(text)
            yield WaitForSeconds(3)
        
        self.defer_close()

    def show_text(self, text):
        self.label.set_text(text)
        self.label.set_visible(True)

    