#
# 2023年3月1日 bianpeng
# 功能类，用来复用一些代码, 这里不带数据，只提供方法
#
import sys

from game.core import *
from game.game_mgr import *
from game.event_name import PRESSED

#
# 弹框，关闭
#
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

    # def popup_dialog(self, speaker, msg, timeout=1.5):
    #     dlg = game_mgr.ui_mgr.npc_dialog_controller
    #     dlg.init()
    #     dlg.show_text2(speaker, msg)
    #     dlg.auto_close(timeout)

    # 自动延时关闭, 用一个coroutine来做, 略显大材小用
    def auto_close(self, timeout):
        def co_wait_close():
            yield timeout
            self.defer_close()
        game_mgr.co_mgr.start(co_wait_close())

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
        self.popup(2, (screen_height-height)-2)

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

    def on_close_click(self):
        self.defer_close()

    def on_ok_click(self):
        self.defer_close()

#
# 武将信息
#
class HeroItem:
    def __init__(self, hero_id, ui_obj):
        self.hero_id = hero_id
        self.ui_obj = ui_obj

    def refresh(self, hero):
        self.age_label.set_text(str(hero.age))
        self.wuli_label.set_text(str(hero.wu))
        self.tongshuai_label.set_text(str(hero.tong))
        self.zhengzhi_label.set_text(str(hero.zheng))
        self.zhili_label.set_text(str(hero.zhi))
        self.ap_label.set_text(str(hero.ap.get_floor()))

        text, color = game_mgr.hero_mgr.get_hero_activity_title(hero)
        self.act_label.set_text(text)
        self.act_label.set_self_modulate(*color)

#
# 武将列表
#
class HeroListTrait:
    def init_header(self, header):
        name_label = header.find_node('Label')
        column_list = ['姓名','身份','年龄','状态','武力','统率','智力','政治', '体力']
        column_width_dict = { '姓名': 80, '状态': 60, }

        for index in range(len(column_list)):
            if index == 0:
                label_obj = name_label
            else:
                label_obj = name_label.dup()
            
            col_name = column_list[index]
            label_obj.set_text(col_name)
            label_obj.set_minimum_size(column_width_dict.get(col_name, 40), 0)

    def init_items(self, item_node, hero_list):
        item_node.set_visible(False)

        # TODO: 做一个缓存
        for item in self.item_list:
            item.ui_obj.destroy()
        self.item_list.clear()

        for hero_id in hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)

            new_item = item_node.dup()
            new_item.set_visible(True)

            hero_item = HeroItem(hero_id, new_item)
            self.item_list.append(hero_item)
            
            name_label = new_item.find_node('Label')
            name_label.set_minimum_size(80, 0)
            name_label.set_text(hero.hero_name)
            hero_item.name_label = name_label
            
            # 身份
            standing_label = name_label.dup()
            standing_label.set_minimum_size(40, 0)
            is_main_hero = game_mgr.hero_mgr.is_main_hero(hero.hero_id)
            standing_label.set_text('主公' if is_main_hero else '')

            # 年龄
            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            
            # 活动
            act_label = name_label.dup()
            act_label.set_minimum_size(60, 0)

            wuli_label = name_label.dup()
            wuli_label.set_minimum_size(40, 0)
            
            tongshuai_label = name_label.dup()
            tongshuai_label.set_minimum_size(40, 0)
            
            zhili_label = name_label.dup()
            zhili_label.set_minimum_size(40, 0)

            zhengzhi_label = name_label.dup()
            zhengzhi_label.set_minimum_size(40, 0)

            ap_label = name_label.dup()
            ap_label.set_minimum_size(40, 0)

            # save refernce
            hero_item.age_label = age_label
            hero_item.wuli_label = wuli_label
            hero_item.tongshuai_label = tongshuai_label
            hero_item.zhili_label = zhili_label
            hero_item.zhengzhi_label = zhengzhi_label
            hero_item.act_label = act_label
            hero_item.ap_label = ap_label

            hero_item.refresh(hero)

    # 得到一个选中的hero_id的list
    def get_selected(self):
        hero_list = []
        for item in self.item_list:
            item_obj = item.ui_obj
            if item_obj.find_node('CheckBox').is_pressed():
                hero_list.append(item.hero_id)
        
        return hero_list
    
    # 把id, 换成实际的hero实例
    def get_selected_hero_list(self):
        hero_list = self.get_selected()
        return list(map(get_hero, hero_list))
        
    def refresh_hero_items(self, hero_list):
        for hero in hero_list:
            item = first(self.item_list, lambda x: x.hero_id == hero.hero_id)
            if item:
                item.refresh(hero)

    def refresh_hero_items_all(self):
        for item in self.item_list:
            item.refresh(get_hero(item.hero_id))
        

