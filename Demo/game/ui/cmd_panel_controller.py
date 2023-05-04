#
# 2023年4月11日 bianpeng
#

from game.core import log_debug, OS
from game.game_mgr import *
from game.base_type import UIController
from game.event_name import *
from game.ui.ui_traits import PopupTrait

#
# 指令界面
#
class CmdPanelController(UIController, PopupTrait):
    def __init__(self):
        self.btn_list = []
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        cmd_list = [
            '移动','攻击','驻扎','驻扎',
            '驻扎','驻扎','驻扎','驻扎',
        ]
        btn_template = self.ui_obj.find_node('Panel/GridContainer/BtnCmd')

        def make_btn_handler(cmd, btn):
            def fun():
                log_debug(cmd)
            return fun
        
        for cmd in cmd_list:
            btn = btn_template.dup()
            btn.find_node('Label').set_text(cmd)
            btn.connect(PRESSED, make_btn_handler(cmd, btn))
            btn.set_visible(True)
            self.btn_list.append((cmd, btn))
            
        btn_template.set_visible(False)
        
        self.label_name = self.ui_obj.find_node('Panel/LabelName')

    def init(self, unit):
        #self.cmd_panel_controller.popup_screen_bottom_left()
        game_mgr.co_mgr.start(self.co_show_panel())
        self.label_name.set_text(unit.unit_name)

    def co_show_panel(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        
        self.show()
        speed = 5
        time = 0
        while time < 1.0:
            time += game_mgr.delta_time * speed
            self.set_position(2, screen_height-(height+2)*time)
            yield None

