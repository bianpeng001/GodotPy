#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr
from game.input_mgr import LEFT_BUTTON_DRAG, LEFT_BUTTON_PRESS

#
class TroopMgr():
    def __init__(self):
        self.troop_map = {}
        self.troop_id_seed = 100

    def add(self, troop):
        troop.troop_id = self.troop_id_seed
        self.troop_id_seed += 1

        self.troop_map[troop.troop_id] = troop

    def update(self, delta_time):
        pass
    
    def test(self):
        game_mgr.event_mgr.add(LEFT_BUTTON_PRESS, self.on_left_button_press)
        game_mgr.event_mgr.add(LEFT_BUTTON_DRAG, self.on_left_button_drag)

    def on_left_button_press(self, x, y, *args):
        print_line('on_left_button_press', x, y)
        #game_mgr.event_mgr.remove(LEFT_BUTTON_PRESS, self.on_left_button_press)

    def on_left_button_drag(self, *args):
        print_line('on_left_button_drag')
