#
# 2023年2月23日 bianpeng
#

import math

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.hero_mgr import *
from game.ui.ui_traits import *
from game.event_name import GUI_INPUT, PRESSED, VALUE_CHANGED, TAB_CHANGED

# 内政，农商将
class NeiZhengController(UIController, PopupTrait, HeroListTrait):
    def __init__(self):
        super().__init__()

        self.tabs = []
        self.tab_index = 0

        self.item_list = []
        self.ignore_slider_change = False

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.bind_ok_cancel_close()

        self.tab_bar = self.ui_obj.find_node('TabBar')
        self.tab_bar.connect(TAB_CHANGED, self.on_tab_changed)

        self.tab_zheng_obj = self.ui_obj.find_node('Panel/TabZheng')
        self.tab_jiang_obj = self.ui_obj.find_node('Panel/TabJiang')
        self.tab_cases_obj = self.ui_obj.find_node('Panel/TabCases')
        self.tab_produce_obj = self.ui_obj.find_node('Panel/TabProduce')
        self.tabs = [
            self.tab_zheng_obj,
            self.tab_jiang_obj,
            self.tab_cases_obj,
            self.tab_produce_obj
        ]

        # 内政页
        self.lbl_detail_obj = self.tab_zheng_obj.find_node('LblCityDetail')
        self.lbl_name_obj = self.tab_zheng_obj.find_node('LblCityName')

        # 根据城的级别,县尉,郡守,太守
        self.lbl_satrap = self.ui_obj.find_node('Panel/TabZheng/LblSatrap')

        self.btn_satrap = self.setup_btn_select_hero('BtnSatrap', self.on_set_satrap)
        self.btn_order_incharge = self.setup_btn_select_hero('BtnOrderCharge', self.on_set_order_incharge)
        self.btn_farmer_incharge = self.setup_btn_select_hero('BtnFarmerCharge', self.on_set_farmer_incharge)
        self.btn_trader_incharge = self.setup_btn_select_hero('BtnTraderCharge', self.on_set_trader_incharge)
        self.btn_fax_incharge = self.setup_btn_select_hero('BtnFaxCharge', self.on_set_fax_incharge)

        self.lbl_order_mass = self.tab_zheng_obj.find_node('LblOrderMass')
        self.lbl_farmer_mass = self.tab_zheng_obj.find_node('LblFarmerMass')
        self.lbl_trader_mass = self.tab_zheng_obj.find_node('LblTraderMass')
        self.lbl_fax_rate_value = self.tab_zheng_obj.find_node('LblFaxRateValue')

        self.slider_order_mass = self.tab_zheng_obj.find_node('SliderOrderMass')
        self.slider_order_mass.connect(VALUE_CHANGED, self.on_order_slide_change)
        self.slider_farmer_mass = self.tab_zheng_obj.find_node('SliderFarmerMass')
        self.slider_farmer_mass.connect(VALUE_CHANGED, self.on_farmer_slide_change)
        self.slider_trader_mass = self.tab_zheng_obj.find_node('SliderTraderMass')
        self.slider_trader_mass.connect(VALUE_CHANGED, self.on_trader_slide_change)

        # 这三个值是联动的, 改一个,三个相加 <= 100
        self.slider_value_list = [100, 0, 0]

        self.slider_fax_rate = self.tab_zheng_obj.find_node('SliderFaxRate')
        self.slider_fax_rate.connect(VALUE_CHANGED, self.on_fax_slide_change)

        # 任免页
        # 武将属性表头
        header = self.tab_jiang_obj.find_node('HeroList/Header')
        self.init_header(header)

        btn_dengyong = self.tab_jiang_obj.find_node('BtnDengYong')
        rm_btns = [btn_dengyong, ]
        rm_texts = ['致仕','训诫','赏赐','爵位','搜索','派遣','征招']
        rm_btns = [btn_dengyong.dup() for i in range(len(rm_texts) - 1)]
        rm_btns.append(btn_dengyong)
        for i in range(len(rm_btns)):
            btn = rm_btns[i]
            btn.set_text(rm_texts[i])
            btn.set_position(20+(50+10)*i, 294)
            btn.connect(PRESSED, self.on_rm_btn_click)

    # 根据实际情况初始化
    def init(self, city_unit):
        self.city_unit = city_unit

        # 根据城的级别, 这个称呼有变化
        satrap_labels = ['首长','县令','太守','州牧']
        self.lbl_satrap.set_text(satrap_labels[self.city_unit.city_type])

        # 缓存一些数据，用于修改，不是直接改
        self.satrap = self.city_unit.satrap
        self.order_incharge = self.city_unit.order_incharge
        self.farmer_incharge = self.city_unit.farmer_incharge
        self.trader_incharge = self.city_unit.trader_incharge
        self.fax_incharge = self.city_unit.fax_incharge

        self.order_mass = self.city_unit.order_mass
        self.farmer_mass = self.city_unit.farmer_mass
        self.trader_mass = self.city_unit.trader_mass
        self.fax_rate = self.city_unit.fax_rate

        # 这个不修改，只是这里用来计算的
        self.population = self.city_unit.population.get_value()

        # 下面初始化ui
        
        # 九州
        province = game_mgr.unit_mgr.get_province(*self.city_unit.get_xz())
        
        # 城市的名字
        self.lbl_name_obj.set_text(f'{province} {self.city_unit.unit_name}')

        # 官员负责人
        self.btn_satrap.set_text(get_hero_name(self.satrap))
        self.btn_order_incharge.set_text(get_hero_name(self.order_incharge))
        self.btn_farmer_incharge.set_text(get_hero_name(self.farmer_incharge))
        self.btn_trader_incharge.set_text(get_hero_name(self.trader_incharge))
        self.btn_fax_incharge.set_text(get_hero_name(self.fax_incharge))

        self.lbl_fax_rate_value.set_text(f'{self.fax_rate}%')

        self.slider_value_list = [
                self.order_mass,
                self.farmer_mass,
                self.trader_mass]
        self.update_slider_value(0, self.order_mass)
        
        # 税率
        self.slider_fax_rate.set_value(self.fax_rate)
        # 详情
        self.update_city_detail()
        
        # 设置当前页
        self.tab_index = 0
        self.tab_bar.set_current_tab(self.tab_index)
        self.on_tab_changed(0)

        self.init_hero_list()

    # 详情
    def update_city_detail(self):
        city_unit = self.city_unit

        config_mgr = game_mgr.config_mgr

        rates = city_unit.get_controller().calc_growth_rate(
                self.satrap, 
                self.order_incharge,
                self.farmer_incharge,
                self.trader_incharge)

        order,rice,money,population,army = map(config_mgr.format_colored_label, rates)

        text = f'''人口 {self.population}人 {population}
治安 {city_unit.order_points} {order}
农业 {city_unit.farmer_points}
商业 {city_unit.trader_points}
粮食 {round(city_unit.rice_amount.get_value())} {rice}
银两 {round(city_unit.money_amount.get_value())} {money}
军队 {round(city_unit.army_amount.get_value())}人 {army}
武将 {len(city_unit.hero_list)}人
'''
        self.lbl_detail_obj.set_text(text)

    # 联动修改, 总数小于100
    def update_slider_value(self, index, value):
        values = self.slider_value_list
        values[index] = round(value)
        
        count = len(values)
        # 这个就挺和谐的
        overflow = sum(values) - 100

        # 第一轮扣超过平均数的, 相当于从大的开始
        if overflow > 0:
            avg = (100 - values[index]) // (count - 1)
            for i in range(count):
                if i != index and values[i] > avg:
                    v = values[i] - avg - overflow
                    if v >= 0:
                        values[i] = v + avg
                        overflow = 0
                    else:
                        overflow -= (values[i] - avg)
                        values[i] = avg

        # 第二轮, 从可以扣的开始
        if overflow > 0:
            for i in range(count):
                if i != index:
                    v = values[i] - overflow
                    if v >= 0:
                        values[i] = v
                        overflow = 0
                        break
                    else:
                        overflow -= values[i]
                        values[i] = 0

        #print(values)
        #print(sum(values))

        # 标记是否要在事件里面,ignore修改,用来区分被动修改,不触发避免死循环
        self.ignore_slider_change = True
        self.slider_order_mass.set_value(values[0])
        self.slider_farmer_mass.set_value(values[1])
        self.slider_trader_mass.set_value(values[2])
        self.ignore_slider_change = False

        # 把修改值的,也都放到这里来,这样省得在value_changed里面去关联
        self.order_mass, self.farmer_mass, self.trader_mass = values
        #print(values)

        calc_mass = game_mgr.config_mgr.calc_mass
        v0, v1, v2 = map(lambda x: calc_mass(x, self.population), values)

        self.lbl_order_mass.set_text(f'{v0}人')
        self.lbl_farmer_mass.set_text(f'{v1}人')
        self.lbl_trader_mass.set_text(f'{v2}人')

    # 任命太守
    def on_set_satrap(self, hero_id):
        self.satrap = hero_id
        # 重新计算内政的数据，更新太守造成的影响
        self.update_city_detail()

    # 税务官
    def on_set_fax_incharge(self, hero_id):
        self.fax_incharge = hero_id
        self.update_city_detail()

    # 任命治安官
    def on_set_order_incharge(self, hero_id):
        self.order_incharge = hero_id
        self.update_city_detail()

    # 任命治安官
    def on_set_farmer_incharge(self, hero_id):
        self.farmer_incharge = hero_id
        self.update_city_detail()
    
    # 任命商业官
    def on_set_trader_incharge(self, hero_id):
        self.trader_incharge = hero_id
        self.update_city_detail()
    
    # 关联按钮，到英雄选择面板
    def setup_btn_select_hero(self, btn_name, set_hero_cb):
        btn_obj = self.tab_zheng_obj.find_node(btn_name)

        def select_cb(hero_list):
            #log_util.debug(hero_list)
            if len(hero_list) > 0:
                hero = get_hero(hero_list[0])
                btn_obj.set_text(hero.hero_name)
                set_hero_cb(hero.hero_id)
            else:
                btn_obj.set_text('')
                set_hero_cb(0)

        def on_btn_click():
            dlg = game_mgr.ui_mgr.select_hero_controller
            dlg.init(self.city_unit, select_cb)
            dlg.select([])
            dlg.set_prev_panel(self)
            dlg.show()

        btn_obj.connect(PRESSED, on_btn_click)
        return btn_obj

    def on_order_slide_change(self, value):
        if not self.ignore_slider_change:
            self.update_slider_value(0, value)

    def on_farmer_slide_change(self, value):
        if not self.ignore_slider_change:
            self.update_slider_value(1, value)

    def on_trader_slide_change(self, value):
        if not self.ignore_slider_change:
            self.update_slider_value(2, value)

    def on_fax_slide_change(self, value):
        self.fax_rate = round(value)
        self.lbl_fax_rate_value.set_text(f'{self.fax_rate}%')

    def on_rm_btn_click(self):
        hero_list = self.get_selected()
        if len(hero_list) > 0:
            speaker_name = get_hero_name(hero_list[0])
            self.popup_dialog(f'{speaker_name}: 任重而道远,贵在持之以恒', 1.5)

    def on_tab_changed(self, index):
        self.tab_index = index
        for i in range(len(self.tabs)):
            self.tabs[i].set_visible(i == self.tab_index)

    def init_hero_list(self):
        item_node = self.tab_jiang_obj.find_node('HeroList/ScrollContainer/VBoxContainer/Item')
        self.init_items(item_node, self.city_unit.hero_list)

    def on_ok_click(self):
        #self.pop_panel()
        self.defer_close()

        # 弹一个对话
        if self.city_unit.satrap != 0 and self.satrap == 0:
            satrap = game_mgr.hero_mgr.get_hero(self.city_unit.satrap)
            msg = f'{satrap.hero_name}: 莫非我不堪此任?'
            self.popup_dialog(msg, 1.5)
        elif self.city_unit.satrap == 0 and self.satrap != 0:
            hero = game_mgr.hero_mgr.get_hero(self.satrap)
            msg = f'{hero.hero_name}: 定当尽心竭力,不负所托.'
            self.popup_dialog(msg, 1.5)
        elif self.satrap != 0:
            hero = game_mgr.hero_mgr.get_hero(self.satrap)
            dlg = random_select_item(game_mgr.config_mgr.neizheng_strap_dialog_list)
            msg = f'{hero.hero_name}: {dlg}'
            self.popup_dialog(msg, 1.5)

        def set_action(hero_id):
            game_mgr.hero_mgr.set_hero_activity(hero_id, ACT_NEIZHENG)

        set_action(self.satrap)
        set_action(self.order_incharge)
        set_action(self.farmer_incharge)
        set_action(self.trader_incharge)
        set_action(self.fax_incharge)

        # 数据回写
        self.city_unit.satrap = self.satrap
        self.city_unit.order_incharge = self.order_incharge
        self.city_unit.farmer_incharge = self.farmer_incharge
        self.city_unit.trader_incharge = self.trader_incharge
        self.city_unit.fax_incharge = self.fax_incharge

        self.city_unit.order_mass = self.order_mass
        self.city_unit.farmer_mass = self.farmer_mass
        self.city_unit.trader_mass = self.trader_mass
        self.city_unit.fax_rate = self.fax_rate
        
        log_debug('apply city property changes')



