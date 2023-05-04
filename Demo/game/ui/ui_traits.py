#
# 2023年3月1日 bianpeng
#
import sys

from game.core import *
from game.game_mgr import *
from game.event_name import *

#------------------------------------------------------------
# traits 功能类，用来复用一些代码, 这里不带数据，只提供方法
#------------------------------------------------------------

# 弹框，关闭
class PopupTrait:
    def defer_close(self):
        game_mgr.ui_mgr.defer_close(self)

    def set_position(self, x,y):
        self.ui_obj.set_position(x,y)

    def popup(self, x, y):
        self.set_position(x, y)
        self.show()

    def popup_at_unit(self, unit):
        x, y = get_main_camera().world_to_screen(unit.get_position())
        self.popup(x, y)

    def popup_at_mouse(self):
        x, y = game_mgr.input_mgr.get_mouse_pos()
        self.popup(x, y)

    def popup_dialog(self, msg, time_out = 1.5):
        controller = game_mgr.ui_mgr.npc_dialog_controller
        controller.init(msg, time_out)

    def popup_screen_center(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup((screen_width-width)/2, (screen_height-height)/2)
        
    def popup_screen_bottom(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup((screen_width-width)/2, (screen_height-height))
        
    def popup_screen_bottom_left(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.popup(2, (screen_height-height)+2)

    def bind_ok_cancel_close(self, ok=True, cancel=True, close=True):
        if close:
            btn_close = self.ui_obj.find_node('Panel/BtnClose')
            if btn_close:
                btn_close.connect(PRESSED, self.on_close_click)
        
        if cancel:
            btn_cancel = self.ui_obj.find_node('Panel/BtnCancel')
            if btn_cancel:
                btn_cancel.connect(PRESSED, self.on_close_click)

        if ok:
            btn_ok = self.ui_obj.find_node('Panel/BtnOk')
            if btn_ok:
                btn_ok.connect(PRESSED, self.on_ok_click)

    def push_panel(self):
        game_mgr.ui_mgr.push_panel(self)

    def pop_panel(self):
        game_mgr.ui_mgr.pop_panel(self)

    def on_close_click(self):
        self.pop_panel()

    def on_ok_click(self):
        self.pop_panel()

# 武将列表
class HeroListTrait:
    def init_header(self, header):
        name_label = header.find_node('Label')
        column_list = ['姓名','身份','年龄','活动','武力','统率','智力','政治', '行动']
        column_width_dict = { '姓名': 80, '活动': 60, }

        for index in range(len(column_list)):
            if index == 0:
                label_obj = name_label
            else:
                label_obj = name_label.dup()
            
            col_name = column_list[index]
            label_obj.set_text(col_name)
            label_obj.set_minimum_size(column_width_dict.get(col_name, 40), 0)

    def init_items(self, item_node, hero_list):
        for item in self.item_list:
            _, item_obj = item
            item_obj.destroy()
        self.item_list.clear()

        for hero_id in hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            if hero.activity != 0:
                continue

            new_item = item_node.dup()
            new_item.set_visible(True)
            self.item_list.append((hero_id, new_item))
            
            name_label = new_item.find_node('Label')
            #log_debug(f'refcnt={sys.getrefcount(name_label)}')
            name_label.set_minimum_size(80, 0)
            name_label.set_text(hero.hero_name)
            #name_label.connect(GUI_INPUT, bind_gui_input())
            
            # 身份
            standing_label = name_label.dup()
            standing_label.set_minimum_size(40, 0)
            is_main_hero = game_mgr.hero_mgr.is_main_hero(hero.hero_id)
            standing_label.set_text('主公' if is_main_hero else '')

            # 身份
            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            age_label.set_text(f'{hero.age}')

            action_label = name_label.dup()
            action_label.set_minimum_size(60, 0)
            action_label.set_text('空闲')

            wuli_label = name_label.dup()
            wuli_label.set_minimum_size(40, 0)
            wuli_label.set_text(f'{hero.wuli}')

            tongshuai_label = name_label.dup()
            tongshuai_label.set_minimum_size(40, 0)
            tongshuai_label.set_text(f'{hero.tongshuai}')

            zhili_label = name_label.dup()
            zhili_label.set_minimum_size(40, 0)
            zhili_label.set_text(f'{hero.zhili}')

            zhengzhi_label = name_label.dup()
            zhengzhi_label.set_minimum_size(40, 0)
            zhengzhi_label.set_text(f'{hero.zhengzhi}')

            zhengzhi_label = name_label.dup()
            zhengzhi_label.set_minimum_size(40, 0)
            zhengzhi_label.set_text(f'{hero.action_points}')

    def get_selected(self):
        hero_list = []
        for item in self.item_list:
            hero_id, item_obj = item
            if item_obj.find_node('CheckBox').is_pressed():
                hero_list.append(hero_id)
        
        return hero_list

