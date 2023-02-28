#
# 2023年2月23日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UIController
from game.event_name import GUI_INPUT, PRESSED, VALUE_CHANGED

# 内政，农商将
class NeiZhengController(UIController):
    def __init__(self):
        super().__init__()

        self.tab_index = 0

        self.tabs = []

        self.last_city_id = 0
        self.item_list = []
        self.init_header = False

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
        game_mgr.ui_mgr.select_hero_controller.ui_obj.set_position(250, 100)
        game_mgr.ui_mgr.select_hero_controller.show()
        game_mgr.ui_mgr.defer_close(self.ui_obj)

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
        game_mgr.ui_mgr.defer_close(self.ui_obj)

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

        if not self.init_header:
            self.init_header = True
            header = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Header')
            
            name_label = header.find_node('Label')
            name_label.set_minimum_size(80, 0)
            name_label.set_text('姓名')

            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            age_label.set_text('年龄')

            action_label = name_label.dup()
            action_label.set_minimum_size(60, 0)
            action_label.set_text('活动')

            wuli_label = name_label.dup()
            wuli_label.set_minimum_size(40, 0)
            wuli_label.set_text('武力')

            tongshuai_label = name_label.dup()
            tongshuai_label.set_minimum_size(40, 0)
            tongshuai_label.set_text('统率')

            zhili_label = name_label.dup()
            zhili_label.set_minimum_size(40, 0)
            zhili_label.set_text('智力')

            zhengzhi_label = name_label.dup()
            zhengzhi_label.set_minimum_size(40, 0)
            zhengzhi_label.set_text('政治')

        # items...
        for item in self.item_list:
            item.destroy()

        hero_list = city.hero_list
        item = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Item')
        for hero_id in hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            #print(hero_id, hero)

            def bind_gui_input():
                a_hero = hero

                def _on_gui_input(is_pressed):
                    if is_pressed:
                        log_util.debug(f'click {a_hero.hero_id} {a_hero.hero_name}')
                
                return _on_gui_input

            new_item = item.dup()
            new_item.set_visible(True)
            self.item_list.append(new_item)

            name_label = new_item.find_node('Label')
            name_label.set_minimum_size(80, 0)
            name_label.set_text(hero.hero_name)
            name_label.connect(GUI_INPUT, bind_gui_input())

            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            age_label.set_text(f'{hero.age}')

            action_label = name_label.dup()
            action_label.set_minimum_size(60, 0)
            action_label.set_text('空闲')

            zhili_label = name_label.dup()
            zhili_label.set_minimum_size(40, 0)
            zhili_label.set_text(f'{hero.zhili}')

            tongshuai_label = name_label.dup()
            tongshuai_label.set_minimum_size(40, 0)
            tongshuai_label.set_text(f'{hero.tongshuai}')

            wuli_label = name_label.dup()
            wuli_label.set_minimum_size(40, 0)
            wuli_label.set_text(f'{hero.wuli}')

            zhengzhi_label = name_label.dup()
            zhengzhi_label.set_minimum_size(40, 0)
            zhengzhi_label.set_text(f'{hero.zhengzhi}')



