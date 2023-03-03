#
# 2023年2月23日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import *
from game.event_name import GUI_INPUT, PRESSED, VALUE_CHANGED, TAB_CHANGED

# 内政，农商将
class NeiZhengController(UIController, PopupTrait, HeroListTrait):
    def __init__(self):
        super().__init__()

        self.tabs = []
        self.tab_index = 0
       
        self.item_list = []

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.btn_close = self.ui_obj.find_node('Panel/BtnClose')
        self.btn_close.connect(PRESSED, self.on_close_click)

        self.tab_bar = self.ui_obj.find_node('TabBar')
        self.tab_bar.connect(TAB_CHANGED, self.on_tab_changed)

        self.tab_zheng_obj = self.ui_obj.find_node('Panel/TabZheng')
        self.tab_jiang_obj = self.ui_obj.find_node('Panel/TabJiang')
        self.tab_wai_obj = self.ui_obj.find_node('Panel/TabWai')
        self.tabs = [
            self.tab_zheng_obj,
            self.tab_jiang_obj,
            self.tab_wai_obj,
        ]
        self.tab_index = 0
        self.tab_bar.set_current_tab(self.tab_index)
        self.on_tab_changed()

        # neizheng tab
        self.btn_satrap = self.setup_btn_select_hero('BtnSatrap', self.on_set_satrap)
        self.btn_order_incharge = self.setup_btn_select_hero('BtnOrderCharge', self.on_set_order_incharge)
        self.btn_farmer_incharge = self.setup_btn_select_hero('BtnFarmerCharge', self.on_set_farmer_incharge)
        self.btn_trader_incharge = self.setup_btn_select_hero('BtnTraderCharge', self.on_set_trader_incharge)

        self.lbl_order_mass = self.tab_zheng_obj.find_node('LblOrderMass')
        self.lbl_farmer_mass = self.tab_zheng_obj.find_node('LblFarmerMass')
        self.lbl_trader_mass = self.tab_zheng_obj.find_node('LblTraderMass')

        self.slider_order_mass = self.tab_zheng_obj.find_node('SliderOrderMass')
        self.slider_order_mass.connect(VALUE_CHANGED, self.on_order_slide_change)
        self.slider_farmer_mass = self.tab_zheng_obj.find_node('SliderFarmerMass')
        self.slider_farmer_mass.connect(VALUE_CHANGED, self.on_farmer_slide_change)
        self.slider_trader_mass = self.tab_zheng_obj.find_node('SliderTraderMass')
        self.slider_trader_mass.connect(VALUE_CHANGED, self.on_trade_slide_change)

        # wujiang tab
        # 武将属性表头
        header = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Header')
        self.init_header(header, ['姓名', '年龄','活动','武力','统率','智力','政治'])

    def on_set_satrap(self, hero_id):
        if self.city_unit.satrap != 0 and hero_id == 0:
            satrap = game_mgr.hero_mgr.get_hero(self.city_unit.satrap)
            msg = f'{satrap.hero_name}: 请主公另选贤明。'
            self.popup_dialog(msg, 1.5)
            self.city_unit.satrap = 0
        elif hero_id != 0:
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            msg = f'{hero.hero_name}: 定当尽心竭力，不负所托。'
            self.popup_dialog(msg, 1.5)

        self.city_unit.satrap = hero_id
        # 重新计算内政的数据，更新太守造成的影响
        self.city_unit.get_controller().refresh_growth_rate()

    def on_set_order_incharge(self, hero_id):
        self.city_unit.order_incharge = hero_id
        self.city_unit.get_controller().refresh_growth_rate()

    def on_set_farmer_incharge(self, hero_id):
        self.city_unit.farmer_incharge = hero_id
        self.city_unit.get_controller().refresh_growth_rate()
    
    def on_set_trader_incharge(self, hero_id):
        self.city_unit.trader_incharge = hero_id
        self.city_unit.get_controller().refresh_growth_rate()
    
    # 根据实际情况初始化
    def init(self, city_unit):
        self.city_unit = city_unit

        self.btn_satrap.set_text(get_hero_name(city_unit.satrap))
        self.btn_order_incharge.set_text(get_hero_name(city_unit.order_incharge))
        self.btn_farmer_incharge.set_text(get_hero_name(city_unit.farmer_incharge))
        self.btn_trader_incharge.set_text(get_hero_name(city_unit.trader_incharge))

        self.lbl_order_mass.set_text(f'{city_unit.order_mass}人')
        self.lbl_farmer_mass.set_text(f'{city_unit.farmer_mass}人')
        self.lbl_trader_mass.set_text(f'{city_unit.trader_mass}人')

    # 关联按钮，到英雄选择面板
    def setup_btn_select_hero(self, btn_name, set_hero_cb):
        btn_obj = self.tab_zheng_obj.find_node(btn_name)

        def select_cb(hero_list):
            #log_util.debug(hero_list)
            if len(hero_list) > 0:
                hero = game_mgr.hero_mgr.get_hero(hero_list[0])
                btn_obj.set_text(hero.hero_name)
                set_hero_cb(hero.hero_id)
            else:
                btn_obj.set_text('')
                set_hero_cb(0)

        def on_btn_click():
            game_mgr.ui_mgr.select_hero_controller.show_dialog(self.city_unit, select_cb)
            self.defer_close()

        btn_obj.connect(PRESSED, on_btn_click)
        
        return btn_obj

    def on_order_slide_change(self, value):
        num = round(value * 10)
        self.city_unit.order_mass = num
        self.lbl_order_mass.set_text(f'{num}人')

    def on_farmer_slide_change(self, value):
        num = round(value * 10)
        self.city_unit.farmer_mass = num
        self.lbl_farmer_mass.set_text(f'{num}人')

    def on_trade_slide_change(self, value):
        num = round(value * 10)
        self.city_unit.trader_mass = num
        self.lbl_trader_mass.set_text(f'{num}人')

    def on_close_click(self):
        self.defer_close()
        if self.city_unit.satrap != 0:
            hero = game_mgr.hero_mgr.get_hero(self.city_unit.satrap)
            if hero:
                dlg = random_select_item(game_mgr.config_mgr.neizheng_strap_dialog_list)
                msg = f'{hero.hero_name}: {dlg}'
                self.popup_dialog(msg, 1.5)

    def on_tab_changed(self, *args):
        self.tab_index = self.tab_bar.get_current_tab()
        for i in range(len(self.tabs)):
            self.tabs[i].set_visible(i == self.tab_index)

        if self.tab_index == 1:
            self.init_hero_list()

    def init_hero_list(self):
        city = game_mgr.ui_mgr.context_unit

        item_node = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, city.hero_list)


