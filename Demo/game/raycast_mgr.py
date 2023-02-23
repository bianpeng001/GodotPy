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
        #set_process(self.get_node(), physics=True)
        self.get_obj().set_process(physics=True)
        pass

    def on_mouse_click(self):
        camera = game_mgr.camera_mgr.main_camera
        x, y = game_mgr.input_mgr.get_mouse_pos()

        if camera.find_control(x, y):
            logutil.debug('click on control, ui event system take over')
            return
        
        wx,wy,wz = camera.screen_to_world(x, y)
        #self.reqs.append((wx, wy, wz))
        #print_line(f'press: {wx},{wy},{wz}')

        # TODO: 找到点击的单位
        tile = game_mgr.ground_mgr.get_tile(wx, wz)
        if tile:
            click_on_unit = False
            for unit in tile.units:
                unit_x, _, unit_z = unit.get_position()
                dx = unit_x - wx
                dz = unit_z - wz
                if dx*dx+dz*dz < unit.radius*unit.radius:
                    #print_line(f'click: {unit.unit_name} {unit.unit_id}')
                    game_mgr.event_mgr.emit(SCENE_UNIT_CLICK, unit)
                    click_on_unit = True
                    break

            if not click_on_unit:
                game_mgr.event_mgr.emit(SCENE_GROUND_CLICK)

    def _physics_process(self):
        camera = game_mgr.camera_mgr.main_camera
        
        for a in self.reqs:
            logutil.debug(f'raycast:{a}')
            shape = raycast_shape(camera, *a)
        self.reqs.clear()




