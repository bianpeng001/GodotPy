#
# 2023年2月1日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import *
from game.troop_ai import *

#
# 视觉感知
#
class AISightComponent(Component):
    def __init__(self):
        self.tick_time = 0
        
        self.angle = 0
        self.angle_speed = 0.3
        
        # 视野距离
        self.radius = 10
        self.lose_radius = 15
        
        # 视野中的单位
        self.unit_dict = {}
        
        self.controller = None
        
    def get_controller(self):
        return self.controller
        
    def update(self):
        # 移动过程里, 还要检查周围的敌军, 有一个视野
        self.angle += self.angle_speed
        self.get_controller().viewarea_obj.set_rotation(0, self.angle, 0)
        if self.angle >= 30 or self.angle <= -30:
            self.angle_speed *= -1

        # sight
        self.tick_time += game_mgr.delta_time
        if self.tick_time > 0.1:
            self.tick_time = 0
            self.check_see_unit()
            
    def check_see_unit(self):
        src_unit = self.get_controller().get_unit()
        x,z = src_unit.get_xz()
        sqr_radius = self.radius**2
        
        if self.get_controller().owner_tile:
            #log_debug('check_see_unit', src_unit.unit_name, len(controller.owner_tile.unit_list))
            for unit in self.get_controller().owner_tile.unit_list:
                if unit.unit_id != src_unit.unit_id and \
                        unit.unit_id not in self.unit_dict:
                    x1,z1 = unit.get_xz()
                    dx,dz = x1-x,z1-z
                    sqrdis = dx*dx+dz*dz
                    if sqrdis <= sqr_radius:
                        self.unit_dict[unit.unit_id] = unit
                        log_debug('in sight', src_unit.unit_name, unit.unit_name)

        if len(self.unit_dict) > 0:
            lose_list = game_mgr.get_reuse_list()
            sqr_lose_radius = self.lose_radius**2
            
            for unit in self.unit_dict.values():
                x1,z1 = unit.get_xz()
                dx,dz = x1-x,z1-z
                sqrdis = dx*dx+dz*dz
                if sqrdis > sqr_lose_radius:
                    lose_list.append(unit.unit_id)
                    log_debug('lose sight', src_unit.unit_name, unit.unit_name)
            
            for unit_id in lose_list:
                self.unit_dict.pop(unit_id)

#
# 管理战斗
#
class TroopFightComponent(Component):
    def __init__(self):
        self.skill_cooldown = 1.0
        
    def update(self):
        if self.skill_cooldown > 0:
            self.skill_cooldown -= game_mgr.delta_time
        
    def is_skill_ready(self):
        return self.skill_cooldown <= 0

#
# 部队的思考组件
#
class TroopBrainComponent(Component):
    def __init__(self):
        pass
    
    def update(self):
        pass
    
    def goto_state(self, name):
        pass
    

#
# 这是一个AIController
# 部队控制，包括特效，动作，位置，朝向...
#
class TroopController(Controller):
    def __init__(self):
        super().__init__()

        # AI 相关
        self.init_ai()
        # 位移请求
        self.move_comp = None
        # 战斗相关
        self.fight_comp = TroopFightComponent()
        self.fight_comp.controller = self
        # 视觉感知
        self.sight_comp = AISightComponent()
        self.sight_comp.controller = self
        # brain
        self.brain_comp = TroopBrainComponent()
        self.brain_comp.controller = self
        
        # 所在的地块
        self.owner_tile = None
        
        # rvo 相关, 计算好的加速度
        self.rvo_acce_x = 0
        self.rvo_acce_y = 0

    def init_ai(self):
        self.ai_tick_time = 0
        self.blackboard = TroopBlackboard()
        
        self.add_state('start', AIState_TroopStart())
        self.add_state('idle', AIState_Idle())
        self.add_state('shoot', AIState_Shoot())
        self.add_state('move_to_pos', AIState_MoveToPos())
        
        self.goto_state('idle')
        
    def on_ai_tick(self, tick_time):
        #unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        #print_line(unit.unit_name)
        self.ai_state.update(self)

    def update_ai(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.1:
            self.ai_tick_time = 0
            self.on_ai_tick(self.ai_tick_time)

    def update_move(self):
        self.add_rvo_force()
        
        req = self.move_comp
        if req and not req.is_done():
            troop = self.get_unit()
            # 位置朝向
            req.update(troop, game_mgr.delta_time)

            # 位置变更之后,刷新tile归属
            x,z = troop.get_xz()
            tile = game_mgr.ground_mgr.get_tile(x, z)
            if self.owner_tile != tile:
                if self.owner_tile:
                    self.owner_tile.remove_unit(troop)
                    self.owner_tile = None

                self.owner_tile = tile
                self.owner_tile.add_unit(troop)

    def start(self):
        self.get_unit().load_model()
        node = self.get_model_node()
        if node:
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
                    for i in range(4*4):
                        row = i // 4 - 1.5
                        col = i % 4 - 1.5
                        obj = temp if i == 0 else temp.dup()
                        obj.set_position(col*0.7, 0, row*0.7)

    def update(self):
        self.update_move()
        self.update_ai()
        self.sight_comp.update()
        self.fight_comp.update()
        
    # 对视野里面的单位, 加一个力, 改善重叠和穿插
    def add_rvo_force(self):
        self.rvo_acce_x = self.rvo_acce_y = 0
        
        if len(self.sight_comp.unit_dict) > 0:
            rvo_sqrdis = game_mgr.config_mgr.rvo_sqrdis
            rvo_factor = game_mgr.config_mgr.rvo_factor
            src_unit = self.get_unit()
            x,z = src_unit.get_xz()
            
            for unit in self.sight_comp.unit_dict.values():
                if unit.unit_type == UT_TROOP:
                    x1,z1 = unit.get_xz()
                    dx,dz = x-x1,z-z1
                    sqrdis = dx*dx+dz*dz
                    if sqrdis < 0.0001:
                        sqrdis = 0.0001
                        dx = random_num(0.001, 0.009)
                        dz = random_num(0.001, 0.009)
                    if sqrdis < rvo_sqrdis:
                        f = rvo_factor*unit.mass*(1.0/sqrdis - 1.0/rvo_sqrdis)
                        self.rvo_acce_x += dx*f
                        self.rvo_acce_y += dz*f

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
        self.get_unit().set_dead()
        
        
    def get_fight_comp(self):
        return self.fight_comp

    def get_brain_comp(self):
        return self.brain_comp
    
    

