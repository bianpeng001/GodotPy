#
# 2023年2月9日 bianepng
#
from game.core import *
from game.game_mgr import game_mgr
from game.coroutine_mgr import Waitable

# wait for seconds
class WaitForSeconds(Waitable):
    def __init__(self, sec):
        self.stop = sec*1000 + game_mgr.time

    def is_done(self):
        return game_mgr.time >= self.stop

def test1():
    def co_print_number():
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)

        print(OS.get_time())
        yield WaitForSeconds(3)
        print(OS.get_time())
    game_mgr.co_mgr.start(co_print_number())

