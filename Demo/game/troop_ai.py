#
# 2023年2月8日 bianpeng
#

from game.core import *
from game.base_type import *
from game.game_mgr import game_mgr

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

# troop ai 信息
class TroopBlackboard:
    def __init__(self):
        self.target_unit_id = 0

# 寻找一个目标城池
class AIState_FindCity(AIState):
    def find_enemy_city(self,controller,col,row):
        for i in range(3):
            for dx,dy in ring_range(i):
                tile = game_mgr.ground_mgr.get_tile_at_colrow(col+dx, row+dy)
                if tile:
                    for unit in tile.units:
                        if unit.unit_id != controller.unit.owner_city_id \
                                and unit.unit_type == 1:
                            return unit
        return None

    def update(self, controller):
        x,y,z = controller.unit.get_location()
        col,row = game_mgr.ground_mgr.get_colrow(x, z)
        city = self.find_enemy_city(controller,col,row)
        if city:
            print_line(f'find emeny: {controller.unit_id} -> {city.unit_name}')
            controller.ai_bb.target_unit_id = city.unit_id
            controller.ai_enter_state(AIState_MoveToCity())
        else:
            controller.ai_enter_state(AIState_Idle())

class AIState_AttackCity(AIState):
    def update(self, controller):
        pass

class AIState_MoveToCity(AIState):
    def enter(self, controller):
        bb = controller.ai_bb
        city = game_mgr.unit_mgr.get_unit(bb.target_unit_id)
        troop = controller.unit
       
        req = controller.move_req
        x,y,z = city.get_location();
        req.line_to(
            *troop.get_location(),
            x,y,z,
            troop.speed)
        
        Node3D.lookat(troop.get_node(), x,y,z)
        
        #print_line(f'enter state: {controller.unit_id}')
    def update(self, controller):
        pass

class AIState_Idle(AIState):
    def update(self, controller):
        if random_max(100) < 10:
            print_line(f'idle {controller.unit_id}')

