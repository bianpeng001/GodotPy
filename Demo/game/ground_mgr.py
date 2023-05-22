#
# 2023年1月31日 bianpeng
#
import math
import random
import struct

from game.core import *
from game.game_mgr import *
from game.base_type import *
from game.load_world_map import Bmp

SQRT_3 = math.sqrt(3)

TILE_SIZE = 30
Z_TILE_SIZE = TILE_SIZE*SQRT_3/2
Z_RATIO = Z_TILE_SIZE/TILE_SIZE

# col,row
def xz_to_colrow(x, z):
    return round(x / TILE_SIZE), round(z / Z_TILE_SIZE)

#
# tile内部，a*寻路
# tile外部，大a*寻路
# 打仗过程里面，走直线, 加一点弧度或者干扰, 别笔直就好了
#
class TileItem:
    def __init__(self, col, row):
        # 区块的ID，坐标/TILE_SIZE, 取整
        self.col = col
        self.row = row
        # 自己的地块模型
        self.model_node = None
        # 附属模型
        self.item_nodes = []
        # 上面的单位列表
        self._unit_list = []

        # 用来控制可见列表
        self.show_age = 1

        self.city_unit = None
        self.corner_flag = None
        
        # 颜色
        self.color = -1

    def get_center_pos(self):
        return self.col*TILE_SIZE,self.row*Z_TILE_SIZE

    def get_local_pos(self, x,z):
        cx,cz = self.get_center_pos()
        return (x-cx)/TILE_SIZE,(z-cz)/TILE_SIZE

    def load(self):
        #log_debug(f'load tile: ({self.col},{self.row})')
        pos_x, pos_z = self.get_center_pos()

        self.model_node = OS.instantiate('res://models/Terrain/Tile03.tscn')
        self.model_node.set_position(pos_x, 0, pos_z)

        mi = self.model_node.find_node('Mesh')
        self.generate_mesh3(mi)

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
        
    def generate_mesh3(self, mi):
        s = TILE_SIZE
        #s += -0.4
        mi.set_scale(s,s,s)
        
        st = FSurfaceTool()
        st.set_uv(0.11,0.11)
        st.set_normal(0, 1, 0)
        
        x_step = 1.0/10
        half_x_step = x_step*0.5
        z_step = half_x_step*SQRT_3
        radius = x_step/SQRT_3
        
        width = 900
        height = 900*Z_RATIO
        
        left = -0.5
        bottom = -0.5*SQRT_3/2
        
        def loop_cells():
            i = 0
            while i < 100:
                z,x = divmod(i, 10)
                yield x,z
                i += 1
                
        pos_x, pos_z = self.get_center_pos()
        def add_vertex(x,y,z):
            st.set_uv((pos_x+x*s)/width+0.5, (pos_z+z*s)/height+0.5)
            st.add_vertex(x, y, z)
        
        vertex_index = 0
        for x,z in loop_cells():
            cx, cz = left+x*x_step, bottom+z*z_step
            if z % 2 != 0:
                cx += half_x_step
                
            add_vertex(cx, 0, cz-radius)
            add_vertex(cx-half_x_step, 0, cz-radius*0.5)
            add_vertex(cx-half_x_step, 0, cz+radius*0.5)
            add_vertex(cx, 0, cz+radius)
            add_vertex(cx+half_x_step, 0, cz+radius*0.5)
            add_vertex(cx+half_x_step, 0, cz-radius*0.5)
            
            st.add_triangle(vertex_index, vertex_index+2, vertex_index+1)
            st.add_triangle(vertex_index, vertex_index+3, vertex_index+2)
            st.add_triangle(vertex_index, vertex_index+4, vertex_index+3)
            st.add_triangle(vertex_index, vertex_index+5, vertex_index+4)
            vertex_index += 6
        
        st.commit(mi)

    def generate_mesh(self, mi):
        
        def get_color(px, py):
            if px >= 0 and px < 300 and \
                    py >= 0 and py < 300:
                b,g,r = bmp.get_color(px, py)
                return r,g,b
            else:
                return 0,0,0
            
        bmp = game_mgr.ground_mgr.terrain_map
        
        st = FSurfaceTool()
        st.set_uv(0.11,0.11)
        st.set_normal(0, 1, 0)
        
        step = 0.2
        half_x_step = step*0.5
        radius = half_x_step*2/math.sqrt(3)
        z_step = 1.5*radius
        
        def grid_xz():
            i = 0
            while i < 100:
                yield i % 10, i // 10
                i += 1
        
        # uv跟每一个六边形的坐标有关, 这样以后就可以用更加精细的地图了
        # has bug...
        def add_vertex_2(x,y,z):
            st.set_uv((px+x*0.5)/(300),(pz*Z_RATIO+z*0.5)/(300*Z_RATIO))
            st.add_vertex(x,y,z)
        
        # uv的获取的方式, 我希望是适配像素地图, 以中心点的uv
        # 真实地图, 各个顶点的真实uv
        uv_type = 1

        vertex_index = 0
        for x,z in grid_xz():
            cz = -1 + z*z_step
            cx = -1 + x*step
            if z % 2 != 0:
                cx += half_x_step
            
            if uv_type == 1:
                # 六边形的中心点对应的位置, 要取像素颜色
                px,pz = x+(self.col+15)*10-5, z+(self.row+15)*10-5
                # 这是用300x300位图, 点采样方式生成世界地图
                st.set_uv(px/300, pz/300)
                
                st.add_vertex(cx, 0, cz-radius)
                st.add_vertex(cx-half_x_step, 0, cz-radius*0.5)
                st.add_vertex(cx-half_x_step, 0, cz+radius*0.5)
                st.add_vertex(cx, 0, cz+radius)
                st.add_vertex(cx+half_x_step, 0, cz+radius*0.5)
                st.add_vertex(cx+half_x_step, 0, cz-radius*0.5)
                
            if uv_type == 2:
                px,pz = x+(self.col+15)*10-5, z+(self.row+15)*10-5
                add_vertex_2(cx, 0, cz-radius)
                add_vertex_2(cx-half_x_step, 0, cz-radius*0.5)
                add_vertex_2(cx-half_x_step, 0, cz+radius*0.5)
                add_vertex_2(cx, 0, cz+radius)
                add_vertex_2(cx+half_x_step, 0, cz+radius*0.5)
                add_vertex_2(cx+half_x_step, 0, cz-radius*0.5)
            
            st.add_triangle(vertex_index, vertex_index+2, vertex_index+1)
            st.add_triangle(vertex_index, vertex_index+3, vertex_index+2)
            st.add_triangle(vertex_index, vertex_index+4, vertex_index+3)
            st.add_triangle(vertex_index, vertex_index+5, vertex_index+4)
            vertex_index += 6
            
        st.commit(mi)
    
    # 生成地形融合, 最好是用贴图来融合
    # 这个版本还是丑, 接下来, 还是老老实实, 用贴图融合吧
    def generate_mesh2(self, mi):
        
        def get_color(col,row):
            if col >= 0 and col < 300 and row >= 0 and row < 300:
                b,g,r = bmp.get_color(col, row)
                
                r = 0 if r < 100 else 255
                return r,g,b
            else:
                return 0,0,0
            
        def fix_color(r, r1,r2,r3,r4):
            s = 0
            pat = 0
            
            if r == 255:
                pat += 1
                
            if r1 == 255:
                s += 1
                pat += (1 << 1)
            if r2 == 255:
                s += 1
                pat += (1 << 2)
            if r3 == 255:
                s += 1
                pat += (1 << 3)
            if r4 == 255:
                s += 1
                pat += (1 << 4)
                
            if s == 0 or s == 1:
                r = 0
                pat = pat & 0b11110
            elif s == 3 or s == 4:
                r = 255
                pat = pat | 0b00001
            
            return r, pat
            
        def get_uv(r):
            if r > 200:
                return 0.11,0.11
            else:
                return 0.36, 0.86
            
        bmp = game_mgr.ground_mgr.terrain_map
        STEP = 0.2
        vertex_index = 0
        
        uv_dict = {
            0b00111: (0.5,0.0,0.0,0.5),
            0b01101: (0.0,0.0,0.5,0.5),
            0b11001: (0.0,0.5,0.5,0.0),
            0b10011: (0.5,0.5,0.0,0.0),
        }
        
        st = FSurfaceTool()
        st.set_color(0.11,0.11,0.36,0.86)
        st.set_normal(0, 1, 0)
        
        for i in range(100):
            x = i % 10
            y = i // 10
            
            col,row = x+(self.col+15)*10, y+(self.row+15)*10
            r,_,_ = get_color(col, row)
            
            #   2
            #  301
            #   4
            r1,_,_ = get_color(col+1, row)
            r2,_,_ = get_color(col, row-1)
            r3,_,_ = get_color(col-1, row)
            r4,_,_ = get_color(col, row+1)
            
            r, pat = fix_color(r,r1,r2,r3,r4)
            
            if pat in uv_dict:
                u1,v1,u2,v2 = uv_dict[pat]
            elif pat & 0b00001 == 0:
                u1,v1,u2,v2 = 0.51,0.51,0.99,0.99
            else:
                u1,v1,u2,v2 = 0.01, 0.51, 0.49, 0.99
            
            st.set_uv(u1,v2)
            st.add_vertex(-1+x*STEP, 0, -1+y*STEP)
            st.set_uv(u2,v2)
            st.add_vertex(-1+(x+1)*STEP, 0, -1+y*STEP)
            st.set_uv(u2,v1)
            st.add_vertex(-1+(x+1)*STEP, 0, -1+(y-1)*STEP)
            st.set_uv(u1,v1)
            st.add_vertex(-1+x*STEP, 0, -1+(y-1)*STEP)
            
            st.add_triangle(vertex_index, vertex_index+2, vertex_index+1)
            st.add_triangle(vertex_index, vertex_index+3, vertex_index+2)
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
                st.set_uv(0.07, 0.18)
                
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
            if random.random() < 0.2:
                path = 'res://models/Tree02.tscn'
            elif random.random() < 0.4:
                path = 'res://models/Tree03.tscn'
            else:
                path = 'res://models/Tree01.tscn'

            rad = random_x()*math.pi
            dis = 6 + random.random()*10
            dx = math.cos(rad)*dis
            dz = math.sin(rad)*dis
            
            self.load_res(path,
                pos_x + dx,
                pos_z + dz,
                0.3 + random.random()*0.7)
        
        # 角旗
        self.corner_flag = self.load_res('res://models/Flag01.tscn',
                pos_x - TILE_SIZE*0.5,
                pos_z - Z_TILE_SIZE*0.5,
                1.0)
        
        # 草
        for i in range(random.randrange(1, 5)):
            rad = random_x()*math.pi
            dis = 6 + random.random()*10
            dx = math.cos(rad)*dis
            dz = math.sin(rad)*dis
            
            self.load_res('res://models/Grass01.tscn',
                pos_x + dx,
                pos_z + dz,
                0.8 + random.random()*0.7)

        # 亭
        if random_100() < 30:
            rad = random_x()*math.pi
            dis = 6 + random.random()*10
            dx = math.cos(rad)*dis
            dz = math.sin(rad)*dis
            
            self.load_res('res://models/Pavilion01.tscn',
                pos_x + dx,
                pos_z + dz,
                1.0)

    def create_city(self):
        if not self.city_unit and \
                self.color == 255 and \
                random_100() < 45:
            pos_x,pos_z = self.get_center_pos()

            self.city_unit = game_mgr.unit_mgr.create_city()
            self.add_unit(self.city_unit)

            self.city_unit.owner_player_id = 0
            self.city_unit.set_position(
                round(pos_x + random_x()*5),
                0,
                round(pos_z + random_x()*5))
            
            # 级别
            v = random_100()
            if v < 50:
                self.city_unit.city_type = CT_XIAN
            elif v < 85:
                self.city_unit.city_type = CT_JUN
            else:
                self.city_unit.city_type = CT_ZHOU
            
            # 生成一段小路
            if random_100() < 10:
                x,z = self.city_unit.get_xz()
                self.create_road(x,0.1,z+self.city_unit.radius)

    def load_res(self, path, x, z, s):
        item = OS.instantiate(path)
        self.item_nodes.append(item)

        item.set_position(x,0,z)
        item.set_scale(s,s,s)
        return item

    def unload(self):
        if self.corner_flag:
            # mesh_node = self.corner_flag.find_node('Mesh')
            # if mesh_node:
            #     mesh_node.set_surface_material(0, None)
            #     mesh_node.set_surface_material(1, None)
            pass
        
        pass

    def update_hud(self):
        for unit in self._unit_list:
            game_mgr.hud_mgr.update_hud(unit)

    def add_unit(self, unit):
        self._unit_list.append(unit)

    def remove_unit(self, unit):
        self._unit_list.remove(unit)
        
    def get_unit_list(self):
        return self._unit_list
        
    def create_road(self, x,y,z):
        pos_x, pos_z = self.get_center_pos()
        road = OS.instantiate('res://models/Road/Road02.tscn')
        road.set_position(x,y,z)
        mi = road.find_node('Mesh')
        st = FSurfaceTool()
        
        st.set_normal(0, 1, 0)
        st.set_uv(0, 10/4)
        st.add_vertex(0, 0, 0)
        st.set_uv(1, 10/4)
        st.add_vertex(1, 0, 0)
        st.set_uv(1, 0)
        st.add_vertex(1, 0, 10)
        st.set_uv(0, 0)
        st.add_vertex(0, 0, 10)
        
        st.add_triangle(0, 1, 2)
        st.add_triangle(0, 2, 3)
        
        st.commit(mi)

