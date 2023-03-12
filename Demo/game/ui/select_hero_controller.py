#
# 2023年2月28日 bianpeng
#

from game.core import log_util_debug
from game.base_type import UIController
from game.game_mgr import *
from game.ui.ui_traits import *
from game.event_name import PRESSED

#
# 选择武将，是一个二级界面
# 点击属性，要进行排序
#
class SelectHeroController(UIController, PopupTrait, HeroListTrait):
    def __init__(self):
        super().__init__()
        
        self.item_list = []
        self.select_callback = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close()
        # 武将属性表头
        header = self.ui_obj.find_node('Panel/HeroList/Header')
        self.init_header(header)

    def show_dialog(self, city_unit, select_callback):
        self.city_unit = city_unit
        self.select_callback = select_callback

        self.init_hero_list()
        self.popup(250, 134)

    def on_close_click(self):
        self.defer_close()
        game_mgr.ui_mgr.pop_panel()

    def on_ok_click(self):
        self.defer_close()
        game_mgr.ui_mgr.pop_panel()

        hero_list = self.get_selected()
        if self.select_callback:
            self.select_callback(hero_list)
            self.select_callback = None

    def init_hero_list(self):
        item_node = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, self.city_unit.hero_list)

