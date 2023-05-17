#
# 2023年4月11日 bianpeng
#

from game.core import log_debug, OS, ResCapsule
from game.game_mgr import *
from game.base_type import UIController, UT_TROOP, UT_CITY, when_visible
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
        self.btn_obj.set_tooltip(cmd)
        
    def set_cur_dlg(self, dlg):
        return game_mgr.ui_mgr.cmd_panel_controller.set_cur_dlg(dlg)
        
    def on_click(self):
        unit_list = game_mgr.ui_mgr.cmd_panel_controller.unit_list
        log_debug('cmd', self.cmd)
        
        if self.cmd == '目标':
            dlg = game_mgr.ui_mgr.select_target_controller
            if not self.set_cur_dlg(dlg):
                def on_select_target_cb():
                    for unit in filter(lambda x: x.unit_type == UT_TROOP, unit_list):
                        unit.target_unit_id = dlg.target_unit_id
                        unit.target_pos = dlg.target_pos
                        
                        brain_comp = unit.get_controller().get_brain_comp()
                        brain_comp.goto_state('start')

                dlg.init(on_select_target_cb)
                dlg.show()
        
        elif self.cmd == '内政':
            dlg = game_mgr.ui_mgr.neizheng_controller
            if not self.set_cur_dlg(dlg):
                unit = next(filter(lambda x: x.unit_type == UT_CITY, unit_list), None)
                if unit:
                    dlg.init(unit)
                    dlg.set_position(250, 80)
                    dlg.show()
        
        elif self.cmd == '出战':
            dlg = game_mgr.ui_mgr.chuzhan_panel_controller
            if not self.set_cur_dlg(dlg):
                unit = next(filter(lambda x: x.unit_type == UT_CITY, unit_list), None)
                if unit:
                    dlg.init(unit)
                    dlg.set_position(250, 106)
                    dlg.show()
#
# 指令界面
#
class CmdPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.btn_list = []
        self.target_list = []
        self.unit_list = []
        
        self.cur_dlg = None

    def on_leave_scene(self):
        self.icon_list = []
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        
        cmd_list = [
            '目标','移动','','',
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
        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        
        self.icon_list = [
            None,
            ResCapsule.load_resource('res://ui/img/Template.png'),
            ResCapsule.load_resource('res://ui/img/Man2.png')
        ]

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
        self.unit_list = list(filter(lambda x: check_main_owner(x), unit_list))
        
        if len(self.unit_list) > 0:
            if not self.is_show():
                self.show_panel()
        else:
            if self.is_show():
                self.hide()
        
        for i in range(len(self.target_list)):
            item = self.target_list[i]
            if i < len(self.unit_list):
                unit = self.unit_list[i]
                item.unit_id = unit.unit_id
                item.btn_obj.set_visible(True)
                item.btn_obj.set_tooltip(unit.unit_name)
                item.btn_obj.set_normal_tex(self.icon_list[unit.unit_type].res)
            else:
                item.unit_id = 0
                item.btn_obj.set_visible(False)

    # 这里的限制要去掉           
    #@when_visible
    def on_scene_unit_click(self, unit):
        if len(self.unit_list) == 0 and check_main_owner(unit):
            self.on_rect_select_units_changed([unit])
        else:
            # 插旗表示目标位置
            x,y,z = get_cursor_position()
            effect_item = game_mgr.effect_mgr.play_effect2(2003)
            effect_item.set_position(x,y,z)
            
            self.set_troop_target_pos(x,z)
    
    def set_troop_target_pos(self, x,z):
        for unit in filter(lambda x: x.unit_type == UT_TROOP, self.unit_list):
            unit.target_unit_id = 0
            unit.target_pos = (x,z)
            
            brain_comp = unit.get_controller().get_brain_comp()
            brain_comp.goto_state('start')
    
    @when_visible
    def on_scene_ground_click(self):
        x,y,z = get_cursor_position()
        # 插旗表示目标位置
        effect_item = game_mgr.effect_mgr.play_effect2(2003)
        effect_item.set_position(x,y,z)
        
        self.set_troop_target_pos(x,z)
    
    def set_cur_dlg(self, dlg):
        if self.cur_dlg and self.cur_dlg.is_show():
            log_debug('close cur dlg', self.cur_dlg)
            self.cur_dlg.defer_close()
            self.cur_dlg = None
        self.cur_dlg = dlg
        if self.cur_dlg and self.cur_dlg.is_show():
            self.cur_dlg.defer_close()
            return True
        



