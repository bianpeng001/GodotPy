#
# 2023年4月17日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

#
# 系统面板
#
class SysPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        pass
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        
        btn_1 = ui_obj.find_node('Panel/Button1')
        
        btn_labels = ['返回', '设置', '存档', '读档', '退出']
        btn_list = [btn_1.dup() for i in range(len(btn_labels) -1)]
        btn_list.append(btn_1)
        
        x,y = 70,40
        for i in range(len(btn_labels)):
            label = btn_labels[i]
            btn = btn_list[i]
            btn.set_text(label)
            btn.set_position(x,y+i*48)
        
        def get_btn(label):
            i = btn_labels.index(label)
            return btn_list[i]
        
        get_btn('设置').connect(PRESSED, self.on_setting_click)
        get_btn('存档').connect(PRESSED, self.on_save)
        get_btn('退出').connect(PRESSED, self.on_quit)
        
    def on_setting_click(self):
        self.hide()
        
        panel = game_mgr.ui_mgr.setting_panel_controller
        panel.init()

    def on_save(self):
        self.game_data.save('01.sav')

    def on_quit(self):
        OS.quit(0)
        
    def init(self):
        self.popup_screen_center()


