#
# 2023年2月9日 bianepng
#
from game.core import *
from game.game_mgr import game_mgr
from game.coroutine_mgr import Waitable

# wait for seconds
class WaitForSeconds(Waitable):
    def __init__(self, sec):
        self.stop = sec + game_mgr.sec_time

    def is_done(self):
        return game_mgr.sec_time >= self.stop

def test_wait_1():
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

        print(f'{OS.get_time()} {game_mgr.sec_time}')
        yield WaitForSeconds(3)
        print(f'{OS.get_time()} {game_mgr.sec_time}')
        
    game_mgr.co_mgr.start(co_print_number())

