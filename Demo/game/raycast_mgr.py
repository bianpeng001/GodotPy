#
# 2023年2月5日 bianpeng
#

from game.core import log_debug, NodeObject
from game.game_mgr import *
from game.event_name import LEFT_BUTTON_CLICK, SCENE_UNIT_CLICK, SCENE_GROUND_CLICK
from game.base_type import UT_TROOP
from game.ground_mgr import pos_to_colrow

#
# raycast管理, 在input的基础上
# 处理场景中的物体点击选中
#
class RaycastMgr(NodeObject):
    def __init__(self):
        super().__init__()

        game_mgr.event_mgr.add(LEFT_BUTTON_CLICK, self.on_mouse_click)
        self.reqs = []
    
    def _create(self):
        #self.get_obj().set_process(physics=True)
        pass

    def on_mouse_click(self):
        camera = game_mgr.camera_mgr.main_camera
        screen_x,screen_y = game_mgr.input_mgr.get_mouse_pos()

        #if camera.find_control(x, y):
        if game_mgr.ui_mgr.is_point_at_gui():
            #log_util.debug('click on control, ui event system take over', st=False)
            return
        
        # 点击点在地面的位置
        x,y,z = camera.screen_to_world(screen_x, screen_y)
        #self.reqs.append((wx, wy, wz))
        #log_debug(f'press: {wx},{wy},{wz}')

        # TODO: 找到点击的单位, 用距离找的,比较土, 但还能用
        # 有可能点到多个单位, 难免会重叠
        
        tile = game_mgr.ground_mgr.get_tile(x, z)
        if tile:
            item_list = []
            
            def check_tile_unit(col, row):
                tile = game_mgr.ground_mgr.get_tile_colrow(col,row)
                if tile:
                    for unit in tile.get_unit_list():
                        unit_x, _, unit_z = unit.get_position()
                        dx = unit_x - x
                        dz = unit_z - z
                        sqrdis = dx*dx+dz*dz
                        if sqrdis < unit.radius*unit.radius:
                            item_list.append((unit, sqrdis))
            
            col, row = tile.col, tile.row
            # 这里根据位置, 少找一些相邻块, 点击的那边也是
            loc_x, loc_z = tile.get_local_pos(x,z)
            
            check_tile_unit(col, row)
            if loc_z < -0.4:
                check_tile_unit(col,row-1)
            if loc_z > 0.4:
                check_tile_unit(col,row+1)
            if loc_x > 0.4:
                check_tile_unit(col+1,row)
            if loc_x < -0.4:
                check_tile_unit(col-1,row)
            
            if loc_x > 0.4 and loc_z < -0.4:
                check_tile_unit(col+1,row-1)
            if loc_x > 0.4 and loc_z > 0.4:
                check_tile_unit(col+1,row+1)
            if loc_x < -0.4 and loc_z < -0.4:
                check_tile_unit(col-1,row-1)
            if loc_x < -0.4 and loc_z > 0.4:
                check_tile_unit(col-1,row+1)
            
            # 最后, 处理结果
            if len(item_list) == 0:
                game_mgr.event_mgr.emit(SCENE_GROUND_CLICK)
            else:
                item_list.sort(key=lambda x: x[1])
                
                a = next(filter(lambda x: x[0].unit_type == UT_TROOP, item_list), None)
                if not a:
                    a = item_list[0]
                game_mgr.event_mgr.emit(SCENE_UNIT_CLICK, a[0])

    def _physics_process(self):
        # camera = game_mgr.camera_mgr.main_camera
        
        # for a in self.reqs:
        #     log_debug(f'raycast:{a}')
        #     shape = raycast_shape(camera, *a)
        # self.reqs.clear()
        pass


