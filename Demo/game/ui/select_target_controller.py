#
# 2023年3月16日 bianpeng
#

from game.core import log_debug
from game.base_type import UIController, UT_CITY
from game.game_mgr import *
from game.event_name import PRESSED,SCENE_GROUND_CLICK,SCENE_UNIT_CLICK
from game.ui.ui_traits import *

#
# 选择目标
#
class SelectTargetController(UIController, PopupTrait):
    def __init__(self):
        self.target_name = '长坂坡'
        self.target_unit_id = 0
        self.target_pos = (0,0)

        self.select_callback = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.bind_ok_cancel_close(close=False)

        self.lbl_target = self.ui_obj.find_node('Panel/LblTarget')
        self.lbl_target.set_text(self.target_name)

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)

    def on_scene_unit_click(self, unit):
        x,y,z = unit.get_position()
        x = round(x)
        z = round(z)

        target_name = f'{unit.unit_name}城'

        self.target_unit_id = 0
        self.target_pos = (x,z)
        self.target_name = target_name
        self.lbl_target.set_text(target_name)

    def on_scene_ground_click(self):
        x,y,z = get_position_under_mouse()
        
        x = round(x)
        z = round(z)
        target_name = f'{x},{z}'

        tile = game_mgr.ground_mgr.get_tile(x, z)
        for unit in tile.unit_list:
            if unit.unit_type == UT_CITY:
                target_name = f'{unit.unit_name} {target_name}'
        
        self.target_unit_id = 0
        self.target_pos = (x,z)
        self.target_name = target_name
        self.lbl_target.set_text(target_name)
        
    def show_dialog(self, select_callback):
        self.select_callback = select_callback
        self.popup(240, 70)
    
    def on_ok_click(self):
        self.pop_panel()
       
        if self.select_callback:
            self.select_callback()

