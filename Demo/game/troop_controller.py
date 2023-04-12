#
# 2023年2月1日 bianpeng
#

from game.core import log_debug
from game.game_mgr import *
from game.base_type import Controller
from game.troop_ai import *

#
# 这是一个AIController
# 部队控制，包括特效，动作，位置，朝向...
#
class TroopController(Controller):
    def __init__(self):
        super().__init__()

        # AI 相关
        self.reset_ai()
        # 位移请求
        self.move_req = None

        # 所在的地块
        self.owner_tile = None
        
        #
        self.sight_tick_time = 0
        self.sight_angle = 0
        self.sight_angle_speed = 0.3

    def reset_ai(self):
        self.ai_tick_time = 0
        self.blackboard = TroopBlackboard()
        self.enter_state(AIState_TroopStart())

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
        req = self.move_req
        if req and not req.is_done():
            troop = self.get_unit()
            # 位置朝向
            req.update(troop, game_mgr.delta_time)

            # 位置变更之后,刷新tile归属
            x,z = troop.unit_position.get_xz()
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
        self.viewarea_obj = node.find_node('ViewArea')
        if node:
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
        self.update_sight()

    # 视觉感知
    def update_sight(self):
        # 移动过程里, 还要检查周围的敌军, 有一个视野
        self.sight_angle += self.sight_angle_speed
        if self.sight_angle >= 30 or self.sight_angle <= -30:
            self.sight_angle_speed *= -1
        self.viewarea_obj.set_rotation(0, self.sight_angle, 0)
        
        self.sight_tick_time += game_mgr.delta_time
        if self.sight_tick_time > 0.1:
            self.sight_tick_time = 0
            
            if self.owner_tile:
                pass

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



