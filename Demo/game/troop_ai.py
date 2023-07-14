#
# 2023年2月8日 bianpeng
#

import math

from game.core import log_debug
from game.base_type import *
from game.game_mgr import *
from game.ground_mgr import xz_to_colrow

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
# 牛顿移动组件, 用物理来实现, 主要体现一个互斥
# 因为部队数量比较大, 后面性能上要追求下的话, 大不了改成c++的
#
class NewtonMoveComponent(MoveComponent):
    def __init__(self):
        super().__init__()
        
        # 目标点
        self._dst_pos = Vector3()
        self._cur_pos = Vector3()
        
        # 累加时长
        self.accu_time = 0
        self.block_time = 0
        
    def update(self, delta_time):
        controller = self.get_controller()
        troop = controller.get_unit()
        blackboard = controller.get_brain_comp().get_blackboard()
        
        if blackboard.target_unit_id > 0:
            unit = get_unit(blackboard.target_unit_id)
            self._dst_pos.set(*unit.get_position())
        else:
            x,z = blackboard.target_pos
            self._dst_pos.set(x,0,z)
        
        self._cur_pos.set(*troop.get_position())
        
        # 参数
        speed = troop.speed * game_mgr.config_mgr.troop_speed_scale
        unit_time = game_mgr.config_mgr.frame_seconds
        fix_block_speed = 0.16
        
        delta = self._dst_pos - self._cur_pos
        dis = delta.magnitude()
        if dis <= unit_time * speed:
            self.complete()
            return
        
        v_x = delta.x*(speed/dis) + controller.rvo_acce_x*unit_time
        v_z = delta.z*(speed/dis) + controller.rvo_acce_z*unit_time
        
        if self.block_time > 0:
            right = delta.cross(Vector3.y_axis) * \
                    (self.block_time*fix_block_speed/dis)
            v_x += right.x
            v_z += right.z
        
        self.accu_time += unit_time
        dx = v_x * self.accu_time
        dz = v_z * self.accu_time
        
        if dx*dx+dz*dz > 0.00005:
            x,y,z = self._cur_pos.x+dx,self._cur_pos.y,self._cur_pos.z+dz
            controller.look_at(x,y,z)
            troop.set_position(x,y,z)
            
            self.accu_time = 0
            self.block_time = max(0, self.block_time-unit_time*0.5)
        else:
            # 动不了
            if self.accu_time > 0:
                self.block_time = min(8, self.block_time+unit_time)

#
# 小步前进, 考虑rvo斥力和障碍
#
class StepMoveComponent(MoveComponent):
    def __init__(self):
        super().__init__()
        
        # 卡主的数量, 如果卡主次数太多了, 还是需要缓缓方向
        # 卡主的次数
        self.block_count = 0
        # 卡主后的累计时长
        self.accu_time = 0
        self.block_time = 0
    
    # 这段这么恶心, 建议放到c++里面去算
    def update(self, troop, delta_time):
        controller = troop.get_controller()
        blackboard = controller.get_brain_comp().get_blackboard()
        
        if blackboard.target_unit_id > 0:
            unit = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)
            dst_pos = Vector3(*unit.get_position())
        else:
            x,z = blackboard.target_pos
            dst_pos = Vector3(x,0,z)
            
        cur_pos = Vector3(*troop.get_position())
        delta = dst_pos - cur_pos

        # 参数
        unit_time = game_mgr.config_mgr.frame_seconds
        start_fix_time = game_mgr.config_mgr.start_fix_time
        fix_block_step = game_mgr.config_mgr.fix_block_step
        
        dis = delta.magnitude()
        if dis <= unit_time*troop.speed:
            self.complete()
            return
        
        num_time = self.block_time-start_fix_time
        if num_time > 0:
            right = delta.cross(Vector3.y_axis) * \
                    (num_time * fix_block_step)
            delta.x += right.x
            delta.z += right.z
            dis = delta.magnitude()

        self.accu_time += unit_time
        v = delta * (troop.speed/dis)
        # 计算rvo的加速对速度增量, 
        # 这里的*delta_time, 因为比较固定, 感觉可以当做常量合并到rvo_factor
        v.x += controller.rvo_acce_x*unit_time
        v.z += controller.rvo_acce_z*unit_time

        d = v * self.accu_time
        if d.sqr_magnitude() > 0.00005:
            x = cur_pos.x+d.x
            y = cur_pos.y
            z = cur_pos.z+d.z
            controller.look_at(x, y, z)
            troop.set_position(x, y, z)
            
            self.accu_time = 0
            self.block_time = max(0, self.block_time-2*unit_time)
        else:
            self.block_time += unit_time
            
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
        return game_mgr.time_sec - self.state_start_time

#
# troop的state的基类，在enter里面记录开始时间
#
class AIState_Troop(AIState):
    def enter(self, brain_comp):
        blackboard = brain_comp.get_blackboard()
        blackboard.state_start_time = game_mgr.time_sec
        
        self.do_enter(brain_comp)

    def do_enter(self, brain_comp):
        pass

