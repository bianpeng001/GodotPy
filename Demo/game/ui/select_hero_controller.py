#
# 2023年2月28日 bianpeng
#

from game.base_type import UIController
from game.event_name import PRESSED
from game.game_mgr import game_mgr
from game.ui.ui_traits import *

# 选择武将
class SelectHeroController(UIController, CloseTrait, HeroListTrait):
    def __init__(self):
        super().__init__()
        
        self.item_list = []
        self.init_header_done = False

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED, self.on_ok_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED, self.on_cancel_click)

    def on_cancel_click(self):
        self.defer_close()
        game_mgr.ui_mgr.neizheng_controller.show()

    def on_ok_click(self):
        self.defer_close()
        game_mgr.ui_mgr.neizheng_controller.show()

    def init_hero_list(self):
        city = game_mgr.ui_mgr.context_unit
        
        for item in self.item_list:
            item.destroy()

        if not self.init_header_done:
            self.init_header_done = True
            header = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Header')
            self.init_header(header)

        item_node = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, city.hero_list)



