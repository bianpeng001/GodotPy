#
# 2023年2月28日 bianpeng
#

from game.base_type import UIController
from game.event_name import PRESSED
from game.game_mgr import game_mgr, UIControllerTrait

#
class SelectHeroController(UIController, UIControllerTrait):
    def __init__(self):
        super().__init__()
        
        self.item_list = []
        self.init_header = False

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('Panel/BtnOk').connect(PRESSED, self.on_ok_click)
        self.ui_obj.find_node('Panel/BtnCancel').connect(PRESSED, self.on_cancel_click)

    def on_cancel_click(self):
        self.defer_close()
        game_mgr.ui_mgr.neizheng_controller.show()

    def on_ok_click(self):
        self.defer_close()
        game_mgr.ui_mgr.neizheng_controller.show()

    def init_hero_list(self, hero_list):
        
        for item in self.item_list:
            item.destroy()

        if not self.init_header:
            self.init_header = True
            header = self.ui_obj.find_node('Panel/HeroList/ScrollContainer/VBoxContainer/Header')
            
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

        for hero in hero_list:
            pass


