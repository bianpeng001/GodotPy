#
# 2023年1月31日 bianpeng
#
import math
import random
import struct

from game.core import *
from game.game_mgr import *
from game.load_world_map import Bmp

TILE_SIZE = 30

# col,row
def pos_to_colrow(x, z):
    return round(x / TILE_SIZE), round(z / TILE_SIZE)

# tile内部，a*寻路
# tile外部，大a*寻路
# 打仗过程里面，走直线, 加一点弧度或者干扰, 别笔直就好了
class Tile:
    def __init__(self, col, row):
        # 区块的ID，坐标/TILE_SIZE, 取整
        self.col = col
        self.row = row
        # 自己的地块模型
        self.model_node = None
        # 附属模型
        self.item_nodes = []
        # 上面的单位列表
        self.unit_list = []

        # 用来控制可见列表
        self.show_age = 1

        self.city_unit = None

        # 颜色
        self.color = -1

    def get_center_pos(self):
        return self.col*TILE_SIZE,self.row*TILE_SIZE

    def load(self):
        #log_debug(f'load tile: ({self.col},{self.row})')
        pos_x, pos_z = self.get_center_pos()

        self.model_node = FNode3D.instantiate('res://models/Tile01.tscn')
        self.model_node.set_position(pos_x, 0, pos_z)

        #self.test_mesh()
        # if self.color == 0:
        #     mi.load_material(0, 'res://models/Terrain/WaterMat.tres')
        # else:
        #     mi.load_material(0, 'res://models/Terrain/GrassMat.tres')
        
        mi = self.model_node.find_node('Mesh')
        self.generate_mesh(mi)
        mat = OS.load_resource('res://models/Terrain/Terrain03Mat.tres')
        mi.set_surface_material(0, mat)

    def test_mesh(self):
        mi = self.model_node.find_node('Mesh')

        st = FSurfaceTool()
        st.set_uv(0, 0)
        st.add_vertex(-1, 0, -1)
        st.set_uv(1, 0)
        st.add_vertex(1, 0, -1)
        st.set_uv(1, 1)
        st.add_vertex(1, 0, 1)
        st.set_uv(0, 1)
        st.add_vertex(-1, 0, 1)

        st.add_triangle(0, 1, 2)
        st.add_triangle(0, 2, 3)

        st.commit(mi)

    
    # 生成地形融合, 最好是用贴图来融合
    def generate_mesh(self, mi):
        
        def get_color(col,row):
            if col >= 0 and col < 300 and row >= 0 and row < 300:
                b,g,r = bmp.get_color(col, row)
                if r != 255:
                    r = 0
                return r,g,b
            else:
                return 0,0,0
        def get_uv(r):
            if r == 255:
                return 0.11,0.11
            else:
                return 0.36, 0.86
            
        bmp = game_mgr.ground_mgr.terrain_map
        STEP = 0.2
        vertex_index = 0
        
        st = FSurfaceTool()
        st.set_color(0.11,0.11,0.36,0.86)
        st.set_normal(0, 1, 0)
        
        for i in range(100):
            x = i % 10
            y = i // 10
            
            col,row = x+(self.col+15)*10, y+(self.row+15)*10
            r,g,b = get_color(col, row)
            u,v = get_uv(r)
            st.set_color(u,v,u,v)
            
            st.set_uv(0.5, 1.0)
            st.add_vertex(-1+x*STEP, 0, -1+y*STEP)
            st.set_uv(1.0, 1.0)
            st.add_vertex(-1+(x+1)*STEP, 0, -1+y*STEP)
            st.set_uv(1.0, 0.0)
            st.add_vertex(-1+(x+1)*STEP, 0, -1+(y+1)*STEP)
            st.set_uv(0.5, 0.0)
            st.add_vertex(-1+x*STEP, 0, -1+(y+1)*STEP)
            
            st.add_triangle(vertex_index, vertex_index+1, vertex_index+2)
            st.add_triangle(vertex_index, vertex_index+2, vertex_index+3)
            vertex_index+=4
            
        st.commit(mi)
    
    # TODO: 根据底图生成mesh, 用来表示地形
    def generate_mesh1(self):
        bmp = game_mgr.ground_mgr.terrain_map
        def get_color(col,row):
            if col >= 0 and col < 300 and row >= 0 and row < 300:
                b,g,r = bmp.get_color(col, row)
                if r != 255:
                    r = 0
                return r,g,b
            else:
                return 0,0,0
            
        def set_uv(r):
            if r == 255:
                st.set_uv(0.11,0.11)
            else:
                st.set_uv(0.36, 0.86)
                
        STEP = 0.2
        st = FSurfaceTool()
        vertex_index = 0
        for y in range(10):
            for x in range(10):
                col,row = x+(self.col+15)*10, y+(self.row+15)*10
                st.set_normal(0, 1, 0)
                
                #  2
                # 301
                #  4
                r0,_,_ = get_color(col, row)
                r1,_,_ = get_color(col+1, row)
                r2,_,_ = get_color(col, row-1)
                r3,_,_ = get_color(col-1, row)
                r4,_,_ = get_color(col, row+1)
                
                if r2 == r3:
                    set_uv(r2)
                    st.add_vertex(-1+x*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+(y+1)*STEP)
                    st.add_vertex(-1+x*STEP, 0, -1+(y+1)*STEP)
                    st.add_triangle(vertex_index, vertex_index+1, vertex_index+2)
                    vertex_index+=3
                    
                    set_uv(r4)
                    st.add_vertex(-1+x*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+(y+1)*STEP)
                    st.add_triangle(vertex_index, vertex_index+1, vertex_index+2)
                    vertex_index+=3
                    
                elif r3 == r4:
                    set_uv(r3)
                    st.add_vertex(-1+x*STEP, 0, -1+(y+1)*STEP)
                    st.add_vertex(-1+x*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+y*STEP)
                    st.add_triangle(vertex_index, vertex_index+1, vertex_index+2)
                    vertex_index+=3
                    
                    set_uv(r2)
                    st.add_vertex(-1+x*STEP, 0, -1+(y+1)*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+(y+1)*STEP)
                    st.add_triangle(vertex_index, vertex_index+1, vertex_index+2)
                    vertex_index+=3
                else:
                    set_uv(r0)
                    st.add_vertex(-1+x*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+y*STEP)
                    st.add_vertex(-1+(x+1)*STEP, 0, -1+(y+1)*STEP)
                    st.add_vertex(-1+x*STEP, 0, -1+(y+1)*STEP)
                    st.add_triangle(vertex_index, vertex_index+1, vertex_index+2)
                    st.add_triangle(vertex_index, vertex_index+2, vertex_index+3)
                    vertex_index+=4
                    
        mi = self.model_node.find_node('Mesh')
        st.commit(mi)

    def load_items(self):
        pos_x, pos_z = self.get_center_pos()
        # 树
        for i in range(random.randrange(1, 10)):
            path = 'res://models/Tree01.tscn'
            if random.random() < 0.2:
                path = 'res://models/Tree02.tscn'
            self.load_res(path,
                pos_x + random_x()*15,
                pos_z + random_x()*15,
                0.5 + random.random()*1.0)

        # 草
        for i in range(random.randrange(1, 5)):
            self.load_res('res://models/Grass01.tscn',
                pos_x + random_x()*15,
                pos_z + random_x()*15,
                0.8 + random.random()*0.7)

        # 亭
        if random_100() < 30:
            rad = random_x()*math.pi
            dis = 6 + random.random()*10
            self.load_res('res://models/Pavilion01.tscn',
                pos_x + math.cos(rad)*dis,
                pos_z + math.sin(rad)*dis,
                1.0)

    def create_city(self):
        if not self.city_unit and \
                self.color == 255 and \
                random_100() < 35:
            pos_x,pos_z = self.get_center_pos()

            self.city_unit = game_mgr.unit_mgr.create_city()
            if random_100() < 50:
                self.city_unit.model_type = 2

            self.city_unit.owner_player_id = 0
            self.city_unit.set_position(
                round(pos_x + random_x()*5),
                0,
                round(pos_z + random_x()*5))
            self.unit_list.append(self.city_unit)

    def load_res(self, path, x, z, s):
        item = FNode3D.instantiate(path)
        self.item_nodes.append(item)

        item.set_position(x, 0, z)
        item.set_scale(s, s, s)

    def unload(self):
        pass

    def update_hud(self):
        for unit in self.unit_list:
            game_mgr.hud_mgr.update_hud(unit)

    def add_unit(self, unit):
        self.unit_list.append(unit)

    def remove_unit(self, unit):
        self.unit_list.remove(unit)

