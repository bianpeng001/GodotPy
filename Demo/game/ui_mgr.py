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
        # 超时自动关闭队列
        self.auto_close_queue = []
        # 
        self.update_list = []

        # 界面栈，用来恢复上级界面用的
        self.panel_stack = []

        # 点击的和正在操作的，做一下语义的区分
        self.click_unit = None
        self.context_unit = None

        self.tick_time = 0

        # 鼠标是否停留在ui上面
        self.last_x, self.last_y = 0, 0
        self.last_point_at_gui = False

    def is_point_at_gui(self):
        x, y = game_mgr.input_mgr.get_mouse_pos()
        dx = x - self.last_x
        dy = y - self.last_y

        if dx*dx + dy*dy > 10:
            camera = game_mgr.camera_mgr.main_camera
            self.last_point_at_gui = camera.find_control(x, y) != None

        return self.last_point_at_gui
        
    def _create(self):
        #self.get_obj().connect("ready", self._ready)
        game_mgr.co_mgr.start(self.co_init_panels())

        from game.event_name import SCENE_UNIT_CLICK, \
                LEFT_BUTTON_BEGIN_DRAG, \
                SCENE_GROUND_CLICK

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        game_mgr.event_mgr.add(LEFT_BUTTON_BEGIN_DRAG, self.on_begin_drag)

    # 因为ready里面，scene_tree的限制，还不让加载对象
    # 所以，用一个coroutine，等一帧
    def co_init_panels(self):
        yield None

        from game.ui.mainui_controller import MainUIController
        self.mainui_panel, self.mainui_controller = self.load_panel(
              'res://ui/MainUI.tscn', MainUIController)
        self.mainui_controller.popup(0, 0)
        
        # 要注意这里的顺序, 有关层级
        from game.ui.city_menu_controller import CityMenuController
        self.city_menu, self.city_menu_controller = self.load_panel(
                'res://ui/CityMenu.tscn', CityMenuController)

        from game.ui.ground_menu_controller import GroundMenuController
        self.ground_menu, self.ground_menu_controller = self.load_panel(
                'res://ui/GroundMenu.tscn', GroundMenuController)

        from game.ui.nav_panel_controller import NavPanelController
        self.nav_panel, self.nav_panel_controller = self.load_panel(
                'res://ui/NavPanel.tscn', NavPanelController)
        self.nav_panel_controller.popup(1010, 100)

        from game.ui.msg_panel_controller import MsgPanelController
        self.msg_panel, self.msg_panel_controller = self.load_panel(
                'res://ui/MsgPanel.tscn', MsgPanelController)
        self.msg_panel_controller.popup(4, 442)

        from game.ui.npc_dialog_controller import NpcDialogController
        self.npc_dialog, self.npc_dialog_controller = self.load_panel(
                'res://ui/NpcDialog.tscn', NpcDialogController)
        self.auto_close_queue.append(self.npc_dialog_controller)

        # 下面是按需弹出
        from game.ui.build_panel_controller import BuildPanelController
        self.build_panel, self.build_panel_controller = self.load_panel(
                'res://ui/BuildPanel.tscn', BuildPanelController)
        self.update_list.append(self.build_panel_controller)

        from game.ui.neizheng_controller import NeiZhengController
        self.neizheng_panel, self.neizheng_controller = self.load_panel(
                'res://ui/NeiZhengPanel.tscn', NeiZhengController)

        from game.ui.select_hero_controller import SelectHeroController
        self.select_hero_dialog, self.select_hero_controller = self.load_panel(
                'res://ui/SelectHeroDialog.tscn', SelectHeroController)

        from game.ui.map_panel_controller import MapPanelController
        self.map_panel, self.map_panel_controller = self.load_panel(
                'res://ui/MapPanel.tscn', MapPanelController)

        

        # load done
        log_util.debug('ui panels load ok')

    def load_panel(self, path, cls):
        ui_obj = FNode3D.instantiate(path)
        ui_obj.reparent(self.get_obj())
        #ui_obj.set_visible(False)

        controller = cls()
        controller.setup(ui_obj)
        controller.hide()

        return ui_obj, controller

    def update(self, delta_time):
        # 前一帧关闭的元素
        if len(self.defer_close_queue) > 0:
            for item in self.defer_close_queue:
                item.hide()
            self.defer_close_queue.clear()

        # 延时关闭的元素
        for item in self.auto_close_queue:
            if item.show_time > 0:
                item.show_time -= delta_time
                if item.show_time <= 0:
                    item.show_time = 0
                    item.hide()

        # 有一些面板需要update
        for panel in self.update_list:
            panel.update()

    # 下一帧开头关闭
    # 避免本帧直接关闭，出现点穿的现象。如果立即关闭，则会判定为在空地上点了一下
    def defer_close(self, ui_controller):
        if ui_controller.is_visible:
            self.defer_close_queue.append(ui_controller)

    # events handlers

    # 开始拖拽场景
    def on_begin_drag(self):
        self.city_menu_controller.defer_close()
        self.ground_menu_controller.defer_close()
        self.click_unit = None

    # 点击空地
    def on_scene_ground_click(self):
        # 正在建设就不用弹菜单了
        if self.build_panel_controller.is_building():
            return

        if self.ground_menu_controller.is_visible:
            self.ground_menu_controller.defer_close()
        else:
            self.city_menu_controller.defer_close()

            self.click_unit = None
            self.ground_menu_controller.popup_at_mouse()

    # 点击c场景中的单位
    def on_scene_unit_click(self, unit):
        self.ground_menu_controller.defer_close()

        self.click_unit = unit
        self.context_unit = unit
        #print_line(f'click: {unit.unit_name}')

        if unit.unit_type == UT_CITY:
            if unit.owner_is_main_player():
                self.city_menu_controller.popup_at_mouse()
            else:
                # TODO
                pass
        else:
            # TODO
            pass


    def push_panel(self, ui_controller):
        ui_controller.defer_close()
        self.panel_stack.append(ui_controller)

    def pop_panel(self):
        if self.panel_stack:
            ui_controller = self.panel_stack.pop()
            ui_controller.show()
            return ui_controller




            