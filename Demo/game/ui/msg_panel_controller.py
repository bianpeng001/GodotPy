#
# 2023年3月5日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED, MSG_PANEL_NEW_MSG

#
# 消息栏
#
class MsgPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.msg_list = []

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.msg_0 = self.ui_obj.find_node('ScrollContainer/VBoxContainer/Item')
        self.msg_0.set_visible(False)

        self.vbar = self.ui_obj.find_node('ScrollContainer').get_vscroll_bar()
        
        game_mgr.event_mgr.add(MSG_PANEL_NEW_MSG, self.on_new_msg)


    def add_msg(self, text):
        if len(self.msg_list) > 20:
            msg = self.msg_list.pop(0)
            msg.set_last()
            #self.vbar.set_value(100)
        else:
            msg = self.msg_0.dup()
            msg.set_visible(True)
        msg.set_text(text)
        self.msg_list.append(msg)


    def on_new_msg(self, msg):
        self.add_msg(msg)



