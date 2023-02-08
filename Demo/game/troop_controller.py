#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import Controller, AIState

# 定义一下移动需要的信息
class MoveReq:
    def __init__(self):
        self.is_done = True
        self.start = Vector3()
        
        self.target_pos = Vector3()
        self.target_unit_id = 0

        self.v = Vector3()
        self.time = 0

        self.path = None

    # 请求走直线
    def move_line(self, x,y,z):
        pass

    def move_path(self, path):
        pass

# 攻击信息
class AttackReq:
    def __init__(self):
        self.target_unit_id = 0

# 寻找一个目标城池
class AIState_FindCity(AIState):
    def update(self, controller):
        pass

class AIState_AttackCity(AIState):
    def update(self, controller):
        pass

# 部队
class TroopController(Controller):
    def __init__(self):
        super().__init__()

        self.ai_tick_time = 0
        self.ai_enter_state(AIState_FindCity())

        self.move_req = MoveReq()

    def ai_enter_state(self, new_state):
        if self.ai_state:
            self.ai_state.leave(self)
            self.ai_state = None

        self.ai_state = new_state

        if self.ai_state:
            self.ai_state.enter(self)

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
        if req.is_done:
            return

        troop = self.unit
        delta = game_mgr.delta_time

        x,y,z = troop.get_location()
        x += troop.velocity.x * delta
        y += troop.velocity.y * delta
        z += troop.velocity.z * delta
        troop.set_location(x,y,z)

    def update(self):
        self.update_ai()
        self.update_move()


