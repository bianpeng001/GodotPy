#
# 2023年2月23日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED,\
        ALERT_DIALOG_MSG

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
        self.text_obj.set_text('')

        game_mgr.event_mgr.add(ALERT_DIALOG_MSG, self.on_alert_msg)

    def on_alert_msg(self, text, duration):
        self.show_alert(text, duration)
    
    def show_alert(self, text, duration=1.5):
        self.text_list.append((text, duration))
        if not self._co_show_alert:
            self._co_show_alert = game_mgr.co_mgr.start(self.co_show_alert())

    def co_show_alert(self):
        self.popup_screen_center()

        while self.text_list:
            text, duration = self.text_list.pop(0)
            self.text_obj.set_text(text)
            yield duration

        self.defer_close()
        self._co_show_alert = None



