#
# 2023年2月5日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.event_name import LEFT_BUTTON_PRESS, SCENE_UNIT_PRESS

#
class RaycastMgr(NodeObject):
    def __init__(self):
        super().__init__()

        game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, self.on_mouse_press)
        self.reqs = []
    
    def _create(self):
        set_process(self.get_node(), physics=False)
        pass

    def on_mouse_press(self, x, y):
        camera = game_mgr.camera_mgr.main_camera

        if find_control(camera, x, y):
            print_line(f'on control {x} {y}')
            return
        
        wx,wy,wz = screen_to_world(camera, x, y)
        #self.reqs.append((wx, wy, wz))
        #print_line(f'press: {wx},{wy},{wz}')

        # TODO: 找到点击的单位
        tile = game_mgr.ground_mgr.get_tile(wx, wz)
        if tile:
            for unit in tile.units:
                dx = unit.location.x - wx
                dz = unit.location.z - wz
                if dx*dx+dz*dz < 3*3*2:
                    #print_line(f'click: {unit.unit_name} {unit.unit_id}')
                    game_mgr.event_mgr.emit(SCENE_UNIT_PRESS, unit)

    def _physics_process(self):
        camera = game_mgr.camera_mgr.main_camera
        
        for a in self.reqs:
            print_line(f'raycast:{a}')
            shape = raycast_shape(camera, *a)
        
        self.reqs.clear()

