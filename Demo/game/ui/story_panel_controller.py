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
        self.bg = self.ui_obj.find_node('Bg')

        self.image.set_visible(False)
        self.label.set_visible(False)

    def init(self):
        pass

    def play_story(self, text_list, on_complete=None):
        game_mgr.co_mgr.start(self.co_play_story(text_list, on_complete))

    def co_play_story(self, text_list, on_complete):
        yield WaitForSeconds(1)

        self.popup(176, 100)
        log_debug('begin play story')

        # text_list = (
        #     '华夏大地, 不知何许年也',
        #     '山河日月, 一如汉唐',
        #     '此城虽小, 可励精图治',
        # )
        for text in text_list:
            self.show_text(text)
            yield WaitForSeconds(1)
        
        self.defer_close()

        if on_complete:
            on_complete()

    def show_text(self, text):
        self.bg.set_visible(True)
        self.label.set_visible(True)
        self.label.set_text(text)

    