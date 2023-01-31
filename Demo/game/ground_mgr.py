#
# 2023年1月31日 bianpeng
#
import math

from game.core import *
from game.game_mgr import game_mgr

TILE_SIZE = 15

class Tile:
    def __init__(self, x, z):
        self.x = x*TILE_SIZE
        self.z = z*TILE_SIZE

    def load(self):
        print_line(f'load tile: {self.x},{self.z}')
        pass

# 地面
class GroundMgr(NodeObject):
    def __init__(self):
        super().__init__()

        self.tile_map = {}

        game_mgr.ground_mgr = self
    
    def _create(self):
        #set_process(self._get_node(), process=False, input=False)
        connect(self._get_node(), "ready", self._ready)
        
        print_line('create GroundMgr ok')

    def _ready(self):
        print_line('GroundMgr ready')

    def update(self):
        #delta_time = get_delta_time()

        center = game_mgr.camera_mgr.center
        x = center.x
        z = center.z

        cx = math.floor((x / TILE_SIZE) + 0.5)
        cz = math.floor((z / TILE_SIZE) + 0.5)

        self.update_tile(cx, cz)
        self.update_tile(cx - 1, cz)
        self.update_tile(cx + 1, cz)

        self.update_tile(cx, cz - 1)
        self.update_tile(cx - 1, cz - 1)
        self.update_tile(cx + 1, cz - 1)

        self.update_tile(cx, cz + 1)
        self.update_tile(cx - 1, cz + 1)
        self.update_tile(cx + 1, cz + 1)

    def update_tile(self, cx, cz):
        key = (cx, cz)
        if key not in self.tile_map:
            t = Tile(*key)
            self.tile_map[key] = t
            t.load()
                
        



