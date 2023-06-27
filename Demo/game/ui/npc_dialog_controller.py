#
# 2023年2月28日 bianpeng
#

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

    def show_text(self, text):
        self.show_text2('', text)

    def show_text2(self, speaker, text):
        self.name_label.set_text(speaker)
        self.content_label.set_text(text)
        # 动一下头像位置, 假装换了一下头像的形状
        self.face_obj.set_position(int(random_1()*10), int(random_1()*10))



