#
# 2023年2月23日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import *

#
# 内政，农商将
#
class AlertDialogController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()

        self._co_show_alert = None
        self.text_list = []

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.text_obj = self.ui_obj.find_node('Text')
    
    def show_alert(self, text):
        self.text_list.append(text)
        if not self._co_show_alert:
            self._co_show_alert = game_mgr.co_mgr.start(self.co_show_alert())

    def co_show_alert(self):
        self.popup_screen_center()

        while self.text_list:
            self.text_obj.set_text(self.text_list.pop(0))
            yield 2.0

        self.defer_close()
        self._co_show_alert = None



