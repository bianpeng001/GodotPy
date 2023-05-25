#
# 2023年2月6日 bianpeng
#

from game.core import log_debug, OS, NodeObject
from game.game_mgr import *
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

        # 控制tick频率
        self.tick_time = 0

        # 鼠标是否停留在ui上面
        self.last_x, self.last_y = 0, 0
        self.control_under_mouse = False
        
        # 加载完毕
        self.load_complete = False

    def is_point_at_gui(self):
        x, y = game_mgr.input_mgr.get_mouse_pos()
        dx = x - self.last_x
        dy = y - self.last_y

        if dx*dx + dy*dy > 10:
            camera = get_main_camera()
            self.control_under_mouse = camera.find_control(x, y)
            
            self.last_x = x
            self.last_y = y

        return self.control_under_mouse != None
        
    def _create(self):
        #self.get_obj().connect("ready", self._ready)
        game_mgr.co_mgr.start(self.co_init_panels())

        # from game.event_name import \
        #         SCENE_UNIT_CLICK,\
        #         LEFT_BUTTON_BEGIN_DRAG,\
        #         SCENE_GROUND_CLICK
        #game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        #game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        #game_mgr.event_mgr.add(LEFT_BUTTON_BEGIN_DRAG, self.on_begin_drag)
        self.text_effect_layer = self.get_obj().find_node('TextEffectLayer')

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

        from game.ui.troop_menu_controller import TroopMenuController
        _, self.troop_menu_controller = self.load_panel(
                'res://ui/TroopMenu.tscn', TroopMenuController)

        from game.ui.nav_panel_controller import NavPanelController
        _, self.nav_panel_controller = self.load_panel(
                'res://ui/NavPanel.tscn', NavPanelController)
        self.nav_panel_controller.popup(1010, 100)

        from game.ui.msg_panel_controller import MsgPanelController
        _, self.msg_panel_controller = self.load_panel(
                'res://ui/MsgPanel.tscn', MsgPanelController)
        self.msg_panel_controller.popup(2, 65)

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
        #self.auto_close_queue.append(self.npc_dialog_controller)

        from game.ui.option_panel_controller import OptionPanelController
        _, self.option_panel_controller = self.load_panel(
                'res://ui/OptionPanel.tscn', OptionPanelController)

        from game.ui.story_panel_controller import StoryPanelController
        _, self.story_panel_controller = self.load_panel(
                'res://ui/StoryPanel.tscn', StoryPanelController)

        from game.ui.setting_panel_controller import SettingPanelController
        _, self.setting_panel_controller = self.load_panel(
                'res://ui/SettingPanel.tscn', SettingPanelController)

        from game.ui.create_player_controller import CreatePlayerController
        _, self.create_player_controller = self.load_panel(
                'res://ui/InputPanel.tscn', CreatePlayerController)
        
        from game.ui.cmd_panel_controller import CmdPanelController
        _, self.cmd_panel_controller = self.load_panel(
                'res://ui/CmdPanel.tscn', CmdPanelController)
        
        from game.ui.sys_panel_controller import SysPanelController
        _, self.sys_panel_controller = self.load_panel(
                'res://ui/SysPanel.tscn', SysPanelController)
        
        from game.ui.cmd_dialog_controller import CmdDialogController
        _, self.cmd_dialog_controller = self.load_panel(
                'res://ui/CmdDialog.tscn', CmdDialogController)
        
        self.init_select_rect()
        
        # load done
        log_debug('ui panels load ok')

        # 菜单列表
        self.context_menu_list = [
            self.city_menu_controller,
            self.ground_menu_controller,
            self.troop_menu_controller,
        ]

        # 一直显示的列表
        self.base_ui_list = [
            self.msg_panel_controller,
            self.nav_panel_controller,
            self.mainui_controller,
        ]
        
        self.load_complete = True

    def load_panel(self, path, cls):
        ui_obj = OS.instantiate(path)
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

    def show_menu(self, menu):
        for item in self.context_menu_list:
            if item == menu:
                if item.is_show():
                    item.defer_close()
                else:
                    item.popup_at_mouse()
            else:
                item.defer_close()

    # 开始拖拽场景
    def on_begin_drag(self):
        self.show_menu(None)
        self.click_unit = None

    def set_context_unit(self, unit):
        self.context_unit = unit
        
        # 去掉单位身上的菜单交互. 菜单太丑恶了.
        # 显示单位指令菜单
        # if unit:
        #     self.cmd_panel_controller.init(unit)
        # else:
        #     self.cmd_panel_controller.defer_close()

    # 点击空地
    def on_scene_ground_click(self):
        if self.get_top_panel():
            log_debug('top panel visible', self.get_top_panel())
            return

        self.set_context_unit(None)
        self.show_menu(self.ground_menu_controller)

    # 点击场景中的单位
    def on_scene_unit_click(self, unit):
        if self.get_top_panel():
            log_debug('top panel visible', self.get_top_panel())
            return

        self.click_unit = unit
        self.set_context_unit(unit)
        #print_line(f'click: {unit.unit_name}')

        if unit.unit_type == UT_CITY:
            if check_main_owner(unit):
                self.city_menu_controller.init(unit)
                self.show_menu(self.city_menu_controller)
            else:
                pass
        elif unit.unit_type == UT_TROOP:
            if check_main_owner(unit):
                self.troop_menu_controller.init(unit)
                self.show_menu(self.troop_menu_controller)
            else:
                pass
            log_debug('troop click', unit.unit_name)
        else:
            self.show_menu(None)

    # region panel stack, 
    # TODO: 这个准备去掉了, 改用面板链, 那个更简单方便好控制
    
    # 界面的入栈出栈,用来恢复上级界面
    def push_panel(self, top_panel):
        if len(self.panel_stack) > 0:
            if self.panel_stack[-1] == top_panel:
                raise Exception('push repeat ui')
            
            self.panel_stack[-1].defer_close()

        self.panel_stack.append(top_panel)
        top_panel.show()

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
        
    # endregion

    def show_base_ui(self, show):
        if show:
            for item in self.base_ui_list:
                item.show()
        else:
            for item in self.base_ui_list:
                item.defer_close()


    def init_select_rect(self):
        from game.ui.rect_select_controller import RectSelectController
        
        ui_obj = game_mgr.scene_root_obj.find_node('UIMgr/SelectRect')
        self.rect_select_controller = RectSelectController()
        self.rect_select_controller.setup(ui_obj)
        self.rect_select_controller.hide()
        
