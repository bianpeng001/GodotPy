#
# 2023年2月23日 bianpeng
#

import math

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.hero_mgr import *
from game.ui.ui_traits import *
from game.event_name import PRESSED

#
# 选择题
#
class OptionPanelController(UIController, PopupTrait):
    def __init__(self):
        self.btn_list = []
        self.pool = []

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.label_msg = self.ui_obj.find_node('Panel/LblMsg')
        self.option_1 = self.ui_obj.find_node('Panel/Option1')
        self.option_1.set_visible(False)

        btn_ok = self.ui_obj.find_node('Panel/BtnOk')
        btn_ok.connect(PRESSED, self.on_ok_click)

    def init(self, msg, option_list, callback):
        self.set_position(350, 100)
        self.callback = callback

        self.label_msg.set_text(msg)

        for btn in self.btn_list:
            btn.set_visible(False)
            self.pool.append(btn)

        x,y = 40,180
        for i in range(len(option_list)):
            if len(self.pool) > 0:
                btn = self.poop.pop()
            else:
                btn = self.option_1.dup()
            btn.set_position(x + (i % 2)*160, y + (i // 2)*30)
            opt = option_list[i]
            btn.set_text(opt)
            self.btn_list.append(btn)
            btn.set_visible(True)

    def on_ok_click(self):
        self.pop_panel()

        if self.callback:
            self.callback(0)

