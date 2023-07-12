#
# 2023年4月11日 bianpeng
#

import io

from game.core import *
from game.game_mgr import *
from game.base_type import UIController,\
        UT_TROOP, UT_CITY,\
        when_visible,\
        StringBuilder
from game.event_name import PRESSED,\
        RECT_SELECT_UNITS_CHANGE,\
        ALERT_DIALOG_MSG,\
        SCENE_UNIT_CLICK,\
        SCENE_GROUND_CLICK,\
        LEAVE_SCENE
from game.ui.ui_traits import PopupTrait

#
# 目标
#
class TargetItem:
    def __init__(self, unit_id, btn_obj):
        self.unit_id = unit_id
        self.btn_obj = btn_obj
        self.btn_obj.set_visible(False)
        self.btn_obj.connect(PRESSED, self.on_click)
    
    def on_click(self):
        log_debug('click', self.unit_id)
        game_mgr.event_mgr.emit(RECT_SELECT_UNITS_CHANGE, (get_unit(self.unit_id),))

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
        origin_unit_list = game_mgr.ui_mgr.cmd_panel_controller.unit_list
        unit_list = list(filter(lambda x: check_main_owner(x), origin_unit_list))
        #log_debug('cmd', self.cmd, len(unit_list))
        
        match self.cmd:
            case '目标':
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
        
            case '内政':
                dlg = game_mgr.ui_mgr.neizheng_controller
                if not self.set_cur_dlg(dlg):
                    unit = next(filter(lambda x: x.unit_type == UT_CITY, unit_list), None)
                    if unit:
                        dlg.init(unit)
                        dlg.set_position(250, 80)
                        dlg.show()
        
            case '出战':
                dlg = game_mgr.ui_mgr.chuzhan_panel_controller
                if not self.set_cur_dlg(dlg):
                    unit = next(filter(lambda x: x.unit_type == UT_CITY, unit_list), None)
                    if unit:
                        dlg.init(unit)
                        dlg.set_position(250, 106)
                        dlg.show()

            case '查看':
                if origin_unit_list:
                    unit = origin_unit_list[0]
                    sb = StringBuilder()
                    sb.writeln(f'{game_mgr.get_unit_name_label(unit)}')
                    if unit.owner_player_id > 0:
                        sb.writeln(f'主公 {get_player_name(unit.owner_player_id)}')
                    sb.writeln(f'士兵 {unit.army_amount.get_floor()}')
                    game_mgr.event_mgr.emit(ALERT_DIALOG_MSG, sb.getvalue(), 3.0)

            case '撤退':
                # 以出发城市为目标， 到达后，自动进驻
                pass

            case '进驻':
                # 部队进程，武将和相关的士兵，资源都进程, 也就是说，军团还有运输功能
                pass

#
# 指令界面
#
class CmdPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.btn_list = []
        self.target_list = []
        self.unit_list = []
        
        self.icon_list = []
        
        # 当前子面板
        self.cur_dlg = None

    def on_leave_scene(self):
        log_debug('cmd panel cleanup')
        self.icon_list = []
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        
        cmd_list = (
            '查看','撤退','','',
            '出战','内政','进驻','',
        )
        btn_cmd_obj = self.ui_obj.find_node('Panel/GridContainer/BtnCmd')
        btn_cmd_obj.set_visible(False)

        for cmd in cmd_list:
            btn = btn_cmd_obj.dup()
            cmd_item = CmdItem(cmd, btn)
            btn.find_node('Label').set_text(cmd)
            btn.connect(PRESSED, cmd_item.on_click)
            
            self.btn_list.append(cmd_item)
        
        self.unit_info_obj = self.ui_obj.find_node('Panel/UnitInfo')
        self.target_units_obj = self.ui_obj.find_node('Panel/TargetUnits')
        self.btn_unit_obj = self.ui_obj.find_node('Panel/TargetUnits/BtnUnit')
        self.btn_unit_obj.set_visible(False)
        self.target_list = [ TargetItem(0, self.btn_unit_obj.dup()) for i in range(9) ]
        
        game_mgr.event_mgr.add(RECT_SELECT_UNITS_CHANGE, self.on_rect_select_units_changed)
        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        game_mgr.event_mgr.add(LEAVE_SCENE, self.on_leave_scene)
        
        self.icon_list = [
            None,
            ResCapsule.load_resource('res://ui/img/Man2.png'),
            ResCapsule.load_resource('res://ui/img/Man3.png'),
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
            yield
            
    def show_panel(self):
        screen_width,screen_height = OS.viewport_get_size()
        _,_,width,height = self.ui_obj.get_rect()
        self.set_position(2, screen_height-(height+2))
        self.show()

    def on_rect_select_units_changed(self, unit_list):
        self.unit_list = unit_list
        
        if len(self.unit_list) > 0:
            if not self.is_show():
                self.show_panel()
        else:
            if self.is_show():
                self.hide()
                return
        
        # 单位信息, 只选中一个的时候, 要多显示一些信息
        if len(self.unit_list) == 1:
            self.unit_info_obj.set_visible(True)
            unit = self.unit_list[0]
            name_label = game_mgr.get_unit_name_label(unit)
            
            if unit.unit_type == UT_TROOP:
                text = f'''{name_label} {unit.army_amount.get_floor()}
行军
'''
            elif unit.unit_type == UT_CITY:
                text = f'''{name_label} {unit.army_amount.get_floor()}
商业
'''
            else:
                text = f'''{name_label}
'''
            self.unit_info_obj.set_text(text)
        else:
            self.unit_info_obj.set_visible(False)

        # 刷新一下选中的目标信息
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
        if not get_main_player():
            return

        if not self.unit_list:
            game_mgr.event_mgr.emit(RECT_SELECT_UNITS_CHANGE, (unit,))
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
        # 插旗表示目标位置
        x,y,z = get_cursor_position()
        effect_item = game_mgr.effect_mgr.play_effect2(2003)
        effect_item.set_position(x,y,z)
        
        self.set_troop_target_pos(x,z)
    
    # 当前弹出面板, 在cmd下面, 统一管理, 只能弹出一个
    def set_cur_dlg(self, dlg):
        if self.cur_dlg and self.cur_dlg.is_show():
            self.cur_dlg.defer_close()
            self.cur_dlg = None
            
        self.cur_dlg = dlg
        
        if self.cur_dlg and self.cur_dlg.is_show():
            self.cur_dlg.defer_close()
            self.cur_dlg = None
            return True




