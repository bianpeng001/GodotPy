#
# 2023年1月31日 bianpeng
#
import math
import random

from game.core import *
from game.game_mgr import game_mgr

TILE_SIZE = 30

#
class Tile:
    def __init__(self, x, z):
        # 坐标
        self.x = x
        self.z = z
        self.model_node = None
        self.item_nodes = []

    def load(self):
        print_line(f'load tile: x={self.x} z={self.z}')
        
        pos_x = self.x*TILE_SIZE
        pos_z = self.z*TILE_SIZE

        self.model_node = instantiate('res://models/Square.tscn')
        set_position(self.model_node, pos_x, 0, pos_z)

        # 随机几颗树

        for i in range(random.randrange(1, 10)):
            self.load_res('res://models/Tree01.tscn',
                pos_x + (random.random()-0.5)*20,
                pos_z + (random.random()-0.5)*20,
                0.6 + random.random())

        self.load_res('res://models/Grass01.tscn', 
            pos_x + (random.random()-0.5)*20,
            pos_z + (random.random()-0.5)*20,
            0.8 + random.random())

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

        self.tile_dict = {}

        game_mgr.ground_mgr = self
    
    def _create(self):
        #set_process(self._get_node(), process=False, input=False)
        connect(self._get_node(), "ready", self._ready)

    def _ready(self):
        print_line('GroundMgr ready')

    def update(self):
        #delta_time = get_delta_time()

        center = game_mgr.camera_mgr.center
        x = center.x
        z = center.z

        cx = math.floor((x / TILE_SIZE) + 0.5)
        cz = math.floor((z / TILE_SIZE) + 0.5)

        self.update_tile(cx    , cz    )
        self.update_tile(cx - 1, cz    )
        self.update_tile(cx + 1, cz    )

        self.update_tile(cx    , cz - 1)
        self.update_tile(cx - 1, cz - 1)
        self.update_tile(cx + 1, cz - 1)
        
        self.update_tile(cx    , cz + 1)
        self.update_tile(cx - 1, cz + 1)
        self.update_tile(cx + 1, cz + 1)

        # 补两个远角
        self.update_tile(cx    , cz - 2)
        self.update_tile(cx + 1, cz - 2)

        self.update_tile(cx - 2, cz    )
        self.update_tile(cx - 2, cz + 1)

    def update_tile(self, cx, cz):
        key = (cx, cz)
        if key not in self.tile_dict:
            t = Tile(*key)
            self.tile_dict[key] = t
            t.load()
                
        



