#
# 2023年5月9日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.ground_mgr import xz_to_colrow
from game.event_name import LEFT_BUTTON_PRESS,\
    LEFT_BUTTON_RELEASE,\
    LEFT_BUTTON_DRAG,\
    RECT_SELECT_UNITS_CHANGE

#
# 框选
#
class RectSelectController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        # 起始点击位置
        self.start_x = self.start_y = 0
        
        # 方框的参数
        self.left = self.left = 0
        self.width = self.height = 100
        
        self.select_list = []
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.ui_obj.set_visible(False)
        self.ui_obj.set_size(100, 100)

        def on_show_select_rect(x,y):
            self.start_x,self.start_y = x,y
            
        def on_drag_select_rect(x,y):
            if not self.is_show():
                self.show()
            
            self.width = abs(self.start_x-x)
            self.height = abs(self.start_y-y)
            self.left = min(self.start_x, x)
            self.top = min(self.start_y, y)
            
            self.ui_obj.set_position(self.left, self.top)
            self.ui_obj.set_size(self.width, self.height)
        
        def on_hide_select_rect():
            if self.is_show():
                self.hide()
                self.do_select()
        
        game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, on_show_select_rect)
        game_mgr.event_mgr.add(LEFT_BUTTON_RELEASE, on_hide_select_rect)
        game_mgr.event_mgr.add(LEFT_BUTTON_DRAG, on_drag_select_rect)
        
    # 框选操作单位
    def do_select(self):
        if not game_mgr.player_mgr.main_player:
            return
        
        def in_rect(x,y):
            return x > self.left and \
                x < self.left + self.width and \
                y > self.top and \
                y < self.top + self.height
                
        def check_tile_unit(col, row):
            tile = game_mgr.ground_mgr.get_tile_colrow(col, row)
            if tile:
                for unit in tile.get_unit_list():
                    screen_x,screen_y = camera.world_to_screen(*unit.get_position())
                    if in_rect(screen_x,screen_y):
                        self.select_list.append(unit)
            
        center_x = self.left + self.width*0.5
        center_y = self.top + self.height*0.5
        
        camera = get_main_camera()
        x,y,z = camera.screen_to_world(center_x, center_y)
        col,row = xz_to_colrow(x, z)

        self.select_list.clear()
        
        #
        # 找视野内的九个格子, 有点丑, 但是正确性有保证. 看看如何优化下.
        # 减少一些world_to_screen 计算, 用世界坐标的距离, 先大体做一个过滤
        #
        check_tile_unit(col, row)
        check_tile_unit(col, row-1)
        check_tile_unit(col, row+1)

        check_tile_unit(col-1, row)
        check_tile_unit(col-1, row-1)
        check_tile_unit(col-1, row+1)
        
        check_tile_unit(col+1, row)
        check_tile_unit(col+1, row-1)
        check_tile_unit(col+1, row+1)
        
        if len(self.select_list) > 0:
            log_debug('select rect', center_x, center_y, self.width, self.height)
            for unit in self.select_list:
                log_debug(unit.unit_name, unit.get_position())
                
        # 通知cmd_panel, 操作目标集合变更, 那边负责响应即可
        game_mgr.event_mgr.notify(RECT_SELECT_UNITS_CHANGE, self.select_list)
        
        







