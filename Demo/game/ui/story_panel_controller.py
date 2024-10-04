#
# 2023年3月3日 bianpeng
#

import queue

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

# 每秒停顿的字数, 方便阅读
CharsPerSecond = 10

#
# 剧情
#
class StoryPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self._co_show_text = None
        self.text_queue = queue.Queue()

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
        self.show()


    #
    # story ?
    #
    def play_story(self, text_list, on_complete=None):
        game_mgr.co_mgr.start(self.co_play_story(text_list, on_complete))

    def co_play_story(self, text_list, on_complete):
        self.hide_all()
        yield self.wait_time

        self.show()
        log_debug('begin play story')

        # text_list = (
        #     '华夏大地, 不知何许年也',
        #     '山河日月, 一如汉唐',
        #     '此城虽小, 可励精图治',
        # )
        for text in text_list:
            self.show_text(text)
            yield self.wait_time
        
        self.hide_all()
        self.defer_close()

        if on_complete:
            on_complete()

    #
    # text
    #
    def set_text(self, text):
        self.text.set_visible(True)
        label = self.text.find_node('Label')
        label.set_text(text)
    
    # 连续播放好几段对话
    def show_text(self, text, wait_time=None):
        self.text_queue.put((text, wait_time))
        if not self._co_show_text:
            def co_show_text():
                self.init()

                while self.text_queue.qsize() > 0:
                    text, wait_time = self.text_queue.get_nowait()
                    self.set_text(text)
                    if wait_time is None:
                        wait_time = 1 * max(math.ceil(len(text)/CharsPerSecond), 1.0)
                    yield wait_time

                self.defer_close()
                self._co_show_text = None
                
            self._co_show_text = game_mgr.co_mgr.start(co_show_text())

    def get_waiter(self):
        return self._co_show_text

    #
    # chapter
    #
    def set_chapter(self, text):
        self.chapter.set_visible(True)
        self.chapter.find_node('Label').set_text(text)

    def show_chapter(self, text):
        def co_show_chapter(text):
            self.init()
            self.set_chapter(text)
            yield 2.5
            self.defer_close()
        return game_mgr.co_mgr.start(co_show_chapter(text))



