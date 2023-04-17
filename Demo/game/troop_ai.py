#
# 2023年2月8日 bianpeng
#

import math

from game.core import log_debug
from game.base_type import *
from game.game_mgr import *
from game.ground_mgr import pos_to_colrow

#
# 移动方式
#
class MoveComponent(Component):
    def __init__(self):
        super().__init__()
        
        self._done = False

        self.start = None
        self.stop = None
        self.delta = None

        self.progress = 0
        self.time_to_progress = 1

    def complete(self):
        self._done = True

    def is_done(self):
        return self._done
    
    def restart(self):
        self._done = False

#
# 直线
#
class LineMoveReq(MoveComponent):
    def update(self, troop, delta_time):
        pass

    def setup(self, x0,y0,z0,x1,y1,z1, speed):
        self.start = Vector3(x0,y0,z0)
        self.stop = Vector3(x1,y1,z1)
        self.delta = self.stop - self.start

        mag = self.delta.magnitude()
        mag1 = mag - 6
        self.delta = self.delta * (mag1 / mag)
        self.time_to_progress = speed / mag1
        
#
# 小步前进, 考虑rvo斥力和障碍
#
class StepMoveReq(MoveComponent):
    def __init__(self):
        super().__init__()
    
    # 这段这么恶心, 建议放到c++里面去算
    def update(self, troop, delta_time):
        controller = troop.get_controller()
        blackboard = controller.get_blackboard()
        
        if blackboard.target_unit_id > 0:
            unit = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)
            self.dst_pos = Vector3(*unit.get_position())
        else:
            x,z = blackboard.target_pos
            self.dst_pos = Vector3(x,0,z)
        
        cur_pos = Vector3(*troop.get_position())
        delta = self.dst_pos - cur_pos
        dis = delta.magnitude()
        if dis <= delta_time*troop.speed:
            self.complete()
            return
        
        v = delta * (troop.speed/dis)
        
        # 计算rvo的加速对速度增量, 
        # 这里的*delta_time, 因为比较固定, 感觉可以当做常量合并到rvo_factor
        v.x += controller.rvo_acce_x*delta_time
        v.z += controller.rvo_acce_y*delta_time
        
        d = v * delta_time
        if d.sqr_magnitude() > 0.00001:
            new_pos = cur_pos + d
            controller.look_at(new_pos.x,new_pos.y,new_pos.z)
            troop.set_position(new_pos.x,new_pos.y,new_pos.z)
        else:
            # 卡住不动了
            pass

#
# 模拟弧线
#
class ArcMoveReq(MoveComponent):
    def __init__(self):
        super().__init__()
        
        self.right = None

    def setup(self,troop,x1,y1,z1, speed,radius):
        self.start = Vector3(*troop.get_position())
        self.stop = Vector3(x1,y1,z1)
        self.delta = self.stop - self.start

        mag = self.delta.magnitude()
        if mag <= 0.01:
            self.complete()
            return
        
        # 减掉双方半径
        dis = mag - radius
        if dis <= 0:
            self.complete()
            return

        duration = dis / speed
        self.delta = self.delta * (dis / mag)
        self.time_to_progress = 1.0 / duration
        self.right = self.delta.cross(Vector3.up).normalized() * 0.6

        # 转身
        self.rot_time = 0
        forward = Vector3(*troop.model_node.get_forward())
        self.rot_v0 = forward * self.delta.magnitude() + self.start

    def update(self, troop, delta_time):
        # move
        self.progress += delta_time * self.time_to_progress
        if self.progress < 1.0:
            y = 1 - (2*self.progress - 1)**2

            p = self.start + self.delta * self.progress
            
            # TODO: 横向位移, 但感觉比较生硬, 暂时注掉
            # 地图上相遇的话, 用敌对来进行控制, 发生战斗, 自然就会有错开的位移了
            p += self.right * y
        else:
            p = self.start + self.delta
            self.complete()
        troop.set_position(p.x,p.y,p.z)

        # 缓动改朝向, 默认给1秒
        rot_duration = 1.0
        if self.rot_time < rot_duration:
            self.rot_time += delta_time
            v0 = self.rot_v0
            v1 = self.stop
            v2 = v0 + (v1 - v0) * (self.rot_time / rot_duration)
            troop.get_controller().look_at(v2.x,v2.y,v2.z)
            
            if self.rot_time >= rot_duration:
                troop.get_controller().look_at(v1.x,v1.y,v1.z)

