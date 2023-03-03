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

        self.ui_obj.find_node('Panel/BtnClose').connect(PRESSED,
                self.on_cancel_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED,
                self.on_cancel_click)
        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED,
                self.on_ok_click)

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

        self.lbl_detail_obj = self.tab_zheng_obj.find_node('LblCityDetail')
        self.lbl_name_obj = self.tab_zheng_obj.find_node('LblCityName')

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

    # 根据实际情况初始化
    def init(self, city_unit):
        self.city_unit = city_unit

        # 缓存一些数据，用于修改，不是直接改
        self.satrap = self.city_unit.satrap
        self.order_incharge = self.city_unit.order_incharge
        self.farmer_incharge = self.city_unit.farmer_incharge
        self.trader_incharge = self.city_unit.trader_incharge

        self.order_mass = self.city_unit.order_mass
        self.farmer_mass = self.city_unit.farmer_mass
        self.trader_mass = self.city_unit.trader_mass

        # 这个不修改，只是这里用来计算的
        self.urban_mass = self.city_unit.urban_mass

        # 然后修改ui

        self.lbl_name_obj.set_text(self.city_unit.unit_name)

        self.btn_satrap.set_text(get_hero_name(self.satrap))
        self.btn_order_incharge.set_text(get_hero_name(self.order_incharge))
        self.btn_farmer_incharge.set_text(get_hero_name(self.farmer_incharge))
        self.btn_trader_incharge.set_text(get_hero_name(self.trader_incharge))

        self.lbl_order_mass.set_text(f'{city_unit.order_mass}人')
        self.lbl_farmer_mass.set_text(f'{city_unit.farmer_mass}人')
        self.lbl_trader_mass.set_text(f'{city_unit.trader_mass}人')

        text = f'''人口:{city_unit.urban_mass}人
治安:{city_unit.order_points}
农业:{city_unit.farmer_points}
商业:{city_unit.trader_points}
粮食:{city_unit.rice_amount}
银两:{city_unit.money_amount}
武将:{len(city_unit.hero_list)}人
军队:{city_unit.army_amount}人
'''
        self.lbl_detail_obj.set_text(text)

    # 任命太守
    def on_set_satrap(self, hero_id):
        self.satrap = hero_id
        # 重新计算内政的数据，更新太守造成的影响
        #self.city_unit.get_controller().refresh_growth_rate()

    # 任命治安官
    def on_set_order_incharge(self, hero_id):
        self.order_incharge = hero_id

    # 任命治安官
    def on_set_farmer_incharge(self, hero_id):
        self.farmer_incharge = hero_id
    
    # 任命治安官
    def on_set_trader_incharge(self, hero_id):
        self.trader_incharge = hero_id
    
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
            game_mgr.ui_mgr.push_panel(self)
            game_mgr.ui_mgr.select_hero_controller.show_dialog(self.city_unit, select_cb)

        btn_obj.connect(PRESSED, on_btn_click)
        
        return btn_obj

    def on_order_slide_change(self, value):
        num = round(value * 10)
        self.order_mass = num
        self.lbl_order_mass.set_text(f'{num}人')

    def on_farmer_slide_change(self, value):
        num = round(value * 10)
        self.farmer_mass = num
        self.lbl_farmer_mass.set_text(f'{num}人')

    def on_trade_slide_change(self, value):
        num = round(value * 10)
        self.trader_mass = num
        self.lbl_trader_mass.set_text(f'{num}人')

    def on_cancel_click(self):
        self.defer_close()

    def on_ok_click(self):
        self.defer_close()

        # 弹一个对话
        if self.city_unit.satrap != 0 and self.satrap == 0:
            satrap = game_mgr.hero_mgr.get_hero(self.city_unit.satrap)
            msg = f'{satrap.hero_name}: 莫非我不堪此任吗？请主公另选贤明。'
            self.popup_dialog(msg, 1.5)
        elif self.city_unit.satrap == 0 and self.satrap != 0:
            hero = game_mgr.hero_mgr.get_hero(self.satrap)
            msg = f'{hero.hero_name}: 定当尽心竭力，不负所托。'
            self.popup_dialog(msg, 1.5)
        elif self.satrap != 0:
            hero = game_mgr.hero_mgr.get_hero(self.satrap)
            dlg = random_select_item(game_mgr.config_mgr.neizheng_strap_dialog_list)
            msg = f'{hero.hero_name}: {dlg}'
            self.popup_dialog(msg, 1.5)

        # 数据回写
        self.city_unit.satrap = self.satrap
        self.city_unit.order_incharge = self.order_incharge
        self.city_unit.farmer_incharge = self.farmer_incharge
        self.city_unit.trader_incharge = self.trader_incharge

        self.city_unit.order_mass = self.order_mass
        self.city_unit.farmer_mass = self.farmer_mass
        self.city_unit.trader_mass = self.trader_mass

        # 并重新计算
        self.city_unit.get_controller().refresh_growth_rate()

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


