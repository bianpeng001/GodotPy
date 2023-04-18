#
# 2023年4月17日 bianpeng
#
from game.core import log_util
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 系统面板
#
class SysPanelController(UIController, PopupTrait):
    def __init__(self):
        pass
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        
        self.btn_1 = ui_obj.find_node('Panel/Button1')
        self.btn_1.set_visible(False)
        
        self.btn_list = []
        
        x,y = 70,40
        btn_labels = ['返回', '设置', '存档', '读档', '退出']
        for label in btn_labels:
            btn = self.btn_1.dup()
            btn.set_text(label)
            btn.set_position(x,y)
            btn.set_visible(True)
            self.btn_list.append((label, btn))
            y += 48
        
        def get_btn(label):
            for it in self.btn_list:
                a,b = it
                if a == label:
                    return b
        
        get_btn('设置').connect(PRESSED, self.on_setting_click)
        
    def on_setting_click(self):
        panel = game_mgr.ui_mgr.setting_panel_controller
        panel.init()
        panel.push_panel()
        
        self.hide()
    
    def init(self):
        self.popup_screen_center()
        
        

