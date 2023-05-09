#
# 2023年5月9日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import UIController
from game.event_name import *
from game.ui.ui_traits import PopupTrait

#
# 框选
#
class RectSelectController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.start_x = self.start_y = 0
        
        self.left = self.left = 0
        self.width = self.height = 100
    
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
        center_x = self.left + self.width*0.5
        center_y = self.top + self.height*0.5
        log_debug('select', center_x, center_y, self.width, self.height)
        
        camera = get_main_camera()
        x,y,z = camera.screen_to_world(center_x, center_y)
        

