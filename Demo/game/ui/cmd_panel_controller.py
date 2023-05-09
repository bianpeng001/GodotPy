#
# 2023年4月11日 bianpeng
#

from game.core import log_debug, OS
from game.game_mgr import *
from game.base_type import UIController
from game.event_name import *
from game.ui.ui_traits import PopupTrait

#
# 操作目标
#
class TargetItem:
    def __init__(self, btn_obj):
        self.unit_id = 0
        self.btn_obj = btn_obj
        self.btn_obj.set_visible(False)


#
# 指令界面
#
class CmdPanelController(UIController, PopupTrait):
    def __init__(self):
        self.btn_list = []
        self.target_list = []
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        cmd_list = [
            '移动','攻击','驻扎','驻扎',
            '驻扎','驻扎','驻扎','驻扎',
        ]
        btn_template = self.ui_obj.find_node('Panel/GridContainer/BtnCmd')
        btn_template.set_visible(False)

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
        
        self.unit_name_obj = self.ui_obj.find_node('Panel/UnitInfo/Name')
        self.target_units_obj = self.ui_obj.find_node('Panel/TargetUnits')
        self.btn_unit_obj = self.ui_obj.find_node('Panel/TargetUnits/BtnUnit')
        self.btn_unit_obj.set_visible(False)
        self.target_list = [ TargetItem(self.btn_unit_obj.dup()) for i in range(9)]
        
        game_mgr.event_mgr.add(RECT_SELECT_UNITS_CHANGE, self.on_rect_select_units_changed)

    def init(self, unit):
        #self.cmd_panel_controller.popup_screen_bottom_left()
        game_mgr.co_mgr.start(self.co_show_panel())
        self.unit_name_obj.set_text(unit.unit_name)

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

    def on_rect_select_units_changed(self, unit_list):
        if len(unit_list) > 0:
            game_mgr.co_mgr.start(self.co_show_panel())
        
        for i in range(len(self.target_list)):
            item = self.target_list[i]
            if i < len(unit_list):
                unit = unit_list[i]
                item.unit_id = unit.unit_id
                item.btn_obj.set_visible(True)
            else:
                item.unit_id = 0
                item.btn_obj.set_visible(False)
        





