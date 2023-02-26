#
# 2023年2月23日 bianpeng
#

from game.game_mgr import game_mgr
from game.config_mgr import new_hero_name

# 内政，农商将
class NeiZhengController:
    def __init__(self):
        self.tab_index = 0

        self.tabs = []

        self.last_city_id = 0
        self.item_list = []
        self.init_header = False

    def setup(self, ui_obj):
        from game.event_name import PRESSED

        self.ui_obj = ui_obj

        self.btn_close = ui_obj.find_node('Panel/BtnClose')
        self.btn_close.connect(PRESSED, self.on_close_click)

        self.tab_bar = ui_obj.find_node('TabBar')
        self.tab_bar.connect('tab_changed', self.on_tab_changed)

        self.tabs = [
            ui_obj.find_node('Panel/TabNong'),
            ui_obj.find_node('Panel/TabShang'),
            ui_obj.find_node('Panel/TabJiang'),
        ]
        self.tab_index = 0
        self.tab_bar.set_current_tab(self.tab_index)
        self.on_tab_changed()

    def on_close_click(self):
        game_mgr.ui_mgr.defer_close(self.ui_obj)

    def on_tab_changed(self):
        self.tab_index = self.tab_bar.get_current_tab()
        for i in range(len(self.tabs)):
            self.tabs[i].set_visible(i == self.tab_index)

        if self.tab_index == 2:
            self.init_hero_list()

    def init_hero_list(self):
        city = game_mgr.ui_mgr.context_unit
        if city.unit_id == self.last_city_id:
            return

        if not self.init_header:
            self.init_header = True
            header = self.tabs[2].find_node('HeroList/ScrollContainer/VBoxContainer/Header')
            
            name_label = header.find_node('Label')
            name_label.set_minimum_size(80, 0)
            name_label.set_text('姓名')

            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            age_label.set_text('年龄')

            action_label = name_label.dup()
            action_label.set_minimum_size(60, 0)
            action_label.set_text('活动')

        # items...
        for item in self.item_list:
            item.destroy()

        hero_list = city.hero_list
        item = self.tabs[2].find_node('HeroList/ScrollContainer/VBoxContainer/Item')
        for hero_id in hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            #print(hero_id, hero)

            new_item = item.dup()
            new_item.set_visible(True)
            self.item_list.append(new_item)

            name_label = new_item.find_node('Label')
            name_label.set_minimum_size(80, 0)
            name_label.set_text(hero.hero_name)
            name_label.connect('gui_input', self.on_gui_input)

            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            age_label.set_text(f'{hero.age}')

            action_label = name_label.dup()
            action_label.set_minimum_size(60, 0)
            action_label.set_text('空闲')

    def on_gui_input(self):
        print('click')


