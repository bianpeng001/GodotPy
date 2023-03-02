#
# 2023年2月28日 bianpeng
#

from game.core import log_util
from game.base_type import UIController
from game.event_name import PRESSED
from game.game_mgr import game_mgr
from game.ui.ui_traits import *

# 选择武将
class SelectHeroController(UIController, PopupTrait, HeroListTrait):
    def __init__(self):
        super().__init__()
        
        self.item_list = []
        self.init_header_done = False
        self.on_ok_cb = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED, self.on_ok_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED, self.on_cancel_click)
        self.ui_obj.find_node('Panel/BtnClose').connect(PRESSED, self.on_cancel_click)

    def show_dialog(self, on_ok_cb):
        self.init_hero_list()
        self.ui_obj.set_position(250, 100)
        self.on_ok_cb = on_ok_cb
        self.show()

    def on_cancel_click(self):
        self.defer_close()
        game_mgr.ui_mgr.neizheng_controller.show()

    def on_ok_click(self):
        self.defer_close()
        game_mgr.ui_mgr.neizheng_controller.show()

        hero_list = []
        for item in self.item_list:
            hero_id, item_obj = item
            if item_obj.find_node('CheckBox').is_pressed():
                hero_list.append(hero_id)

        if self.on_ok_cb:
            self.on_ok_cb(hero_list)

    def init_hero_list(self):
        city = game_mgr.ui_mgr.context_unit

        if not self.init_header_done:
            self.init_header_done = True
            header = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Header')
            self.init_header(header)

        item_node = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, city.hero_list)

