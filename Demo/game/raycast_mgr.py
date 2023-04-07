#
# 2023年2月5日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.event_name import LEFT_BUTTON_CLICK, SCENE_UNIT_CLICK, SCENE_GROUND_CLICK

# raycast场景中的物体的操作，并发事件
class RaycastMgr(NodeObject):
    def __init__(self):
        super().__init__()

        game_mgr.event_mgr.add(LEFT_BUTTON_CLICK, self.on_mouse_click)
        self.reqs = []
    
    def _create(self):
        self.get_obj().set_process(physics=True)
        pass

    def on_mouse_click(self):
        camera = game_mgr.camera_mgr.main_camera
        screen_x,screen_y = game_mgr.input_mgr.get_mouse_pos()

        #if camera.find_control(x, y):
        if game_mgr.ui_mgr.is_point_at_gui():
            #log_util.debug('click on control, ui event system take over', st=False)
            return
        
        x,y,z = camera.screen_to_world(screen_x, screen_y)
        #self.reqs.append((wx, wy, wz))
        #log_debug(f'press: {wx},{wy},{wz}')

        # TODO: 找到点击的单位, 用距离找的,比较土, 但还能用
        # 有可能点到多个单位, 难免会重叠
        tile = game_mgr.ground_mgr.get_tile(x, z)
        if tile:
            item_list = []
            for unit in tile.unit_list:
                unit_x, _, unit_z = unit.get_position()
                dx = unit_x - x
                dz = unit_z - z
                if dx*dx+dz*dz < unit.radius*unit.radius:
                    item_list.append(unit)

            if len(item_list) == 0:
                game_mgr.event_mgr.emit(SCENE_GROUND_CLICK)
            else:
                # TODO: 这里以后加条件
                game_mgr.event_mgr.emit(SCENE_UNIT_CLICK, item_list[0])

    def _physics_process(self):
        camera = game_mgr.camera_mgr.main_camera
        
        for a in self.reqs:
            log_debug(f'raycast:{a}')
            shape = raycast_shape(camera, *a)
        self.reqs.clear()




