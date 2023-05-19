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
        super().__init__()
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        
        self.chapter = self.ui_obj.find_node('Chapter')
        self.picture = self.ui_obj.find_node('Picture')
        self.text = self.ui_obj.find_node('Text')
        
        self.wait_time = 1
        
        self.init()
        
        
    def hide_all(self):
        self.chapter.set_visible(False)
        self.picture.set_visible(False)
        self.text.set_visible(False)
        
    def init(self):
        self.hide_all()
        self.set_position(176, 100)

    def play_story(self, text_list, on_complete=None):
        game_mgr.co_mgr.start(self.co_play_story(text_list, on_complete))

    def co_play_story(self, text_list, on_complete):
        self.hide_all()
        yield WaitForSeconds(self.wait_time)

        self.show()
        log_debug('begin play story')

        # text_list = (
        #     '华夏大地, 不知何许年也',
        #     '山河日月, 一如汉唐',
        #     '此城虽小, 可励精图治',
        # )
        for text in text_list:
            self.show_text(text)
            yield WaitForSeconds(self.wait_time)
        
        self.hide_all()
        self.defer_close()

        if on_complete:
            on_complete()

    def show_text(self, text):
        self.text.set_visible(True)
        label = self.text.find_node('Label')
        label.set_text(text)
        
    def show_chapter(self, text):
        self.chapter.find_node('Label').set_text(text)
        self.chapter.set_visible(True)

    