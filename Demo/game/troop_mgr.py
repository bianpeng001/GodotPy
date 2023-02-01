#
# 2023年2月1日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

#
class TroopMgr():
    def __init__(self):
        self.troops = {}

    def update(self, delta_time):
        pass
    
    def test(self):
        game_mgr.event_mgr.add('left_button_press', self.on_left_button_press)

    def on_left_button_press(self, x, y, *args):
        print_line(f'on_left_button_press: {x} {y}')
        print_line('on_left_button_press', x, y)
        game_mgr.event_mgr.remove('left_button_press', self.on_left_button_press)

