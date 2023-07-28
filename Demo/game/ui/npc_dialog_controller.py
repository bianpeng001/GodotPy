#
# 2023年2月28日 bianpeng
#
import math
import queue

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait

#
# npc对话框
#
class NpcDialogController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()

        self._co_show_dialog = None
        self.dialog_queue = queue.Queue()

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.content_label = self.ui_obj.find_node('Label')
        self.name_label = self.ui_obj.find_node('Face/Name')
        self.face_obj = self.ui_obj.find_node('Face')

    def init(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup((screen_width-width)/2+70, screen_height-height-2)
        
        self.set_text('', '')

        self.show()

    def set_text(self, speaker, text):
        self.name_label.set_text(speaker)
        self.content_label.set_text(text)
        # 动一下头像位置, 假装换了一下头像的形状
        self.face_obj.set_position(int(random_1()*10), int(random_1()*10))

    def show_dialog(self, speaker, text = '', wait_time=None):
        self.dialog_queue.put((speaker, text, wait_time))
        if not self._co_show_dialog:
                def co_show_dialog():
                    self.init()

                    while self.dialog_queue.qsize() > 0:
                        speaker,text,wait_time = self.dialog_queue.get_nowait()

                        if speaker is None:
                            #self.defer_close()
                            if self.is_show():
                                self.hide()
                            yield 1.0
                        else:
                            if not self.is_show():
                                self.show()
                            self.set_text(speaker, text)
                            if wait_time is None:
                                wait_time = 1.5 * max(math.ceil(len(text)/15), 1.0)
                            yield wait_time
                            

                    self.defer_close()
                    self._co_show_dialog = None

            self._co_show_dialog = game_mgr.co_mgr.start(co_show_dialog())

    def get_waiter(self):
        return self._co_show_dialog