# 地面，管理
class GroundMgr(NodeObject):
    def __init__(self):
        super().__init__()
        game_mgr.ground_mgr = self

        # 地块
        self.tile_dict = {}

        # 可见的地块, 用来卸载不可见的地块, 或者还要加一个age
        self.show_tile_list = []

    def _create(self):
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        log_util.debug('GroundMgr ready')

    # create new tile , if not exists
    def get_tile(self, x, z):
        col,row = pos_to_colrow(x, z)
        #return self.get_tile_colrow(col, row)
        tile, _ = self.create_tile(col, row)
        return tile

    # tile: col,row => x,y
    # return NONE if not exists
    def get_tile_colrow(self, col, row):
        return self.tile_dict.get((col,row), None)

    def update(self, delta_time):
        x,z = game_mgr.camera_mgr.get_focus_xz()

        cx = math.floor((x / TILE_SIZE) + 0.5)
        cz = math.floor((z / TILE_SIZE) + 0.5)

        # 中心九宫格
        self.update_tile(cx    , cz    )
        self.update_tile(cx - 1, cz    )
        self.update_tile(cx + 1, cz    )

        self.update_tile(cx    , cz - 1)
        self.update_tile(cx - 1, cz - 1)
        self.update_tile(cx + 1, cz - 1)

        self.update_tile(cx    , cz + 1)
        self.update_tile(cx - 1, cz + 1)
        self.update_tile(cx + 1, cz + 1)

        # 左右远角，视觉上面有坑
        self.update_tile(cx    , cz - 2)
        self.update_tile(cx + 1, cz - 2)

        self.update_tile(cx - 2, cz    )
        self.update_tile(cx - 2, cz + 1)

        self.show_tile_list.clear()

        # refresh done, clear no hit hud
        game_mgr.hud_mgr.update_hud_items()

    def create_tile(self,col,row):
        key = (col, row)
        tile = self.get_tile_colrow(col, row)
        if tile:
            return tile, False

        tile = Tile(col, row)
        self.tile_dict[key] = tile

        return tile, True

    # 只有在刷可见性调用,来自update
    def update_tile(self, col, row):
        tile, first_hit = self.create_tile(col, row)
        if first_hit or not tile.model_node:
            tile.load()
            if tile.color == 255:
                tile.load_items()

        tile.update_hud()
        self.show_tile_list.append(tile)

    # 从数据中加载
    def load_data(self):
        w,h = 30,30
        cx,cy = w//2,h//2

        log_util.enable_debug = False
        bmp = Bmp(r'game\data\world_map.bmp')
        for y in range(h):
            for x in range(w):
                b,g,r = bmp.get_color(x,y)
                col = x - cx
                row = y - cy

                tile, _ = self.create_tile(col, row)
                tile.color = r
                tile.create_city()
        log_util.enable_debug = True

        self.terrain_map = Bmp(r'game\data\world_terrain.bmp')


