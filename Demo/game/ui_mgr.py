#
# 2023年2月6日 bianpeng
#

from game.core import *
from game.event_name import SCENE_UNIT_CLICK, LEFT_BUTTON_BEGIN_DRAG, SCENE_GROUND_CLICK
from game.game_mgr import game_mgr

#
class UIMgr(NodeObject):
    def __init__(self):
        super().__init__()
        game_mgr.ui_mgr = self

        # 排队等关闭的ui，ui不能马上关闭，需要排队，不然马上就响应ui下面的元素被点击了
        self.hide_item_queue = []
        self.context_unit = None

    def _create(self):
        set_process(self.get_node(), process=False)
        connect(self.get_node(), 'ready', self._ready)

        game_mgr.event_mgr.add(SCENE_UNIT_CLICK, self.on_scene_unit_click)
        game_mgr.event_mgr.add(SCENE_GROUND_CLICK, self.on_scene_ground_click)
        game_mgr.event_mgr.add(LEFT_BUTTON_BEGIN_DRAG, self.on_begin_drag)

    def _ready(self):
        cm = find_node(self.get_node(), 'ContextMenu')
        self.context_menu_node = cm
        connect(find_node(cm, 'Panel/Button1'), 'pressed', self.on_cm_button1)
        connect(find_node(cm, 'Panel/Button2'), 'pressed', self.on_cm_button2)
        connect(find_node(cm, 'Panel/Button3'), 'pressed', self.on_cm_button3)
        pass

    def on_begin_drag(self):
        self.close(self.context_menu_node)
        self.context_unit = None

    def on_scene_ground_click(self):
        self.close(self.context_menu_node)
        self.context_unit = None

    def on_scene_unit_click(self, unit):
        self.context_unit = unit
        print_line(f'click: {unit.unit_name}')

        camera = game_mgr.camera_mgr.main_camera
        #x, y = world_to_screen(camera , unit.location.x, unit.location.y, unit.location.z)
        x, y = game_mgr.input_mgr.x, game_mgr.input_mgr.y
        set_position_2d(self.context_menu_node, x, y)
        set_visible_2d(self.context_menu_node, True)

    def on_cm_button1(self):
        self.close(self.context_menu_node)
        print_line(f'{self.context_unit.unit_name} neizheng')
    
    def on_cm_button2(self):
        self.close(self.context_menu_node)
        print_line(f'{self.context_unit.unit_name} chuzhan')

    def on_cm_button3(self):
        self.close(self.context_menu_node)
        print_line(f'{self.context_unit.unit_name} tansuo')
    
    def update(self, delta_time):
        for a in self.hide_item_queue:
            set_visible_2d(a, False)
        self.hide_item_queue.clear()

    def close(self, item):
        self.hide_item_queue.append(item)


