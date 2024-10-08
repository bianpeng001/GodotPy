#
# 2023年2月28日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import UIController
from game.event_name import PRESSED
from game.ui.ui_traits import PopupTrait, HeroListTrait

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

    def init(self, city_unit, select_callback):
        self.city_unit = city_unit
        self.select_callback = select_callback

        self.init_hero_list()
        self.set_position(250, 114)
        
    def on_ok_click(self):
        self.defer_close()

        hero_list = self.get_selected()
        if self.select_callback:
            self.select_callback(hero_list)
            self.select_callback = None

    def init_hero_list(self):
        item_node = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, self.city_unit.hero_list)

    # 选中已经选中的
    def select(self, hero_list):
        for item in self.item_list:
            check = item.ui_obj.find_node('CheckBox')
            check.set_pressed(item.hero_id in hero_list)




