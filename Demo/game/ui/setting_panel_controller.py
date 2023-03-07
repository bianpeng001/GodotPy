#
# 2023年3月7日 bianpeng
#
import math

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

# 设置界面
class SettingPanelController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.check_city_ai = self.ui_obj.find_node('Panel/CheckCityAI')
        self.check_city_ai.connect(PRESSED, self.on_city_ai_click)

        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED, self.on_ok_click)

        self.ui_obj.find_node('Panel/BtnClose').connect(PRESSED, self.on_close_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED, self.on_close_click)

    def init(self):
        self.enable_city_ai = game_mgr.enable_city_ai
        self.check_city_ai.set_pressed(self.enable_city_ai)

    def on_close_click(self):
        self.defer_close()

    def on_ok_click(self):
        self.defer_close()

        game_mgr.enable_city_ai = self.enable_city_ai

    def on_city_ai_click(self):
        print('city_ai', self.check_city_ai.is_pressed())
        self.enable_city_ai = self.check_city_ai.is_pressed()


