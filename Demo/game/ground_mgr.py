#
# 2023年1月31日 bianpeng
#
import math
import random
import struct

from game.core import *
from game.game_mgr import *

TILE_SIZE = 30

# col,row
def pos_to_colrow(x, z):
    return round(x / TILE_SIZE), round(z / TILE_SIZE)

# tile内部，a*寻路
# tile外部，大a*寻路
# 打仗过程里面，走直线, 加一点弧度或者干扰, 别笔直就好了
class Tile:
    def __init__(self, col, row):
        # 区块的ID，坐标/TILE_SIZE, 取证
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

        # 颜色
        self.color = -1

    def get_center_pos(self):
        return self.col*TILE_SIZE,self.row*TILE_SIZE

    def load(self):
        log_util.debug(f'load tile: ({self.col},{self.row})')
        pos_x, pos_z = self.get_center_pos()

        self.model_node = FNode3D.instantiate('res://models/Tile01.tscn')
        self.model_node.set_position(pos_x, 0, pos_z)

        self.test_mesh()

        mi = self.model_node.find_node('Mesh')
        if self.color == 0:
            mi.load_material(0, 'res://models/Terrain/WaterMat.tres')
        else:
            mi.load_material(0, 'res://models/Terrain/GrassMat.tres')

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
        if random.random() < 0.3:
            rad = random_x()*math.pi
            dis = 6 + random.random()*10
            self.load_res('res://models/Pavilion01.tscn',
                pos_x + math.cos(rad)*dis,
                pos_z + math.sin(rad)*dis,
                1.0)

        # 城
        if random.random() < 0.8:
            city = game_mgr.unit_mgr.create_city()
            city.owner_player_id = 0
            city.set_position(
                round(pos_x + random_x()*5),
                0,
                round(pos_z + random_x()*5))
            self.unit_list.append(city)


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

    def get_tile(self, x, z):
        col,row = pos_to_colrow(x, z)
        return self.get_tile_colrow(col, row)

    # tile: col,row => x,y
    def get_tile_colrow(self, col, row):
        key = (col,row)
        return self.tile_dict.get(key, None)

    def update(self, delta_time):
        x, z = game_mgr.camera_mgr.center.get_xz()

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
        data = []
        # with open('world_map.json') as f:
        #     data = json.load(f)
        # 一整块数据, 地图块数据, 不包含说明信息
        w,h = 30,30
        cx, cy = w//2,h//2
        with open('game\\data\\world_map.dat', 'rb') as f:
            buf = f.read()
            for i in range(len(buf) // 3):
                x = i % w
                y = i // h
                r,g,b = struct.unpack('>BBB', buf[i*3:(i+1)*3])
                item = (x-cx,y-cy,r)
                data.append(item)

        for item in data:
            x,y,r = item
            tile, _ = self.create_tile(x, y)
            tile.color = r

