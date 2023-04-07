#
# 2023年3月3日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED, NAV_PANEL_LOSE_CITY, NAV_PANEL_GAIN_CITY

#
# 定位面板，快速去到我的城，军队，武将
#
class NavPanelController(UIController, PopupTrait):
    def __init__(self):
        self.btn_dict = {}
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.main_city_button = self.ui_obj.find_node('ScrollContainer/VBoxContainer/BtnMainCity')
        self.main_city_button.connect(PRESSED, self.on_main_city_click)
        #self.main_city_button.connect(PRESSED, self.on_main_city_click)
        #self.main_city_button.clear_connection(PRESSED)
        #self.main_city_button.connect(PRESSED, self.on_main_city_click)
        
        game_mgr.event_mgr.add(NAV_PANEL_GAIN_CITY, self.on_gain_city)
        game_mgr.event_mgr.add(NAV_PANEL_LOSE_CITY, self.on_lose_city)
        
    def goto_unit(self, unit):
        game_mgr.camera_mgr.set_target_focus(*unit.get_position())

    def on_main_city_click(self):
        log_debug('11111111111111')
        mp = get_main_player()
        city_unit = game_mgr.unit_mgr.get_unit(mp.main_city_id)
        self.goto_unit(city_unit)
        
        
    def on_gain_city(self, player_id, city_unit_id):
        if player_id != get_main_player_id():
            return
        
        def make_on_click():
            city_unit = game_mgr.unit_mgr.get_unit(city_unit_id)
            self.goto_unit(city_unit)
        
        btn = self.main_city_button.dup()
        btn.connect(PRESSED, make_on_click)
        btn.set_text(get_unit_name(city_unit_id))
        self.btn_dict[city_unit_id] = btn
    
    def on_lose_city(self, player_id, city_unit_id):
        if player_id != get_main_player_id():
            return
        
        if city_unit_id in self.btn_dict:
            btn = self.btn_dict.pop(city_unit_id)
            btn.destroy()

    # 强制重建
    def rebuild(self):
        pass
        # TODO:
        