# 寻找一个目标城池
class AIState_FindCity(AIState_Troop):
    # 从内而外的一圈圈的找目标
    def find_enemy_city(self,brain_comp,col,row):
        owner_player_id = brain_comp.get_unit().owner_player_id
        
        for dx,dy in narudo_range(4):
            tile = game_mgr.ground_mgr.get_tile_colrow(col+dx, row+dy)
            if not tile:
                continue
            for unit in tile.get_unit_list():
                if unit.unit_type == UT_CITY and \
                        (unit.owner_player_id == 0 or \
                        unit.owner_player_id != owner_player_id):
                    return unit

    def update(self, brain_comp):
        x,y,z = brain_comp.get_unit().get_position()
        col,row = xz_to_colrow(x, z)
        city = self.find_enemy_city(brain_comp,col,row)
        if city:
            log_util.debug(f'find emeny: {brain_comp.get_unit().unit_id} -> {city.unit_name}')
            brain_comp.get_blackboard().target_unit_id = city.unit_id
            brain_comp.enter_state(AIState_MarchToCity())
        else:
            brain_comp.enter_state(AIState_TroopDie())

# 行军, 先寻路，然后监控周围的敌人
class AIState_MarchToCity(AIState_Troop):
    def do_enter(self, brain_comp):
        blackboard = brain_comp.get_blackboard()
        troop = brain_comp.get_unit()

        city = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)

        req = ArcMoveReq()
        req.setup(*troop.get_position(),
            *city.get_position(),
            troop.speed,
            city.radius + troop.radius)

        brain_comp.get_controller().move_comp = req
        brain_comp.get_controller().look_at_unit(city)
        #print_line(f'enter state: {controller.unit_id}')

    def update(self, brain_comp):
        if brain_comp.get_controller().move_comp.is_done():
            brain_comp.enter_state(AIState_AttackCity())

        blackboard = brain_comp.get_blackboard()
        city = game_mgr.unit_mgr.get_unit(blackboard.target_unit_id)
        brain_comp.get_controller().look_at_unit(city)

# 解散
class AIState_TroopDie(AIState_Troop):
    def do_enter(self, brain_comp):
        log_util.debug(f'kill {brain_comp.get_unit().unit_id}')
        brain_comp.get_controller().kill()

# 空闲
class AIState_Idle(AIState_Troop):
    def update(self, brain_comp):
        #if random_100() < 4:
            #log_util.debug(f'idle {controller.get_unit().unit_name}')
        pass

#
# 攻城战
#
class AIState_AttackCity(AIState_Troop):
    def update(self, brain_comp):
        blackboard = brain_comp.get_blackboard()
        controller = brain_comp.get_controller()

        # 射箭
        if not blackboard.shoot_effect:
            path = 'res://effects/Shoot01.tscn'
            blackboard.shoot_effect = OS.instantiate(path)
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

        if game_mgr.time_sec - blackboard.attack_time > 2.4:
            blackboard.attack_time = game_mgr.time_sec

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
    def do_enter(self, brain_comp):
        controller = brain_comp.get_controller()
        troop = controller.get_unit()
        blackboard = brain_comp.get_blackboard()

        if not controller.move_comp:
            #controller.move_comp = StepMoveComponent()
            controller.move_comp = NewtonMoveComponent()
            controller.move_comp.setup(controller)
        controller.move_comp.restart()

    def update(self, brain_comp):
        controller = brain_comp.get_controller()
        
        
        if controller.move_comp.is_done():
            brain_comp.goto_state('idle')
        elif controller.get_fight_comp().is_skill_ready():
            blackboard = brain_comp.get_blackboard()
            troop = controller.get_unit()
            
            sight_comp = controller.sight_comp
            for unit in sight_comp.loop_units():
                if not game_mgr.is_league(unit, troop):
                    blackboard.enemy_unit_id = unit.unit_id
                    
                    # 停下来, 原地射击, 等到目标死亡,离开, 再决策
                    controller.move_comp.complete()
                    brain_comp.goto_state('shoot')
                    
                    break

#
# 起始,根据目标的设置,进行跳转
#
class AIState_TroopStart(AIState_Troop):
    def update(self, brain_comp):
        controller = brain_comp.get_controller()
        troop = controller.get_unit()
        blackboard = controller.get_brain_comp().get_blackboard()

        if troop.target_unit_id > 0:
            blackboard.target_unit_id = troop.target_unit_id
            unit = game_mgr.unit_mgr.get_unit(troop.target_unit_id)
            blackboard.target_pos = unit.get_xz()
            #controller.enter_state(AIState_MarchToCity())
            #controller.enter_state(AIState_MoveToPos())
            brain_comp.goto_state('move_to_pos')
        else:
            blackboard.target_unit_id = 0
            blackboard.target_pos = troop.target_pos
            #controller.enter_state(AIState_MoveToPos())
            brain_comp.goto_state('move_to_pos')

#
# 射箭
#
class AIState_Shoot(AIState_Troop):
    def do_enter(self, brain_comp):
        controller = brain_comp.get_controller()
        blackboard = brain_comp.get_blackboard()
        fight_comp = controller.get_fight_comp()
        troop = controller.get_unit()
        
        # 检查技能cd, 攻击目标, 否则就结束
        #log_debug('shoot', fight_comp.is_skill_ready(), blackboard.enemy_unit_id)
        if fight_comp.is_skill_ready() and \
                blackboard.enemy_unit_id != 0:
            enemy_unit = game_mgr.unit_mgr.get_unit(blackboard.enemy_unit_id)
            game_mgr.game_play.cast_skill(3001, troop, enemy_unit)
            
        blackboard.shoot_time = 0
        
    def update(self, brain_comp):
        blackboard = brain_comp.get_blackboard()
        blackboard.shoot_time += game_mgr.delta_time
        
        #log_debug(blackboard.shoot_time)
        if blackboard.shoot_time > 0.3:
            brain_comp.goto_state('start')




