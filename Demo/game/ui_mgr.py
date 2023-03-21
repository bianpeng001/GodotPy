#
# 2023年2月6日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import UT_CITY, UT_TROOP

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
        self.control_under_mouse = False

    def is_point_at_gui(self):
        x, y = game_mgr.input_mgr.get_mouse_pos()
        dx = x - self.last_x
        dy = y - self.last_y

        if dx*dx + dy*dy > 10:
            camera = game_mgr.camera_mgr.main_camera
            self.control_under_mouse = camera.find_control(x, y)

        return self.control_under_mouse != None
        
    def _create(self):
        #self.get_obj().connect("ready", self._ready)
        game_mgr.co_mgr.start(self.co_init_panels())

        from game.event_name import SCENE_UNIT_CLICK,\
                LEFT_BUTTON_BEGIN_DRAG,\
                SCENE_GROUND_CLICK

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        game_mgr.event_mgr.add(LEFT_BUTTON_BEGIN_DRAG, self.on_begin_drag)

    # 因为ready里面，scene_tree的限制，还不让加载对象
    # 所以，用一个coroutine，等一帧
    def co_init_panels(self):
        yield None

        from game.ui.mainui_controller import MainUIController
        _, self.mainui_controller = self.load_panel(
              'res://ui/MainUI.tscn', MainUIController)
        self.mainui_controller.popup(0, 0)
        
        # 要注意这里的顺序, 有关层级
        from game.ui.city_menu_controller import CityMenuController
        _, self.city_menu_controller = self.load_panel(
                'res://ui/CityMenu.tscn', CityMenuController)

        from game.ui.ground_menu_controller import GroundMenuController
        _, self.ground_menu_controller = self.load_panel(
                'res://ui/GroundMenu.tscn', GroundMenuController)

        from game.ui.nav_panel_controller import NavPanelController
        _, self.nav_panel_controller = self.load_panel(
                'res://ui/NavPanel.tscn', NavPanelController)
        self.nav_panel_controller.popup(1010, 100)

        from game.ui.msg_panel_controller import MsgPanelController
        _, self.msg_panel_controller = self.load_panel(
                'res://ui/MsgPanel.tscn', MsgPanelController)
        self.msg_panel_controller.popup(4, 484)

        # 下面是按需弹出
        from game.ui.build_panel_controller import BuildPanelController
        _, self.build_panel_controller = self.load_panel(
                'res://ui/BuildPanel.tscn', BuildPanelController)
        self.update_list.append(self.build_panel_controller)

        from game.ui.neizheng_controller import NeiZhengController
        _, self.neizheng_controller = self.load_panel(
                'res://ui/NeiZhengPanel.tscn', NeiZhengController)

        from game.ui.map_panel_controller import MapPanelController
        _, self.map_panel_controller = self.load_panel(
                'res://ui/MapPanel.tscn', MapPanelController)

        from game.ui.select_hero_controller import SelectHeroController
        _, self.select_hero_controller = self.load_panel(
                'res://ui/SelectHeroDialog.tscn', SelectHeroController)

        from game.ui.select_target_controller import SelectTargetController
        _, self.select_target_controller = self.load_panel(
                'res://ui/SelectTarget.tscn', SelectTargetController)

        from game.ui.chuzhan_panel_controller import ChuZhanPanelController
        _, self.chuzhan_panel_controller = self.load_panel(
                'res://ui/ChuZhanPanel.tscn', ChuZhanPanelController)

        from game.ui.npc_dialog_controller import NpcDialogController
        _, self.npc_dialog_controller = self.load_panel(
                'res://ui/NpcDialog.tscn', NpcDialogController)
        self.auto_close_queue.append(self.npc_dialog_controller)

        from game.ui.setting_panel_controller import SettingPanelController
        _, self.setting_panel_controller = self.load_panel(
                'res://ui/SettingPanel.tscn', SettingPanelController)

        from game.ui.story_panel_controller import StoryPanelController
        _, self.story_panel_controller = self.load_panel(
                'res://ui/StoryPanel.tscn', StoryPanelController)
        # load done
        log_debug('ui panels load ok')

    def load_panel(self, path, cls):
        ui_obj = FNode3D.instantiate(path)
        ui_obj.reparent(self.get_obj())

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
        if ui_controller.is_show():
            self.defer_close_queue.append(ui_controller)

    # 开始拖拽场景
    def on_begin_drag(self):
        self.city_menu_controller.defer_close()
        self.ground_menu_controller.defer_close()
        self.click_unit = None

    # 点击空地
    def on_scene_ground_click(self):
        if self.get_top_panel():
            log_debug('top panel visible', self.get_top_panel())
            return

        self.city_menu_controller.defer_close()
        if self.ground_menu_controller.is_show():
            self.ground_menu_controller.defer_close()
        else:
            self.click_unit = None
            self.ground_menu_controller.popup_at_mouse()

    # 点击场景中的单位
    def on_scene_unit_click(self, unit):
        if self.get_top_panel():
            log_debug('top panel visible', self.get_top_panel())
            return

        self.click_unit = unit
        self.context_unit = unit
        #print_line(f'click: {unit.unit_name}')

        self.ground_menu_controller.defer_close()
        if unit.unit_type == UT_CITY:
            if unit.owner_is_main_player():
                self.city_menu_controller.popup_at_mouse()
            else:
                pass
        elif unit.unit_type == UT_TROOP:
            log_debug('troop click', unit.unit_name)
        else:
            pass

    # 界面的入栈出栈,用来恢复上级界面
    def push_panel(self, cur_ui):
        if len(self.panel_stack) > 0:
            self.panel_stack[-1].defer_close()
        self.panel_stack.append(cur_ui)
        cur_ui.show()

    def pop_panel(self, cur_ui):
        # 判断只有自己能关闭自己,别人都不行
        if cur_ui and cur_ui != self.get_top_panel():
            raise Exception('top ui should be close by itself')

        # 关闭当前的
        if len(self.panel_stack) > 0:
            self.panel_stack.pop().defer_close()
            
        # 上级界面恢复显示, 如果有的话
        if len(self.panel_stack) > 0:
            self.panel_stack[-1].show()

    # 获取当前的顶层ui controller
    def get_top_panel(self):
        if len(self.panel_stack) > 0:
            return self.panel_stack[-1]