#
# 左右移动
#
class LeftRightMoveReq(MoveComponent):
    def setup(self, x0,y0,z0, x1,y1,z1, speed):
        v0 = Vector3(x0,y0,z0)
        v1 = Vector3(x1,y1,z1)
        delta = v1 - v0

        proj_z = delta.dot(Vector3(0, 0, 1))
        proj_x = delta.dot(Vector3(1, 0, 0))

        if abs(proj_z) > abs(proj_x):
            normal = Vector3(0, 0, -1 if proj_z > 0 else 1)
        else:
            normal = Vector3(-1 if proj_x > 0 else 1, 0, 0)
        
        right = normal.cross(Vector3.up)

        center = v1 + normal * 6
        self.stops = [center + right*2, center - right*2]
        self.stop_index = 0
        self.speed = speed
        self.reset(v0)
        self.target = v1

    def reset(self, v0):
        self.stop_index = (self.stop_index + 1) % 2

        self.start = v0
        self.stop = self.stops[self.stop_index] + \
                Vector3(random_x()*0.5,0,random_x()*0.5)
        self.delta = self.stop - self.start

        duration = self.delta.magnitude() / self.speed
        self.time_to_progress = 1.0 / duration
        self.progress = 0

    def update(self, troop, delta_time):
        self.progress += delta_time * self.time_to_progress
        if self.progress < 1.0:
            p = self.start + self.delta * self.progress
            troop.set_position(p.x,p.y,p.z)
            
            t = self.target
            troop.get_controller().look_at(t.x,t.y,t.z)
        else:
            self.reset(self.stop)

#
# 路径移动
#
class PathMoveReq(MoveComponent):
    def update(self, troop, delta_time):
        pass
    
    def setup(self):
        pass
    

#----------------------------------------------------------------------------
# AI 节点
#----------------------------------------------------------------------------

#
# 黑板，用于读写信息，状态之间传递数据
#
class TroopBlackboard(AIBlackboard):
    def __init__(self):
        super().__init__()
        
        self.state_start_time = 0
        
        self.target_unit_id = 0
        self.target_pos = (0, 0)
        
        self.enemy_unit_id = 0
        self.attack_time = 0

    # 状态持续时间
    def get_state_time(self):
        return game_mgr.sec_time - self.state_start_time

#
# troop的state的基类，在enter里面记录开始时间
#
class AIState_Troop(AIState):
    def enter(self, controller):
        blackboard = controller.get_blackboard()
        blackboard.state_start_time = game_mgr.sec_time
        
        self.do_enter(controller)

    def do_enter(self, controller):
        pass

# 寻找一个目标城池
class AIState_FindCity(AIState_Troop):
    # 从内而外的一圈圈的找目标
    def find_enemy_city(self,controller,col,row):
        owner_player_id = controller.get_unit().owner_player_id
        
        for dx,dy in narudo_range(4):
            tile = game_mgr.ground_mgr.get_tile_colrow(col+dx, row+dy)
            if not tile:
                continue
            for unit in tile.unit_list:
                if unit.unit_type == UT_CITY and \
                        (unit.owner_player_id == 0 or \
                        unit.owner_player_id != owner_player_id):
                    return unit
        return None

    def update(self, controller):
        x,y,z = controller.get_unit().get_position()
        col,row = pos_to_colrow(x, z)
        city = self.find_enemy_city(controller,col,row)
        if city:
            log_util.debug(f'find emeny: {controller.unit_id} -> {city.unit_name}')
            controller.get_blackboard().target_unit_id = city.unit_id
            controller.enter_state(AIState_MarchToCity())
        else:
            controller.enter_state(AIState_TroopDie())

# 行军, 先寻路，然后监控周围的敌人
class AIState_MarchToCity(AIState_Troop):
    def do_enter(self, controller):
        blackboard = controller.get_blackboard()

        city = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)
        troop = controller.get_unit()

        req = ArcMoveReq()
        req.setup(*troop.get_position(),
            *city.get_position(),
            troop.speed,
            city.radius + troop.radius)

        controller.move_comp = req
        controller.look_at_unit(city)
        #print_line(f'enter state: {controller.unit_id}')

    def update(self, controller):
        if controller.move_comp.is_done():
            controller.enter_state(AIState_AttackCity())

        blackboard = controller.get_blackboard()
        city = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)
        controller.look_at_unit(city)

# 解散
class AIState_TroopDie(AIState_Troop):
    def do_enter(self, controller):
        log_util.debug(f'kill {controller.unit_id}')
        controller.kill()

