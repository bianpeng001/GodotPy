#
# 2023年3月3日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController, HeroSlot
from game.hero_mgr import *
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED,\
        VALUE_CHANGED,\
        ITEM_SELECTED,\
        GUI_INPUT

ITEM_SIZE = 80

#
# 带一个位置信息
#
class HeroItem(HeroSlot):
    def __init__(self):
        super().__init__()
        
        self.hero_item_obj = None

    def get_position(self):
        col, row = divmod(self.pos_index, 3)
        return row*ITEM_SIZE, col*ITEM_SIZE

    def set_index(self, pos_index):
        self.pos_index = pos_index
        self.hero_item_obj.set_position(*self.get_position())

    def get_hero(self):
        #return game_mgr.hero_mgr.get_hero(self.hero_id)
        return get_hero(self.hero_id)

#
# 出战
#
class ChuZhanPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.max_army_mass = 1000
        self.hero_item_list = []
        self.back_hero_item_list = []

        # 处理拖拽
        self.is_drag = False
        self.pos0 = (0, 0)
        self.pos1 = (0, 0)

        self.army_amount = 0

        self.target_unit_id = 0
        self.target_pos = (0,0)

    # 是否选中状态
    def is_selected(self, hero_id):
        for item in self.hero_item_list:
            if item.hero_id == hero_id:
                return True
        return False

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close()

        self.lbl_members = self.ui_obj.find_node('Panel/LblMembers')
        self.btn_select = self.ui_obj.find_node('Panel/BtnHeros')
        self.lbl_army_mass = self.ui_obj.find_node('Panel/LblArmyAmount')
        self.slider_army_mass = self.ui_obj.find_node('Panel/SliderArmy')
        self.btn_form = self.ui_obj.find_node('Panel/BtnForm')
        self.form_list = self.ui_obj.find_node('Panel/FormList')
        self.btn_army_type = self.ui_obj.find_node('Panel/BtnType')
        self.army_type_list = self.ui_obj.find_node('Panel/TypeList')
        
        
        #self.form_root = self.ui_obj.find_node('Panel/FormRoot')
        self.btn_target = self.ui_obj.find_node('Panel/BtnTarget')
        self.btn_target.connect(PRESSED, self.on_select_target)

        self.hero_item_obj = self.ui_obj.find_node('Panel/FormRoot/HeroItem')
        self.hero_item_obj.set_visible(False)

        self.lbl_members.set_text('')
        self.btn_select.connect(PRESSED, self.on_select_click)

        self.slider_army_mass.connect(VALUE_CHANGED, self.on_slider_army_mass_changed)

        # 阵形
        # 弹出选择阵形列表
        def on_form_select():
            self.form_list.set_visible(True)
        # 阵形选择完毕
        def on_form_selected(index):
            self.form_list.set_visible(False)
            text = self.form_list.get_item_text(index)
            self.btn_form.set_text(text)
            log_debug('form_type', index, text)
        self.btn_form.connect(PRESSED, on_form_select)

        self.form_list.clear()
        for label in game_mgr.config_mgr.get_army_form_list():
            self.form_list.add_item(label)
        
        self.form_list.connect(ITEM_SELECTED, on_form_selected)
        self.form_list.set_visible(False)

        # 兵种
        def on_army_type_select():
            self.army_type_list.set_visible(True)
        def on_army_type_selected(index):
            self.army_type_list.set_visible(False)
            text = self.army_type_list.get_item_text(index)
            self.btn_army_type.set_text(text)
            log_debug('army_type', index, text)
        self.btn_army_type.connect(PRESSED, on_army_type_select)
        self.army_type_list.clear()
        for label in game_mgr.config_mgr.get_army_type_list():
            self.army_type_list.add_item(label)
        self.army_type_list.connect(ITEM_SELECTED, on_army_type_selected)
        self.army_type_list.set_visible(False)

    def on_hero_item_input(self, hero_item, pressed):
        hero_item_obj = hero_item.hero_item_obj
        input_mgr = game_mgr.input_mgr
        if input_mgr.is_mouse_pressed(1):
            if not self.is_drag:
                self.is_drag = True
                self.pos0 = hero_item.get_position()
                self.pos1 = input_mgr.get_mouse_pos()
                hero_item_obj.set_last()
            else:
                pos = input_mgr.get_mouse_pos()
                hero_item_obj.set_position(
                        self.pos0[0]+pos[0]-self.pos1[0],
                        self.pos0[1]+pos[1]-self.pos1[1])
        else:
            if self.is_drag:
                self.is_drag = False
                
                # drag stop...
                x,y = hero_item_obj.get_rect()[0:2]
                x,y = x+ITEM_SIZE/2,y+ITEM_SIZE/2
                if x >= 0 and x < ITEM_SIZE*3 and \
                        y >= 0 and y < ITEM_SIZE*3:
                    x = math.floor(x/ITEM_SIZE)
                    y = math.floor(y/ITEM_SIZE)
                    pos_index = y*3+x
                    if pos_index != hero_item.pos_index:
                        prev_item = self.get_hero_at_pos_index(pos_index)
                        if prev_item:
                            prev_item.set_index(hero_item.pos_index)
                    hero_item.set_index(pos_index)
                else:
                    hero_item.set_index(hero_item.pos_index)

    def on_select_click(self):
        def select_cb(hero_list):
            hero_list = list(filter(lambda x: not game_mgr.hero_mgr.is_hero_busy(x),
                    map(lambda x: get_hero(x), hero_list)))
            
            if hero_list:
                text = ' '.join(map(lambda x: x.hero_name, hero_list))
                self.init_form(hero_list)
            else:
                text = ''
            self.lbl_members.set_text(text)

        # select heros
        dlg = game_mgr.ui_mgr.select_hero_controller
        dlg.init(self.city_unit, select_cb)
        dlg.select([ item.hero_id for item in self.hero_item_list ])
        dlg.show()
        dlg.set_prev_panel(self)

    # 选择目标
    def on_select_target(self):
        dlg = game_mgr.ui_mgr.select_target_controller
        def select_cb():
            self.btn_target.set_text(dlg.target_name)
            self.target_unit_id = dlg.target_unit_id
            self.target_pos = dlg.target_pos
            
        dlg.init(select_cb)
        dlg.show()
        dlg.set_prev_panel(self)

    def on_slider_army_mass_changed(self, value):
        self.army_amount = round(value*0.01*self.max_army_amount)
        self.lbl_army_mass.set_text(f'{self.army_amount}/{self.max_army_amount}人')

    def init(self, city_unit):
        self.city_unit = city_unit

        self.max_army_amount = min(1000, self.city_unit.army_amount.get_value())
        self.army_amount = self.max_army_amount
        self.slider_army_mass.set_value(100)
        self.on_slider_army_mass_changed(100)

        self.clear_form()
        self.lbl_members.set_text('')
        self.form_list.set_visible(False)
        
        # 初始化目标
        self.target_unit_id = 0
        x,z = city_unit.get_xz()
        self.target_pos = (x, z+10)
        self.btn_target.set_text('%d,%d' % self.target_pos)

    def clear_form(self):
        for item in self.hero_item_list:
            item.hero_item_obj.set_visible(False)
            self.back_hero_item_list.append(item)
        self.hero_item_list.clear()

    # 刷新一下阵型的界面
    def init_form(self, hero_list):
        self.clear_form()

        for hero in hero_list:
            if len(self.back_hero_item_list) > 0:
                hero_item = self.back_hero_item_list.pop()
            else:
                hero_item = HeroItem()
                hero_item.hero_item_obj = self.hero_item_obj.dup()

                def bind_on_input(hero_item):
                    return lambda pressed: self.on_hero_item_input(hero_item, pressed)

                hero_item.hero_item_obj.connect(GUI_INPUT, bind_on_input(hero_item))
            
            hero_item.hero_id = hero.hero_id
            hero_item.set_index(len(self.hero_item_list))
            hero_item.hero_item_obj.set_visible(True)

            label = hero_item.hero_item_obj.find_node('Label')
            label.set_text(get_hero_name(hero.hero_id))
            avatar = hero_item.hero_item_obj.find_node('Avatar')

            # if hero_id % 3 == 0:
            #     tex = ResCapsule.load_resource('res://ui/face/XuShu.png')
            #     avatar.set_tex(tex.res)
            # elif hero_id % 3 == 1:
            #     tex = ResCapsule.load_resource('res://ui/face/DiaoChan.png')
            #     avatar.set_tex(tex.res)
            tex = ResCapsule.load_resource('res://ui/face/Any.png')
            avatar.set_tex(tex.res)

            self.hero_item_list.append(hero_item)

    def get_hero_at_pos_index(self, pos_index):
        for item in self.hero_item_list:
            if item.pos_index == pos_index:
                return item

    def on_ok_click(self):
        if len(self.hero_item_list) > 0:
            self.defer_close()
            log_debug('chuzhan ok', len(self.hero_item_list))

            x,y,z = self.city_unit.get_position()

            hero_list = []
            for hero_item in self.hero_item_list:
                new_hero_item = HeroSlot()
                new_hero_item.hero_id = hero_item.hero_id
                new_hero_item.pos_index = hero_item.pos_index
                hero_list.append(new_hero_item)
                game_mgr.hero_mgr.set_hero_activity(get_hero(hero_item.hero_id), ACT_CHUZHAN)

            army_amount = min(self.army_amount, self.city_unit.army_amount.value)
            self.city_unit.army_amount.value -= army_amount

            troop = game_mgr.game_play.create_troop(
                    self.city_unit,
                    hero_list,
                    x,y,z,
                    army_amount,
                    4)
            # 设置目标,策略
            troop.target_unit_id = self.target_unit_id
            troop.target_pos = self.target_pos
            # start ai
            troop.get_controller().get_brain_comp().goto_state('start')
            
        else:
            log_debug('no hero selected')





