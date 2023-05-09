#
# 2023年3月4日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED, SCENE_GROUND_CLICK

#
# 建设面板
#
class BuildPanelController(UIController, PopupTrait):
    def __init__(self):
        self.item_list = []
        self.active_obj = None

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.ui_obj.find_node('HBoxContainer/Left/BtnClose').connect(PRESSED, self.on_close_click)
        self.ui_obj.find_node('HBoxContainer/BtnFarm').connect(PRESSED, self.on_build_farm_click)
        self.ui_obj.find_node('HBoxContainer/BtnWorkHouse').connect(PRESSED, self.on_build_work_house_click)

        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)

        farm_obj = FNode3D.instantiate('res://models/Farm01.tscn')
        work_house_obj = FNode3D.instantiate('res://models/WorkHouse01.tscn')
        self.item_list.append(farm_obj)
        self.item_list.append(work_house_obj)

        for item in self.item_list:
            item.set_visible(False)

    # 是否正在建设激活状态
    def is_building(self):
        return self.is_show() and self.active_obj

    def set_active_obj(self, obj):
        if self.active_obj:
            self.active_obj.set_visible(False)
        self.active_obj = obj
        self.active_obj.set_visible(True)
    
    def on_scene_ground_click(self):
        if not self.is_building():
            return

        self.active_obj.dup()
        # TODO: 修改数据,创建附属建筑等操作略

    def on_close_click(self):
        if self.active_obj:
            self.active_obj.set_visible(False)
        self.active_obj = None

        self.pop_panel()

    def on_build_farm_click(self):
        self.set_active_obj(self.item_list[0])
        
    def on_build_work_house_click(self):
        self.set_active_obj(self.item_list[1])

    def update(self):
        if self.is_show() and self.active_obj:
            x,y,z = get_cursor_position()
            x = round(x)
            z = round(z)
            self.active_obj.set_position(x,0,z)

