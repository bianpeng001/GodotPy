#
# 2023年2月28日 bianpeng
#
import math

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
        self.dialog_list = []

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.content_label = self.ui_obj.find_node('Label')
        self.name_label = self.ui_obj.find_node('Face/Name')
        self.face_obj = self.ui_obj.find_node('Face')

    def init(self):
        #self.name_label.set_text('')
        #self.content_label.set_text(text)

        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup((screen_width-width)/2+70, screen_height-height-2)
        self.show()

    def set_text(self, speaker, text):
        self.name_label.set_text(speaker)
        self.content_label.set_text(text)
        # 动一下头像位置, 假装换了一下头像的形状
        self.face_obj.set_position(int(random_1()*10), int(random_1()*10))

    def show_dialog(self, speaker, text):
        self.dialog_list.append((speaker, text))
        if not self._co_show_dialog:
            self._co_show_dialog = game_mgr.co_mgr.start(self.co_show_dialog())

    def co_show_dialog(self):
        self.init()

        while self.dialog_list:
            item = self.dialog_list.pop(0)
            if len(item) == 2:
                speaker,text = item
                self.set_text(speaker, text)
                yield 1.5 * math.ceil(len(text)/15)
            elif len(item) == 3:
                speaker,text,time = item
                self.set_text(speaker, text)
                yield time

        self.defer_close()
        self._co_show_dialog = None

    def get_waiter(self):
        return self._co_show_dialog



