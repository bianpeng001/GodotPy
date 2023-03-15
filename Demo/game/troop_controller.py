#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import Controller
from game.troop_ai import *
from game.ground_mgr import pos_to_colrow

# 部队控制，包括特效，动作，位置，朝向...
class TroopController(Controller):
    def __init__(self):
        super().__init__()

        # AI 相关
        self.ai_tick_time = 0
        self.ai_bb = TroopBlackboard()
        self.ai_enter_state(AIState_FindCity())
        
        # 位移请求
        self.move_req = None

        # 所在的地块
        self.owner_tile = None

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
            req.update(troop, game_mgr.delta_time)

            # 刷新tile归属
            x,z = troop.unit_position.get_xz()
            col,row = pos_to_colrow(x,z)
            if self.owner_tile:
                if self.owner_tile.col != col or \
                        self.owner_tile.row != row:
                    self.owner_tile.unit_list.remove(troop)
                    self.owner_tile, _ = game_mgr.ground_mgr.create_tile(col,row)
                    self.owner_tile.unit_list.append(troop)
            else:
                self.owner_tile, _ = game_mgr.ground_mgr.create_tile(col,row)
                self.owner_tile.unit_list.append(troop)

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

