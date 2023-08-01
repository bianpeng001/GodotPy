#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import *
from game.troop_ai import *

#
# 视觉感知
#
class TroopSightComponent(Component):
    # 公用的list, 减少分配. 因为每帧每个单位都要用到
    _lose_list = []
    _enter_list = []
    _leave_list = []

    def __init__(self):
        super().__init__()
        
        # 视觉扇形片的角速度
        self.angle = 0
        self.angle_speed = 0.3
        
        # 视野距离
        #self.radius = 4
        #self.lose_radius = 6
        
        # 视野中的单位
        self._unit_dict = {}
        
    def loop_units(self):
        return iter(self._unit_dict.values())

    # 转动视野
    # 移动过程里, 还要检查周围的敌军, 有一个视野
    def update_viewarea(self, delta_time):
        self.angle += self.angle_speed
        self.get_controller().viewarea_obj.set_rotation(0, self.angle, 0)
        if abs(self.angle) > 30:
            self.angle_speed *= -1
        
    def update(self, delta_time):
        self.check_see_unit()

    def check_see_unit(self):
        self_unit = self.get_controller().get_unit()
        x,z = self_unit.get_xz()
        #sqr_radius = self.radius**2
        sqr_radius = game_mgr.config_mgr.sight_sqrdis
        
        def check_tile_unit(col,row):
            tile = game_mgr.ground_mgr.get_tile_colrow(col,row)
            if tile:
                #log_debug('check owner tile', self_unit.unit_name, len(tile.get_unit_list()))
                for unit in tile.get_unit_list():
                    if unit.unit_id != self_unit.unit_id and \
                            unit.unit_id not in self._unit_dict and \
                            self_unit.get_xz_sqrdis_to(unit) < sqr_radius:
                        self._unit_dict[unit.unit_id] = unit
                        #log_debug('see unit', self_unit.unit_name, '->', unit.unit_name)

                if tile.city_unit:
                    if tile.city_unit.unit_id not in self._unit_dict:
                        self._unit_dict[tile.city_unit.unit_id] = tile.city_unit

        # 要扫描周围几个tile
        owner_tile = self.get_controller().owner_tile
        if owner_tile:
            col, row = owner_tile.col, owner_tile.row
            # 这里根据位置, 少找一些相邻块, 点击的那边也是
            loc_x, loc_z = owner_tile.get_local_pos(x,z)
            
            check_tile_unit(col,row)
            
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

        if len(self._unit_dict) > 0:
            lose_list = TroopSightComponent._lose_list
            lose_list.clear()

            #sqr_lose_radius = self.lose_radius**2
            lose_sight_sqrdis = game_mgr.config_mgr.lose_sight_sqrdis
            
            for unit in self.loop_units():
                if self_unit.get_xz_sqrdis_to(unit) > lose_sight_sqrdis:
                    lose_list.append(unit)
            
            if lose_list:
                for unit in lose_list:
                    self._unit_dict.pop(unit.unit_id)
                lose_list.clear()

#
# 管理战斗
#
class TroopFightComponent(Component):
    def __init__(self):
        super().__init__()
        self.skill_cooldown = 1.0
        
    def update(self, delta_time):
        if self.skill_cooldown > 0:
            self.skill_cooldown -= delta_time
        
    def is_skill_ready(self):
        return self.skill_cooldown <= 0

