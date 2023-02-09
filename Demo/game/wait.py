#
# 2023年2月9日 bianepng
#
from game.core import *
from game.game_mgr import game_mgr
from game.coroutine_mgr import Waitable

class WaitForSeconds(Waitable):
    def __init__(self, sec):
        self.stop = sec*1000 + game_mgr.time

    def is_done(self):
        return game_mgr.time >= self.stop

def co_print_number():
    print_line(game_mgr.frame_number)
    yield None
    print_line(game_mgr.frame_number)
    yield None
    print_line(game_mgr.frame_number)
    yield None
    print_line(game_mgr.frame_number)
    yield None
    print_line(game_mgr.frame_number)

    print_line(OS.get_time())
    yield WaitForSeconds(3)
    print_line(OS.get_time())

def test1():
    game_mgr.co_mgr.start(co_print_number())