# 地面，管理
class GroundMgr(NodeObject):
    def __init__(self):
        super().__init__()
        game_mgr.ground_mgr = self

        # 地块
        self.tile_dict = {}

        # 可见的地块, 用来卸载不可见的地块, 或者还要加一个age
        self.show_tile_list = []
        
        #
        self.load_complete = False

    def _create(self):
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        log_util.debug('GroundMgr ready')

    # create new tile , if not exists
    def get_tile(self, x, z):
        col,row = xz_to_colrow(x, z)
        #return self.get_tile_colrow(col, row)
        tile, _ = self.create_tile(col, row)
        return tile

    # tile: col,row => x,y
    # return NONE if not exists
    def get_tile_colrow(self, col, row):
        return self.tile_dict.get((col,row), None)

    def update(self, delta_time):
        x,z = game_mgr.camera_mgr.get_focus_xz()
        col,row = xz_to_colrow(x, z)
        #cx = math.floor((x / TILE_SIZE) + 0.5)
        #cz = math.floor((z / Z_TILE_SIZE) + 0.5)

        # 中心九宫格
        self.update_tile(col    , row    )
        self.update_tile(col - 1, row    )
        self.update_tile(col + 1, row    )

        self.update_tile(col    , row - 1)
        self.update_tile(col - 1, row - 1)
        self.update_tile(col + 1, row - 1)

        self.update_tile(col    , row + 1)
        self.update_tile(col - 1, row + 1)
        self.update_tile(col + 1, row + 1)

        # 左右远角，视觉上面有坑
        self.update_tile(col    , row - 2)
        self.update_tile(col + 1, row - 2)

        self.update_tile(col - 2, row    )
        self.update_tile(col - 2, row + 1)

        self.show_tile_list.clear()

        # refresh done, clear no hit hud
        game_mgr.hud_mgr.update_hud_items()

    def create_tile(self,col,row):
        tile = self.get_tile_colrow(col, row)
        if tile:
            return tile, False

        tile = TileItem(col, row)
        self.tile_dict[(col, row)] = tile

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
                _,_,r = bmp.get_color(x,y)
                col = x - cx
                row = y - cy

                tile, _ = self.create_tile(col, row)
                tile.color = 255 if r > 190 else 0
                tile.create_city()
        log_util.enable_debug = True

        self.terrain_map = Bmp(r'game\data\world_terrain.bmp')
        self.load_complete = True

    def loop_tiles(self):
        return self.tile_dict.values()