#
# 这是一个AIController
# 部队控制，包括特效，动作，位置，朝向...
#
class TroopController(Controller):
    def __init__(self, unit):
        super().__init__(unit)

        # 位移请求
        self.move_comp = None
        # 战斗相关
        self.fight_comp = TroopFightComponent()
        self.fight_comp.setup(self)
        # 视觉感知
        self.sight_comp = TroopSightComponent()
        self.sight_comp.setup(self)
        # AI 相关
        self.brain_comp = BrainComponent()
        self.brain_comp.setup(self)
        self.init_ai()

        self.brain_tick_time = 0
        
        # 所在的地块
        self.owner_tile = None
        
        # rvo 相关, 计算好的加速度
        self.rvo_acce_x = 0
        self.rvo_acce_z = 0

    def init_ai(self):
        brain_comp = self.get_brain_comp()
        brain_comp.blackboard = TroopBlackboard()
        
        brain_comp.add_state('start', AIState_TroopStart())
        brain_comp.add_state('idle', AIState_Idle())
        brain_comp.add_state('shoot', AIState_Shoot())
        brain_comp.add_state('move_to_pos', AIState_MoveToPos())
        
        brain_comp.goto_state('idle')

    def update_move(self, delta_time):
        self.add_rvo_force()
        
        move_comp = self.move_comp
        if move_comp and not move_comp.is_done():
            # 位置朝向
            move_comp.update(delta_time)

            # 位置变更之后,刷新tile归属
            troop = self.get_unit()
            x,z = troop.get_xz()
            tile = game_mgr.ground_mgr.get_tile(x, z)
            if self.owner_tile != tile:
                if self.owner_tile:
                    self.owner_tile.remove_unit(troop)
                    self.owner_tile = None

                self.owner_tile = tile
                self.owner_tile.add_unit(troop)

    # 刷新旗帜颜色, 可能被调用多次
    def set_flag_color(self):
        if not self.get_model_node():
            return

        flag_obj = self.get_model_node().find_node('Flag')
        if not flag_obj:
            return

        player_id = self.get_unit().owner_player_id
        if player_id > 0:
            player = get_player(player_id)

            path = 'res://models/Color/FlagTroopMat.tres'
            if not player.troop_flag_mat:
                mat = ResCapsule.load_resource(path)
                player.troop_flag_mat = mat.duplicate()
                r,g,b = player.flag_color
                player.troop_flag_mat.set_shader_color('_color',r,g,b,1)
            flag_obj.set_surface_material(1, player.troop_flag_mat.res)

    def start(self):
        self.get_unit().load_model()
        node = self.get_model_node()
        if node:
            # 设置旗帜颜色
            self.set_flag_color()

            # 视野显示
            self.viewarea_obj = node.find_node('ViewArea')

            # 初始化士兵的数量
            if self.get_unit().model_type == 2:
                anim_name = "SoldierAnimLib/Run"
                for i in range(2, 11):
                    node_path = f"Soldier{i:02}/Model/AnimationPlayer"

                    anim_player = node.find_node(node_path)
                    if anim_player:
                        anim_player.play(anim_name)
                        anim_player.set_speed_scale(2.6)

            elif self.get_unit().model_type == 4:
                temp = node.find_node('Soldier5')
                
                if 0:
                    i = 0
                    for hero_item in self.get_unit().hero_list:
                        obj = temp if i == 0 else temp.dup()
                        i += 1
                        row = hero_item.pos_index // 3 - 1
                        col = hero_item.pos_index % 3 - 1
                        obj.set_position(col*0.8, 0, row*0.8)
                else:
                    # 4x4的方阵, 少于这个, 看起来会有点稀疏
                    for i in range(4*4):
                        row, col = divmod(i, 4)
                        row, col = row-1.5, col-1.5
                        obj = temp if i == 0 else temp.dup()
                        obj.set_position(col*0.7, 0, row*0.7)

    def update(self):
        delta_time = game_mgr.delta_time
        
        self.update_move(delta_time)
        self.sight_comp.update_viewarea(delta_time)

        self.brain_tick_time += delta_time
        if self.brain_tick_time > BRAIN_TICK_TIME:
            self.sight_comp.update(self.brain_tick_time)
            self.fight_comp.update(self.brain_tick_time)
            self.brain_comp.update(self.brain_tick_time)
            self.brain_tick_time = 0
        
    # 对视野里面的单位, 加一个力, 改善重叠和穿插
    def add_rvo_force(self):
        self.rvo_acce_x = self.rvo_acce_z = 0
        
        if len(self.sight_comp._unit_dict) > 0:
            rvo_sqrdis = game_mgr.config_mgr.rvo_sqrdis
            rvo_factor = game_mgr.config_mgr.rvo_factor
            
            self_unit = self.get_unit()
            x,z = self_unit.get_xz()
            
            for unit in self.sight_comp.loop_units():
                # if unit.unit_type == UT_TROOP and \
                #         unit.owner_player_id != self_unit.owner_player_id:
                if unit.unit_type == UT_CITY:
                    if unit.owner_player_id == self_unit.owner_player_id:
                        continue

                x1,z1 = unit.get_xz()
                dx,dz = x-x1,z-z1
                sqrdis = dx*dx+dz*dz
                if sqrdis < 0.001:
                    sqrdis = 0.001
                    dx = random_num(0.001, 0.002)
                    dz = random_num(0.001, 0.002)

                if sqrdis < rvo_sqrdis:
                    f = unit.mass*(1.0/sqrdis - 1.0/rvo_sqrdis)
                    self.rvo_acce_x += dx*f
                    self.rvo_acce_z += dz*f
            
            self.rvo_acce_x *= rvo_factor/self_unit.mass
            self.rvo_acce_z *= rvo_factor/self_unit.mass
            #log_debug('rvo force', self_unit.unit_name, self.rvo_acce_x, self.rvo_acce_z)

    def look_at(self,x,y,z):
        node = self.get_model_node()
        if node:
            node.look_at(x,y,z)

    def look_at_unit(self, unit):
        x,y,z = unit.get_position()
        self.look_at(x,y,z)
    
    def get_forward(self):
        node = self.get_model_node()
        return node.get_forward()
    
    def kill(self):
        if self.owner_tile:
            self.owner_tile.remove_unit(self.get_unit())
        self.get_unit().set_death()
        
    def get_sight_comp(self):
        return self.sight_comp
        
    def get_fight_comp(self):
        return self.fight_comp

    def get_brain_comp(self):
        return self.brain_comp
    
    def get_move_comp(self):
        return self.move_comp
    
    

