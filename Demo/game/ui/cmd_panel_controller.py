#
# 2023年4月11日 bianpeng
#

from game.core import log_debug, OS
from game.game_mgr import *
from game.base_type import UIController, UT_TROOP, UT_CITY
from game.event_name import *
from game.ui.ui_traits import PopupTrait

#
# 目标
#
class TargetItem:
    def __init__(self, unit_id, btn_obj):
        self.unit_id = unit_id
        self.btn_obj = btn_obj
        self.btn_obj.set_visible(False)

#
# 指令
#
class CmdItem:
    def __init__(self, cmd, btn_obj):
        self.cmd = cmd
        self.btn_obj = btn_obj
        self.btn_obj.set_visible(True)

    def on_click(self):
        unit_list = list(map(lambda x: get_unit(x.unit_id),
                            filter(lambda x: x.unit_id != 0, 
                            game_mgr.ui_mgr.cmd_panel_controller.target_list)))
        log_debug('cmd', self.cmd)
        
        if self.cmd == '目标':
            dlg = game_mgr.ui_mgr.select_target_controller
            
            def on_select_target_cb():
                for unit in unit_list:
                    if unit.unit_type == UT_TROOP:
                        unit.target_unit_id = dlg.target_unit_id
                        unit.target_pos = dlg.target_pos
                        
                        brain_comp = unit.get_controller().get_brain_comp()
                        brain_comp.goto_state('start')
            dlg.init(on_select_target_cb)
        
        elif self.cmd == '内政':
            dlg = game_mgr.ui_mgr.neizheng_controller
            
            for unit in unit_list:
                if unit.unit_type == UT_CITY:
                    dlg.init(unit)
                    dlg.set_position(250, 100)
                    dlg.push_panel()
                    break
        
        elif self.cmd == '出战':
            dlg = game_mgr.ui_mgr.chuzhan_panel_controller
            
            for unit in unit_list:
                if unit.unit_type == UT_CITY:
                    dlg.init(unit)
                    dlg.popup(250, 100)
                    dlg.push_panel()
                    break
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
            '目标','撤退','','',
            '内政','出战','','',
        ]
        btn_cmd_obj = self.ui_obj.find_node('Panel/GridContainer/BtnCmd')
        btn_cmd_obj.set_visible(False)

        for cmd in cmd_list:
            btn = btn_cmd_obj.dup()
            cmd_item = CmdItem(cmd, btn)
            btn.find_node('Label').set_text(cmd)
            btn.connect(PRESSED, cmd_item.on_click)
            self.btn_list.append(cmd_item)
        
        self.unit_name_obj = self.ui_obj.find_node('Panel/UnitInfo/Name')
        self.target_units_obj = self.ui_obj.find_node('Panel/TargetUnits')
        self.btn_unit_obj = self.ui_obj.find_node('Panel/TargetUnits/BtnUnit')
        self.btn_unit_obj.set_visible(False)
        self.target_list = [ TargetItem(0, self.btn_unit_obj.dup()) for i in range(9) ]
        
        game_mgr.event_mgr.add(RECT_SELECT_UNITS_CHANGE, self.on_rect_select_units_changed)

    def init(self, unit):
        #self.cmd_panel_controller.popup_screen_bottom_left()
        game_mgr.co_mgr.start(self.co_show_panel())
        self.unit_name_obj.set_text(unit.unit_name)

    # TODO: 这种动画效果, 后面再说吧
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
            
    def show_panel(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.set_position(2, screen_height-(height+2))
        self.show()

    def on_rect_select_units_changed(self, unit_list):
        # 只能操作自己的单位
        unit_list = list(filter(lambda x: x.owner_is_main_player(), unit_list))
        
        if len(unit_list) > 0:
            if not self.is_show():
                self.show_panel()
        else:
            if self.is_show():
                self.hide()
        
        for i in range(len(self.target_list)):
            item = self.target_list[i]
            if i < len(unit_list):
                unit = unit_list[i]
                item.unit_id = unit.unit_id
                item.btn_obj.set_visible(True)
            else:
                item.unit_id = 0
                item.btn_obj.set_visible(False)
        


