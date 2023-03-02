#
# 2023年2月23日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UIController
from game.event_name import GUI_INPUT, PRESSED, VALUE_CHANGED
from game.ui.ui_traits import *

# 内政，农商将
class NeiZhengController(UIController, PopupTrait, HeroListTrait):
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

        self.btn_satrap = self.setup_btn_select_hero('BtnSatrap', self.on_set_satrap)
        self.btn_order_incharge = self.setup_btn_select_hero('BtnOrderCharge', self.on_set_order_incharge)
        self.btn_farmer_incharge = self.setup_btn_select_hero('BtnFarmerCharge', self.on_set_farmer_incharge)
        self.btn_trader_incharge = self.setup_btn_select_hero('BtnTraderCharge', self.on_set_trader_incharge)

    def on_set_satrap(self, hero):
        self.city_unit.satrap = hero.hero_id

    def on_set_order_incharge(self, hero):
        self.city_unit.order_incharge = hero.hero_id

    def on_set_farmer_incharge(self, hero):
        self.city_unit.farmer_incharge = hero.hero_id
    
    def on_set_trader_incharge(self, hero):
        self.city_unit.trader_incharge = hero.hero_id
    
    # 根据实际情况初始化
    def init(self, city_unit):
        def get_hero_name(hero_id):
            if hero_id == 0:
                return ''
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            return hero.hero_name

        self.city_unit = city_unit

        self.btn_satrap.set_text(get_hero_name(city_unit.satrap))
        self.btn_order_incharge.set_text(get_hero_name(city_unit.order_incharge))
        self.btn_farmer_incharge.set_text(get_hero_name(city_unit.farmer_incharge))
        self.btn_trader_incharge.set_text(get_hero_name(city_unit.trader_incharge))

    # 关联按钮，到英雄选择面板
    def setup_btn_select_hero(self, btn_name, set_hero_cb):
        btn_obj = self.tab_zheng_obj.find_node(btn_name)

        def select_cb(hero_list):
            #log_util.debug(hero_list)
            if len(hero_list) > 0:
                hero = game_mgr.hero_mgr.get_hero(hero_list[0])
                btn_obj.set_text(hero.hero_name)
                set_hero_cb(hero)

        def on_btn_click():
            game_mgr.ui_mgr.select_hero_controller.show_dialog(select_cb)
            self.defer_close()

        btn_obj.connect(PRESSED, on_btn_click)
        
        return btn_obj

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

        if not self.init_header_done:
            self.init_header_done = True
            header = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Header')
            self.init_header(header)

        item_node = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, city.hero_list)


