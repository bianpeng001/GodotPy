#
# 2023年3月16日 bianpeng
#

from game.core import log_debug, OS
from game.base_type import UIController, UT_CITY, when_visible
from game.game_mgr import *
from game.event_name import PRESSED,SCENE_GROUND_CLICK,SCENE_UNIT_CLICK
from game.ui.ui_traits import PopupTrait

#
# 军队, 选择目标
#
class SelectTargetController(UIController, PopupTrait):
    def __init__(self):
        # 返回的数据
        self.target_name = ''
        self.target_unit_id = 0
        self.target_pos = (0,0)

        # 回调
        self.select_cb = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close(close=False)

        self.lbl_target = self.ui_obj.find_node('Panel/LblTarget')
        self.lbl_target.set_text(self.target_name)

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        
        # 指示目标用的小红旗
        self.flag_obj = OS.instantiate('res://models/Flag02.tscn')
        self.flag_obj.set_visible(False)
        
    def on_show(self, show):
        self.flag_obj.set_visible(show)

    def set_target(self, unit_id, pos):
        self.target_unit_id = unit_id
        self.target_pos = pos

        if unit_id > 0:
            target_name = get_unit_name(unit_id)
        else:
            x,z = pos
            target_name = f'{x},{z}'
            tile = game_mgr.ground_mgr.get_tile(x,z)
            for unit in tile.get_unit_list():
                if unit.unit_type == UT_CITY:
                    target_name = f'{unit.unit_name} {target_name}'
                    break

        self.target_name = target_name
        self.lbl_target.set_text(target_name)

    @when_visible
    def on_scene_unit_click(self, unit):
        x,y,z = unit.get_position()
        self.flag_obj.set_position(x,y,z)
        self.set_target(unit.unit_id, (round(x),round(z)))

    @when_visible
    def on_scene_ground_click(self):
        x,y,z = get_cursor_position()
        self.flag_obj.set_position(x,y,z)
        self.set_target(0, (round(x), round(z)))
        
    def init(self, select_cb):
        self.select_cb = select_cb
        self.set_target(0, (0,0))
        self.set_position(400, 70)
        self.push_panel()
    
    def on_ok_click(self):
        self.pop_panel()
        
        if self.select_cb:
            self.select_cb()




