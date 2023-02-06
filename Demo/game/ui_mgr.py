#
# 2023年2月6日 bianpeng
#

from game.core import *
from game.event_name import *
from game.game_mgr import game_mgr

#
class UIMgr(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        self.context_menu_node = find_node(self.get_node(), 'ContextMenu')
        game_mgr.event_mgr.add(SCENE_UNIT_PRESS, self.on_scene_unit_press)

    def on_scene_unit_press(self, unit):
        print_line(f'click: {unit.unit_name}')
        camera = game_mgr.camera_mgr.main_camera
        #x, y = world_to_screen(camera , unit.location.x, unit.location.y, unit.location.z)
        x, y = game_mgr.input_mgr.x, game_mgr.input_mgr.y
        set_visible_2d(self.context_menu_node, True)
        set_position_2d(self.context_menu_node, x, y)



