#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.base_type import Controller
from game.troop_ai import *

# 定义一下移动需要的信息
class MoveReq:
    def __init__(self):
        self.is_run = False
        self.start = Vector3()
        self.stop = Vector3()

        #self.target_unit_id = 0

        self.progress = 0
        self.time_scale = 1
        self.delta = Vector3()

    # 请求走直线
    def line_to(self, x0,y0,z0,x,y,z,speed):
        self.is_run = True
        self.progress = 0

        self.start.set(x0,y0,z0)
        self.stop.set(x,y,z)
        self.delta = self.stop - self.start

        len1 = self.delta.length()
        len2 = len1 - 5
        if len2 > 0:
            self.delta = self.delta.scaled(len2/len1)
            self.time_to_progress = speed / len2
        else:
            self.is_run = False

    def move_path(self, path):
        pass

    def update(self, troop, delta_time):
        self.progress += delta_time * self.time_to_progress
        if self.progress < 1.0:
            p = self.start + self.delta.scaled(self.progress)
        else:
            p = self.start + self.delta
            self.is_run = False
        troop.set_location(p.x,p.y,p.z)

# 部队
class TroopController(Controller):
    def __init__(self):
        super().__init__()

        self.ai_tick_time = 0

        self.ai_bb = TroopBlackboard()
        self.ai_enter_state(AIState_FindCity())
        
        self.move_req = MoveReq()

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
        if req.is_run:
            troop = self.unit
            delta = game_mgr.delta_time
            req.update(troop, delta)

    def update(self):
        self.update_ai()
        self.update_move()

    def lookat(self,x,y,z):
        Node3D.lookat(self.model_node, x,y,z)

    def kill(self):
        self.unit.set_dead()

