#
# 2023年3月3日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED,VALUE_CHANGED,ITEM_SELECTED,GUI_INPUT

#
# 出战
#
class ChuZhanPanelController(UIController, PopupTrait):
    def __init__(self):
        self.max_army_mass = 1000
        self.form_item_list = []

        # 处理拖拽
        self.is_drag = False
        self.pos0 = (0, 0)
        self.pos1 = (0, 0)

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close()

        self.lbl_members = self.ui_obj.find_node('Panel/LblMembers')
        self.btn_select = self.ui_obj.find_node('Panel/BtnHeros')
        self.lbl_army_mass = self.ui_obj.find_node('Panel/LblArmy')
        self.slider_army_mass = self.ui_obj.find_node('Panel/SliderArmyMass')
        self.btn_form = self.ui_obj.find_node('Panel/BtnForm')
        self.form_list = self.ui_obj.find_node('Panel/FormList')
        self.form_bg = self.ui_obj.find_node('Panel/FormBg')

        self.hero_item = self.ui_obj.find_node('Panel/FormBg/HeroItem')
        self.hero_item.connect(GUI_INPUT, self.on_hero_item_input)

        self.lbl_members.set_text('')
        self.btn_select.connect(PRESSED, self.on_select_click)

        self.slider_army_mass.connect(VALUE_CHANGED,
                self.on_slider_army_mass_changed)
        self.btn_form.connect(PRESSED, self.on_form_select)
        self.form_list.connect(ITEM_SELECTED, self.on_form_selected)

    def on_hero_item_input(self, pressed, *args):
        input_mgr = game_mgr.input_mgr
        log_debug(pressed)
        if pressed:
            if not self.is_drag:
                self.is_drag = True
                x,y,_,_ = self.hero_item.get_rect()
                self.pos0 = x,y
                self.pos1 = input_mgr.get_mouse_pos()
            else:
                x,y = input_mgr.get_mouse_pos()
                dx,dy = x-self.pos1[0],y-self.pos1[1]
                log_debug(dx, dy)
                self.hero_item.set_position(self.pos0[0]+dx, self.pos0[1]+dy)
        else:
            if self.is_drag:
                self.is_drag = False

    def on_form_select(self):
        self.form_list.set_visible(True)

    def on_form_selected(self, index):
        self.form_list.set_visible(False)
        log_debug(index)

    def on_select_click(self):
        def select_cb(hero_list):
            if len(hero_list) > 0:
                #log_util(hero_list)
                text = ','.join(map(
                        lambda x: get_hero_name(x), 
                        hero_list))
                self.init_form(hero_list)
            else:
                text = ''
            self.lbl_members.set_text(text)

        game_mgr.ui_mgr.push_panel(self)
        game_mgr.ui_mgr.select_hero_controller.show_dialog(
                self.city_unit, select_cb)

    def on_slider_army_mass_changed(self, value):
        v = round(value*0.01*self.max_army_mass)
        self.lbl_army_mass.set_text(f'{v}/{self.max_army_mass}人')

    def init(self, city_unit):
        self.city_unit = city_unit

        self.max_army_mass = 1000
        self.slider_army_mass.set_value(100)

    def init_form(self, hero_list):
        self.form_item_list.clear()

    def on_ok_click(self):
        self.defer_close()

        log_debug(f'chuzhan ok')




