#
# 2023年2月8日 bianpeng
#

from game.core import *
from game.base_type import *
from game.game_mgr import game_mgr

# 移动方式
class BaseMoveReq:
    def __init__(self):
        self.is_move = True

        self.start = None
        self.stop = None
        self.delta = None

        self.progress = 0
        self.time_to_progress = 1

# 直线
class LineMoveReq(BaseMoveReq):
    def update(self, troop, delta_time):
        pass

    def setup(self, x0,y0,z0,x1,y1,z1, speed):
        self.start = Vector3(x0,y0,z0)
        self.stop = Vector3(x1,y1,z1)
        self.delta = self.stop - self.start

        mag = self.delta.magnitude()
        mag1 = mag - 6
        if mag1 < 0:
            self.is_move = False
            return

        self.delta = self.delta * (mag1 / mag)
        self.time_to_progress = speed / mag1

        self.is_move = True


# 模拟弧线
class ArcMoveReq(BaseMoveReq):
    def __init__(self):
        super().__init__()
        
        self.right = None

    def setup(self,x0,y0,z0,x1,y1,z1, speed):
        self.start = Vector3(x0,y0,z0)
        self.stop = Vector3(x1,y1,z1)
        self.delta = self.stop - self.start

        mag = self.delta.magnitude()
        mag1 = mag - 6
        if mag1 < 0:
            self.is_move = False
            return

        duration = mag1 / speed
        self.delta = self.delta * (mag1 / mag)
        self.time_to_progress = 1.0 / duration
        self.right = self.delta.cross(Vector3.up).normlized() * 2

        self.is_move = True

    def update(self, troop, delta_time):
        self.progress += delta_time * self.time_to_progress
        if self.progress < 1.0:
            x = 2*self.progress - 1
            #y = math.sqrt(1 - x*x)
            y = 1 - x*x

            p = self.start + \
                self.delta * self.progress + \
                self.right * y
            troop.set_location(p.x,p.y,p.z)
        else:
            p = self.start + self.delta
            troop.set_location(p.x,p.y,p.z)
            self.is_move = False


# 左右移动
class LeftRightMoveReq(BaseMoveReq):
    def setup(self, x0,y0,z0, x1,y1,z1, speed):
        self.is_left = True

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
        self.is_move = True

    def reset(self, v0):
        self.stop_index = (self.stop_index + 1) % 2

        self.start = v0
        self.stop = self.stops[self.stop_index]
        self.delta = self.stop - self.start

        duration = self.delta.magnitude() / self.speed
        self.time_to_progress = 1.0 / duration
        self.progress = 0


    def update(self, troop, delta_time):
        self.progress += delta_time * self.time_to_progress
        if self.progress < 1.0:
            p = self.start + self.delta * self.progress
            troop.set_location(p.x,p.y,p.z)
            
            t = self.target
            troop.get_controller().look_at(t.x,t.y,t.z)
        else:
            self.reset(self.stop)


# 遍历一周，顺序如下
# 012
# 7X3
# 654
def ring_range(n):
    s = 2 * n
    for i in range(s):
        yield -n + i, -n
    for i in range(s):
        yield n, -n + i
    for i in range(s):
        yield n - i, n
    for i in range(s):
        yield -n, n - i

# 黑板，用于读写信息，状态之间传递数据
class TroopBlackboard(AIBlackboard):
    def __init__(self):
        self.target_unit_id = 0
        self.state_start_time = 0
        self.shoot_effect = None

    # 状态持续时间
    def get_state_time(self):
        return game_mgr.time - self.state_start_time

# troop的state的基类，在enter里面记录开始时间
class AIState_Troop(AIState):
    def enter(self, controller):
        bb = controller.get_blackboard()
        bb.state_start_time = game_mgr.time

        self.do_enter(controller, bb)

    def do_enter(self, controller, bb):
        pass

# 寻找一个目标城池
class AIState_FindCity(AIState_Troop):
    def find_enemy_city(self,controller,col,row):
        owner_city_id = controller.unit.owner_city_id
        for i in range(3):
            for dx,dy in ring_range(i):
                tile = game_mgr.ground_mgr.get_tile_at_colrow(col+dx, row+dy)
                if not tile:
                    continue
                for unit in tile.units:
                    if unit.unit_type == 1 and\
                            unit.unit_id != owner_city_id:
                        return unit
        return None

    def update(self, controller):
        x,y,z = controller.unit.get_location()
        col,row = game_mgr.ground_mgr.get_colrow(x, z)
        city = self.find_enemy_city(controller,col,row)
        if city:
            logutil.debug(f'find emeny: {controller.unit_id} -> {city.unit_name}')
            controller.ai_bb.target_unit_id = city.unit_id
            controller.ai_enter_state(AIState_MatchToCity())
        else:
            controller.ai_enter_state(AIState_TroopDie())

# 行军, 先寻路，然后监控周围的敌人
class AIState_MatchToCity(AIState_Troop):
    def do_enter(self, controller, bb):
        city = game_mgr.unit_mgr.get_unit(bb.target_unit_id)
        troop = controller.unit
       
        req = ArcMoveReq()
        req.setup(*troop.get_location(),
            *city.get_location(),
            troop.speed)

        controller.move_req = req
        controller.look_at_unit(city)

        #print_line(f'enter state: {controller.unit_id}')
    def update(self, controller):
        if not controller.move_req.is_move:
            controller.ai_enter_state(AIState_AttackCity())

        bb = controller.get_blackboard()
        city = game_mgr.unit_mgr.get_unit(bb.target_unit_id)
        controller.look_at_unit(city)

# 解散
class AIState_TroopDie(AIState_Troop):
    def do_enter(self, controller, bb):
        logutil.debug(f'kill {controller.unit_id}')
        controller.kill()

# 空闲
class AIState_Idle(AIState_Troop):
    def update(self, controller):
        if random_max(100) < 10:
            logutil.debug(f'idle {controller.unit_id}')

#------------------------------------------------------------
# 攻城战
#------------------------------------------------------------
class AIState_AttackCity(AIState_Troop):
    def update(self, controller):
        bb = controller.get_blackboard()

        # 射箭
        if not bb.shoot_effect:
            bb.shoot_effect = instantiate('res://effect/Shoot01.tscn')
            Node.reparent(bb.shoot_effect, controller.model_node)

        # 左右横移
        if not controller.move_req or \
                not controller.move_req.is_move:
            city = game_mgr.unit_mgr.get_unit(bb.target_unit_id)
            troop = controller.unit

            req = LeftRightMoveReq()
            req.setup(*troop.get_location(),
                *city.get_location(),
                troop.speed*0.25)

            controller.move_req = req
            controller.look_at_unit(city)

        # 结束战斗
        if bb.get_state_time() > 30000:
            controller.ai_enter_state(AIState_TroopDie())


