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
        self.start_x = self.start_y = 0
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.ui_obj.set_visible(False)
        self.ui_obj.set_size(100, 100)

        def on_show_select_rect(x,y):
            self.start_x,self.start_y = x,y
            
        def on_drag_select_rect(x,y):
            if not self.is_show():
                self.show()
                
            self.ui_obj.set_position(min(self.start_x,x), min(self.start_y,y))
            self.ui_obj.set_size(abs(self.start_x-x), abs(self.start_y-y))
        
        def on_hide_select_rect():
            if self.is_show():
                self.hide()
                # TODO: 框选操作单位
                log_debug('select rectangle')
        
        game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, on_show_select_rect)
        game_mgr.event_mgr.add(LEFT_BUTTON_RELEASE, on_hide_select_rect)
        game_mgr.event_mgr.add(LEFT_BUTTON_DRAG, on_drag_select_rect)
        

