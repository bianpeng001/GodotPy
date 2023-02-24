#
# 2023年2月6日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UT_CITY
from game.event_name import SCENE_UNIT_CLICK, \
        LEFT_BUTTON_BEGIN_DRAG, \
        SCENE_GROUND_CLICK

from game.ui.mainui_controller import MainUIController

#
# ui 管理器
# 一个ui面板对应一个controller
#
class UIMgr(NodeObject):
    def __init__(self):
        super().__init__()
        game_mgr.ui_mgr = self

        # 排队等关闭的ui，ui不能马上关闭，需要排队，不然马上就响应ui下面的元素被点击了
        self.defer_close_queue = []

        self.context_unit = None
        self.tick_time = 0

        self.mainui_panel = None
        self.mainui_controller = None

    def _create(self):
        self.get_obj().connect("ready", self._ready)

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        game_mgr.event_mgr.add(LEFT_BUTTON_BEGIN_DRAG, self.on_begin_drag)

        # init ui
        self.mainui_panel = self.get_obj().find_node("MainUI")
        self.mainui_controller = MainUIController()
        self.mainui_controller.setup(self.mainui_panel)

    def co_init_panels(self):
        yield None
        
        from game.ui.city_menu_controller import CityMenuController
        self.city_menu, self.city_menu_controller = self.load_panel(
                'res://ui/CityMenu.tscn', CityMenuController)

        from game.ui.ground_menu_controller import GroundMenuController
        self.ground_menu, self.ground_menu_controller = self.load_panel(
                'res://ui/GroundMenu.tscn', GroundMenuController)

        from game.ui.neizheng_controller import NeiZhengController
        self.neizheng_panel, self.neizheng_controller = self.load_panel(\
                'res://ui/NeiZhengPanel.tscn', NeiZhengController)
        

    def _ready(self):
        game_mgr.co_mgr.start(self.co_init_panels())
        pass

    def load_panel(self, path, cls):
        ui_obj = FNode3D.instantiate(path)
        ui_obj.reparent(self.get_obj())
        ui_obj.set_visible(False)

        controller = cls()
        controller.setup(ui_obj)

        return ui_obj, controller

    def update(self, delta_time):
        if len(self.defer_close_queue) > 0:
            for ui_obj in self.defer_close_queue:
                ui_obj.set_visible(False)
            self.defer_close_queue.clear()

    def close(self, item):
        self.defer_close(item)

    def defer_close(self, ui_obj):
        if ui_obj.is_show:
            self.defer_close_queue.append(ui_obj)

    # events handlers

    def on_begin_drag(self):
        self.close(self.city_menu)
        self.close(self.ground_menu)

        self.context_unit = None

    def on_scene_ground_click(self):
        if self.ground_menu.is_show:
            self.close(self.ground_menu)
        else:
            self.close(self.city_menu)
            self.context_unit = None

            x, y = game_mgr.input_mgr.get_mouse_pos()
            self.ground_menu.set_position(x, y)
            self.ground_menu.set_visible(True)

    def on_scene_unit_click(self, unit):
        self.close(self.ground_menu)
        self.context_unit = unit
        #print_line(f'click: {unit.unit_name}')

        if unit.unit_type == UT_CITY and \
                unit.owner_player_id == game_mgr.player_mgr.main_player_id:
            
            x, y = game_mgr.input_mgr.get_mouse_pos()

            self.city_menu.set_position(x, y)
            self.city_menu.set_visible(True)

