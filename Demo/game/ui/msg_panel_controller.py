#
# 2023年3月5日 bianpeng
#

import queue

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
        
        self.msg_queue = queue.Queue()
        self.max_count = 50

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.container = self.ui_obj.find_node('ScrollContainer')
        self.msg_0 = self.ui_obj.find_node('ScrollContainer/VBoxContainer/Item')
        self.msg_0.set_visible(False)
        
        game_mgr.event_mgr.add(MSG_PANEL_NEW_MSG, self.on_new_msg)

    def add_msg(self, text):
        if self.msg_list.qsize() > self.max_count:
            msg = self.msg_queue.get_nowait()
        else:
            msg = self.msg_0.dup()
            msg.set_visible(True)
        msg.set_last()
        msg.set_text(text)

        self.msg_queue.put(msg)
        self.container.set_v_scroll(1000)

    def on_new_msg(self, msg):
        self.add_msg(msg)



