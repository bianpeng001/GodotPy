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
            troop = self.get_unit()
            delta = game_mgr.delta_time
            req.update(troop, delta)

    def start(self):
        node = self.get_model_node()
        if node:
            anim_name = "SoldierAnimLib/Run"
            if self.get_unit().model_type == 2:
                for i in range(2, 11):
                    node_path = f"Soldier{i:02}/Model/AnimationPlayer"

                    anim_player = node.find_node(node_path)
                    if anim_player:
                        anim_player.play(anim_name)
                        anim_player.set_speed_scale(2.6)
            else:
                pass

    def update(self):
        self.update_move()
        self.update_ai()

    def look_at(self,x,y,z):
        node = self.get_model_node()
        if node:
            node.look_at(x,y,z)


    def look_at_unit(self, unit):
        x,y,z = unit.get_position()
        self.look_at(x,y,z)

    def kill(self):
        self.get_unit().set_dead()

