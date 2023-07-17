#
# 2023年3月3日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import UIController, UT_CITY, UT_TROOP
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED, TAB_CHANGED,\
        NAV_PANEL_REMOVE_UNIT,\
        NAV_PANEL_ADD_UNIT,\
        RECT_SELECT_UNITS_CHANGE


#
# 定位面板，快速去到我的城，军队，武将
#
class NavPanelController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        
        self.btn_dict = {}
        self.cur_tab_index = 0

        self.btn_pool = []
    
    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.btn_1 = self.ui_obj.find_node('ScrollContainer/VBoxContainer/Button1')
        self.btn_1.set_visible(False)
        #self.main_city_button = self.ui_obj.find_node('ScrollContainer/VBoxContainer/Button1')
        #self.main_city_button.connect(PRESSED, self.on_main_city_click)
        #self.main_city_button.set_visible(False)
        #self.main_city_button.connect(PRESSED, self.on_main_city_click)
        #self.main_city_button.clear_connection(PRESSED)
        #self.main_city_button.connect(PRESSED, self.on_main_city_click)

        self.tab_obj = self.ui_obj.find_node('TabBar')
        self.tab_obj.connect(TAB_CHANGED, self.on_tab_changed)
        
        game_mgr.event_mgr.add(NAV_PANEL_ADD_UNIT, self.on_add_unit)
        game_mgr.event_mgr.add(NAV_PANEL_REMOVE_UNIT, self.on_lose_unit)

    def on_tab_changed(self, tab_index):
        log_debug('click', tab_index)
        if self.cur_tab_index != tab_index:
            self.cur_tab_index = tab_index
            self.refresh_buttons()

    def get_unit_type(self):
        match self.cur_tab_index:
            case 0:
                return UT_CITY
            case 1:
                return UT_TROOP
            case 2:
                return 100

    def goto_unit(self, unit_id):
        unit = get_unit(unit_id)
        game_mgr.camera_mgr.set_target_focus(*unit.get_position())
        game_mgr.event_mgr.notify(RECT_SELECT_UNITS_CHANGE, (unit,))

    def on_main_city_click(self):
        log_debug('back to main city')
        mp = get_main_player()
        self.goto_unit(mp.main_city_id)
        
    # 获得一个城市
    def on_add_unit(self, player_id, unit_id):
        if player_id != get_main_player_id():
            return
        
        def make_on_click():
            self.goto_unit(unit_id)
        
        if self.btn_pool:
            btn = self.btn_pool.pop()
        else:
            btn = self.btn_1.dup()
            btn.connect(PRESSED, make_on_click)

        unit = get_unit(unit_id)
        btn.set_text(unit.unit_name)
        btn.set_visible(unit.unit_type == self.get_unit_type())
        self.btn_dict[unit_id] = btn
    
    # 失去一个城市
    def on_lose_unit(self, player_id, unit_id):
        if player_id != get_main_player_id():
            return
        
        if unit_id in self.btn_dict:
            btn = self.btn_dict.pop(unit_id)
            btn.set_visible(False)
            self.btn_pool.append(btn)
    
    # 刷新全部
    def refresh_buttons(self):
        cur_unit_type = self.get_unit_type()
        for unit_id in self.btn_dict:
            btn = self.btn_dict[unit_id]
            btn.set_visible(get_unit(unit_id).unit_type == cur_unit_type)




