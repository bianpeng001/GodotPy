#
# 2023年2月6日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UT_CITY

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

        self.auto_close_queue = []


    def _create(self):
        #self.get_obj().connect("ready", self._ready)
        game_mgr.co_mgr.start(self.co_init_panels())

        from game.event_name import SCENE_UNIT_CLICK, \
                LEFT_BUTTON_BEGIN_DRAG, \
                SCENE_GROUND_CLICK

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        game_mgr.event_mgr.add(LEFT_BUTTON_BEGIN_DRAG, self.on_begin_drag)

        # init ui
        

    # 因为ready里面，scene_tree的限制，还不让加载对象
    # 所以，用一个coroutine，等一帧
    def co_init_panels(self):
        yield None

        from game.ui.mainui_controller import MainUIController
        self.mainui_panel, self.mainui_controller = self.load_panel(
            'res://ui/MainUI.tscn', MainUIController)
        self.mainui_panel.set_position(0, 0)
        self.mainui_panel.set_visible(True)
        
        from game.ui.city_menu_controller import CityMenuController
        self.city_menu, self.city_menu_controller = self.load_panel(
                'res://ui/CityMenu.tscn', CityMenuController)

        from game.ui.ground_menu_controller import GroundMenuController
        self.ground_menu, self.ground_menu_controller = self.load_panel(
                'res://ui/GroundMenu.tscn', GroundMenuController)

        from game.ui.neizheng_controller import NeiZhengController
        self.neizheng_panel, self.neizheng_controller = self.load_panel(
                'res://ui/NeiZhengPanel.tscn', NeiZhengController)

        from game.ui.npc_dialog_controller import NpcDialogController
        self.npc_dialog, self.npc_dialog_controller = self.load_panel(
            'res://ui/NpcDialog.tscn', NpcDialogController)

        from game.ui.select_hero_controller import SelectHeroController
        self.select_hero_dialog, self.select_hero_controller = self.load_panel(
            'res://ui/SelectHeroDialog.tscn', SelectHeroController)
        
        self.auto_close_queue.append(self.npc_dialog_controller)


    # def _ready(self):
    #     game_mgr.co_mgr.start(self.co_init_panels())
    #     pass

    def load_panel(self, path, cls):
        ui_obj = FNode3D.instantiate(path)
        ui_obj.reparent(self.get_obj())
        ui_obj.set_visible(False)

        controller = cls()
        controller.setup(ui_obj)

        return ui_obj, controller

    def update(self, delta_time):
        # 前一帧关闭的元素
        if len(self.defer_close_queue) > 0:
            for ui_obj in self.defer_close_queue:
                ui_obj.set_visible(False)
            self.defer_close_queue.clear()

        # 延时关闭的元素
        for item in self.auto_close_queue:
            if item.show_time > 0:
                item.show_time -= delta_time
                if item.show_time <= 0:
                    item.show_time = 0
                    self.defer_close(item.ui_obj)

    # 下一帧开头关闭
    # 避免本帧直接关闭，出现点穿的现象。如果立即关闭，则会判定为在空地上点了一下
    def defer_close(self, ui_obj):
        if ui_obj.visible:
            self.defer_close_queue.append(ui_obj)

    # events handlers

    def on_begin_drag(self):
        self.defer_close(self.city_menu)
        self.defer_close(self.ground_menu)

        self.context_unit = None

    def on_scene_ground_click(self):
        if self.ground_menu.visible:
            self.defer_close(self.ground_menu)
        else:
            self.defer_close(self.city_menu)

            self.context_unit = None
            x, y = game_mgr.input_mgr.get_mouse_pos()
            self.ground_menu.set_position(x, y)
            self.ground_menu.set_visible(True)

    def on_scene_unit_click(self, unit):
        self.defer_close(self.ground_menu)

        self.context_unit = unit
        #print_line(f'click: {unit.unit_name}')

        if unit.unit_type == UT_CITY:
            print(unit.owner_is_main_player())
            if unit.owner_is_main_player():
                x, y = game_mgr.input_mgr.get_mouse_pos()
                self.city_menu.set_position(x, y)
                self.city_menu.set_visible(True)
            else:
                # TODO
                pass
        else:
            # TODO
            pass