# 空闲
class AIState_Idle(AIState_Troop):
    def update(self, controller):
        #if random_100() < 4:
            #log_util.debug(f'idle {controller.get_unit().unit_name}')
        pass

#
# 攻城战
#
class AIState_AttackCity(AIState_Troop):
    def update(self, controller):
        blackboard = controller.get_blackboard()

        # 射箭
        if not blackboard.shoot_effect:
            path = 'res://effects/Shoot01.tscn'
            blackboard.shoot_effect = FNode3D.instantiate(path)
            blackboard.shoot_effect.reparent(controller.get_model_node())
            blackboard.shoot_effect.set_position(0, 0, 0)
            blackboard.shoot_effect.set_rotation(0, 0, 0)

        # 左右横移
        if not controller.move_comp or \
                controller.move_comp.is_done():
            city = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)
            troop = controller.get_unit()

            req = LeftRightMoveReq()
            req.setup(*troop.get_position(),
                *city.get_position(),
                troop.speed*0.25)

            controller.move_comp = req
            controller.look_at_unit(city)

        # 是否可以解散了
        troop_dismiss = False

        if game_mgr.sec_time - blackboard.attack_time > 2.4:
            blackboard.attack_time = game_mgr.sec_time

            troop = controller.get_unit()
            city = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)

            game_mgr.effect_mgr.play_effect1(
                *troop.get_position(),
                *city.get_position())

            game_mgr.game_play.troop_attack_city(troop, city)
            if city.army_amount.value <= 0:
                troop_dismiss = True

        # 超时直接结束战斗
        if blackboard.get_state_time() > 50:
            troop_dismiss = True

        # 队伍可以解散
        if troop_dismiss:
            controller.enter_state(AIState_TroopDie())

#
# 移动到目标位置, 然后警戒, 现在停在那里即可
#
class AIState_MoveToPos(AIState_Troop):
    def do_enter(self, controller):
        troop = controller.get_unit()
        blackboard = controller.get_blackboard()

        if not controller.move_comp:
            controller.move_comp = StepMoveReq()
        controller.move_comp.restart()

    def update(self, controller):
        if controller.move_comp.is_done():
            controller.goto_state('idle')
        elif controller.get_fight_comp().is_skill_ready():
            troop = controller.get_unit()
            blackboard = controller.get_blackboard()
            
            sight = controller.sight_comp
            for unit in sight.unit_dict.values():
                if not game_mgr.is_league(unit, troop):
                    blackboard.enemy_unit_id = unit.unit_id
                    
                    # 停下来, 原地射击, 等到目标死亡,离开, 再决策
                    controller.move_comp.complete()
                    controller.goto_state('shoot')
                    
                    break

#
# 起始,根据目标的设置,进行跳转
#
class AIState_TroopStart(AIState_Troop):
    def update(self, controller):
        troop = controller.get_unit()
        blackboard = controller.get_blackboard()

        if troop.target_unit_id > 0:
            blackboard.target_unit_id = troop.target_unit_id
            unit = game_mgr.unit_mgr.get_unit(troop.target_unit_id)
            blackboard.target_pos = unit.get_xz()
            #controller.enter_state(AIState_MarchToCity())
            #controller.enter_state(AIState_MoveToPos())
            controller.goto_state('move_to_pos')
        else:
            blackboard.target_unit_id = 0
            blackboard.target_pos = troop.target_pos
            #controller.enter_state(AIState_MoveToPos())
            controller.goto_state('move_to_pos')

#
# 射箭
#
class AIState_Shoot(AIState_Troop):
    def do_enter(self, controller):
        blackboard = controller.get_blackboard()
        fight_comp = controller.get_fight_comp()
        troop = controller.get_unit()
        
        # 检查技能cd, 攻击目标, 否则就结束
        #log_debug('shoot', fight_comp.is_skill_ready(), blackboard.enemy_unit_id)
        if fight_comp.is_skill_ready() and \
                blackboard.enemy_unit_id != 0:
            enemy_unit = game_mgr.unit_mgr.get_unit(blackboard.enemy_unit_id)
            effect_item = game_mgr.effect_mgr.play_effect2(2001)
            effect_item.set_position(*troop.get_position())
            effect_item.look_at(*enemy_unit.get_position())
            fight_comp.skill_cooldown = 4.0
            
        blackboard.shoot_time = 0
        
    def update(self, controller):
        blackboard = controller.get_blackboard()
        blackboard.shoot_time += game_mgr.delta_time
        
        #log_debug(blackboard.shoot_time)
        if blackboard.shoot_time > 0.3:
            controller.goto_state('start')




