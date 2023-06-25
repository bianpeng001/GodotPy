#
# 2023年2月28日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait

#
# npc对话框
#
class NpcDialogController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()

        self.co = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.content_label = self.ui_obj.find_node('Label')
        self.name_label = self.ui_obj.find_node('Face/Name')
        self.face_obj = self.ui_obj.find_node('Face')

    def init(self, text=''):
        self.content_label.set_text(text)

        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup((screen_width-width)/2+60, screen_height-height-1)
        self.show()

    def auto_close(self, timeout):
        if self.co:
            game_mgr.co_mgr.cancel(self.co)
            self.co = None

        def wait_close():
            yield timeout
            self.defer_close()
        
        self.co = game_mgr.co_mgr.start(wait_close())

    def show_text(self, text):
        self.show_text2('', text)

    def show_text2(self, speaker, text):
        self.content_label.set_text(text)
        self.name_label.set_text(speaker)
        self.face_obj.set_position(int(random_1()*10), int(random_1()*10))



