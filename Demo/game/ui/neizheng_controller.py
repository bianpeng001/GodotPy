#
# 2023年2月23日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UIController
from game.event_name import GUI_INPUT, PRESSED, VALUE_CHANGED
from game.ui.ui_traits import *

# 内政，农商将
class NeiZhengController(UIController, CloseTrait, HeroListTrait):
    def __init__(self):
        super().__init__()

        self.tab_index = 0

        self.tabs = []

        self.last_city_id = 0
        
        self.item_list = []
        self.init_header_done = False

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.btn_close = self.ui_obj.find_node('Panel/BtnClose')
        self.btn_close.connect(PRESSED, self.on_close_click)

        self.tab_bar = self.ui_obj.find_node('TabBar')
        self.tab_bar.connect('tab_changed', self.on_tab_changed)

        self.tab_zheng_obj = self.ui_obj.find_node('Panel/TabZheng')
        self.tab_jiang_obj = self.ui_obj.find_node('Panel/TabJiang')
        self.tabs = [
            self.tab_zheng_obj,
            self.tab_jiang_obj,
        ]
        self.tab_index = 0
        self.tab_bar.set_current_tab(self.tab_index)
        self.on_tab_changed()

        # slider
        zheng_obj = self.tab_zheng_obj
        zheng_obj.find_node('SliderOrderMass').connect(VALUE_CHANGED, self.on_order_slide_change)
        self.order_mass_label = zheng_obj.find_node('LblOrderMass')
        zheng_obj.find_node('SliderFarmerMass').connect(VALUE_CHANGED, self.on_farmer_slide_change)
        self.farmer_mass_label = zheng_obj.find_node('LblFarmerMass')
        zheng_obj.find_node('SliderTraderMass').connect(VALUE_CHANGED, self.on_trade_slide_change)
        self.trade_mass_label = zheng_obj.find_node('LblTraderMass')

        zheng_obj.find_node('BtnSatrap').connect(PRESSED, self.on_select_satrap)

    def on_select_satrap(self):
        game_mgr.ui_mgr.select_hero_controller.init_hero_list()
        game_mgr.ui_mgr.select_hero_controller.ui_obj.set_position(250, 100)
        game_mgr.ui_mgr.select_hero_controller.show()
        self.defer_close()

    def on_order_slide_change(self, value):
        num = round(value * 100)
        self.order_mass_label.set_text(f'{num}人')

    def on_farmer_slide_change(self, value):
        num = round(value * 100)
        self.farmer_mass_label.set_text(f'{num}人')

    def on_trade_slide_change(self, value):
        num = round(value * 100)
        self.trade_mass_label.set_text(f'{num}人')

    def on_close_click(self):
        self.defer_close()
        game_mgr.ui_mgr.npc_dialog_controller.show_dialog('诸葛亮：主公请放心。', 2)

    def on_tab_changed(self, *args):
        self.tab_index = self.tab_bar.get_current_tab()
        for i in range(len(self.tabs)):
            self.tabs[i].set_visible(i == self.tab_index)

        if self.tab_index == 1:
            self.init_hero_list()

    def init_hero_list(self):
        city = game_mgr.ui_mgr.context_unit
        if city.unit_id == self.last_city_id:
            return

        if not self.init_header_done:
            self.init_header_done = True
            header = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Header')
            self.init_header(header)

        item_node = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, city.hero_list)

        def bind_gui_input():
            a_hero = hero

            def _on_gui_input(is_pressed):
                if is_pressed:
                    log_util.debug(f'click {a_hero.hero_id} {a_hero.hero_name}')
            
            return _on_gui_input


            



