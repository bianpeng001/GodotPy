#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import Controller
from game.troop_ai import *

# 部队控制，包括特效，动作，位置，朝向...
class TroopController(Controller):
    def __init__(self):
        super().__init__()

        self.ai_tick_time = 0

        self.ai_bb = TroopBlackboard()
        self.ai_enter_state(AIState_FindCity())
        
        self.move_req = None

    def get_blackboard(self):
        return self.ai_bb

    def on_ai_tick(self, tick_time):
        #unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        #print_line(unit.unit_name)
        self.ai_state.update(self)

    def update_ai(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.1:
            self.on_ai_tick(self.ai_tick_time)
            self.ai_tick_time = 0

    def update_move(self):
        req = self.move_req
        if req and req.is_move:
            troop = self.unit
            delta = game_mgr.delta_time
            req.update(troop, delta)

    def update(self):
        self.update_ai()
        self.update_move()

    def look_at(self,x,y,z):
        if self.model_node:
            Node3D.look_at(self.model_node, x,y,z)

    def look_at_unit(self, unit):
        x,y,z = unit.get_location()
        self.look_at(x,y,z)

    def kill(self):
        self.unit.set_dead()

