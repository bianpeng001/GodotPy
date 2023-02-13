#
# 2023年1月31日 bianpeng
#
import math
import random

from game.core import *
from game.game_mgr import game_mgr

TILE_SIZE = 30

# tile内部，a*寻路
# tile外部，大a*寻路
# 打仗过程里面，走直线
class Tile:
    def __init__(self, col, row):
        # 区块的ID，坐标/TILE_SIZE, 取证
        self.col = col
        self.row = row
        self.model_node = None
        self.item_nodes = []
        self.units = []

    def get_center_pos(self):
        return self.col*TILE_SIZE,self.row*TILE_SIZE

    def load(self):
        logutil.debug(f'load tile: ({self.col},{self.row})')
        
        #pos_x = self.col*TILE_SIZE
        #pos_z = self.row*TILE_SIZE
        pos_x, pos_z = self.get_center_pos()

        self.model_node = instantiate('res://models/Square.tscn')
        set_position(self.model_node, pos_x, 0, pos_z)

        # 树
        for i in range(random.randrange(1, 10)):
            self.load_res('res://models/Tree01.tscn',
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
        if random.random() < 0.5:
            rad = random_x()*math.pi
            dis = 3 + random.random()*10
            self.load_res('res://models/Pavilion01.tscn',
                pos_x + math.cos(rad)*dis,
                pos_z + math.sin(rad)*dis,
                1.0)

        # 城
        if random.random() < 0.3:
            city = game_mgr.unit_mgr.create_city()
            city.owner_player_id = 0
            city.set_location(pos_x + random_x()*5,
                0,
                pos_z + random_x()*5)
            self.units.append(city)

        

    def load_res(self, path, x, z, s):
        item = instantiate(path)
        self.item_nodes.append(item)

        set_position(item, x, 0, z)
        set_scale(item, s, s, s)

    def unload(self):
        pass

# 地面
class GroundMgr(NodeObject):
    def __init__(self):
        super().__init__()
        game_mgr.ground_mgr = self

        self.tile_dict = {}
    
    def _create(self):
        #set_process(self._get_node(), process=False, input=False)
        connect(self.get_node(), "ready", self._ready)

    def _ready(self):
        logutil.debug('GroundMgr ready')

    def get_tile(self, x, z):
        #col = math.floor((x / TILE_SIZE) + 0.5)
        #row = math.floor((z / TILE_SIZE) + 0.5)
        col,row = self.get_colrow(x, z)
        return self.tile_dict.get((col, row), None)

    def get_colrow(self, x, z):
        #col = math.floor((x / TILE_SIZE) + 0.5)
        #row = math.floor((z / TILE_SIZE) + 0.5)
        col, row = int(round(x / TILE_SIZE)), int(round(z / TILE_SIZE))
        return col, row

    def get_tile_at_colrow(self, col, row):
        return self.tile_dict.get((col, row), None)

    def update(self, delta_time):
        center = game_mgr.camera_mgr.center
        x = center.x
        z = center.z

        cx = math.floor((x / TILE_SIZE) + 0.5)
        cz = math.floor((z / TILE_SIZE) + 0.5)

        # 中心九宫格
        self.refresh_tile(cx    , cz    )
        self.refresh_tile(cx - 1, cz    )
        self.refresh_tile(cx + 1, cz    )

        self.refresh_tile(cx    , cz - 1)
        self.refresh_tile(cx - 1, cz - 1)
        self.refresh_tile(cx + 1, cz - 1)
        
        self.refresh_tile(cx    , cz + 1)
        self.refresh_tile(cx - 1, cz + 1)
        self.refresh_tile(cx + 1, cz + 1)

        # 左右远角，视觉上面有坑
        self.refresh_tile(cx    , cz - 2)
        self.refresh_tile(cx + 1, cz - 2)

        self.refresh_tile(cx - 2, cz    )
        self.refresh_tile(cx - 2, cz + 1)

    def refresh_tile(self, col, row):
        key = (col, row)
        if key not in self.tile_dict:
            t = Tile(col, row)
            self.tile_dict[key] = t
            t.load()
                
        



