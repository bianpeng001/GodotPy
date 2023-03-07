#
# 2023年2月28日 bianpeng
#

from game.core import log_util
from game.base_type import UIController
from game.event_name import PRESSED
from game.game_mgr import game_mgr
from game.ui.ui_traits import *

#
# 选择武将，是一个二级界面
# 点击属性，要进行排序
#
class SelectHeroController(UIController, PopupTrait, HeroListTrait):
    def __init__(self):
        super().__init__()
        
        self.item_list = []
        self.ok_cb = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED, self.on_ok_click)
        self.ui_obj.find_node('Panel/BtnClose').connect(PRESSED, self.on_cancel_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED, self.on_cancel_click)

        # 武将属性表头
        header = self.ui_obj.find_node('Panel/HeroList/Header')
        self.init_header(header, ['姓名', '年龄','活动','武力','统率','智力','政治'])

    def show_dialog(self, city_unit, ok_cb):
        self.city_unit = city_unit
        self.init_hero_list()
        self.ok_cb = ok_cb
        self.popup(250, 100)

    def on_cancel_click(self):
        self.defer_close()
        game_mgr.ui_mgr.pop_panel()

    def on_ok_click(self):
        self.defer_close()
        game_mgr.ui_mgr.pop_panel()

        hero_list = self.get_selected()
        if self.ok_cb:
            self.ok_cb(hero_list)
            self.ok_cb = None

    def init_hero_list(self):
        item_node = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, self.city_unit.hero_list)



